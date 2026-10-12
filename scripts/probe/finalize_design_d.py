"""Paired-tests for Design D (heterograph) vs canonical c2hgi.

Reads per-fold JSON from docs/results/phase1_perfold/.
Writes docs/results/paired_tests/design_d_diagnostic.json.

Note: D's apparent cat lift is contaminated by a POI2Vec→checkin leak via
2-hop GCN through visit/seq edges. We still report the numbers but flag
them as not-trustworthy in `docs/studies/merge_design/MERGE_DESIGN_NOTES.md`.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[2]
PERFOLD = REPO / "docs/results/phase1_perfold"
PAIRED = REPO / "docs/results/paired_tests"


def per_fold(p: Path, key: str) -> list[float]:
    d = json.load(p.open())
    return [d[f"fold_{i}"][key] for i in range(5)]


def wilcoxon_g(x, y):
    diff = np.asarray(x) - np.asarray(y)
    if np.all(diff == 0):
        return 0.0, 1.0
    res = stats.wilcoxon(diff, alternative="greater", zero_method="zsplit")
    return float(diff.mean()), float(res.pvalue)


def tost_ni(x, y, margin):
    diff = np.asarray(x) - np.asarray(y)
    n = len(diff)
    se = diff.std(ddof=1) / np.sqrt(n)
    if se == 0:
        return 0.0 if diff.mean() > -margin else 1.0
    t = (diff.mean() + margin) / se
    return float(1 - stats.t.cdf(t, df=n - 1))


def main():
    out = {}
    for code, name in [("AL", "alabama"), ("AZ", "arizona")]:
        d_cat = PERFOLD / f"{code}_design_d_cat_gru_5f50ep.json"
        c_cat = PERFOLD / f"{code}_check2hgi_cat_gru_5f50ep.json"
        d_reg = PERFOLD / f"{code}_design_d_reg_gethard_pf_5f50ep.json"
        c_reg = PERFOLD / f"{code}_check2hgi_reg_gethard_pf_5f50ep.json"
        h_reg = PERFOLD / f"{code}_hgi_reg_gethard_pf_5f50ep.json"

        x = per_fold(d_cat, "f1")
        y = per_fold(c_cat, "f1")
        d_cat_mean, p_cat = wilcoxon_g(x, y)
        tost_cat = tost_ni(x, y, 0.02)

        a_d = per_fold(d_reg, "acc10")
        a_c = per_fold(c_reg, "acc10")
        a_h = per_fold(h_reg, "acc10")
        d_vs_c, p_vs_c = wilcoxon_g(a_d, a_c)
        d_vs_h, p_vs_h = wilcoxon_g(a_d, a_h)

        block = {
            "cat": {
                "design": x, "canonical": y,
                "delta": d_cat_mean,
                "wilcoxon_p_greater": p_cat,
                "tost_p_lower_2pp": tost_cat,
                "FLAG": "leak: 2-hop GCN propagates POI2Vec→checkin; cat lift is artifact",
            },
            "reg_acc10": {
                "design": a_d, "canonical": a_c, "hgi": a_h,
                "delta_vs_canonical": d_vs_c,
                "p_gt_can": p_vs_c,
                "delta_vs_hgi": d_vs_h,
                "p_gt_hgi": p_vs_h,
            },
        }
        out[name] = block
        print(f"\n=== {name} ===")
        print(f"  cat  Δ = {d_cat_mean*100:+.2f}pp  p_gt={p_cat:.4f}  (LEAK FLAGGED)")
        print(f"  reg  Δ vs can = {d_vs_c*100:+.2f}pp  p_gt={p_vs_c:.4f}")
        print(f"  reg  Δ vs hgi = {d_vs_h*100:+.2f}pp  p_gt={p_vs_h:.4f}")

    out_path = PAIRED / "design_d_diagnostic.json"
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {out_path}")


if __name__ == "__main__":
    main()
