"""Finalize the C2HGI+POI2Vec reg-STL diagnostic.

Mirrors finalize_postpool_diagnostic.py but reads the
``check2hgi_poi2vec_reg_gethard_pf_5f50ep`` tag.
"""

from __future__ import annotations

import json
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
    tag = f"STL_{upstate}_check2hgi_poi2vec_reg_gethard_pf_5f50ep"
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
    dest = PERFOLD / f"{code}_check2hgi_poi2vec_reg_gethard_pf_5f50ep.json"
    dest.write_text(json.dumps(out, indent=2))
    return dest


def per_fold_metric(path: Path, metric: str) -> list[float]:
    d = json.load(path.open())
    return [d[f"fold_{i}"][metric] for i in range(5)]


def wilcoxon_one_sided_greater(x: list[float], y: list[float]) -> tuple[float, float]:
    from scipy import stats

    x = np.asarray(x); y = np.asarray(y)
    diff = x - y
    if np.all(diff == 0):
        return 0.0, 1.0
    res = stats.wilcoxon(diff, alternative="greater", zero_method="zsplit")
    return float(diff.mean()), float(res.pvalue)


def tost_non_inferiority(x: list[float], y: list[float], margin: float) -> float:
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
    print("c2hgi + POI2Vec features — extract + paired tests")
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
        poi2vec = dest

        if not (canonical.exists() and hgi.exists()):
            print(f"[{state}] missing baseline per-fold JSONs")
            continue

        print()
        print(f"  {state} — Acc@10 / MRR per-substrate (mean ± std):")
        for label, p in [("canonical", canonical), ("poi2vec ", poi2vec), ("hgi      ", hgi)]:
            a = np.array(per_fold_metric(p, "acc10"))
            m = np.array(per_fold_metric(p, "mrr"))
            print(f"    {label}  Acc@10={a.mean()*100:6.2f} ± {a.std(ddof=1)*100:.2f}    "
                  f"MRR={m.mean()*100:6.2f} ± {m.std(ddof=1)*100:.2f}")

        a_p2v = per_fold_metric(poi2vec, "acc10")
        a_can = per_fold_metric(canonical, "acc10")
        a_hgi = per_fold_metric(hgi, "acc10")

        d_vs_can, p_vs_can = wilcoxon_one_sided_greater(a_p2v, a_can)
        d_vs_hgi, p_vs_hgi = wilcoxon_one_sided_greater(a_p2v, a_hgi)
        tost_p = tost_non_inferiority(a_p2v, a_hgi, 0.02)

        gap_canonical_hgi = (np.mean(a_hgi) - np.mean(a_can))
        gap_poi2vec_hgi = (np.mean(a_hgi) - np.mean(a_p2v))
        gap_closed_pp = gap_canonical_hgi - gap_poi2vec_hgi
        gap_closed_pct = (gap_closed_pp / gap_canonical_hgi * 100) if gap_canonical_hgi != 0 else 0.0

        print()
        print(f"  paired tests on Acc@10:")
        print(f"    Δ̄ poi2vec − canonical = {d_vs_can*100:+.2f} pp  (Wilcoxon p_greater = {p_vs_can:.4f})")
        print(f"    Δ̄ poi2vec − hgi       = {d_vs_hgi*100:+.2f} pp  (Wilcoxon p_greater = {p_vs_hgi:.4f})")
        print(f"    TOST δ=2pp vs hgi p_lower = {tost_p:.4f}  "
              f"({'non-inferior ✓' if tost_p < 0.05 else 'fails non-inf'})")
        print()
        print(f"  gap closed: {gap_closed_pp*100:+.2f} pp  "
              f"({gap_closed_pct:.1f}% of canonical→hgi gap of {gap_canonical_hgi*100:.2f} pp)")
        print()

        out_json = {
            "state": state,
            "metric": "acc10",
            "comparison": "poi2vec vs canonical (c2hgi) and vs hgi",
            "poi2vec_per_fold": a_p2v,
            "canonical_per_fold": a_can,
            "hgi_per_fold": a_hgi,
            "delta_poi2vec_minus_canonical": d_vs_can,
            "wilcoxon_p_poi2vec_gt_canonical": p_vs_can,
            "delta_poi2vec_minus_hgi": d_vs_hgi,
            "wilcoxon_p_poi2vec_gt_hgi": p_vs_hgi,
            "tost_delta_2pp_p_lower": tost_p,
            "gap_canonical_to_hgi_pp": gap_canonical_hgi * 100,
            "gap_poi2vec_to_hgi_pp": gap_poi2vec_hgi * 100,
            "gap_closed_pp": gap_closed_pp * 100,
            "gap_closed_pct": gap_closed_pct,
        }
        out_path = PAIRED / f"{state}_poi2vec_diagnostic_acc10.json"
        out_path.write_text(json.dumps(out_json, indent=2, default=float))
        print(f"  wrote {out_path}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
