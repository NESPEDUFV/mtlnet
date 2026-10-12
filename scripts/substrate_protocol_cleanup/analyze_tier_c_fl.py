"""FL Tier C (C2 reg-freeze / C3 zero-cat-kv) TWO-FRONT analysis.

Pure re-analysis of FL B9 per-fold val CSVs. Methodology byte-identical to
``analyze_tier_b_fl.py``: reg = top10_acc_indist, cat = f1; disjoint = each
head's own best-val epoch; joint = single epoch maximising
sqrt(cat_f1 * reg_top10_indist). Baseline = the FL canonical Tier B MTL cell.
RAW per-fold Wilcoxon (scipy auto-exact).

Cells:
  C2: c2_n2, c2_n4, c2_n6  (--reg-freeze-at-epoch N)
  C3: c3_zerokv            (--zero-cat-kv)

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_tier_c_fl.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TB = REPO / "docs/results/substrate_protocol_cleanup/tier_b_fl"
TC = REPO / "docs/results/substrate_protocol_cleanup/tier_c_fl"

CELLS = {
    "c2_n2": "C2 reg-freeze N=2",
    "c2_n4": "C2 reg-freeze N=4",
    "c2_n6": "C2 reg-freeze N=6",
    "c3_zerokv": "C3 zero-cat-kv",
}


def _metrics_dir(base: Path) -> Path:
    cands = sorted(base.rglob("metrics"), key=lambda p: p.stat().st_mtime, reverse=True)
    for c in cands:
        if (c / "fold1_next_region_val.csv").exists():
            return c
    raise FileNotFoundError(f"no metrics dir under {base}")


def _per_fold(metrics: Path) -> dict:
    out = {"disjoint_reg": [], "disjoint_cat": [], "joint_reg": [], "joint_cat": []}
    for fold in range(1, 6):
        cat_df = pd.read_csv(metrics / f"fold{fold}_next_category_val.csv")
        reg_df = pd.read_csv(metrics / f"fold{fold}_next_region_val.csv")
        cat_by = {int(r.epoch): r for _, r in cat_df.iterrows()}
        reg_by = {int(r.epoch): r for _, r in reg_df.iterrows()}
        cb = max(cat_by, key=lambda e: cat_by[e]["f1"])
        rb = max(reg_by, key=lambda e: reg_by[e]["top10_acc_indist"])
        out["disjoint_cat"].append(float(cat_by[cb]["f1"]) * 100)
        out["disjoint_reg"].append(float(reg_by[rb]["top10_acc_indist"]) * 100)
        shared = sorted(set(cat_by) & set(reg_by))

        def geom(ep):
            c = float(cat_by[ep]["f1"]); r = float(reg_by[ep]["top10_acc_indist"])
            return math.sqrt(c * r) if c > 0 and r > 0 else 0.0

        ge = max(shared, key=geom)
        out["joint_cat"].append(float(cat_by[ge]["f1"]) * 100)
        out["joint_reg"].append(float(reg_by[ge]["top10_acc_indist"]) * 100)
    return out


def _mean(xs):
    return sum(xs) / len(xs)


def _wilcox(design, base, alt):
    d = [design[i] - base[i] for i in range(len(design))]
    try:
        w = wilcoxon(d, alternative=alt)
        return d, _mean(d), float(w.pvalue)
    except ValueError:
        return d, _mean(d), float("nan")


def main():
    base = _per_fold(_metrics_dir(TB / "mtl_canonical" / "florida" / "seed42"))
    print(f"BASELINE canonical FL: disjoint_reg={_mean(base['disjoint_reg']):.2f} "
          f"disjoint_cat={_mean(base['disjoint_cat']):.2f} "
          f"joint_reg={_mean(base['joint_reg']):.2f} joint_cat={_mean(base['joint_cat']):.2f}")
    print()
    result = {"baseline": {k: _mean(v) for k, v in base.items()}, "baseline_per_fold": base, "cells": {}}
    for tag, label in CELLS.items():
        try:
            pf = _per_fold(_metrics_dir(TC / tag / "florida" / "seed42"))
        except FileNotFoundError as e:
            print(f"{tag}: MISSING ({e})")
            continue
        # reg: does cell HURT reg? one-sided base>cell  -> test cell<base via 'less'
        dreg_dj, mreg_dj, preg_dj = _wilcox(pf["disjoint_reg"], base["disjoint_reg"], "less")
        dreg_jo, mreg_jo, preg_jo = _wilcox(pf["joint_reg"], base["joint_reg"], "less")
        # cat: does cell IMPROVE cat? one-sided cell>base
        dcat_dj, mcat_dj, pcat_dj = _wilcox(pf["disjoint_cat"], base["disjoint_cat"], "greater")
        dcat_jo, mcat_jo, pcat_jo = _wilcox(pf["joint_cat"], base["joint_cat"], "greater")
        result["cells"][tag] = dict(
            label=label, per_fold=pf,
            disjoint=dict(reg_mean=_mean(pf["disjoint_reg"]), reg_delta=mreg_dj, reg_p_less=preg_dj, reg_deltas=dreg_dj,
                          cat_mean=_mean(pf["disjoint_cat"]), cat_delta=mcat_dj, cat_p_gt=pcat_dj, cat_deltas=dcat_dj),
            joint=dict(reg_mean=_mean(pf["joint_reg"]), reg_delta=mreg_jo, reg_p_less=preg_jo,
                       cat_mean=_mean(pf["joint_cat"]), cat_delta=mcat_jo, cat_p_gt=pcat_jo),
        )
        print(f"{tag:10s} [{label}]")
        print(f"  DISJOINT: reg={_mean(pf['disjoint_reg']):.2f} Δ={mreg_dj:+.2f} (p_hurt={preg_dj:.4f}) | "
              f"cat={_mean(pf['disjoint_cat']):.2f} Δ={mcat_dj:+.2f} (p_gt={pcat_dj:.4f})")
        print(f"  JOINT:    reg={_mean(pf['joint_reg']):.2f} Δ={mreg_jo:+.2f} (p_hurt={preg_jo:.4f}) | "
              f"cat={_mean(pf['joint_cat']):.2f} Δ={mcat_jo:+.2f} (p_gt={pcat_jo:.4f})")
        print(f"  reg disjoint Δ per-fold: {[round(x,2) for x in dreg_dj]}")
    (TC / "tier_c_fl_analysis.json").write_text(json.dumps(result, indent=2))
    print(f"\nWrote {TC / 'tier_c_fl_analysis.json'}")


if __name__ == "__main__":
    main()
