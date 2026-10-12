#!/usr/bin/env python3
"""Replicate F_TIER_A1_LEAK_AUDIT.md §4 MI computation at FL/CA/TX.

Computes MI(last_region_idx ; target region_idx) / H(target) on the full
next_region.parquet (population-level, matching the AL/AZ audit method).
"""
import sys
import numpy as np
import pandas as pd

EPS = 1e-12


def entropy_bits(counts):
    p = counts / counts.sum()
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def audit(state):
    df = pd.read_parquet(f"output/check2hgi/{state}/input/next_region.parquet")
    last = df["last_region_idx"].to_numpy(np.int64)
    tgt = df["region_idx"].to_numpy(np.int64)
    # exclude pad-only rows (last == -1) — they carry no last-region signal,
    # matching the audit's "structural prior" framing.
    keep = last >= 0
    last, tgt = last[keep], tgt[keep]
    n = len(tgt)
    n_regions = int(max(last.max(), tgt.max())) + 1

    # marginal entropies
    H_t = entropy_bits(np.bincount(tgt, minlength=n_regions).astype(np.float64))
    H_l = entropy_bits(np.bincount(last, minlength=n_regions).astype(np.float64))

    # joint -> H(target | last); use sparse pairing via unique
    pair = last.astype(np.int64) * n_regions + tgt.astype(np.int64)
    _, joint_counts = np.unique(pair, return_counts=True)
    H_joint = entropy_bits(joint_counts.astype(np.float64))
    H_t_given_l = H_joint - H_l
    MI = H_t - H_t_given_l

    # top-1 determinism: E_X[ max_y P(Y|X=last) ]
    # and P(last == target)
    from collections import defaultdict
    cond = defaultdict(lambda: defaultdict(int))
    last_counts = defaultdict(int)
    for l, t in zip(last, tgt):
        cond[l][t] += 1
        last_counts[l] += 1
    top1 = 0.0
    for l, cnt in last_counts.items():
        mx = max(cond[l].values())
        top1 += (mx / cnt) * (cnt / n)  # weight by P(last)
    p_identity = float((last == tgt).mean())

    return dict(
        state=state, n_rows=n, n_regions=n_regions,
        H_target=H_t, H_last=H_l, H_t_given_l=H_t_given_l,
        MI=MI, MI_over_H=MI / H_t, top1=top1, p_identity=p_identity,
    )


if __name__ == "__main__":
    states = sys.argv[1:] or ["florida", "california", "texas"]
    rows = [audit(s) for s in states]
    print(f"{'state':<12}{'n_rows':>9}{'n_reg':>7}{'H(t)':>8}{'H(l)':>8}"
          f"{'H(t|l)':>8}{'MI':>8}{'MI/H(t)':>9}{'top1':>7}{'P(l=t)':>8}")
    for r in rows:
        print(f"{r['state']:<12}{r['n_rows']:>9}{r['n_regions']:>7}"
              f"{r['H_target']:>8.3f}{r['H_last']:>8.3f}{r['H_t_given_l']:>8.3f}"
              f"{r['MI']:>8.3f}{r['MI_over_H']:>9.3f}{r['top1']:>7.3f}"
              f"{r['p_identity']:>8.3f}")
