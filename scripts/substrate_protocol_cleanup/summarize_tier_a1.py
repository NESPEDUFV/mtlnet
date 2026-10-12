"""Summarise Tier A1 multi-seed log_T-KD sweep into a three-frontier table.

Reads per-cell run dirs at
    docs/results/substrate_protocol_cleanup/tier_a1/{state}/{W0.0|W0.2}/seed{S}/<mtlnet_*>/metrics/
and emits per-state three-frontier (best-cat, best-reg, joint-best) numbers
plus a paired Wilcoxon (one-sided, W=0.2 > W=0.0) on disjoint-reg
top10_acc_indist with n = 4 seeds × 5 folds = 20.

Usage:
    .venv/bin/python scripts/substrate_protocol_cleanup/summarize_tier_a1.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "docs" / "results" / "substrate_protocol_cleanup" / "tier_a1"
STATES = ["alabama", "arizona"]
SEEDS = [0, 1, 7, 100]
WEIGHTS = ["W0.0", "W0.2"]
CAT = "next_category"
REG = "next_region"


def _find_run_dir(cell: Path) -> Path | None:
    cands = sorted(p for p in cell.iterdir() if p.is_dir() and p.name.startswith("mtlnet_"))
    return cands[-1] if cands else None


def _per_fold(run_dir: Path, n_folds: int = 5) -> list[dict]:
    rows = []
    for k in range(1, n_folds + 1):
        cat_p = run_dir / "metrics" / f"fold{k}_{CAT}_val.csv"
        reg_p = run_dir / "metrics" / f"fold{k}_{REG}_val.csv"
        if not (cat_p.exists() and reg_p.exists()):
            return []
        cat = pd.read_csv(cat_p)
        reg = pd.read_csv(reg_p)
        epochs = sorted(set(cat["epoch"]) & set(reg["epoch"]))
        cat_by = {int(e): cat[cat["epoch"] == e].iloc[0] for e in epochs}
        reg_by = {int(e): reg[reg["epoch"] == e].iloc[0] for e in epochs}
        cat_best = max(epochs, key=lambda e: cat_by[e]["f1"])
        reg_best = max(epochs, key=lambda e: reg_by[e]["top10_acc_indist"])

        def _geom(e):
            return math.sqrt(max(float(cat_by[e]["f1"]), 0.0) * max(float(reg_by[e]["top10_acc_indist"]), 0.0))
        geom = max(epochs, key=_geom)
        rows.append({
            "fold": k,
            "disjoint_cat_f1": float(cat_by[cat_best]["f1"]) * 100,
            "disjoint_reg_top10": float(reg_by[reg_best]["top10_acc_indist"]) * 100,
            "geom_cat_f1": float(cat_by[geom]["f1"]) * 100,
            "geom_reg_top10": float(reg_by[geom]["top10_acc_indist"]) * 100,
        })
    return rows


def gather() -> dict:
    """Returns {state: {weight: {seed: [fold_rows]}}}."""
    out = {}
    for state in STATES:
        out[state] = {}
        for w in WEIGHTS:
            out[state][w] = {}
            for s in SEEDS:
                cell = ROOT / state / w / f"seed{s}"
                rd = _find_run_dir(cell) if cell.exists() else None
                if rd is None:
                    out[state][w][s] = None
                    continue
                rows = _per_fold(rd)
                out[state][w][s] = rows if rows else None
    return out


def _mean_std(xs):
    arr = np.array(xs)
    return float(arr.mean()), float(arr.std(ddof=1)) if len(arr) > 1 else 0.0


def summarise(data: dict) -> str:
    md = ["# Tier A1 — log_T-KD multi-seed promotion sweep summary\n"]
    md.append(f"**Date**: 2026-05-28")
    md.append(f"**Scope**: {STATES} × seeds {SEEDS} × W ∈ {WEIGHTS} × 5 folds → n=20 per cell per state")
    md.append("")
    md.append("## Three-frontier table per state\n")
    for state in STATES:
        md.append(f"### {state.title()}\n")
        md.append("| W | disjoint reg (top10_acc) | geom_simple reg | disjoint cat F1 | geom cat F1 |")
        md.append("|---|---:|---:|---:|---:|")
        for w in WEIGHTS:
            dr, gr, dc, gc = [], [], [], []
            for s in SEEDS:
                rows = data[state][w][s]
                if not rows:
                    continue
                for r in rows:
                    dr.append(r["disjoint_reg_top10"])
                    gr.append(r["geom_reg_top10"])
                    dc.append(r["disjoint_cat_f1"])
                    gc.append(r["geom_cat_f1"])
            if not dr:
                md.append(f"| {w} | MISSING | MISSING | MISSING | MISSING |")
                continue
            md.append(
                f"| {w} | {np.mean(dr):.2f} ± {np.std(dr, ddof=1):.2f} (n={len(dr)}) "
                f"| {np.mean(gr):.2f} ± {np.std(gr, ddof=1):.2f} "
                f"| {np.mean(dc):.2f} ± {np.std(dc, ddof=1):.2f} "
                f"| {np.mean(gc):.2f} ± {np.std(gc, ddof=1):.2f} |"
            )
        md.append("")
    md.append("## Wilcoxon (one-sided, paired by seed×fold, W=0.2 > W=0.0) on disjoint reg top10_acc\n")
    md.append("| State | n | mean Δ pp | median Δ pp | folds positive | p-value | verdict @ α=0.05 |")
    md.append("|---|---:|---:|---:|---:|---:|---|")
    for state in STATES:
        pairs = []
        for s in SEEDS:
            a = data[state]["W0.0"][s]
            b = data[state]["W0.2"][s]
            if not a or not b:
                continue
            for r0, r2 in zip(a, b):
                pairs.append((r0["disjoint_reg_top10"], r2["disjoint_reg_top10"]))
        if not pairs:
            md.append(f"| {state} | 0 | n/a | n/a | n/a | n/a | INSUFFICIENT DATA |")
            continue
        x0 = np.array([p[0] for p in pairs])
        x2 = np.array([p[1] for p in pairs])
        d = x2 - x0
        try:
            stat, p = wilcoxon(d, alternative="greater")
        except ValueError:
            stat, p = float("nan"), float("nan")
        pos = int((d > 0).sum())
        verdict = "PROMOTE" if (p is not None and not math.isnan(p) and p <= 0.05) else "null"
        md.append(
            f"| {state} | {len(d)} | {d.mean():+.2f} | {np.median(d):+.2f} | "
            f"{pos}/{len(d)} | {p:.4g} | {verdict} |"
        )
    md.append("")
    md.append("## Per-fold deltas (W=0.2 − W=0.0) on disjoint reg top10_acc\n")
    for state in STATES:
        md.append(f"### {state.title()}\n")
        md.append("| seed | fold | W=0.0 | W=0.2 | Δ pp |")
        md.append("|---:|---:|---:|---:|---:|")
        for s in SEEDS:
            a = data[state]["W0.0"][s]
            b = data[state]["W0.2"][s]
            if not a or not b:
                md.append(f"| {s} | – | MISSING | MISSING | – |")
                continue
            for r0, r2 in zip(a, b):
                md.append(
                    f"| {s} | {r0['fold']} | {r0['disjoint_reg_top10']:.2f} "
                    f"| {r2['disjoint_reg_top10']:.2f} "
                    f"| {r2['disjoint_reg_top10'] - r0['disjoint_reg_top10']:+.2f} |"
                )
        md.append("")
    return "\n".join(md)


if __name__ == "__main__":
    data = gather()
    out = summarise(data)
    out_path = ROOT / "phase_a1_verdict.md"
    out_path.write_text(out)
    print(out)
    print(f"\n[written to {out_path}]")
