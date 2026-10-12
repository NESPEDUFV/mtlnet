"""tier_resln analysis — MTL two-front (disjoint + joint/geom_simple) + STL.

Pure re-analysis of per-fold val CSVs (MTL) and B3_baselines JSONs (STL). No GPU.

MTL fronts per (variant, state):
  - DISJOINT: each head at its OWN best val epoch
      reg = max top10_acc_indist ; cat = max f1
  - JOINT (geom_simple): both heads at the single epoch maximising
      sqrt(cat_f1 * reg_top10_indist) over shared epochs
Wilcoxon: RAW per-fold, paired by fold, one-sided variant>canonical.

Variants: resln_canonical, resln_design_b vs canonical_noresln baseline.

STL: parses the next_getnext_hard reg JSON + next_gru cat JSON per variant.

Usage: .venv/bin/python scripts/substrate_protocol_cleanup/analyze_resln.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
TIER = REPO / "docs/results/substrate_protocol_cleanup/tier_resln"

MTL_VARIANTS = {
    "resln_canonical": "ResLN-canonical",
    "resln_design_b": "ResLN + Design B",
}
STATES = ("alabama", "arizona", "florida")


def _mtl_run_dir(tag: str, state: str) -> Path | None:
    cell = TIER / tag / state / "seed42"
    cands = sorted(cell.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return cands[0] if cands else None


def _per_fold(run_dir: Path) -> dict:
    out = {"disjoint_reg": [], "disjoint_cat": [], "joint_reg": [], "joint_cat": []}
    for fold in range(1, 6):
        cat_p = run_dir / "metrics" / f"fold{fold}_next_category_val.csv"
        reg_p = run_dir / "metrics" / f"fold{fold}_next_region_val.csv"
        if not cat_p.exists() or not reg_p.exists():
            return {}
        cat_df = pd.read_csv(cat_p)
        reg_df = pd.read_csv(reg_p)
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
    return sum(xs) / len(xs) if xs else float("nan")


def _wilcox_gt(a, b):
    deltas = [a[i] - b[i] for i in range(len(a))]
    try:
        w = wilcoxon(deltas, alternative="greater")
        W, p = float(w.statistic), float(w.pvalue)
    except ValueError:
        W, p = float("nan"), float("nan")
    return deltas, _mean(deltas), W, p


def _compare(v_pf, base_pf):
    res = {}
    for front, rk, ck in [("disjoint", "disjoint_reg", "disjoint_cat"),
                          ("joint", "joint_reg", "joint_cat")]:
        dr, mr, Wr, pr = _wilcox_gt(v_pf[rk], base_pf[rk])
        dc, mc, Wc, pc = _wilcox_gt(v_pf[ck], base_pf[ck])
        res[front] = {
            "reg_v_mean": _mean(v_pf[rk]), "reg_base_mean": _mean(base_pf[rk]),
            "reg_delta_mean": mr, "reg_deltas": dr, "reg_W": Wr, "reg_p_gt": pr,
            "cat_v_mean": _mean(v_pf[ck]), "cat_base_mean": _mean(base_pf[ck]),
            "cat_delta_mean": mc, "cat_deltas": dc, "cat_W": Wc, "cat_p_gt": pc,
        }
    return res


def _stl_json(axis: str, variant: str, state: str) -> dict | None:
    cell = TIER / axis / variant / state / "seed42"
    if not cell.exists():
        return None
    jsons = list(cell.glob("*.json"))
    if not jsons:
        return None
    try:
        return json.loads(jsons[0].read_text())
    except Exception:
        return None


def main():
    result = {"mtl": {}, "stl": {}}

    for state in STATES:
        base_dir = _mtl_run_dir("canonical_noresln", state)
        if base_dir is None:
            continue
        base_pf = _per_fold(base_dir)
        if not base_pf:
            continue
        result["mtl"][state] = {"canonical_noresln": {"per_fold": base_pf}}
        for tag, label in MTL_VARIANTS.items():
            vdir = _mtl_run_dir(tag, state)
            if vdir is None:
                continue
            v_pf = _per_fold(vdir)
            if not v_pf:
                continue
            result["mtl"][state][tag] = {
                "label": label, "per_fold": v_pf,
                "compare": _compare(v_pf, base_pf),
            }

    for state in STATES:
        result["stl"].setdefault(state, {})
        for variant in ("resln", "resln_design_b", "canonical"):
            result["stl"][state][variant] = {
                "reg": _stl_json("stl_reg", variant, state),
                "cat": _stl_json("stl_cat", variant, state),
            }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
