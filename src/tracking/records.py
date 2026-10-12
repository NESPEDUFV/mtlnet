"""Best-run record tracking for engine+state result directories.

Scans ``full_summary.json`` files across training runs to identify per-task
F1 records, compares the current run against historical bests, and persists
the record state to ``best_record.json`` at the engine+state root.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class TaskRecord:
    """Comparison result for a single task."""

    task: str
    current_f1: float
    previous_best_f1: float  # 0.0 if no prior runs
    previous_best_run: str  # folder name of prior best, "" if none
    is_new_record: bool


@dataclass
class RecordComparison:
    """Aggregated comparison across all tasks in a run."""

    tasks: List[TaskRecord] = field(default_factory=list)

    @property
    def any_new_record(self) -> bool:
        return any(t.is_new_record for t in self.tasks)


def _build_task_entry(
    f1_mean: float,
    task_summary: Dict,
    run_folder: str,
    now: str,
) -> Dict:
    """Build a single task entry for ``best_record.json``."""
    return {
        "f1_mean": f1_mean,
        "f1_std": task_summary.get("f1", {}).get("std", 0.0),
        "accuracy_mean": task_summary.get("accuracy", {}).get("mean", 0.0),
        "run_folder": run_folder,
        "updated_at": now,
    }


def _write_record(record_path: Path, tasks_record: Dict, now: str) -> Path:
    """Write the ``best_record.json`` file."""
    record = {
        "last_updated": now,
        "tasks": tasks_record,
    }
    record_path.write_text(
        json.dumps(record, indent=4, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return record_path


def scan_previous_bests(
    results_dir: Path,
    exclude_folder: str = "",
) -> Dict[str, Tuple[float, str]]:
    """Scan all ``full_summary.json`` in *results_dir*, return per-task best.

    Returns ``{task: (best_mean_f1, run_folder_name)}``.
    *exclude_folder* is the current run's folder name — skipped to avoid
    self-comparison.
    """
    bests: Dict[str, Tuple[float, str]] = {}

    for summary_path in sorted(results_dir.glob("*/summary/full_summary.json")):
        run_folder = summary_path.parent.parent.name
        if run_folder == exclude_folder:
            continue
        try:
            data = json.loads(summary_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Skipping unreadable summary %s: %s", summary_path, exc)
            continue

        for task, metrics in data.items():
            if not isinstance(metrics, dict):
                continue
            f1_block = metrics.get("f1")
            if not isinstance(f1_block, dict):
                continue
            f1_mean = f1_block.get("mean")
            if not isinstance(f1_mean, (int, float)):
                continue
            prev_best, _ = bests.get(task, (0.0, ""))
            if f1_mean > prev_best:
                bests[task] = (f1_mean, run_folder)

    return bests


def _load_task_summary(results_dir: Path, run_folder: str, task: str) -> Dict:
    """Read the task's block from a run's ``full_summary.json``."""
    summary_path = results_dir / run_folder / "summary" / "full_summary.json"
    if not summary_path.exists():
        return {}
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
        return data.get(task, {})
    except (json.JSONDecodeError, OSError):
        return {}


def compare_records(
    results_dir: Path,
    current_summary: Dict,
    current_folder: str,
) -> RecordComparison:
    """Compare the current run's metrics against historical bests.

    *current_summary* is the parsed ``full_summary.json`` of the current run.
    """
    previous = scan_previous_bests(results_dir, exclude_folder=current_folder)
    comparison = RecordComparison()

    for task, metrics in current_summary.items():
        if not isinstance(metrics, dict):
            continue
        f1_block = metrics.get("f1")
        if not isinstance(f1_block, dict):
            continue
        current_f1 = f1_block.get("mean", 0.0)
        if not isinstance(current_f1, (int, float)):
            continue

        prev_f1, prev_run = previous.get(task, (0.0, ""))
        # A degenerate run (F1=0.0) is never a meaningful record.
        # For a genuine first run (no previous), only mark as record if F1 > 0.
        is_new = current_f1 > prev_f1 if prev_run != "" else current_f1 > 0.0

        comparison.tasks.append(TaskRecord(
            task=task,
            current_f1=current_f1,
            previous_best_f1=prev_f1,
            previous_best_run=prev_run,
            is_new_record=is_new,
        ))

    return comparison


def save_best_record(
    results_dir: Path,
    comparison: RecordComparison,
    current_summary: Dict,
    current_folder: str,
) -> Optional[Path]:
    """Write/update ``results_dir/best_record.json`` with per-task bests.

    Returns the path if written, ``None`` if nothing changed.
    """
    if not comparison.any_new_record:
        return None

    record_path = results_dir / "best_record.json"
    now = datetime.now().isoformat(timespec="seconds")

    # Load existing record if present.
    existing: Dict = {}
    if record_path.exists():
        try:
            existing = json.loads(record_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    tasks_record = existing.get("tasks", {})

    for tr in comparison.tasks:
        if tr.is_new_record:
            task_summary = current_summary.get(tr.task, {})
            tasks_record[tr.task] = _build_task_entry(
                tr.current_f1, task_summary, current_folder, now,
            )

    return _write_record(record_path, tasks_record, now)


def compute_best_record(results_dir: Path) -> Path:
    """Standalone: scan all runs in *results_dir*, write ``best_record.json``.

    Useful for the pipeline script to compute records outside of a training run.
    Returns the path to the written ``best_record.json``.
    """
    bests = scan_previous_bests(results_dir, exclude_folder="")
    now = datetime.now().isoformat(timespec="seconds")

    tasks_record = {}
    for task, (f1_mean, run_folder) in bests.items():
        task_summary = _load_task_summary(results_dir, run_folder, task)
        tasks_record[task] = _build_task_entry(f1_mean, task_summary, run_folder, now)

    return _write_record(results_dir / "best_record.json", tasks_record, now)
