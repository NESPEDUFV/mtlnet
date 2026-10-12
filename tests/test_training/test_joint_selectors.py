"""`_compute_joint_selectors` — the 5 joint scalars + the checkpoint-selector dispatch."""

import math

from training.runners.mtl_cv import _compute_joint_selectors


def test_joint_scalars_and_default_geom_simple():
    f1_b, f1_a, acc1_b, acc1_a, reg10 = 0.06, 0.64, 0.30, 0.67, 0.71
    mb, ma = 0.225, 0.342
    js, ja1, jgl, jal, jgs, sel = _compute_joint_selectors(
        f1_b, f1_a, acc1_b, acc1_a, reg10, mb, ma, "geom_simple"
    )
    lb, la = max(acc1_b / mb, 1e-8), max(acc1_a / ma, 1e-8)
    assert js == 0.5 * (f1_b + f1_a)
    assert ja1 == 0.5 * (acc1_b + acc1_a)
    assert jgl == math.sqrt(lb * la)
    assert jal == 0.5 * (lb + la)
    assert jgs == math.sqrt(max(f1_a, 0.0) * max(reg10, 0.0))
    assert sel == jgs  # geom_simple is the default selector


def test_selector_dispatch():
    args = (0.06, 0.64, 0.30, 0.67, 0.71, 0.225, 0.342)
    js, _, jgl, _, jgs, _ = _compute_joint_selectors(*args, "geom_simple")
    assert _compute_joint_selectors(*args, "joint_f1_mean")[5] == js   # v11 legacy
    assert _compute_joint_selectors(*args, "geom_lift")[5] == jgl       # interim
    assert _compute_joint_selectors(*args, "geom_simple")[5] == jgs     # default


def test_non_region_taskb_geom_simple_uses_f1_fallback():
    # The caller passes reg_acc10 = f1_b when task_b has no top10 key → sqrt(f1_a * f1_b).
    f1_b, f1_a = 0.40, 0.55
    _, _, _, _, jgs, _ = _compute_joint_selectors(
        f1_b, f1_a, 0.4, 0.55, f1_b, 0.3, 0.3, "geom_simple"
    )
    assert jgs == math.sqrt(f1_a * f1_b)
