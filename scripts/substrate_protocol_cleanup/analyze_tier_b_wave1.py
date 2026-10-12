"""Tier B Wave 1 verdict — Designs B/J/L vs the canonical_baseline cell.

Unlike summarize_tier_b.py (which paired against a separate phase1v3 JSON),
this paires each design's per-fold disjoint reg top10_acc against the
`canonical_baseline` MTL cell AT THE SAME STATE (same seed=42, same H3-alt
recipe, same folds), per the Tier B task brief. Wilcoxon is run on RAW
per-fold values (no rounding), one-sided (design > canonical), paired by fold.

Frontiers extracted per fold from the val metric CSVs:
    - disjoint reg  = max over epochs of top10_acc_indist  (reg-best epoch)
    - disjoint cat  = max over epochs of f1               (cat-best epoch)
    - geom_simple   = epoch maximising sqrt(cat_f1 * reg_top10) over shared epochs
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TIER_B = REPO / "docs/results/substrate_protocol_cleanup/tier_b"

DESIGNS = {
    "design_b": "Design B (POI2Vec @ pool boundary)",
    "design_j": "Design J (H + anchor λ=0.1)",
    "design_l": "Lever 5 (KL distill)",
}
# STL ceilings for reg top10 (next_stan_flow matched head), RESULTS_TABLE §0.1 v11 L70-71
STL_REG = {"alabama": 61.21, "arizona": 53.06}


def _run_dir(tag: str, state: str) -> Path:
    cell = TIER_B / tag / state / "seed42"
    cands = sorted(cell.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0]


def _per_fold(run_dir: Path) -> dict:
    out = {"disjoint_reg": [], "disjoint_cat": [], "geom_reg": [], "geom_cat": []}
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
        out["geom_cat"].append(float(cat_by[ge]["f1"]) * 100)
        out["geom_reg"].append(float(reg_by[ge]["top10_acc_indist"]) * 100)
    return out


def _mean(xs):
    return sum(xs) / len(xs)


def main():
    result = {}
    for state in ("alabama", "arizona"):
        base = _per_fold(_run_dir("canonical_baseline", state))
        result[state] = {
            "canonical_baseline": {
                "disjoint_reg_mean": _mean(base["disjoint_reg"]),
                "disjoint_cat_mean": _mean(base["disjoint_cat"]),
                "geom_reg_mean": _mean(base["geom_reg"]),
                "geom_cat_mean": _mean(base["geom_cat"]),
                "per_fold": base,
                "stl_reg_ceiling": STL_REG[state],
            }
        }
        for tag, label in DESIGNS.items():
            v = _per_fold(_run_dir(tag, state))
            deltas = [v["disjoint_reg"][i] - base["disjoint_reg"][i] for i in range(5)]
            # one-sided: design > canonical
            try:
                w = wilcoxon(deltas, alternative="greater")
                W, p = float(w.statistic), float(w.pvalue)
            except ValueError:
                # all-zero deltas degenerate
                W, p = float("nan"), float("nan")
            d_reg = _mean(deltas)
            d_cat = _mean(v["disjoint_cat"]) - _mean(base["disjoint_cat"])
            d_geom_reg = _mean(v["geom_reg"]) - _mean(base["geom_reg"])
            folds_pos = sum(1 for d in deltas if d > 0)
            if not math.isnan(p) and p <= 0.05 and d_cat >= -0.5:
                verdict = "PROMOTE"
            elif not math.isnan(p) and p <= 0.05 and d_cat < -0.5:
                verdict = "SIG-BUT-CAT-REGRESS"
            elif not math.isnan(p):
                verdict = "NULL" if d_reg >= 0 else "FALSIFIED"
            else:
                verdict = "INDETERMINATE"
            result[state][tag] = {
                "label": label,
                "disjoint_reg_mean": _mean(v["disjoint_reg"]),
                "disjoint_cat_mean": _mean(v["disjoint_cat"]),
                "geom_reg_mean": _mean(v["geom_reg"]),
                "geom_cat_mean": _mean(v["geom_cat"]),
                "per_fold": v,
                "deltas_disjoint_reg": deltas,
                "delta_disjoint_reg_mean": d_reg,
                "delta_disjoint_cat_mean": d_cat,
                "delta_geom_reg_mean": d_geom_reg,
                "folds_positive": folds_pos,
                "wilcoxon_W": W,
                "wilcoxon_p": p,
                "verdict": verdict,
            }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
