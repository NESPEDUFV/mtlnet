"""Regression test for F20 per-fold partial persistence.

Verifies that MLHistory.step() persists the completed fold's artefacts to
disk before advancing, so a mid-CV crash preserves whatever fold data has
already been collected.

Motivating incident: 2026-04-23 B3 FL 5-fold crashed at fold 2 epoch 22
(likely OOM SIGKILL on M4 Pro MPS). End-of-CV-only persistence wiped the
completed fold 1 data. This test guarantees that regression never recurs.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
import json

from tracking.experiment import MLHistory
from tracking.parms.neural import NeuralParams


def _make_params() -> NeuralParams:
    return NeuralParams(
        learning_rate=1e-4,
        batch_size=2048,
        num_epochs=2,
    )


def _log_fold_data(history: MLHistory, fold_idx: int, *, tasks: list[str]) -> None:
    """Seed a fold with minimal train/val/report data so _save_reports has something to persist."""
    # step() operates on the *current* fold, so we set curr_i_fold first if needed
    assert history.curr_i_fold == fold_idx, (
        f"expected history at fold {fold_idx}, got {history.curr_i_fold}"
    )
    fold = history.folds[fold_idx]
    for task_name in tasks:
        th = fold.task(task_name)
        th.train.log(loss=0.5, accuracy=0.8, f1=0.75)
        th.train.log(loss=0.4, accuracy=0.85, f1=0.80)
        th.val.log(loss=0.6, accuracy=0.7, f1=0.68)
        th.val.log(loss=0.5, accuracy=0.78, f1=0.77)
        # best-tracker must see epoch updates for diagnostic_best_epochs to populate
        for ep, v in enumerate([0.68, 0.77]):
            th.best.update(epoch=ep, metric_value=v, model_state={})
        # classification report (required for _save_fold_report)
        th.report = {
            "0": {"precision": 0.8, "recall": 0.7, "f1-score": 0.75, "support": 100},
            "1": {"precision": 0.6, "recall": 0.8, "f1-score": 0.69, "support": 80},
        }


def test_save_fold_partial_persists_after_step(tmp_path: Path):
    """After step() on fold 0, fold1_info.json must exist on disk."""
    h = MLHistory(
        model_name="Test",
        tasks="next",
        num_folds=3,
        model_parms=_make_params(),
        save_path=tmp_path,
    )
    h.start()

    # Seed fold 0 with data
    _log_fold_data(h, fold_idx=0, tasks=["next"])

    h.step()  # should persist fold 0 on disk + advance to fold 1

    # Find the run dir — there should be exactly one under tmp_path with folds/
    run_dirs = [d for d in tmp_path.iterdir() if d.is_dir() and (d / "folds").exists()]
    assert len(run_dirs) == 1, f"expected exactly one run dir, got {run_dirs}"
    folds_dir = run_dirs[0] / "folds"
    assert (folds_dir / "fold1_info.json").exists(), "fold1_info.json must persist after step()"
    # The fold_info should have the expected schema
    info = json.loads((folds_dir / "fold1_info.json").read_text())
    assert info["fold_number"] == 1
    assert "diagnostic_best_epochs" in info
    assert "next" in info["diagnostic_best_epochs"]


def test_simulated_crash_preserves_completed_folds(tmp_path: Path):
    """Simulate a SIGKILL mid fold-2: history never reaches __exit__, yet fold 1 persists."""
    h = MLHistory(
        model_name="Test",
        tasks="next",
        num_folds=3,
        model_parms=_make_params(),
        save_path=tmp_path,
    )
    h.start()

    # Fold 0 — complete it
    _log_fold_data(h, fold_idx=0, tasks=["next"])
    h.step()

    # Fold 1 — start logging, then simulate a crash (do NOT call step(), do NOT exit context)
    fold1 = h.folds[1]
    fold1.task("next").train.log(loss=0.45, accuracy=0.82, f1=0.78)
    fold1.task("next").val.log(loss=0.55, accuracy=0.76, f1=0.71)
    fold1.task("next").best.update(epoch=0, metric_value=0.71, model_state={})

    # No step(), no __exit__ → emulates a mid-fold SIGKILL.
    # The only way fold 0's data survives is if step() already wrote it.

    run_dirs = [d for d in tmp_path.iterdir() if d.is_dir() and (d / "folds").exists()]
    assert len(run_dirs) == 1
    folds_dir = run_dirs[0] / "folds"

    # Fold 1's data MUST exist (that's the F20 guarantee)
    assert (folds_dir / "fold1_info.json").exists(), \
        "fold1_info.json must survive a mid-fold-2 crash"

    # Fold 2's data MUST NOT exist (it never completed)
    assert not (folds_dir / "fold2_info.json").exists()

    # Verify fold1_info.json is well-formed JSON with expected metrics
    info = json.loads((folds_dir / "fold1_info.json").read_text())
    assert info["fold_number"] == 1
    assert info["diagnostic_best_epochs"]["next"]["f1"] == pytest.approx(0.77)


def test_partial_save_is_best_effort(tmp_path: Path):
    """If save_fold_partial raises, step() should still advance (training never aborts)."""
    h = MLHistory(
        model_name="Test",
        tasks="next",
        num_folds=3,
        model_parms=_make_params(),
        save_path=tmp_path,
    )
    h.start()

    # Force the partial save to fail by pointing save_path at a non-writable location
    # (after init — simulates a disk-full scenario mid-run)
    _log_fold_data(h, fold_idx=0, tasks=["next"])
    h._save_path = Path("/nonexistent-directory-12345/cannot-write")

    # step() must still complete and advance curr_i_fold — the partial-save
    # failure is swallowed by the best-effort wrapper.
    h.step()
    assert h.curr_i_fold == 1


def test_multi_task_partial_persist(tmp_path: Path):
    """Partial persist writes per-task reports for MTL configurations."""
    h = MLHistory(
        model_name="Test",
        tasks={"next_category", "next_region"},
        num_folds=2,
        model_parms=_make_params(),
        save_path=tmp_path,
    )
    h.start()
    _log_fold_data(h, fold_idx=0, tasks=["next_category", "next_region"])
    h.step()

    run_dirs = [d for d in tmp_path.iterdir() if d.is_dir() and (d / "folds").exists()]
    folds_dir = run_dirs[0] / "folds"
    # Both tasks' reports should exist
    assert (folds_dir / "fold1_next_category_report.json").exists()
    assert (folds_dir / "fold1_next_region_report.json").exists()
    assert (folds_dir / "fold1_info.json").exists()
