"""Aggregate Tier C1 route_task_best per-fold JSONs into a routing verdict.

Per state, reads route_fold{1..5}.json and reports:
  * reg routing gain: reg_best Acc@10 vs joint_best Acc@10 (decision-gate metric)
  * cat routing gain: cat_best F1 vs joint_best F1
with mean Δ, per-fold deltas, folds-positive, and one-sided Wilcoxon
(routed > joint) on RAW per-fold values.

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_tier_c1.py
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TC = REPO / "docs/results/substrate_protocol_cleanup/tier_c"
STATES = ["alabama", "arizona"]


def gather(state):
    rows = []
    for f in range(1, 6):
        p = TC / state / "C1_route" / f"route_fold{f}.json"
        if not p.exists():
            return None
        d = json.loads(p.read_text())
        s = d["summary"]
        rows.append(dict(
            fold=f,
            reg_routed=s["reg_routed_top10_acc"] * 100,
            reg_joint=s["joint_reg_top10_acc"] * 100,
            cat_routed=s["cat_routed_f1"] * 100,
            cat_joint=s["joint_cat_f1"] * 100,
        ))
    return rows


def wlx(d):
    d = np.array(d)
    pos = int((d > 0).sum())
    try:
        _, p = wilcoxon(d, alternative="greater")
    except ValueError:
        p = float("nan")
    return float(d.mean()), float(p), pos


def main():
    result = {}
    for st in STATES:
        rows = gather(st)
        if rows is None:
            print(f"{st}: MISSING route JSONs")
            result[st] = None
            continue
        reg_d = [r["reg_routed"] - r["reg_joint"] for r in rows]
        cat_d = [r["cat_routed"] - r["cat_joint"] for r in rows]
        rm, rp, rpos = wlx(reg_d)
        cm, cp, cpos = wlx(cat_d)
        result[st] = dict(
            reg_routed_mean=float(np.mean([r["reg_routed"] for r in rows])),
            reg_joint_mean=float(np.mean([r["reg_joint"] for r in rows])),
            cat_routed_mean=float(np.mean([r["cat_routed"] for r in rows])),
            cat_joint_mean=float(np.mean([r["cat_joint"] for r in rows])),
            reg_delta_per_fold=[round(x, 4) for x in reg_d],
            cat_delta_per_fold=[round(x, 4) for x in cat_d],
            reg_mean_delta=rm, reg_p_greater=rp, reg_folds_pos=rpos,
            cat_mean_delta=cm, cat_p_greater=cp, cat_folds_pos=cpos,
        )
        print(f"== {st} ==")
        print(f"  REG  reg_best Acc@10 {result[st]['reg_routed_mean']:.2f} vs joint {result[st]['reg_joint_mean']:.2f} "
              f"Δ={rm:+.2f} ({rpos}/5+, p_gt={rp:.4g}) per-fold {result[st]['reg_delta_per_fold']}")
        print(f"  CAT  cat_best F1     {result[st]['cat_routed_mean']:.2f} vs joint {result[st]['cat_joint_mean']:.2f} "
              f"Δ={cm:+.2f} ({cpos}/5+, p_gt={cp:.4g}) per-fold {result[st]['cat_delta_per_fold']}")
    out = TC / "tier_c1_routing_analysis.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print(f"saved {out}")


if __name__ == "__main__":
    main()
