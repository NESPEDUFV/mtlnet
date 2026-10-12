"""Summarise the Tier A1 large-state pilot (FL 5-fold + CA/TX 1-fold).

Single seed=42 sign-and-magnitude pilot. Reuses the EXACT extraction logic of
summarize_tier_a1.py:
  - "disjoint reg"   = per-fold max top10_acc_indist (best epoch)
  - "geom_simple reg"= top10_acc_indist at the epoch maximising geo-mean(cat f1, reg top10_acc_indist)
  - "disjoint cat F1"= per-fold max f1 (best epoch)
Raw per-fold values (×100). FL: paired Wilcoxon one-sided (W=0.2 > W=0.0), n=5.
CA/TX: report fold-1 Δ only (sign+magnitude, no test at n=1).

Usage:
    .venv/bin/python scripts/substrate_protocol_cleanup/summarize_tier_a1_largestate.py
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "docs" / "results" / "substrate_protocol_cleanup" / "tier_a1_largestate"
WEIGHTS = ["W0.0", "W0.2"]
CAT = "next_category"
REG = "next_region"
SEED = 42
# states: florida 5-fold, california/texas analyse fold 1 only
STATE_FOLDS = {"florida": 5, "california": 1, "texas": 1}


def _find_run_dir(cell: Path) -> Path | None:
    if not cell.exists():
        return None
    cands = sorted(p for p in cell.iterdir() if p.is_dir() and p.name.startswith("mtlnet_"))
    return cands[-1] if cands else None


def _per_fold(run_dir: Path, folds) -> list[dict]:
    rows = []
    for k in folds:
        cat_p = run_dir / "metrics" / f"fold{k}_{CAT}_val.csv"
        reg_p = run_dir / "metrics" / f"fold{k}_{REG}_val.csv"
        if not (cat_p.exists() and reg_p.exists()):
            continue
        cat = pd.read_csv(cat_p)
        reg = pd.read_csv(reg_p)
        epochs = sorted(set(cat["epoch"]) & set(reg["epoch"]))
        if not epochs:
            continue
        cat_by = {int(e): cat[cat["epoch"] == e].iloc[0] for e in epochs}
        reg_by = {int(e): reg[reg["epoch"] == e].iloc[0] for e in epochs}
        cat_best = max(epochs, key=lambda e: cat_by[e]["f1"])
        reg_best = max(epochs, key=lambda e: reg_by[e]["top10_acc_indist"])

        def _geom(e):
            return math.sqrt(max(float(cat_by[e]["f1"]), 0.0) *
                             max(float(reg_by[e]["top10_acc_indist"]), 0.0))
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
    out = {}
    for state, nf in STATE_FOLDS.items():
        folds = list(range(1, nf + 1))
        out[state] = {}
        for w in WEIGHTS:
            cell = ROOT / state / w / f"seed{SEED}"
            rd = _find_run_dir(cell)
            out[state][w] = _per_fold(rd, folds) if rd else None
    return out


def main():
    data = gather()
    md = ["# Tier A1 large-state pilot — analysis tables\n",
          "**Date**: 2026-05-28  ·  **Seed**: 42 (development seed) — sign-and-magnitude pilot, NOT paper-grade.\n"]
    for state in STATE_FOLDS:
        nf = STATE_FOLDS[state]
        md.append(f"## {state.title()} (analysed folds: {nf})\n")
        md.append("| W | disjoint reg (top10_acc_indist) | geom_simple reg | disjoint cat F1 | geom cat F1 |")
        md.append("|---|---:|---:|---:|---:|")
        for w in WEIGHTS:
            rows = data[state][w]
            if not rows:
                md.append(f"| {w} | MISSING | MISSING | MISSING | MISSING |")
                continue
            dr = [r["disjoint_reg_top10"] for r in rows]
            gr = [r["geom_reg_top10"] for r in rows]
            dc = [r["disjoint_cat_f1"] for r in rows]
            gc = [r["geom_cat_f1"] for r in rows]
            if len(dr) > 1:
                md.append(f"| {w} | {np.mean(dr):.2f} ± {np.std(dr, ddof=1):.2f} (n={len(dr)}) "
                          f"| {np.mean(gr):.2f} ± {np.std(gr, ddof=1):.2f} "
                          f"| {np.mean(dc):.2f} ± {np.std(dc, ddof=1):.2f} "
                          f"| {np.mean(gc):.2f} ± {np.std(gc, ddof=1):.2f} |")
            else:
                md.append(f"| {w} | {dr[0]:.2f} (fold1, n=1) | {gr[0]:.2f} "
                          f"| {dc[0]:.2f} | {gc[0]:.2f} |")
        md.append("")

        a, b = data[state]["W0.0"], data[state]["W0.2"]
        if a and b:
            pairs = [(r0["disjoint_reg_top10"], r2["disjoint_reg_top10"])
                     for r0, r2 in zip(a, b)]
            d = np.array([p[1] - p[0] for p in pairs])
            md.append("**Per-fold Δ disjoint reg (W=0.2 − W=0.0):**\n")
            md.append("| fold | W=0.0 | W=0.2 | Δ pp |")
            md.append("|---:|---:|---:|---:|")
            for (x0, x2), r0 in zip(pairs, a):
                md.append(f"| {r0['fold']} | {x0:.2f} | {x2:.2f} | {x2 - x0:+.2f} |")
            md.append("")
            if len(d) >= 5:
                stat, p = wilcoxon(d, alternative="greater")
                pos = int((d > 0).sum())
                md.append(f"**Wilcoxon (one-sided, W=0.2>W=0.0, n={len(d)}, raw per-fold):** "
                          f"mean Δ = {d.mean():+.2f} pp, median Δ = {np.median(d):+.2f} pp, "
                          f"{pos}/{len(d)} folds positive, p = {p:.4g}.\n")
            else:
                md.append(f"**n={len(d)} fold — sign-and-magnitude only (no significance test):** "
                          f"Δ disjoint reg = {d.mean():+.2f} pp.\n")
    print("\n".join(md))
    return "\n".join(md)


if __name__ == "__main__":
    main()
