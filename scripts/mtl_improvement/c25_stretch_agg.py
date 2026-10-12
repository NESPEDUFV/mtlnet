#!/usr/bin/env python
"""Aggregate the C25 stretch sweeps (T2.3 MoE + T2.4 SwiGLU + #19 B9 continuity).

Reads the three manifests, groups by arm tag, averages the per-seed FL results
across seeds {0,1,7,100}, and ranks every arm against the FL reference anchors:

  (c) STL ceiling         reg 73.31 / cat 69.97   (frozen STL dual-axis best)
  base_a (v14 onecycle)   reg 71.55 / cat 71.89   (c25_revalidate FL, the zero-point)
  canon  (v11 onecycle)   reg 70.74 / cat 72.07   (c25_revalidate FL)
  dual_gated (T2.1)       reg 73.06               (c25_tier2_refix FL — current best)

Metric fields (the C25 convention; see docs + memory ref_mtl_metric_field):
  reg = per_metric_best.next_region.top10_acc_indist.mean   (DISJOINT, selector-independent)
  cat = diagnostic_task_best.next_category.f1.mean          (per-task diagnostic best)

  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/c25_stretch_agg.py
"""
import json
import statistics as st
from pathlib import Path

MANIFESTS = {
    "T2.3/T2.0-2 (c25_tier2_refix)": "c25_tier2_refix_manifest.tsv",
    "T2.4 SwiGLU (c25_t24_swiglu)": "c25_t24_swiglu_manifest.tsv",
    "#19 B9 §0.1 continuity (c25_fl_b9_continuity)": "c25_fl_b9_continuity_manifest.tsv",
}

ANCHORS = {  # name: (reg, cat) — cat may be None
    "(c) STL ceiling": (73.31, 69.97),
    "base_a v14 onecycle": (71.55, 71.89),
    "canon v11 onecycle": (70.74, 72.07),
    "dual_gated (T2.1)": (73.06, None),
}


def _metrics(rd):
    """(reg_disjoint, cat_diagnostic) in percent, or None if unreadable."""
    p = Path(rd) / "summary" / "full_summary.json"
    if not p.exists():
        return None
    try:
        s = json.load(open(p))
        reg = s["per_metric_best"]["next_region"]["top10_acc_indist"]["mean"] * 100
        cat = s["diagnostic_task_best"]["next_category"]["f1"]["mean"] * 100
        return (round(reg, 2), round(cat, 2))
    except Exception:
        return None


def _load(mf):
    """tag -> list of (reg, cat) across seeds."""
    out = {}
    p = Path("scripts/mtl_improvement") / mf
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        key, tag, rd = parts[0], parts[1], parts[2]
        m = _metrics(rd)
        if m is None:
            continue
        out.setdefault(tag, []).append(m)
    return out


def _fmt(vals):
    if not vals:
        return "—", "—", 0
    regs = [v[0] for v in vals]
    cats = [v[1] for v in vals]
    n = len(vals)
    rm = st.mean(regs)
    cm = st.mean(cats)
    rs = st.pstdev(regs) if n > 1 else 0.0
    cs = st.pstdev(cats) if n > 1 else 0.0
    return f"{rm:5.2f}±{rs:.2f}", f"{cm:5.2f}±{cs:.2f}", n


def main():
    CEIL_R, CEIL_C = ANCHORS["(c) STL ceiling"]
    BASE_R = ANCHORS["base_a v14 onecycle"][0]

    print("\n" + "=" * 78)
    print("C25 STRETCH — FL multi-seed {0,1,7,100}, UNWEIGHTED real-joint (reg disjoint / cat diag)")
    print("=" * 78)
    print("\n  anchors:")
    for name, (r, c) in ANCHORS.items():
        cc = f"{c:5.2f}" if c is not None else "  —  "
        print(f"    {name:<24} reg={r:5.2f}  cat={cc}")

    rows = []
    for label, mf in MANIFESTS.items():
        data = _load(mf)
        if not data:
            print(f"\n  [{label}] — no landed results yet")
            continue
        print(f"\n  [{label}]")
        print(f"    {'arm':<14}{'reg@10 disj':>16}{'cat-F1 diag':>16}{'n':>4}"
              f"{'Δreg vs base_a':>16}{'Δreg vs ceiling':>17}")
        for tag in sorted(data):
            rfmt, cfmt, n = _fmt(data[tag])
            rmean = st.mean([v[0] for v in data[tag]])
            d_base = rmean - BASE_R
            d_ceil = rmean - CEIL_R
            flag = "  ★ABOVE CEILING" if rmean > CEIL_R else ""
            print(f"    {tag:<14}{rfmt:>16}{cfmt:>16}{n:>4}"
                  f"{d_base:>+16.2f}{d_ceil:>+17.2f}{flag}")
            rows.append((label, tag, rmean, st.mean([v[1] for v in data[tag]])))

    print("\n  " + "-" * 60)
    above = [r for r in rows if r[2] > CEIL_R]
    if above:
        print("  ★ arms that pushed FL reg ABOVE the STL ceiling (73.31):")
        for label, tag, r, c in sorted(above, key=lambda x: -x[2]):
            print(f"      {tag:<14} reg={r:5.2f} (+{r-CEIL_R:.2f})  cat={c:5.2f}  [{label}]")
    else:
        print("  no arm exceeded the STL ceiling (73.31) — dual_gated 73.06 remains FL best")
    print()


if __name__ == "__main__":
    main()
