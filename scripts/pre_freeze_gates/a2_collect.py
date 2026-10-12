"""A2 — extract the correct per-fold metric from p1_region_head_ablation JSON.

CRITICAL: the harness's per-fold "snapshot" printed in logs is the *top10-best* epoch.
For the CATEGORY target Acc@10 is trivially ~100% (7 classes) → top10-best = epoch 1 →
a near-random macro-F1. The honest cat number is the **f1-best** epoch's macro-F1.
For the REGION target the headline is **top10_acc-best** Acc@10.

Usage:
    python scripts/pre_freeze_gates/a2_collect.py <result.json> --target category|region
"""
from __future__ import annotations

import argparse
import json
import sys


def per_fold_metric(path: str, target: str, head: str = "next_gru"):
    """Return (list of per-fold values, metric_name)."""
    with open(path) as f:
        d = json.load(f)
    heads = d.get("heads", d)
    if head not in heads:
        # single-head files sometimes store directly
        cand = [k for k in heads if "per_fold" in (heads[k] if isinstance(heads[k], dict) else {})]
        head = head if head in heads else (cand[0] if cand else head)
    pf = heads[head]["per_fold"]

    if target == "category":
        sel, metric = "f1", "f1"
    elif target == "region":
        sel, metric = "top10_acc", "top10_acc"
    else:
        raise ValueError(target)

    vals = []
    for fold in pf:
        pmb = fold.get("per_metric_best")
        if pmb and sel in pmb:
            # per_metric_best[sel] IS the snapshot dict of all metrics at sel's best epoch.
            vals.append(float(pmb[sel][metric]))
        else:
            # fallback: the flat snapshot (only valid when sel == reported snapshot)
            vals.append(float(fold[metric]))
    return vals, metric


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--target", choices=["category", "region"], required=True)
    ap.add_argument("--head", default="next_gru")
    args = ap.parse_args()
    vals, metric = per_fold_metric(args.path, args.target, args.head)
    import statistics as st
    mean = st.mean(vals)
    std = st.stdev(vals) if len(vals) > 1 else 0.0
    print(f"{metric}: per-fold={[round(v*100,2) for v in vals]}")
    print(f"{metric}: mean={mean*100:.2f}  std={std*100:.2f}  n={len(vals)}")


if __name__ == "__main__":
    main()
