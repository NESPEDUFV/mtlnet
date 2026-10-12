"""Epoch selection against the reference's own scoring module.

The reference implementation of this logic is already clean and dependency-free, so the risk is not
that it is wrong — it is that a reimplementation drifts on a tie-break or a gate boundary, both of
which change which epoch a number is read from without changing anything that looks broken.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

from ._old_repo import OLD_REPO

OLD_SRC = OLD_REPO / "src"


@pytest.fixture(scope="module")
def reference():
    if not OLD_SRC.exists():
        pytest.skip("reference repo absent")
    if str(OLD_SRC) not in sys.path:
        sys.path.insert(0, str(OLD_SRC))
    try:
        from tracking import scoring
    except Exception as exc:                                   # pragma: no cover
        pytest.skip(f"reference scoring not importable: {exc}")
    return scoring


def _series(n: int, seed: int) -> tuple[dict, dict]:
    rng = random.Random(seed)
    cat = {"f1": [rng.random() for _ in range(n)]}
    reg = {
        "f1": [rng.random() for _ in range(n)],
        "top10_acc_indist": [rng.random() for _ in range(n)],
        "ood_fraction": [rng.random() * 0.05 for _ in range(n)],
    }
    return cat, reg


@pytest.mark.equivalence
@pytest.mark.parametrize("seed", range(6))
@pytest.mark.parametrize("min_best_epoch", [0, 5])
def test_standard_scores_match(reference, seed: int, min_best_epoch: int) -> None:
    from mtlcheck.train import scoring as mine

    cat, reg = _series(50, seed)
    theirs = reference.compute_standard_scores(cat, reg, selector_name="geom_simple",
                                               min_best_epoch=min_best_epoch)
    ours = mine.standard_scores(cat, reg, selector="geom_simple", min_best_epoch=min_best_epoch)

    for block in ("cat_diag_best", "reg_diag_best", "joint_best"):
        assert ours[block]["epoch"] == theirs[block]["epoch"], f"{block} epoch (seed {seed})"
    assert ours["cat_diag_best"]["f1"] == theirs["cat_diag_best"]["f1"]
    assert ours["reg_diag_best"]["top10_full"] == pytest.approx(theirs["reg_diag_best"]["top10_full"])
    assert ours["joint_best"]["top10_full"] == pytest.approx(theirs["joint_best"]["top10_full"])
    assert ours["reg_metric_used"] == theirs["reg_metric_used"]


@pytest.mark.equivalence
def test_ties_go_to_the_earliest_epoch(reference) -> None:
    """Training replaces its checkpoint on a strict improvement, so an equal later epoch loses."""
    from mtlcheck.train import scoring as mine

    cat = {"f1": [0.5, 0.9, 0.9, 0.4]}
    reg = {"f1": [0.5, 0.9, 0.9, 0.4], "top10_acc_indist": [0.5, 0.9, 0.9, 0.4],
           "ood_fraction": [0.0] * 4}
    ours = mine.standard_scores(cat, reg)
    theirs = reference.compute_standard_scores(cat, reg)
    assert ours["joint_best"]["epoch"] == theirs["joint_best"]["epoch"] == 2


@pytest.mark.equivalence
def test_the_gate_is_zero_based(reference) -> None:
    """`min_best_epoch` indexes 0-based while reported epochs are 1-based — an easy off-by-one."""
    from mtlcheck.train import scoring as mine

    cat = {"f1": [0.9, 0.1, 0.1]}
    reg = {"f1": [0.9, 0.1, 0.1], "top10_acc_indist": [0.9, 0.1, 0.1], "ood_fraction": [0.0] * 3}
    ours = mine.standard_scores(cat, reg, min_best_epoch=1)
    theirs = reference.compute_standard_scores(cat, reg, min_best_epoch=1)
    assert ours["joint_best"]["epoch"] == theirs["joint_best"]["epoch"] == 2


@pytest.mark.equivalence
def test_diag_best_is_ungated(reference) -> None:
    """The gate applies to the joint checkpoint only; per-task best epochs see the whole series."""
    from mtlcheck.train import scoring as mine

    cat = {"f1": [0.9, 0.1, 0.1]}
    reg = {"f1": [0.1, 0.1, 0.9], "top10_acc_indist": [0.1, 0.1, 0.9], "ood_fraction": [0.0] * 3}
    ours = mine.standard_scores(cat, reg, min_best_epoch=2)
    assert ours["cat_diag_best"]["epoch"] == 1
    assert ours["reg_diag_best"]["epoch"] == 3
    assert ours["joint_best"]["epoch"] == 3
    assert ours["cat_diag_best"]["epoch"] == reference.compute_standard_scores(
        cat, reg, min_best_epoch=2)["cat_diag_best"]["epoch"]


@pytest.mark.equivalence
def test_region_selection_uses_the_banked_convention() -> None:
    """The dedicated-region lane must reproduce what p1 banked, not the joint's convention.

    p1 selects on plain `top10_acc` over all validation rows and banks that value
    (`p1_region_head_ablation.py:863` returns `per_metric_best["top10_acc"]["snapshot"]`; the driver
    reads `aggregate['top10_acc_mean']`, run_wave.sh:185). The joint's diag-best region figure is a
    different quantity at a different epoch: in-distribution top-10, discounted by the OOD share.

    The series below is built so the two conventions pick DIFFERENT epochs — otherwise the test
    would pass under either implementation.
    """
    from mtlcheck.train import scoring as mine

    series = {
        "top10_acc":        [0.700, 0.690, 0.680],   # best at epoch 1
        "top10_acc_indist": [0.690, 0.710, 0.700],   # best at epoch 2
        "ood_fraction":     [0.020, 0.030, 0.020],
    }
    out = mine.single_task_best(series, "top10_acc_indist")

    assert out["lane"] == "dedicated_banked"
    assert out["metric"] == "top10_acc"
    assert out["epoch"] == 1, "the banked lane selects on plain top-10"
    assert out["value"] == pytest.approx(0.700)

    joint = out["joint_convention"]
    assert joint["epoch"] == 2, "the joint lane selects on the in-distribution series"
    assert joint["top10_full"] == pytest.approx(0.710 * 0.97)
    assert joint["epoch"] != out["epoch"], "the two lanes must be distinguishable here"


@pytest.mark.equivalence
def test_category_selection_is_unambiguous() -> None:
    from mtlcheck.train import scoring as mine

    out = mine.single_task_best({"f1": [0.1, 0.4, 0.3]}, "f1")
    assert out["epoch"] == 2 and out["metric"] == "f1" and out["lane"] == "diag_best"


@pytest.mark.equivalence
def test_region_selection_needs_both_series() -> None:
    from mtlcheck.train import scoring as mine
    with pytest.raises(ValueError, match="both top10_acc"):
        mine.single_task_best({"top10_acc_indist": [0.5]}, "top10_acc_indist")
