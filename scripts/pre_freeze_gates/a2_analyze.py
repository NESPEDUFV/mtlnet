"""pre_freeze_gates A2 — paired Wilcoxon analysis across arms.

Pairs per (seed, fold) — StratifiedGroupKFold(seed) gives identical folds across arms at a
given seed, so (seed,fold) is a valid matched unit (board convention: 4 seeds × 5 folds =
n=20 per state). Reports per-arm means and paired Wilcoxon for the gate contrasts:
  hgifeat vs hgi   — does feature-concat lift HGI? (and by how much of the gap)
  v14    vs hgifeat — residual Check2HGI advantage after feature injection
  v14    vs hgi    — total substrate gap

Metric: macro-F1 (category, f1-best epoch) / Acc@10 (region, top10-best epoch).
"""
from __future__ import annotations

import argparse
import statistics as st
from pathlib import Path

from scipy.stats import wilcoxon

import sys
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "scripts"))
from pre_freeze_gates.a2_collect import per_fold_metric

ALL_ARMS = ["hgi", "hgifeat", "v14", "v11"]


def cell_path(state, task, arm, seed, folds, epochs):
    it = "checkin" if task == "category" else "region"
    return _root / "docs" / "results" / "P1" / f"region_head_{state}_{it}_{folds}f_{epochs}ep_A2_{arm}_{task}_s{seed}.json"


def gather(state, task, seeds, folds, epochs, arms):
    """Return {arm: [per (seed,fold) values]} aligned by (seed, fold).

    Only seeds for which ALL requested arms exist (with equal fold counts) are used,
    so every arm is paired on the identical (seed,fold) units.
    """
    head = "next_gru" if task == "category" else "next_stan_flow"
    data = {a: [] for a in arms}
    used_seeds = []
    for seed in seeds:
        ok = True
        cols = {}
        for arm in arms:
            p = cell_path(state, task, arm, seed, folds, epochs)
            if not p.exists():
                ok = False
                break
            vals, _ = per_fold_metric(str(p), task, head)
            cols[arm] = vals
        if not ok or len({len(v) for v in cols.values()}) != 1:
            print(f"  [skip] {state} {task} seed={seed}: missing/uneven ({'present' if ok else 'absent'})")
            continue
        used_seeds.append(seed)
        for arm in arms:
            data[arm].extend(cols[arm])
    return data, used_seeds


def contrast(a, b):
    """Wilcoxon paired a vs b (a-b). Returns (mean_a, mean_b, delta, p, n)."""
    n = len(a)
    ma, mb = st.mean(a), st.mean(b)
    try:
        _, p = wilcoxon(a, b)
    except ValueError:
        p = float("nan")
    return ma, mb, ma - mb, p, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="+", required=True)
    ap.add_argument("--seeds", nargs="+", type=int, required=True)
    ap.add_argument("--tasks", nargs="+", default=["category", "region"])
    ap.add_argument("--arms", nargs="+", default=ALL_ARMS, choices=ALL_ARMS)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    args = ap.parse_args()

    for state in args.states:
        for task in args.tasks:
            data, used = gather(state, task, args.seeds, args.folds, args.epochs, args.arms)
            present = [a for a in args.arms if used and len(data[a]) > 0]
            if "hgi" not in present or "hgifeat" not in present:
                print(f"\n### {state} / {task}: no complete data (present={present})")
                continue
            unit = "macro-F1" if task == "category" else "Acc@10"
            print(f"\n### {state} / {task} ({unit}) — seeds={used}, n={len(data['hgi'])}")
            for a in present:
                print(f"    {a:8s} mean={st.mean(data[a])*100:6.2f}  std={st.pstdev(data[a])*100:.2f}")
            # gate contrasts: concat lift, then each Check2HGI substrate vs hgi/hgifeat
            contrasts = [("hgifeat", "hgi")]
            for c in ("v14", "v11"):
                if c in present:
                    contrasts += [(c, "hgifeat"), (c, "hgi")]
            for (x, y) in contrasts:
                mx, my, d, p, n = contrast(data[x], data[y])
                print(f"    {x} vs {y}: Δ={d*100:+.2f}pp  p={p:.2e}  n={n}")
            closed = (st.mean(data["hgifeat"]) - st.mean(data["hgi"])) * 100
            for c in ("v14", "v11"):
                if c in present:
                    gap = (st.mean(data[c]) - st.mean(data["hgi"])) * 100
                    if abs(gap) > 1e-6:
                        print(f"    feature-concat closes {closed/gap*100:.1f}% of the {c}→HGI gap "
                              f"(gap={gap:+.2f}pp, concat lift={closed:+.2f}pp)")


if __name__ == "__main__":
    main()
