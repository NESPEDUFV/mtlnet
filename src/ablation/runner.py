"""Run staged MTL ablations from the candidate matrix.

This module is the execution engine used by the canonical script entrypoint
(`scripts/run_mtl_ablation.py`).
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field, fields as dc_fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_logger = logging.getLogger(__name__)

from ablation._utils import format_cli_value

_root = Path(__file__).resolve().parents[2]
_src = str(_root / "src")
if _src in sys.path:
    sys.path.remove(_src)
sys.path.insert(0, _src)
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from ablation.candidates import (
    HeadCandidate,
    MTLCandidate,
    get_candidate,
    get_head_candidate,
    iter_candidates,
    iter_head_candidates,
)


@dataclass
class AblationResult:
    candidate: str
    stage: str
    epochs: int
    folds: int
    seed: int | None
    status: str
    returncode: int
    run_dir: str
    log_file: str
    duration_seconds: float
    command: str
    joint_score: float | None = None
    next_f1: float | None = None
    category_f1: float | None = None
    error: str = ""


def _default_results_root() -> Path:
    return _root / "results" / "ablations"


def _default_data_root() -> Path:
    return Path(os.environ.get("DATA_ROOT", str(_root / "data")))


def _default_output_dir() -> Path:
    return Path(os.environ.get("OUTPUT_DIR", str(_root / "output")))


@dataclass(frozen=True)
class AblationRunConfig:
    """Execution config for a staged ablation run."""

    state: str = "alabama"
    engine: str = "dgi"
    stage: str = "phase1"
    candidate_names: tuple[str, ...] = ()
    epochs: int = 10
    folds: int = 1
    seed: int | None = None
    embedding_dim: int | None = None
    promote_top: int = 0
    promote_epochs: int = 15
    promote_folds: int = 2
    timeout_seconds: int | None = None  # per-candidate subprocess timeout
    results_root: Path = field(default_factory=_default_results_root)
    data_root: Path = field(default_factory=_default_data_root)
    output_dir: Path = field(default_factory=_default_output_dir)



def _candidate_argv(
    candidate: MTLCandidate,
    state: str,
    engine: str,
    epochs: int,
    folds: int,
    seed: int | None,
    embedding_dim: int | None = None,
) -> list[str]:
    argv = [
        sys.executable,
        "scripts/train.py",
        "--task",
        "mtl",
        "--state",
        state,
        "--engine",
        engine,
        "--epochs",
        str(epochs),
        "--folds",
        str(folds),
        "--model",
        candidate.model_name,
        "--mtl-loss",
        candidate.mtl_loss,
    ]
    if seed is not None:
        argv.extend(["--seed", str(seed)])
    if embedding_dim is not None:
        argv.extend(["--embedding-dim", str(embedding_dim)])
    # CAGrad / Aligned-MTL / PCGrad require per-step gradient surgery and are
    # incompatible with gradient accumulation >1. Force accumulation=1 for
    # these losses so ablation runs complete instead of crashing.
    if candidate.mtl_loss in {"cagrad", "aligned_mtl", "pcgrad"}:
        argv.extend(["--gradient-accumulation-steps", "1"])
    for key, value in candidate.model_params.items():
        argv.extend(["--model-param", f"{key}={format_cli_value(value)}"])
    for key, value in candidate.mtl_loss_params.items():
        if candidate.mtl_loss == "static_weight" and key == "category_weight":
            argv.extend(["--category-weight", str(value)])
        else:
            argv.extend(["--mtl-loss-param", f"{key}={format_cli_value(value)}"])
    return argv


def _latest_run_dir(candidate_root: Path, engine: str, state: str, epochs: int) -> Path | None:
    state_root = candidate_root / engine / state
    if not state_root.exists():
        return None
    runs = [
        path
        for path in state_root.iterdir()
        if path.is_dir() and f"_ep{epochs}_" in path.name
    ]
    if not runs:
        return None
    return max(runs, key=lambda path: path.stat().st_mtime)


def _execute_subprocess(
    argv: list[str],
    candidate_name: str,
    candidate_root: Path,
    label_root: Path,
    seed: int | None,
    data_root: Path,
    output_dir: Path,
    engine: str,
    state: str,
    epochs: int,
    timeout_seconds: int | None,
) -> tuple[subprocess.CompletedProcess | None, Path, float, Path | None]:
    """Run a training subprocess, redirect output to a log file, and return metadata.

    Returns ``(proc, log_file, duration, run_dir)``.  ``proc`` is ``None`` on timeout.
    """
    log_dir = label_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    seed_tag = f"_seed{seed}" if seed is not None else ""
    log_file = log_dir / f"{candidate_name}{seed_tag}.log"

    env = os.environ.copy()
    env["DATA_ROOT"] = str(data_root)
    env["OUTPUT_DIR"] = str(output_dir)
    env["RESULTS_ROOT"] = str(candidate_root)
    env["PYTHONPATH"] = f"{_root / 'src'}:{_root}"

    started = time.time()
    proc: subprocess.CompletedProcess | None = None
    with log_file.open("w", encoding="utf-8") as log:
        log.write("$ " + " ".join(argv) + "\n\n")
        try:
            proc = subprocess.run(
                argv,
                cwd=_root,
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            log.write(f"\n[ablation] TIMED OUT after {timeout_seconds}s\n")
            _logger.warning("[ablation] %s timed out after %ss", candidate_name, timeout_seconds)

    duration = time.time() - started
    run_dir = _latest_run_dir(candidate_root, engine, state, epochs)
    return proc, log_file, duration, run_dir


def _parse_metrics(
    run_dir: Path | None,
    candidate_name: str = "",
) -> tuple[float | None, float | None, float | None]:
    if run_dir is None:
        _logger.warning("[ablation] no run directory found for %s", candidate_name)
        return None, None, None
    summary_path = run_dir / "summary" / "full_summary.json"
    if not summary_path.exists():
        _logger.warning("[ablation] summary not found: %s", summary_path)
        return None, None, None
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _logger.warning("[ablation] failed to parse %s: %s", summary_path, exc)
        return None, None, None
    next_f1 = data.get("next", {}).get("f1", {}).get("mean")
    category_f1 = data.get("category", {}).get("f1", {}).get("mean")
    # Prefer the pre-computed joint_score from the summary; fall back to equal weighting.
    joint_score = data.get("model", {}).get("joint_score", {}).get("mean")
    if joint_score is None and next_f1 is not None and category_f1 is not None:
        joint_score = 0.5 * (float(next_f1) + float(category_f1))
    return joint_score, next_f1, category_f1


def _write_summary(path: Path, rows: list[AblationResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [f.name for f in dc_fields(AblationResult)]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _load_summary(path: Path) -> list[AblationResult]:
    """Load completed results from an existing summary CSV."""
    if not path.exists():
        return []
    rows: list[AblationResult] = []
    try:
        with path.open(encoding="utf-8", newline="") as f:
            for record in csv.DictReader(f):
                try:
                    rows.append(AblationResult(
                        candidate=record["candidate"],
                        stage=record["stage"],
                        epochs=int(record["epochs"]),
                        folds=int(record["folds"]),
                        seed=int(record["seed"]) if record.get("seed") else None,
                        status=record["status"],
                        returncode=int(record["returncode"]),
                        run_dir=record["run_dir"],
                        log_file=record["log_file"],
                        duration_seconds=float(record["duration_seconds"]),
                        command=record["command"],
                        joint_score=float(record["joint_score"]) if record.get("joint_score") else None,
                        next_f1=float(record["next_f1"]) if record.get("next_f1") else None,
                        category_f1=float(record["category_f1"]) if record.get("category_f1") else None,
                        error=record.get("error", ""),
                    ))
                except (KeyError, ValueError) as exc:
                    _logger.warning("[ablation] skipping malformed summary row: %s", exc)
    except OSError as exc:
        _logger.warning("[ablation] could not read existing summary %s: %s", path, exc)
    return rows


def _run_candidate(
    candidate: MTLCandidate,
    state: str,
    engine: str,
    epochs: int,
    folds: int,
    seed: int | None,
    label_root: Path,
    data_root: Path,
    output_dir: Path,
    embedding_dim: int | None = None,
    timeout_seconds: int | None = None,
) -> AblationResult:
    candidate_root = label_root / candidate.name
    argv = _candidate_argv(candidate, state, engine, epochs, folds, seed, embedding_dim)
    command = " ".join(argv)
    print(f"[ablation] running {candidate.name} ({folds} fold(s), {epochs} epochs)")
    proc, log_file, duration, run_dir = _execute_subprocess(
        argv, candidate.name, candidate_root, label_root, seed,
        data_root, output_dir, engine, state, epochs, timeout_seconds,
    )
    joint_score, next_f1, category_f1 = _parse_metrics(run_dir, candidate.name)
    if proc is None:
        status, returncode = "timeout", -1
        error = f"timed out after {timeout_seconds}s; see {log_file}"
    else:
        status = "ok" if proc.returncode == 0 else "failed"
        returncode = proc.returncode
        error = "" if proc.returncode == 0 else f"see {log_file}"
    print(
        "[ablation] finished "
        f"{candidate.name}: status={status} joint={joint_score} "
        f"next={next_f1} category={category_f1}"
    )
    return AblationResult(
        candidate=candidate.name,
        stage=candidate.stage,
        epochs=epochs,
        folds=folds,
        seed=seed,
        status=status,
        returncode=returncode,
        run_dir=str(run_dir) if run_dir else "",
        log_file=str(log_file),
        duration_seconds=duration,
        command=command,
        joint_score=joint_score,
        next_f1=next_f1,
        category_f1=category_f1,
        error=error,
    )


def _top_candidates(rows: list[AblationResult], top_k: int) -> list[str]:
    successful = [
        row for row in rows
        if row.status == "ok" and row.joint_score is not None
    ]
    successful.sort(key=lambda row: row.joint_score or float("-inf"), reverse=True)
    return [row.candidate for row in successful[:top_k]]


def _write_manifest(
    path: Path,
    *,
    stage: str,
    state: str,
    engine: str,
    epochs: int,
    folds: int,
    seed: int | None,
    candidates: tuple[MTLCandidate, ...],
    promoted_from: str | None = None,
) -> None:
    data = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "stage": stage,
        "state": state,
        "engine": engine,
        "epochs": epochs,
        "folds": folds,
        "seed": seed,
        "promoted_from": promoted_from,
        "candidates": [
            {
                "name": candidate.name,
                "stage": candidate.stage,
                "model_name": candidate.model_name,
                "model_params": dict(candidate.model_params),
                "mtl_loss": candidate.mtl_loss,
                "mtl_loss_params": dict(candidate.mtl_loss_params),
                "rationale": candidate.rationale,
            }
            for candidate in candidates
        ],
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_ablation(config: AblationRunConfig) -> dict[str, Path | None]:
    """Execute a staged ablation run and return generated summary paths."""
    if config.stage not in {"phase1", "phase2", "phase3", "phase4", "all"}:
        raise ValueError(f"Invalid stage: {config.stage!r}")
    if config.epochs <= 0:
        raise ValueError("epochs must be > 0")
    if config.folds <= 0:
        raise ValueError("folds must be > 0")
    if config.promote_top < 0:
        raise ValueError("promote_top must be >= 0")
    if config.promote_epochs <= 0:
        raise ValueError("promote_epochs must be > 0")
    if config.promote_folds <= 0:
        raise ValueError("promote_folds must be > 0")

    candidates = (
        tuple(get_candidate(name) for name in tuple(config.candidate_names))
        if config.candidate_names
        else iter_candidates(config.stage)
    )

    seed_suffix = f"_seed{config.seed}" if config.seed is not None else ""
    label = f"{config.stage}_{config.folds}fold_{config.epochs}ep{seed_suffix}"
    label_root = config.results_root / label
    label_root.mkdir(parents=True, exist_ok=True)
    manifest_path = label_root / "manifest.json"
    _write_manifest(
        manifest_path,
        stage=config.stage,
        state=config.state,
        engine=config.engine,
        epochs=config.epochs,
        folds=config.folds,
        seed=config.seed,
        candidates=candidates,
    )
    print(f"[ablation] wrote manifest: {manifest_path}")

    summary_path = label_root / "summary.csv"
    current_names = {c.name for c in candidates}
    prior_rows = [r for r in _load_summary(summary_path) if r.candidate in current_names]
    completed_names = {r.candidate for r in prior_rows if r.status == "ok"}
    if completed_names:
        print(f"[ablation] resuming — skipping {len(completed_names)} already-completed candidate(s): {', '.join(sorted(completed_names))}")

    new_rows = [
        _run_candidate(
            candidate,
            state=config.state,
            engine=config.engine,
            epochs=config.epochs,
            folds=config.folds,
            seed=config.seed,
            label_root=label_root,
            data_root=config.data_root,
            output_dir=config.output_dir,
            embedding_dim=config.embedding_dim,
            timeout_seconds=config.timeout_seconds,
        )
        for candidate in candidates
        if candidate.name not in completed_names
    ]
    rows = prior_rows + new_rows
    _write_summary(summary_path, rows)
    print(f"[ablation] wrote summary: {summary_path}")

    promoted_summary_path: Path | None = None
    if config.promote_top > 0:
        promoted_names = _top_candidates(rows, config.promote_top)
        promoted_candidates = tuple(get_candidate(name) for name in promoted_names)
        promoted_label = (
            f"{config.stage}_promoted_{config.promote_folds}fold_"
            f"{config.promote_epochs}ep{seed_suffix}"
        )
        promoted_root = config.results_root / promoted_label
        promoted_root.mkdir(parents=True, exist_ok=True)
        promoted_manifest = promoted_root / "manifest.json"
        _write_manifest(
            promoted_manifest,
            stage=f"{config.stage}_promoted",
            state=config.state,
            engine=config.engine,
            epochs=config.promote_epochs,
            folds=config.promote_folds,
            seed=config.seed,
            candidates=promoted_candidates,
            promoted_from=str(summary_path),
        )
        print(f"[ablation] wrote promoted manifest: {promoted_manifest}")
        print(f"[ablation] promoting: {', '.join(promoted_names)}")
        promoted_summary_path = promoted_root / "summary.csv"
        current_promoted_names = {c.name for c in promoted_candidates}
        prior_promoted_rows = [r for r in _load_summary(promoted_summary_path) if r.candidate in current_promoted_names]
        completed_promoted = {r.candidate for r in prior_promoted_rows if r.status == "ok"}
        if completed_promoted:
            print(f"[ablation] resuming promoted — skipping {len(completed_promoted)} candidate(s): {', '.join(sorted(completed_promoted))}")
        new_promoted_rows = [
            _run_candidate(
                candidate,
                state=config.state,
                engine=config.engine,
                epochs=config.promote_epochs,
                folds=config.promote_folds,
                seed=config.seed,
                label_root=promoted_root,
                data_root=config.data_root,
                output_dir=config.output_dir,
                embedding_dim=config.embedding_dim,
                timeout_seconds=config.timeout_seconds,
            )
            for candidate in promoted_candidates
            if candidate.name not in completed_promoted
        ]
        promoted_rows = prior_promoted_rows + new_promoted_rows
        _write_summary(promoted_summary_path, promoted_rows)
        print(f"[ablation] wrote promoted summary: {promoted_summary_path}")

    return {
        "summary": summary_path,
        "promoted_summary": promoted_summary_path,
    }


# =====================================================================
# Head ablation — standalone head variant comparison
# =====================================================================


@dataclass(frozen=True)
class HeadAblationResult:
    """Result of a single head ablation candidate run."""

    candidate: str
    task: str
    model_name: str
    epochs: int
    folds: int
    seed: int | None
    status: str
    returncode: int
    run_dir: str
    log_file: str
    duration_seconds: float
    command: str
    f1: float | None
    accuracy: float | None
    error: str = ""


@dataclass(frozen=True)
class HeadAblationConfig:
    """Execution config for a head ablation run."""

    task: str = "category"  # "category", "next", or "all"
    state: str = "alabama"
    engine: str = "dgi"
    candidate_names: tuple[str, ...] = ()
    epochs: int = 10
    folds: int = 1
    seed: int | None = None
    embedding_dim: int | None = None
    timeout_seconds: int | None = None  # per-candidate subprocess timeout
    results_root: Path = field(default_factory=_default_results_root)
    data_root: Path = field(default_factory=_default_data_root)
    output_dir: Path = field(default_factory=_default_output_dir)


def _head_candidate_argv(
    candidate: HeadCandidate,
    state: str,
    engine: str,
    epochs: int,
    folds: int,
    seed: int | None,
    embedding_dim: int | None,
) -> list[str]:
    # Build the full config to get the resolved model_params, then pass
    # ALL of them via --replace-model-params + --model-param. This
    # avoids signature conflicts between the default factory's params
    # and the target head's constructor.
    config = candidate.build_config(state, engine, epochs, folds)
    argv = [
        sys.executable,
        "scripts/train.py",
        "--task",
        candidate.task,
        "--state",
        state,
        "--engine",
        engine,
        "--epochs",
        str(epochs),
        "--folds",
        str(folds),
        "--model",
        candidate.model_name,
        "--replace-model-params",
    ]
    if seed is not None:
        argv.extend(["--seed", str(seed)])
    if embedding_dim is not None:
        argv.extend(["--embedding-dim", str(embedding_dim)])
    for key, value in config.model_params.items():
        argv.extend(["--model-param", f"{key}={format_cli_value(value)}"])
    return argv


def _parse_head_metrics(
    run_dir: Path | None,
    task: str,
    candidate_name: str = "",
) -> tuple[float | None, float | None]:
    """Extract F1 and accuracy from a standalone head run."""
    if run_dir is None:
        _logger.warning("[head-ablation] no run directory found for %s", candidate_name)
        return None, None
    summary_path = run_dir / "summary" / "full_summary.json"
    if not summary_path.exists():
        _logger.warning("[head-ablation] summary not found: %s", summary_path)
        return None, None
    try:
        data = json.loads(summary_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        _logger.warning("[head-ablation] failed to parse %s: %s", summary_path, exc)
        return None, None
    task_data = data.get(task, {})
    f1 = task_data.get("f1", {}).get("mean")
    accuracy = task_data.get("accuracy", {}).get("mean")
    return f1, accuracy


def _run_head_candidate(
    candidate: HeadCandidate,
    state: str,
    engine: str,
    epochs: int,
    folds: int,
    seed: int | None,
    embedding_dim: int | None,
    label_root: Path,
    data_root: Path,
    output_dir: Path,
    timeout_seconds: int | None = None,
) -> HeadAblationResult:
    candidate_root = label_root / candidate.name
    argv = _head_candidate_argv(candidate, state, engine, epochs, folds, seed, embedding_dim)
    command = " ".join(argv)
    print(f"[head-ablation] running {candidate.name} (task={candidate.task}, {folds} fold(s), {epochs} epochs)")
    proc, log_file, duration, run_dir = _execute_subprocess(
        argv, candidate.name, candidate_root, label_root, seed,
        data_root, output_dir, engine, state, epochs, timeout_seconds,
    )
    f1, accuracy = _parse_head_metrics(run_dir, candidate.task, candidate.name)
    if proc is None:
        status, returncode = "timeout", -1
        error = f"timed out after {timeout_seconds}s; see {log_file}"
    else:
        status = "ok" if proc.returncode == 0 else "failed"
        returncode = proc.returncode
        error = "" if proc.returncode == 0 else f"see {log_file}"
    print(
        f"[head-ablation] finished {candidate.name}: "
        f"status={status} f1={f1} accuracy={accuracy}"
    )
    return HeadAblationResult(
        candidate=candidate.name,
        task=candidate.task,
        model_name=candidate.model_name,
        epochs=epochs,
        folds=folds,
        seed=seed,
        status=status,
        returncode=returncode,
        run_dir=str(run_dir) if run_dir else "",
        log_file=str(log_file),
        duration_seconds=duration,
        command=command,
        f1=f1,
        accuracy=accuracy,
        error=error,
    )


def _write_head_summary(path: Path, rows: list[HeadAblationResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [f.name for f in dc_fields(HeadAblationResult)]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def run_head_ablation(config: HeadAblationConfig) -> Path:
    """Execute a head ablation run and return the summary CSV path."""
    if config.task not in {"category", "next", "all"}:
        raise ValueError(f"Invalid task: {config.task!r}")
    if config.epochs <= 0:
        raise ValueError("epochs must be > 0")
    if config.folds <= 0:
        raise ValueError("folds must be > 0")

    candidates = (
        tuple(get_head_candidate(name) for name in config.candidate_names)
        if config.candidate_names
        else iter_head_candidates(config.task)
    )

    seed_suffix = f"_seed{config.seed}" if config.seed is not None else ""
    label = f"head_{config.task}_{config.folds}fold_{config.epochs}ep{seed_suffix}"
    label_root = config.results_root / label
    label_root.mkdir(parents=True, exist_ok=True)

    # Write manifest
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "task": config.task,
        "state": config.state,
        "engine": config.engine,
        "epochs": config.epochs,
        "folds": config.folds,
        "seed": config.seed,
        "embedding_dim": config.embedding_dim,
        "candidates": [
            {
                "name": c.name,
                "task": c.task,
                "model_name": c.model_name,
                "model_params": dict(c.model_params),
                "rationale": c.rationale,
            }
            for c in candidates
        ],
    }
    manifest_path = label_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"[head-ablation] wrote manifest: {manifest_path}")

    rows = [
        _run_head_candidate(
            candidate,
            state=config.state,
            engine=config.engine,
            epochs=config.epochs,
            folds=config.folds,
            seed=config.seed,
            embedding_dim=config.embedding_dim,
            label_root=label_root,
            data_root=config.data_root,
            output_dir=config.output_dir,
            timeout_seconds=config.timeout_seconds,
        )
        for candidate in candidates
    ]

    summary_path = label_root / "summary.csv"
    _write_head_summary(summary_path, rows)
    print(f"[head-ablation] wrote summary: {summary_path}")

    # Print ranking
    successful = [r for r in rows if r.status == "ok" and r.f1 is not None]
    if successful:
        successful.sort(key=lambda r: r.f1 or 0.0, reverse=True)
        print(f"\n[head-ablation] === {config.task.upper()} HEAD RANKING ===")
        for i, r in enumerate(successful, 1):
            print(f"  {i}. {r.candidate:30s}  F1={r.f1:.4f}  Acc={r.accuracy:.4f}  Time={r.duration_seconds:7.1f}s")

    return summary_path


def _parse_legacy_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Run staged MTL ablation candidates (legacy parser).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--engine", default="dgi")
    parser.add_argument("--stage", choices=("phase1", "phase2", "phase3", "phase4", "all"), default="phase1")
    parser.add_argument("--candidate", action="append", default=[])
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--folds", type=int, default=1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--embedding-dim", type=int, default=None,
                        help="Override embedding dimension (e.g. 128 for fusion).")
    parser.add_argument("--promote-top", type=int, default=0)
    parser.add_argument("--promote-epochs", type=int, default=15)
    parser.add_argument("--promote-folds", type=int, default=2)
    parser.add_argument(
        "--results-root",
        type=Path,
        default=_root / "results" / "ablations",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(os.environ.get("DATA_ROOT", str(_root / "data"))),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.environ.get("OUTPUT_DIR", str(_root / "output"))),
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    """Legacy CLI entrypoint for compatibility shims."""
    args = _parse_legacy_args(argv)
    config = AblationRunConfig(
        state=args.state,
        engine=args.engine,
        stage=args.stage,
        candidate_names=tuple(args.candidate),
        epochs=args.epochs,
        folds=args.folds,
        seed=args.seed,
        embedding_dim=args.embedding_dim,
        promote_top=args.promote_top,
        promote_epochs=args.promote_epochs,
        promote_folds=args.promote_folds,
        results_root=args.results_root,
        data_root=args.data_root,
        output_dir=args.output_dir,
    )
    run_ablation(config)


if __name__ == "__main__":
    main()
