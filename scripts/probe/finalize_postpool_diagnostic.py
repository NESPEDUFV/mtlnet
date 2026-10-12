"""Finalize the C2HGI post-pool reg-STL diagnostic.

For each state in {alabama, arizona}:
  1. Read the P1 result JSON for the postpool tag.
  2. Write a flat per-fold JSON under docs/.../phase1_perfold/.
  3. Run paired Wilcoxon vs canonical c2hgi (Phase-3 leak-free baseline) and
     vs hgi (Phase-3 leak-free baseline). TOST δ=2pp on Acc@10.
  4. Print a summary table comparing canonical / postpool / hgi.

Run after both training jobs land.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
DOCS_RES = REPO / "docs" / "studies" / "check2hgi" / "results"
P1 = DOCS_RES / "P1"
PERFOLD = DOCS_RES / "phase1_perfold"
PAIRED = DOCS_RES / "paired_tests"

STATES = ["alabama", "arizona"]
STATE_CODE = {"alabama": "AL", "arizona": "AZ"}


def extract(state: str) -> Path | None:
    upstate = state.upper()
    tag = f"STL_{upstate}_check2hgi_postpool_reg_gethard_pf_5f50ep"
    p1_path = P1 / f"region_head_{state}_region_5f_50ep_{tag}.json"
    if not p1_path.exists():
        print(f"[{state}] MISSING {p1_path.name}")
        return None
    d = json.load(p1_path.open())
    pf = d["heads"]["next_getnext_hard"]["per_fold"]
    out = {}
    for i, f in enumerate(pf):
        out[f"fold_{i}"] = {
            "f1": f.get("f1"),
            "acc1": f.get("accuracy"),
            "acc5": f.get("top5_acc"),
            "acc10": f.get("top10_acc"),
            "mrr": f.get("mrr"),
        }
    code = STATE_CODE[state]
    dest = PERFOLD / f"{code}_check2hgi_postpool_reg_gethard_pf_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    return dest


def per_fold_metric(path: Path, metric: str) -> list[float]:
    d = json.load(path.open())
    return [d[f"fold_{i}"][metric] for i in range(5)]


def wilcoxon_one_sided_greater(x: list[float], y: list[float]) -> tuple[float, float]:
    """Paired Wilcoxon, H1: x > y (i.e. mean(x-y) > 0). Returns (mean_delta, p)."""
    from scipy import stats

    x = np.asarray(x); y = np.asarray(y)
    diff = x - y
    if np.all(diff == 0):
        return 0.0, 1.0
    res = stats.wilcoxon(diff, alternative="greater", zero_method="zsplit")
    return float(diff.mean()), float(res.pvalue)


def tost_non_inferiority(x: list[float], y: list[float], margin: float) -> float:
    """TOST: lower bound. p_lower = P(mean(x-y) < -margin)."""
    from scipy import stats

    x = np.asarray(x); y = np.asarray(y)
    diff = x - y
    n = len(diff)
    se = diff.std(ddof=1) / np.sqrt(n)
    if se == 0:
        return 0.0 if diff.mean() > -margin else 1.0
    t = (diff.mean() + margin) / se
    p_lower = 1 - stats.t.cdf(t, df=n - 1)
    return float(p_lower)


def main() -> int:
    print("=" * 64)
    print("Postpool diagnostic — extract + paired tests")
    print("=" * 64)

    for state in STATES:
        code = STATE_CODE[state]
        dest = extract(state)
        if dest is None:
            print(f"[{state}] skip — no P1 JSON")
            continue
        print(f"[{state}] wrote {dest.name}")

        canonical = PERFOLD / f"{code}_check2hgi_reg_gethard_pf_5f50ep.json"
        hgi = PERFOLD / f"{code}_hgi_reg_gethard_pf_5f50ep.json"
        postpool = dest

        if not (canonical.exists() and hgi.exists()):
            print(f"[{state}] missing baseline per-fold JSONs")
            continue

        print()
        print(f"  {state} — Acc@10 / MRR per-substrate (mean ± std):")
        for label, p in [("canonical", canonical), ("postpool", postpool), ("hgi", hgi)]:
            a = np.array(per_fold_metric(p, "acc10"))
            m = np.array(per_fold_metric(p, "mrr"))
            print(f"    {label:10s}  Acc@10={a.mean()*100:6.2f} ± {a.std(ddof=1)*100:.2f}    "
                  f"MRR={m.mean()*100:6.2f} ± {m.std(ddof=1)*100:.2f}")

        a_post = per_fold_metric(postpool, "acc10")
        a_can = per_fold_metric(canonical, "acc10")
        a_hgi = per_fold_metric(hgi, "acc10")
        m_post = per_fold_metric(postpool, "mrr")
        m_hgi = per_fold_metric(hgi, "mrr")

        d_vs_can, p_vs_can = wilcoxon_one_sided_greater(a_post, a_can)
        d_vs_hgi, p_vs_hgi = wilcoxon_one_sided_greater(a_post, a_hgi)
        tost_p = tost_non_inferiority(a_post, a_hgi, 0.02)

        gap_canonical_hgi = (np.mean(a_hgi) - np.mean(a_can))
        gap_postpool_hgi = (np.mean(a_hgi) - np.mean(a_post))
        gap_closed_pp = gap_canonical_hgi - gap_postpool_hgi
        gap_closed_pct = (gap_closed_pp / gap_canonical_hgi * 100) if gap_canonical_hgi != 0 else 0.0

        print()
        print(f"  paired tests on Acc@10:")
        print(f"    Δ̄ postpool − canonical = {d_vs_can*100:+.2f} pp  (Wilcoxon p_greater = {p_vs_can:.4f})")
        print(f"    Δ̄ postpool − hgi       = {d_vs_hgi*100:+.2f} pp  (Wilcoxon p_greater = {p_vs_hgi:.4f})")
        print(f"    TOST δ=2pp vs hgi p_lower = {tost_p:.4f}  "
              f"({'non-inferior ✓' if tost_p < 0.05 else 'fails non-inf'})")
        print()
        print(f"  gap closed: {gap_closed_pp*100:+.2f} pp  "
              f"({gap_closed_pct:.1f}% of canonical→hgi gap of {gap_canonical_hgi*100:.2f} pp)")
        print()

        # Persist paired-test JSON
        out_json = {
            "state": state,
            "metric": "acc10",
            "comparison": "postpool vs canonical (c2hgi) and vs hgi",
            "postpool_per_fold": a_post,
            "canonical_per_fold": a_can,
            "hgi_per_fold": a_hgi,
            "delta_postpool_minus_canonical": d_vs_can,
            "wilcoxon_p_postpool_gt_canonical": p_vs_can,
            "delta_postpool_minus_hgi": d_vs_hgi,
            "wilcoxon_p_postpool_gt_hgi": p_vs_hgi,
            "tost_delta_2pp_p_lower": tost_p,
            "gap_canonical_to_hgi_pp": gap_canonical_hgi * 100,
            "gap_postpool_to_hgi_pp": gap_postpool_hgi * 100,
            "gap_closed_pp": gap_closed_pp * 100,
            "gap_closed_pct": gap_closed_pct,
        }
        out_path = PAIRED / f"{state}_postpool_diagnostic_acc10.json"
        out_path.write_text(json.dumps(out_json, indent=2, default=float))
        print(f"  wrote {out_path}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
