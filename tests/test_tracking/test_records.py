"""Unit tests for ``tracking.records`` — best-run record tracking."""
from __future__ import annotations

import json

import pytest

from tracking.records import (
    RecordComparison,
    TaskRecord,
    compare_records,
    compute_best_record,
    save_best_record,
    scan_previous_bests,
)


def _write_summary(base: "Path", folder: str, summary: dict) -> None:
    """Helper: write a fake full_summary.json under base/folder/summary/."""
    summary_dir = base / folder / "summary"
    summary_dir.mkdir(parents=True, exist_ok=True)
    (summary_dir / "full_summary.json").write_text(
        json.dumps(summary), encoding="utf-8"
    )


class TestScanPreviousBests:
    def test_finds_max_f1_per_task(self, tmp_path):
        _write_summary(tmp_path, "run_a", {
            "category": {"f1": {"mean": 0.40, "std": 0.01}, "accuracy": {"mean": 0.50}},
            "next": {"f1": {"mean": 0.30, "std": 0.02}, "accuracy": {"mean": 0.35}},
        })
        _write_summary(tmp_path, "run_b", {
            "category": {"f1": {"mean": 0.50, "std": 0.01}, "accuracy": {"mean": 0.55}},
            "next": {"f1": {"mean": 0.25, "std": 0.01}, "accuracy": {"mean": 0.30}},
        })
        _write_summary(tmp_path, "run_c", {
            "category": {"f1": {"mean": 0.45, "std": 0.01}, "accuracy": {"mean": 0.52}},
            "next": {"f1": {"mean": 0.35, "std": 0.03}, "accuracy": {"mean": 0.40}},
        })

        bests = scan_previous_bests(tmp_path)

        assert bests["category"] == pytest.approx((0.50, "run_b"), abs=1e-9)
        assert bests["next"] == pytest.approx((0.35, "run_c"), abs=1e-9)

    def test_excludes_specified_folder(self, tmp_path):
        _write_summary(tmp_path, "run_a", {
            "category": {"f1": {"mean": 0.80, "std": 0.01}},
        })
        _write_summary(tmp_path, "run_b", {
            "category": {"f1": {"mean": 0.40, "std": 0.01}},
        })

        bests = scan_previous_bests(tmp_path, exclude_folder="run_a")

        assert bests["category"][0] == pytest.approx(0.40)
        assert bests["category"][1] == "run_b"

    def test_empty_dir_returns_empty(self, tmp_path):
        assert scan_previous_bests(tmp_path) == {}

    def test_corrupted_json_skipped(self, tmp_path):
        summary_dir = tmp_path / "bad_run" / "summary"
        summary_dir.mkdir(parents=True)
        (summary_dir / "full_summary.json").write_text("not valid json")

        _write_summary(tmp_path, "good_run", {
            "next": {"f1": {"mean": 0.30, "std": 0.01}},
        })

        bests = scan_previous_bests(tmp_path)
        assert "next" in bests
        assert bests["next"][0] == pytest.approx(0.30)

    def test_mixed_task_sets(self, tmp_path):
        """MTL run has category+next, single-task run has only next."""
        _write_summary(tmp_path, "mtl_run", {
            "category": {"f1": {"mean": 0.45, "std": 0.01}},
            "next": {"f1": {"mean": 0.30, "std": 0.01}},
        })
        _write_summary(tmp_path, "next_only_run", {
            "next": {"f1": {"mean": 0.40, "std": 0.01}},
        })

        bests = scan_previous_bests(tmp_path)
        assert bests["category"][0] == pytest.approx(0.45)
        assert bests["next"][0] == pytest.approx(0.40)
        assert bests["next"][1] == "next_only_run"


class TestCompareRecords:
    def test_new_record(self, tmp_path):
        _write_summary(tmp_path, "old_run", {
            "category": {"f1": {"mean": 0.40, "std": 0.01}},
        })

        current = {"category": {"f1": {"mean": 0.50, "std": 0.02}}}
        comp = compare_records(tmp_path, current, "current_run")

        assert len(comp.tasks) == 1
        assert comp.tasks[0].is_new_record is True
        assert comp.tasks[0].current_f1 == pytest.approx(0.50)
        assert comp.tasks[0].previous_best_f1 == pytest.approx(0.40)
        assert comp.any_new_record is True

    def test_not_a_record(self, tmp_path):
        _write_summary(tmp_path, "old_run", {
            "next": {"f1": {"mean": 0.50, "std": 0.01}},
        })

        current = {"next": {"f1": {"mean": 0.40, "std": 0.02}}}
        comp = compare_records(tmp_path, current, "current_run")

        assert len(comp.tasks) == 1
        assert comp.tasks[0].is_new_record is False
        assert comp.tasks[0].previous_best_run == "old_run"
        assert comp.any_new_record is False

    def test_first_run_is_new_record(self, tmp_path):
        current = {
            "category": {"f1": {"mean": 0.40, "std": 0.01}},
            "next": {"f1": {"mean": 0.30, "std": 0.01}},
        }
        comp = compare_records(tmp_path, current, "first_run")

        assert len(comp.tasks) == 2
        assert all(t.is_new_record for t in comp.tasks)

    def test_degenerate_first_run_not_a_record(self, tmp_path):
        """A first run with F1=0.0 should not be marked as a record."""
        current = {
            "category": {"f1": {"mean": 0.0, "std": 0.0}},
        }
        comp = compare_records(tmp_path, current, "broken_run")

        assert len(comp.tasks) == 1
        assert comp.tasks[0].is_new_record is False

    def test_mixed_tasks_some_record_some_not(self, tmp_path):
        _write_summary(tmp_path, "old_run", {
            "category": {"f1": {"mean": 0.50, "std": 0.01}},
            "next": {"f1": {"mean": 0.20, "std": 0.01}},
        })

        current = {
            "category": {"f1": {"mean": 0.45, "std": 0.01}},  # worse
            "next": {"f1": {"mean": 0.30, "std": 0.01}},       # better
        }
        comp = compare_records(tmp_path, current, "new_run")

        cat = next(t for t in comp.tasks if t.task == "category")
        nxt = next(t for t in comp.tasks if t.task == "next")
        assert cat.is_new_record is False
        assert nxt.is_new_record is True
        assert comp.any_new_record is True


class TestSaveBestRecord:
    def test_creates_best_record_json(self, tmp_path):
        comparison = RecordComparison(tasks=[
            TaskRecord("category", 0.50, 0.40, "old_run", True),
            TaskRecord("next", 0.25, 0.30, "old_run", False),
        ])
        current_summary = {
            "category": {"f1": {"mean": 0.50, "std": 0.02}, "accuracy": {"mean": 0.55}},
            "next": {"f1": {"mean": 0.25, "std": 0.01}, "accuracy": {"mean": 0.30}},
        }

        path = save_best_record(tmp_path, comparison, current_summary, "new_run")

        assert path is not None
        assert path.exists()
        data = json.loads(path.read_text())
        assert "category" in data["tasks"]
        assert data["tasks"]["category"]["f1_mean"] == pytest.approx(0.50)
        assert data["tasks"]["category"]["run_folder"] == "new_run"
        # next was not a record — should not be in tasks (no prior entry either).
        assert "next" not in data["tasks"]

    def test_returns_none_when_no_new_records(self, tmp_path):
        comparison = RecordComparison(tasks=[
            TaskRecord("next", 0.25, 0.30, "old_run", False),
        ])
        current_summary = {
            "next": {"f1": {"mean": 0.25, "std": 0.01}},
        }

        result = save_best_record(tmp_path, comparison, current_summary, "new_run")

        assert result is None
        assert not (tmp_path / "best_record.json").exists()

    def test_updates_existing_record(self, tmp_path):
        # Pre-existing record.
        existing = {
            "last_updated": "2026-04-10T00:00:00",
            "tasks": {
                "next": {
                    "f1_mean": 0.30,
                    "f1_std": 0.01,
                    "accuracy_mean": 0.35,
                    "run_folder": "old_best",
                    "updated_at": "2026-04-10T00:00:00",
                }
            },
        }
        (tmp_path / "best_record.json").write_text(json.dumps(existing))

        comparison = RecordComparison(tasks=[
            TaskRecord("category", 0.50, 0.0, "", True),
        ])
        current_summary = {
            "category": {"f1": {"mean": 0.50, "std": 0.02}, "accuracy": {"mean": 0.55}},
        }

        save_best_record(tmp_path, comparison, current_summary, "new_run")

        data = json.loads((tmp_path / "best_record.json").read_text())
        # Both tasks should be present.
        assert data["tasks"]["category"]["f1_mean"] == pytest.approx(0.50)
        assert data["tasks"]["next"]["f1_mean"] == pytest.approx(0.30)


class TestComputeBestRecord:
    def test_standalone_computation(self, tmp_path):
        _write_summary(tmp_path, "run_a", {
            "category": {"f1": {"mean": 0.40, "std": 0.01}, "accuracy": {"mean": 0.50}},
            "next": {"f1": {"mean": 0.35, "std": 0.02}, "accuracy": {"mean": 0.40}},
        })
        _write_summary(tmp_path, "run_b", {
            "category": {"f1": {"mean": 0.50, "std": 0.02}, "accuracy": {"mean": 0.55}},
            "next": {"f1": {"mean": 0.30, "std": 0.01}, "accuracy": {"mean": 0.35}},
        })

        path = compute_best_record(tmp_path)

        assert path.exists()
        data = json.loads(path.read_text())
        assert data["tasks"]["category"]["f1_mean"] == pytest.approx(0.50)
        assert data["tasks"]["category"]["run_folder"] == "run_b"
        assert data["tasks"]["next"]["f1_mean"] == pytest.approx(0.35)
        assert data["tasks"]["next"]["run_folder"] == "run_a"

    def test_empty_dir_writes_empty_tasks(self, tmp_path):
        path = compute_best_record(tmp_path)

        data = json.loads(path.read_text())
        assert data["tasks"] == {}
