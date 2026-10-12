"""Paired-tests for Designs I/J/M vs canonical c2hgi (cat) and HGI (reg).

Wilcoxon one-sided greater for both cat and reg (alpha=0.0312, n=5 floor).
TOST non-inferiority at δ=2pp for cat (matches B/H dominance criterion).
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


def block(code: str, design_tag: str) -> dict | None:
    d_cat = PERFOLD / f"{code}_{design_tag}_cat_gru_5f50ep.json"
    c_cat = PERFOLD / f"{code}_check2hgi_cat_gru_5f50ep.json"
    d_reg = PERFOLD / f"{code}_{design_tag}_reg_gethard_pf_5f50ep.json"
    c_reg = PERFOLD / f"{code}_check2hgi_reg_gethard_pf_5f50ep.json"
    h_reg = PERFOLD / f"{code}_hgi_reg_gethard_pf_5f50ep.json"

    has_cat = d_cat.exists() and c_cat.exists()
    if not all(p.exists() for p in [d_reg, c_reg, h_reg]):
        missing = [p.name for p in [d_reg, c_reg, h_reg] if not p.exists()]
        print(f"  [{code}/{design_tag}] missing reg: {missing}")
        return None

    if has_cat:
        x = per_fold(d_cat, "f1"); y = per_fold(c_cat, "f1")
        d_cat_mean, p_cat = wilcoxon_g(x, y)
        tost_cat = tost_ni(x, y, 0.02)
    else:
        x = y = []
        d_cat_mean = 0.0; p_cat = 1.0; tost_cat = 1.0

    a_d = per_fold(d_reg, "acc10")
    a_c = per_fold(c_reg, "acc10")
    a_h = per_fold(h_reg, "acc10")
    d_vs_c, p_vs_c = wilcoxon_g(a_d, a_c)
    d_vs_h, p_vs_h = wilcoxon_g(a_d, a_h)

    return {
        "cat": {
            "design": x, "canonical": y,
            "delta": d_cat_mean,
            "wilcoxon_p_greater": p_cat,
            "tost_p_lower_2pp": tost_cat,
            "non_inferior": tost_cat < 0.05,
            "strict_better": p_cat < 0.05,
        },
        "reg_acc10": {
            "design": a_d, "canonical": a_c, "hgi": a_h,
            "delta_vs_canonical": d_vs_c,
            "p_gt_can": p_vs_c,
            "delta_vs_hgi": d_vs_h,
            "p_gt_hgi": p_vs_h,
            "strict_better_than_can": p_vs_c < 0.05,
        },
    }


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--designs", nargs="+", default=["b", "i", "j", "m"])
    ap.add_argument("--states", nargs="+",
                    default=["alabama", "arizona", "florida"])
    ap.add_argument("--out", default="design_ijm_diagnostic.json")
    args = ap.parse_args()
    code_of = {"alabama": "AL", "arizona": "AZ", "florida": "FL"}
    out = {}
    for design in args.designs:
        print(f"\n=== Design {design.upper()} ===")
        for state in args.states:
            code = code_of[state]
            blk = block(code, f"design_{design}")
            if blk is None:
                continue
            out[f"{state}_{design}"] = blk
            cat = blk["cat"]; reg = blk["reg_acc10"]
            print(f"  {state}:")
            print(f"    cat  Δ={cat['delta']*100:+.2f}pp  Wilcox p_gt={cat['wilcoxon_p_greater']:.4f}  "
                  f"TOST p={cat['tost_p_lower_2pp']:.4f}  "
                  f"{'NON-INF ✓' if cat['non_inferior'] else 'fails non-inf ✗'}")
            print(f"    reg  Δ vs can={reg['delta_vs_canonical']*100:+.2f}pp  p_gt={reg['p_gt_can']:.4f}  "
                  f"Δ vs HGI={reg['delta_vs_hgi']*100:+.2f}pp")

    out_path = PAIRED / args.out
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {out_path}")

    print("\n" + "=" * 72)
    print("DOMINANCE VERDICT (cat non-inf @ TOST p<0.05 + reg superior to canonical)")
    print("=" * 72)
    for k, b in out.items():
        cat_ok = b["cat"]["non_inferior"]
        reg_better = b["reg_acc10"]["delta_vs_canonical"] > 0
        reg_strict = b["reg_acc10"]["strict_better_than_can"]
        verdict = "✓ DOMINANCE" if cat_ok and reg_better else "✗"
        if cat_ok and reg_strict:
            verdict += " (strict reg)"
        print(f"  {k:18s}  cat_non_inf={cat_ok}  reg_>can={reg_better}  reg_strict={reg_strict}  → {verdict}")


if __name__ == "__main__":
    main()
