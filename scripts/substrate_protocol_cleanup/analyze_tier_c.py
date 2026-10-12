"""Summarise Tier C C2 (reg-freeze-at-epoch) + C3 (zero-cat-kv) cells.

Three-frontier per cell (best-cat / best-reg / joint geom_simple), RAW-value
paired Wilcoxon (5 folds) vs the Tier B canonical_baseline at the same state.

Baseline: docs/results/substrate_protocol_cleanup/tier_b/canonical_baseline/{state}/seed42/<mtlnet_*>/
Cells:    docs/results/substrate_protocol_cleanup/tier_c/{state}/{C2_n2,C2_n4,C2_n6,C3_zerokv}/

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_tier_c.py
"""
from __future__ import annotations
import math, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TC = REPO / "docs/results/substrate_protocol_cleanup/tier_c"
TB = REPO / "docs/results/substrate_protocol_cleanup/tier_b/canonical_baseline"
STATES = ["alabama", "arizona"]
CELLS = ["C2_n2", "C2_n4", "C2_n6", "C3_zerokv"]
CAT, REG = "next_category", "next_region"


def _metrics_dir_for_baseline(state: str) -> Path:
    base = TB / state / "seed42"
    runs = sorted(p for p in base.iterdir() if p.is_dir() and p.name.startswith("mtlnet_"))
    return runs[-1] / "metrics"


def per_fold(metrics_dir: Path, n=5):
    rows = []
    for k in range(1, n + 1):
        cat_p = metrics_dir / f"fold{k}_{CAT}_val.csv"
        reg_p = metrics_dir / f"fold{k}_{REG}_val.csv"
        if not (cat_p.exists() and reg_p.exists()):
            return None
        cat = pd.read_csv(cat_p); reg = pd.read_csv(reg_p)
        ep = sorted(set(cat.epoch) & set(reg.epoch))
        cb = {int(e): cat[cat.epoch == e].iloc[0] for e in ep}
        rb = {int(e): reg[reg.epoch == e].iloc[0] for e in ep}
        cat_best = max(ep, key=lambda e: cb[e]["f1"])
        reg_best = max(ep, key=lambda e: rb[e]["top10_acc_indist"])
        g = lambda e: math.sqrt(max(cb[e]["f1"], 0) * max(rb[e]["top10_acc_indist"], 0))
        geom = max(ep, key=g)
        rows.append(dict(
            fold=k,
            disjoint_cat_f1=float(cb[cat_best]["f1"]) * 100,
            disjoint_reg_top10=float(rb[reg_best]["top10_acc_indist"]) * 100,
            geom_cat_f1=float(cb[geom]["f1"]) * 100,
            geom_reg_top10=float(rb[geom]["top10_acc_indist"]) * 100,
            reg_peak_epoch=int(reg_best),
            reg_peak_top10=float(rb[reg_best]["top10_acc_indist"]) * 100,
        ))
    return rows


def col(rows, key):
    return [r[key] for r in rows]


def msd(xs):
    a = np.array(xs)
    return a.mean(), (a.std(ddof=1) if len(a) > 1 else 0.0)


def wlx(cell, base, key):
    """One-sided Wilcoxon cell > base on RAW per-fold key. Returns (mean_d, p, pos)."""
    d = np.array(col(cell, key)) - np.array(col(base, key))
    pos = int((d > 0).sum())
    try:
        _, p_gt = wilcoxon(d, alternative="greater")
    except ValueError:
        p_gt = float("nan")
    return float(d.mean()), float(p_gt), pos


def main():
    base = {s: per_fold(_metrics_dir_for_baseline(s)) for s in STATES}
    result = {"baseline": {}, "cells": {}}
    for s in STATES:
        b = base[s]
        dr_m, dr_s = msd(col(b, "disjoint_reg_top10"))
        dc_m, dc_s = msd(col(b, "disjoint_cat_f1"))
        result["baseline"][s] = dict(
            disjoint_reg_mean=dr_m, disjoint_reg_std=dr_s,
            disjoint_cat_mean=dc_m, disjoint_cat_std=dc_s,
            geom_reg_mean=msd(col(b, "geom_reg_top10"))[0],
            geom_cat_mean=msd(col(b, "geom_cat_f1"))[0],
            reg_peak_epochs=col(b, "reg_peak_epoch"),
            reg_peak_mean=msd(col(b, "reg_peak_epoch"))[0],
            per_fold=b,
        )

    print("=" * 100)
    print("BASELINE (Tier B canonical_baseline, seed42 5-fold)")
    for s in STATES:
        rb = result["baseline"][s]
        print(f"  {s}: disjoint reg {rb['disjoint_reg_mean']:.2f}±{rb['disjoint_reg_std']:.2f}  "
              f"cat {rb['disjoint_cat_mean']:.2f}±{rb['disjoint_cat_std']:.2f}  "
              f"reg_peak_ep {rb['reg_peak_epochs']} (mean {rb['reg_peak_mean']:.1f})")

    for cell in CELLS:
        print("=" * 100)
        print(f"CELL {cell}")
        result["cells"][cell] = {}
        for s in STATES:
            cdir = TC / s / cell / "metrics"
            rows = per_fold(cdir) if cdir.exists() else None
            if rows is None:
                print(f"  {s}: MISSING ({cdir})")
                result["cells"][cell][s] = None
                continue
            b = base[s]
            dr_m, dr_s = msd(col(rows, "disjoint_reg_top10"))
            dc_m, dc_s = msd(col(rows, "disjoint_cat_f1"))
            gr_m = msd(col(rows, "geom_reg_top10"))[0]
            gc_m = msd(col(rows, "geom_cat_f1"))[0]
            d_reg, p_reg_gt, pos_reg = wlx(rows, b, "disjoint_reg_top10")
            d_cat, p_cat_gt, pos_cat = wlx(rows, b, "disjoint_cat_f1")
            sigma = result["baseline"][s]["disjoint_reg_std"]
            peaks = col(rows, "reg_peak_epoch")
            peak_mean = msd(peaks)[0]
            result["cells"][cell][s] = dict(
                disjoint_reg_mean=dr_m, disjoint_reg_std=dr_s,
                disjoint_cat_mean=dc_m, disjoint_cat_std=dc_s,
                geom_reg_mean=gr_m, geom_cat_mean=gc_m,
                d_reg=d_reg, p_reg_greater=p_reg_gt, reg_folds_pos=pos_reg,
                d_cat=d_cat, p_cat_greater=p_cat_gt, cat_folds_pos=pos_cat,
                reg_sigma_baseline=sigma,
                reg_peak_epochs=peaks, reg_peak_mean=peak_mean,
                per_fold=rows,
            )
            print(f"  {s}: reg {dr_m:.2f}±{dr_s:.2f} (Δ{d_reg:+.2f}, {pos_reg}/5+, p_gt={p_reg_gt:.4g}, σ_base={sigma:.2f})")
            print(f"        cat {dc_m:.2f}±{dc_s:.2f} (Δ{d_cat:+.2f}, {pos_cat}/5+, p_gt={p_cat_gt:.4g})")
            print(f"        geom reg {gr_m:.2f} cat {gc_m:.2f}  reg_peak_ep {peaks} (mean {peak_mean:.1f})")

    out = TC / "tier_c_c2c3_analysis.json"
    out.write_text(json.dumps(result, indent=2, default=str))
    print("=" * 100)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
