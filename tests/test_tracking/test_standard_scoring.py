"""Tests for the standard scoring module (tracking/scoring.py) + the post-hoc
joint-best scorer (scripts/closing_data/score_joint_best.py).

Covers the scoring-standardization fix (2026-07): the joint-best epoch selection
(argmax of geom_simple with the min-best-epoch gate, ties -> earliest), the
full = indist * (1 - ood) arithmetic, the diag-best (a40) values, epoch alignment
with unequal-length series, the FoldHistory-level wrapper + storage hook, and the
script's fold-CSV path against a fake rundir.
"""
from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from tracking.scoring import (
    compute_standard_scores,
    fold_standard_scores,
    identify_cat_reg_tasks,
    selector_value,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "closing_data" / "score_joint_best.py"


# ---------------------------------------------------------------------------
# Synthetic series: 5 epochs.
#   cat f1:            .50 .60 .70 .65 .64   -> diag-best epoch 3 (f1 .70)
#   reg top10_indist:  .30 .40 .45 .60 .58   -> diag-best epoch 4 (indist .60)
#   ood_fraction:      .10 .10 .20 .10 .10   -> reg diag full = .60 * .90 = .54
#   geom_simple:       .3873 .4899 .5612 .6245 .6094 -> joint-best epoch 4
# ---------------------------------------------------------------------------
CAT = {"f1": [0.50, 0.60, 0.70, 0.65, 0.64]}
REG = {
    "f1": [0.10, 0.12, 0.13, 0.14, 0.13],
    "top10_acc_indist": [0.30, 0.40, 0.45, 0.60, 0.58],
    "ood_fraction": [0.10, 0.10, 0.20, 0.10, 0.10],
}


def test_joint_best_epoch_and_arithmetic():
    s = compute_standard_scores(CAT, REG)
    jb = s["joint_best"]
    assert jb["epoch"] == 4
    assert jb["cat_f1"] == pytest.approx(0.65)
    assert jb["top10_indist"] == pytest.approx(0.60)
    assert jb["ood_fraction"] == pytest.approx(0.10)
    # full = indist * (1 - ood)
    assert jb["top10_full"] == pytest.approx(0.60 * 0.90)
    assert jb["selector"] == pytest.approx(math.sqrt(0.65 * 0.60))
    assert s["selector_name"] == "geom_simple"
    assert s["reg_metric_used"] == "top10_acc_indist"


def test_diag_best_matches_a40_convention():
    s = compute_standard_scores(CAT, REG)
    assert s["cat_diag_best"] == {"epoch": 3, "f1": pytest.approx(0.70)}
    rd = s["reg_diag_best"]
    assert rd["epoch"] == 4
    assert rd["top10_indist"] == pytest.approx(0.60)
    assert rd["top10_full"] == pytest.approx(0.54)
    # diag-best and joint-best are DIFFERENT epochs for cat (3 vs 4) — the whole point.
    assert s["cat_diag_best"]["epoch"] != s["joint_best"]["epoch"]


def test_min_best_epoch_gate():
    # A huge epoch-1 selector value must be skipped when gated out.
    cat = {"f1": [0.99, 0.60, 0.70]}
    reg = {"f1": [0.1] * 3, "top10_acc_indist": [0.99, 0.40, 0.45], "ood_fraction": [0.0] * 3}
    ungated = compute_standard_scores(cat, reg, min_best_epoch=0)
    assert ungated["joint_best"]["epoch"] == 1
    gated = compute_standard_scores(cat, reg, min_best_epoch=1)  # 0-based: epoch 1 excluded
    assert gated["joint_best"]["epoch"] == 3
    # Gate does NOT apply to diag-best (a40 convention).
    assert gated["cat_diag_best"]["epoch"] == 1
    # Gate beyond the series -> no joint-best, with a warning.
    empty = compute_standard_scores(cat, reg, min_best_epoch=10)
    assert empty["joint_best"] is None
    assert any("no epoch eligible" in w for w in empty["warnings"])


def test_tie_goes_to_earliest_epoch():
    cat = {"f1": [0.50, 0.70, 0.70]}
    reg = {"f1": [0.1] * 3, "top10_acc_indist": [0.60, 0.60, 0.60], "ood_fraction": [0.0] * 3}
    s = compute_standard_scores(cat, reg)
    assert s["joint_best"]["epoch"] == 2  # strict `>` improvement, like training


def test_unequal_length_series_align_on_common_prefix():
    reg_short = {k: v[:3] for k, v in REG.items()}
    s = compute_standard_scores(CAT, reg_short)
    # joint restricted to epochs 1..3; best of geom_simple there is epoch 3
    assert s["joint_best"]["epoch"] == 3
    assert any("unequal series lengths" in w for w in s["warnings"])
    # cat diag-best still sees its full 5-epoch series
    assert s["cat_diag_best"]["epoch"] == 3


def test_missing_ood_fraction_treated_as_zero_with_warning():
    reg = {"f1": REG["f1"], "top10_acc_indist": REG["top10_acc_indist"]}
    s = compute_standard_scores(CAT, reg)
    assert any("ood_fraction" in w for w in s["warnings"])
    assert s["reg_diag_best"]["top10_full"] == pytest.approx(0.60)  # * (1 - 0)


def test_reg_metric_fallback_to_f1():
    reg = {"f1": [0.30, 0.40, 0.35]}
    s = compute_standard_scores({"f1": [0.5, 0.6, 0.7]}, reg)
    assert s["reg_metric_used"] == "f1"
    # selector uses reg f1 (the mtl_cv fallback), epoch 3: sqrt(.7*.35) < epoch 2: sqrt(.6*.4)?
    assert s["joint_best"]["selector"] == pytest.approx(
        max(math.sqrt(0.5 * 0.3), math.sqrt(0.6 * 0.4), math.sqrt(0.7 * 0.35))
    )


def test_selector_series_overrides_recompute():
    # A recorded model_task selector series wins over recomputation.
    series = [0.0, 0.0, 1.0, 0.0, 0.0]
    s = compute_standard_scores(CAT, REG, selector_series=series)
    assert s["selector_source"] == "model_task_val_f1"
    assert s["joint_best"]["epoch"] == 3
    assert s["joint_best"]["selector"] == pytest.approx(1.0)


def test_joint_f1_mean_selector():
    assert selector_value("joint_f1_mean", 0.6, 0.99, reg_f1=0.2) == pytest.approx(0.4)
    s = compute_standard_scores(CAT, REG, selector_name="joint_f1_mean")
    means = [0.5 * (a + b) for a, b in zip(REG["f1"], CAT["f1"])]
    assert s["joint_best"]["epoch"] == means.index(max(means)) + 1


def test_returns_none_without_f1_series():
    assert compute_standard_scores({}, REG) is None
    assert compute_standard_scores(CAT, {}) is None


# ---------------------------------------------------------------------------
# FoldHistory-level wrapper + storage hook
# ---------------------------------------------------------------------------

def _make_fold():
    from tracking.fold import FoldHistory, TaskHistory

    fold = FoldHistory.standalone({"next_category", "next_region"})
    for i in range(5):
        fold.log_val("next_category", f1=CAT["f1"][i], accuracy=0.5)
        fold.log_val(
            "next_region",
            f1=REG["f1"][i],
            accuracy=0.2,
            top10_acc_indist=REG["top10_acc_indist"][i],
            ood_fraction=REG["ood_fraction"][i],
        )
    # model_task val f1 = the training-time joint selector (C21 convention)
    fold.model_task = TaskHistory()
    for i in range(5):
        sel = math.sqrt(max(CAT["f1"][i], 0) * max(REG["top10_acc_indist"][i], 0))
        fold.model_task.log_val(f1=sel, accuracy=0, loss=1.0, model_state={"w": i})
    return fold


def test_fold_standard_scores_with_checkpoint_crosscheck():
    fold = _make_fold()
    out = fold_standard_scores(fold, cat_task="next_category", reg_task="next_region")
    assert out["joint_best"]["epoch"] == 4
    assert out["selector_source"] == "model_task_val_f1"
    # tracker best_epoch is 0-based 3 -> 1-based 4; must agree with joint_best
    assert out["checkpoint_epoch"] == 4
    assert not any("saved-checkpoint" in w for w in out["warnings"])


def test_identify_cat_reg_tasks_by_top10():
    fold = _make_fold()
    assert identify_cat_reg_tasks(fold, ["next_category", "next_region"]) == (
        "next_category", "next_region",
    )
    assert identify_cat_reg_tasks(fold, ["next_category"]) is None


def test_storage_hook_writes_standard_scores(tmp_path):
    from tracking.experiment import MLHistory
    from tracking.parms.neural import NeuralParams

    h = MLHistory(
        model_name="Test",
        tasks={"next_category", "next_region"},
        num_folds=1,
        model_parms=NeuralParams(learning_rate=1e-4, batch_size=2048, num_epochs=5),
        save_path=tmp_path,
    )
    h.scoring_task_names = ("next_category", "next_region")  # as mtl_cv annotates
    h.checkpoint_selector = "geom_simple"
    h.start()
    fold = h.folds[0]
    src = _make_fold()
    fold.tasks = src.tasks
    fold.model_task = src.model_task
    h.step()  # fold end -> save_fold_partial -> standard-scores export

    files = list(tmp_path.glob("*/metrics/fold1_standard_scores.json"))
    assert len(files) == 1, "fold1_standard_scores.json must be written at fold end"
    payload = json.loads(files[0].read_text())
    assert payload["fold"] == 1
    assert payload["cat_task"] == "next_category"
    assert payload["joint_best"]["epoch"] == 4
    assert payload["cat_diag_best"]["epoch"] == 3
    assert payload["schema_version"] == 1


# ---------------------------------------------------------------------------
# Script fold-CSV path (fake rundir)
# ---------------------------------------------------------------------------

def _write_csv(path: Path, header, rows):
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _make_rundir(tmp_path: Path) -> Path:
    rundir = tmp_path / "mtlnet_lr1e-04_bs8192_ep50_fake"
    (rundir / "metrics").mkdir(parents=True)
    cat_rows = [[i + 1, CAT["f1"][i], 0.5] for i in range(5)]
    reg_rows = [
        [i + 1, REG["f1"][i], REG["top10_acc_indist"][i], REG["ood_fraction"][i]]
        for i in range(5)
    ]
    for fid in (1, 3):  # non-contiguous REAL fold ids on purpose
        _write_csv(rundir / "metrics" / f"fold{fid}_next_category_val.csv",
                   ["epoch", "f1", "accuracy"], cat_rows)
        _write_csv(rundir / "metrics" / f"fold{fid}_next_region_val.csv",
                   ["epoch", "f1", "top10_acc_indist", "ood_fraction"], reg_rows)
    return rundir


def test_script_scores_fake_rundir(tmp_path):
    rundir = _make_rundir(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(rundir), "--seed", "0", "--tag", "unit"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    sidecar = rundir / "joint_best_score.json"
    assert sidecar.exists()
    out = json.loads(sidecar.read_text())
    assert out["min_best_epoch"] == 0  # default matches the v17 board (no --min-best-epoch pin)
    jb, db = out["joint_best"], out["diag_best"]
    # joint-best: epoch 4 on both folds; percent values
    assert jb["epochs"] == [4, 4]
    assert jb["cat_per_fold"] == [pytest.approx(65.0)] * 2
    assert jb["reg_per_fold"] == [pytest.approx(54.0)] * 2  # 0.60*0.90*100
    # diag-best reproduces the a40 convention: cat epoch 3 (.70), reg epoch 4 full 54.0
    assert db["cat_best_epochs"] == [3, 3]
    assert db["cat_macro_f1_mean"] == pytest.approx(70.0)
    assert db["reg_full_top10_mean"] == pytest.approx(54.0)
    assert out["delta_joint_minus_diag"]["cat"] == pytest.approx(-5.0)
    # matched by REAL fold id
    assert [row["fold"] for row in out["per_fold"]] == [1, 3]


def test_script_min_best_epoch_flag(tmp_path):
    rundir = _make_rundir(tmp_path)
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(rundir), "--min-best-epoch", "4"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads((rundir / "joint_best_score.json").read_text())
    # 0-based gate 4 -> only epoch 5 eligible
    assert out["joint_best"]["epochs"] == [5, 5]


def test_script_prefers_standard_scores_artifact(tmp_path):
    rundir = _make_rundir(tmp_path)
    # Drop a matching artifact for fold 1 with a DIFFERENT (sentinel) joint epoch to
    # prove it is preferred over the CSVs.
    art = compute_standard_scores(CAT, REG)
    art["joint_best"]["epoch"] = 5
    art["joint_best"]["cat_f1"] = 0.64
    (rundir / "metrics" / "fold1_standard_scores.json").write_text(json.dumps(art))
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(rundir)],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    out = json.loads((rundir / "joint_best_score.json").read_text())
    by_fold = {row["fold"]: row for row in out["per_fold"]}
    assert by_fold[1]["source"] == "standard_scores.json"
    assert by_fold[1]["joint_best"]["epoch"] == 5
    assert by_fold[3]["source"] == "csv"
    assert by_fold[3]["joint_best"]["epoch"] == 4
    # A mismatched min-best-epoch must fall back to CSVs.
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), str(rundir), "--min-best-epoch", "1"],
        capture_output=True, text=True, timeout=60,
    )
    out = json.loads((rundir / "joint_best_score.json").read_text())
    assert all(row["source"] == "csv" for row in out["per_fold"])
