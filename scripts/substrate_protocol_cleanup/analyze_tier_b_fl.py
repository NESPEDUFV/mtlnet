"""FL Tier B (B9) TWO-FRONT analysis — disjoint AND joint(geom_simple), reg AND cat.

Pure re-analysis of the FL B9 per-fold val CSVs produced under
``docs/results/substrate_protocol_cleanup/tier_b_fl/<tag>/florida/seed42/mtlnet_*``.
Methodology is byte-identical to ``analyze_tier_b_two_front.py`` (the AL/AZ
analyzer): reg = ``top10_acc_indist``, cat = ``f1``; disjoint = each head's own
best-val epoch; joint = single epoch maximising sqrt(cat_f1 * reg_top10_indist)
over shared epochs. Wilcoxon one-sided design>canon on RAW per-fold values
(scipy auto-exact when no ties).

Cells (all FL, seed42, 5-fold, B9 recipe):
  α-default (alpha_init=0.1, trainable): mtl_canonical, mtl_design_b/j/l
  α=0 (freeze_alpha=true, alpha_init=0.0): a0_canonical, a0_design_b

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_tier_b_fl.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
FL = REPO / "docs/results/substrate_protocol_cleanup/tier_b_fl"

DESIGNS = {
    "mtl_design_b": "Design B (POI2Vec @ pool boundary)",
    "mtl_design_j": "Design J (H + anchor lambda=0.1)",
    "mtl_design_l": "Lever 5 (KL distill)",
}


def _run_dir(tag: str) -> Path:
    cell = FL / tag / "florida" / "seed42"
    cands = sorted(cell.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not cands:
        raise FileNotFoundError(f"no mtlnet_* under {cell}")
    return cands[0]


def _per_fold(run_dir: Path) -> dict:
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
    deltas = [design_vals[i] - base_vals[i] for i in range(len(design_vals))]
    try:
        w = wilcoxon(deltas, alternative="greater")
        W, p = float(w.statistic), float(w.pvalue)
    except ValueError:
        W, p = float("nan"), float("nan")
    return deltas, _mean(deltas), W, p


def _compare(design_pf, base_pf):
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
    result = {"alpha_default": {}, "alpha_0": {}}

    # ---- α-default Tier B cells ----
    base_pf = _per_fold(_run_dir("mtl_canonical"))
    result["alpha_default"]["florida"] = {"canonical_baseline": {"per_fold": base_pf}}
    for tag, label in DESIGNS.items():
        try:
            d_pf = _per_fold(_run_dir(tag))
        except FileNotFoundError:
            result["alpha_default"]["florida"][tag] = {"label": label, "status": "MISSING"}
            continue
        result["alpha_default"]["florida"][tag] = {
            "label": label,
            "per_fold": d_pf,
            "compare": _compare(d_pf, base_pf),
        }

    # ---- α=0 cells: design_b vs canonical ----
    try:
        base_pf0 = _per_fold(_run_dir("a0_canonical"))
        db_pf0 = _per_fold(_run_dir("a0_design_b"))
        result["alpha_0"]["florida"] = {
            "canonical_baseline": {"per_fold": base_pf0},
            "design_b": {
                "label": "Design B (alpha frozen=0)",
                "per_fold": db_pf0,
                "compare": _compare(db_pf0, base_pf0),
            },
        }
    except FileNotFoundError as e:
        result["alpha_0"]["florida"] = {"status": f"MISSING: {e}"}

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
