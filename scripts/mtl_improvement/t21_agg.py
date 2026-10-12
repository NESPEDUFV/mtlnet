#!/usr/bin/env python
"""Aggregate a T2.1 dual-tower run set into a ranked per-state table.

Reads a manifest (TSV: ``state|tag<TAB>tag<TAB>rundir``) and for each run pulls,
from ``<rundir>/summary/full_summary.json``:
  * reg disjoint Acc@10  = per_metric_best.next_region.top10_acc_indist.mean  (CAPACITY)
  * reg deploy   Acc@10  = next_region.top10_acc_indist.mean                  (geom_simple)
  * cat disjoint macroF1 = diagnostic_task_best.next_category.f1.mean
  * cat deploy   macroF1 = next_category.f1.mean

Ranks by reg disjoint Acc@10 (the cleanest signal of how well the private tower
trains). Prints the frozen (c) STL reg ceiling + the (a) v14-MTL deployable
baseline as reference anchors.

Usage:
  PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/t21_agg.py \
      --manifest scripts/mtl_improvement/t21_lrsweep_manifest.tsv
"""
import argparse
import json
from pathlib import Path

# Frozen yardstick (HANDOFF §9) — reference only, never recomputed.
FROZEN_C_REG = {"alabama": 62.88, "arizona": 55.11, "georgia": 58.45, "florida": 73.31}
FROZEN_D_REG = {"alabama": 63.58, "arizona": 55.11, "georgia": 58.76, "florida": 73.62}
A_BASE_DEPLOY_REG = {"alabama": 50.14, "arizona": 37.78, "georgia": 42.64, "florida": 61.21}
FROZEN_C_CAT = {"alabama": 49.97, "arizona": 51.01, "georgia": 58.12, "florida": 69.97}


def _g(d, *path, default=None):
    for k in path:
        if not isinstance(d, dict) or k not in d:
            return default
        d = d[k]
    return d


def extract(rundir: str):
    fs = Path(rundir) / "summary" / "full_summary.json"
    if not fs.exists():
        return None
    s = json.load(open(fs))
    pct = lambda v: round(v * 100, 2) if isinstance(v, (int, float)) else None
    return {
        "reg_disjoint": pct(_g(s, "per_metric_best", "next_region", "top10_acc_indist", "mean")),
        "reg_disjoint_std": pct(_g(s, "per_metric_best", "next_region", "top10_acc_indist", "std")),
        "reg_deploy": pct(_g(s, "next_region", "top10_acc_indist", "mean")),
        "reg_deploy_std": pct(_g(s, "next_region", "top10_acc_indist", "std")),
        "cat_disjoint": pct(_g(s, "diagnostic_task_best", "next_category", "f1", "mean")),
        "cat_deploy": pct(_g(s, "next_category", "f1", "mean")),
    }


def load_manifest(path: Path):
    """Return {state: [(tag, rundir), ...]}."""
    out = {}
    if not path.exists():
        return out
    import re
    for line in path.read_text().splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        key, tag, rd = parts[0], parts[1], parts[2]
        # Derive state from the rundir path (robust to key format differences
        # between drivers: LR-sweep uses state|regime, ladder uses tag|state).
        m = re.search(r"/(alabama|arizona|florida|georgia|california|texas)/", rd)
        state = m.group(1) if m else key.split("|")[0]
        out.setdefault(state, []).append((tag, rd))
    return out


def show_ladder(state, rows_by_tag, baseline_tag):
    """Ladder view: Δreg/Δcat vs the matched-baseline arm + position vs (c)/(d)."""
    base = rows_by_tag.get(baseline_tag)
    cbase = FROZEN_C_REG.get(state)
    dbase = FROZEN_D_REG.get(state)
    print(f"\n########## {state.upper()} (ladder; Δ vs '{baseline_tag}', the matched (a)@recipe zero-point) ##########")
    print(f"  anchors:  (a)landed-deploy-reg={A_BASE_DEPLOY_REG.get(state,'?')}  "
          f"(c)STL-reg={cbase}  (d)composite-reg={dbase}  (c)STL-cat={FROZEN_C_CAT.get(state,'?')}")
    if base is None:
        print(f"  (baseline arm '{baseline_tag}' not present yet)")
    hdr = (f"  {'arm':<14}{'reg@10 disj':>12}{'reg@10 dep':>12}{'cat-F1 dep':>11}"
           f"{'Δreg vs base':>13}{'Δcat vs base':>13}{'%gap(disj→c)':>13}")
    print(hdr)
    order = ["base_a", "dt_gated_on", "dt_priv_on", "dt_priv_off"]
    tags = [t for t in order if t in rows_by_tag] + [t for t in rows_by_tag if t not in order]
    for tag in tags:
        m = rows_by_tag[tag]
        dvb_r = f"{m['reg_disjoint']-base['reg_disjoint']:+.2f}" if base else "?"
        dvb_c = f"{m['cat_deploy']-base['cat_deploy']:+.2f}" if base else "?"
        # fraction of the disjoint→(c) gap the arm closes relative to base_a
        pct = "?"
        if base and cbase and (cbase - base['reg_disjoint']) > 0:
            pct = f"{100*(m['reg_disjoint']-base['reg_disjoint'])/(cbase-base['reg_disjoint']):+.0f}%"
        print(f"  {tag:<14}{m['reg_disjoint']:>9.2f}±{m['reg_disjoint_std'] or 0:<2.0f}"
              f"{m['reg_deploy'] or 0:>9.2f}  {m['cat_deploy'] or 0:>10.2f}"
              f"{dvb_r:>13}{dvb_c:>13}{pct:>13}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--baseline-tag", default=None,
                    help="if set, render a ladder view with Δ vs this arm tag")
    args = ap.parse_args()
    if args.baseline_tag:
        man = load_manifest(Path(args.manifest))
        for state in sorted(man):
            rows = {tag: extract(rd) for tag, rd in man[state]}
            rows = {t: m for t, m in rows.items() if m and m["reg_disjoint"] is not None}
            if rows:
                show_ladder(state, rows, args.baseline_tag)
        return
    man = load_manifest(Path(args.manifest))
    if not man:
        print(f"(no runs in manifest {args.manifest} yet)")
        return

    for state in sorted(man):
        print(f"\n########## {state.upper()} ##########")
        print(f"  anchors:  (a)deploy-reg={A_BASE_DEPLOY_REG.get(state,'?')}  "
              f"(c)STL-reg={FROZEN_C_REG.get(state,'?')}  (d)composite-reg={FROZEN_D_REG.get(state,'?')}  "
              f"(c)STL-cat={FROZEN_C_CAT.get(state,'?')}")
        rows = []
        for tag, rd in man[state]:
            m = extract(rd)
            if m and m["reg_disjoint"] is not None:
                rows.append((tag, m))
        if not rows:
            print("  (no completed full_summary yet)")
            continue
        rows.sort(key=lambda r: r[1]["reg_disjoint"], reverse=True)
        best = rows[0][1]["reg_disjoint"]
        cbase = FROZEN_C_REG.get(state)
        print(f"  {'regime':<20} {'reg@10 disj':>12} {'reg@10 deploy':>14} "
              f"{'cat-F1 disj':>12} {'cat-F1 deploy':>14} {'Δreg vs(c)':>11}")
        for tag, m in rows:
            star = "  <== BEST(disj)" if m["reg_disjoint"] == best else ""
            dvc = f"{m['reg_disjoint']-cbase:+.2f}" if cbase else "?"
            print(f"  {tag:<20} {m['reg_disjoint']:>7.2f}±{m['reg_disjoint_std'] or 0:>4.2f} "
                  f"{m['reg_deploy'] or 0:>9.2f}±{m['reg_deploy_std'] or 0:>4.2f} "
                  f"{m['cat_disjoint'] or 0:>12.2f} {m['cat_deploy'] or 0:>14.2f} {dvc:>11}{star}")


if __name__ == "__main__":
    main()
