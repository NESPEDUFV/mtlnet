"""Tier B TWO-FRONT analysis — disjoint AND joint(geom_simple) for reg AND cat.

Pure re-analysis of existing per-fold val CSVs. No GPU, no retraining.

Two fronts per (design, state, task):
  - DISJOINT: each head at its OWN best val epoch.
      reg = max-over-epochs top10_acc_indist ; cat = max-over-epochs f1
  - JOINT (geom_simple): both heads read off the SINGLE epoch maximising
      sqrt(cat_f1 * reg_top10_indist) over shared epochs.

Wilcoxon: RAW per-fold values, paired by fold, one-sided design>canon for reg
(scipy auto-exact when no ties). For cat we report two-sided as well as the
delta sign; the promotion gate uses Δcat >= -0.5 not a p-test.

Method matches scripts/analyze_tier_b_wave1.py (disjoint+geom) and the Tier A1
geom_simple definition (geo-mean of cat f1 and reg top10_acc_indist).
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TIER_B = REPO / "docs/results/substrate_protocol_cleanup/tier_b"

# α=0.1 (canonical recipe) Tier B cells
A01_DESIGNS = {
    "design_b": "Design B (POI2Vec @ pool boundary)",
    "design_j": "Design J (H + anchor lambda=0.1)",
    "design_l": "Lever 5 (KL distill)",
}
STL_REG = {"alabama": 61.21, "arizona": 53.06}


def _run_dir_a01(tag: str, state: str) -> Path:
    cell = TIER_B / tag / state / "seed42"
    cands = sorted(cell.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"no mtlnet_* under {cell}")
    return cands[0]


def _run_dir_a0(which: str) -> Path:
    # α=0 reaudit cells (AL only)
    base = TIER_B / "reaudit_d1"
    if which == "design_b":
        root = base / "d1_design_b_a0" / "check2hgi_design_b" / "alabama"
    elif which == "canonical_baseline":
        root = base / "d1_canonical_a0" / "check2hgi" / "alabama"
    else:
        raise ValueError(which)
    cands = sorted(root.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"no mtlnet_* under {root}")
    return cands[0]


def _per_fold(run_dir: Path) -> dict:
    """Return per-fold raw % values for all 4 fronts."""
    out = {"disjoint_reg": [], "disjoint_cat": [], "joint_reg": [], "joint_cat": []}
    for fold in range(1, 6):
        cat_df = pd.read_csv(run_dir / "metrics" / f"fold{fold}_next_category_val.csv")
        reg_df = pd.read_csv(run_dir / "metrics" / f"fold{fold}_next_region_val.csv")
        cat_by = {int(r.epoch): r for _, r in cat_df.iterrows()}
        reg_by = {int(r.epoch): r for _, r in reg_df.iterrows()}
        cb = max(cat_by, key=lambda e: cat_by[e]["f1"])
        rb = max(reg_by, key=lambda e: reg_by[e]["top10_acc_indist"])
        out["disjoint_cat"].append(float(cat_by[cb]["f1"]) * 100)
        out["disjoint_reg"].append(float(reg_by[rb]["top10_acc_indist"]) * 100)
        shared = sorted(set(cat_by) & set(reg_by))

        def geom(ep):
            c = float(cat_by[ep]["f1"])
            r = float(reg_by[ep]["top10_acc_indist"])
            return math.sqrt(c * r) if c > 0 and r > 0 else 0.0

        ge = max(shared, key=geom)
        out["joint_cat"].append(float(cat_by[ge]["f1"]) * 100)
        out["joint_reg"].append(float(reg_by[ge]["top10_acc_indist"]) * 100)
    return out


def _mean(xs):
    return sum(xs) / len(xs)


def _wilcox_gt(design_vals, base_vals):
    """One-sided design>base on RAW per-fold values."""
    deltas = [design_vals[i] - base_vals[i] for i in range(len(design_vals))]
    try:
        w = wilcoxon(deltas, alternative="greater")
        W, p = float(w.statistic), float(w.pvalue)
    except ValueError:
        W, p = float("nan"), float("nan")
    return deltas, _mean(deltas), W, p


def _compare(design_pf, base_pf):
    """All-front comparison of one design vs base."""
    res = {}
    for front, regkey, catkey in [
        ("disjoint", "disjoint_reg", "disjoint_cat"),
        ("joint", "joint_reg", "joint_cat"),
    ]:
        d_reg, m_reg, W_reg, p_reg = _wilcox_gt(design_pf[regkey], base_pf[regkey])
        d_cat, m_cat, W_cat, p_cat = _wilcox_gt(design_pf[catkey], base_pf[catkey])
        res[front] = {
            "reg_design_mean": _mean(design_pf[regkey]),
            "reg_base_mean": _mean(base_pf[regkey]),
            "reg_delta_mean": m_reg,
            "reg_deltas": d_reg,
            "reg_W": W_reg,
            "reg_p_gt": p_reg,
            "cat_design_mean": _mean(design_pf[catkey]),
            "cat_base_mean": _mean(base_pf[catkey]),
            "cat_delta_mean": m_cat,
            "cat_deltas": d_cat,
            "cat_W": W_cat,
            "cat_p_gt": p_cat,
        }
    return res


def main():
    result = {"alpha_0p1": {}, "alpha_0": {}}

    # ---- α=0.1 canonical Tier B cells (AL + AZ) ----
    for state in ("alabama", "arizona"):
        base_pf = _per_fold(_run_dir_a01("canonical_baseline", state))
        result["alpha_0p1"][state] = {
            "canonical_baseline": {"per_fold": base_pf},
            "stl_reg_ceiling": STL_REG[state],
        }
        for tag, label in A01_DESIGNS.items():
            d_pf = _per_fold(_run_dir_a01(tag, state))
            result["alpha_0p1"][state][tag] = {
                "label": label,
                "per_fold": d_pf,
                "compare": _compare(d_pf, base_pf),
            }

    # ---- α=0 reaudit cells (AL only): design_b vs canonical ----
    base_pf0 = _per_fold(_run_dir_a0("canonical_baseline"))
    db_pf0 = _per_fold(_run_dir_a0("design_b"))
    result["alpha_0"]["alabama"] = {
        "canonical_baseline": {"per_fold": base_pf0},
        "design_b": {
            "label": "Design B (alpha frozen=0)",
            "per_fold": db_pf0,
            "compare": _compare(db_pf0, base_pf0),
        },
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
