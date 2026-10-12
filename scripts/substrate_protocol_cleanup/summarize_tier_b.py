"""Summarize Tier B Wave 1 MTL results.

For each (design, state) cell, extract per-fold:
    - cat F1 @ cat-best epoch (disjoint)
    - reg top10_acc_indist @ reg-best epoch (disjoint)
    - cat F1 + reg top10 @ geom_simple-best epoch (joint)

Compute 5-fold means; Wilcoxon one-sided (greater) on disjoint reg vs
canonical c2hgi seed=42 baseline from phase1v3_5states_three_frontier.json.
Δcat is mean substrate cat F1 minus canonical cat F1.

Writes a markdown verdict table to stdout (and optionally a file).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]


def _load_canonical_baseline() -> Dict[str, Dict[str, List[float]]]:
    """Load AL/AZ seed=42 canonical baseline per-fold values from phase1v3."""
    p = REPO / "docs/results/mtl_protocol_fix/phase1v3_5states_three_frontier.json"
    with open(p) as f:
        d = json.load(f)
    out = {}
    for state_key, state_name in [("AL_H3alt", "alabama"), ("AZ_H3alt", "arizona")]:
        per_fold = d[state_key]["per_fold"]
        out[state_name] = {
            "disjoint_reg_top10": [
                per_fold[str(f)]["per_task_disjoint"]["reg"]["reg_top10_indist"] * 100
                for f in range(1, 6)
            ],
            "disjoint_cat_f1": [
                per_fold[str(f)]["per_task_disjoint"]["cat"]["cat_f1"] * 100
                for f in range(1, 6)
            ],
            "geom_cat_f1": [
                per_fold[str(f)]["joint_geom_simple"]["cat_f1"] * 100
                for f in range(1, 6)
            ],
            "geom_reg_top10": [
                per_fold[str(f)]["joint_geom_simple"]["reg_top10_indist"] * 100
                for f in range(1, 6)
            ],
        }
    return out


def _extract_per_fold_from_run(run_dir: Path) -> Dict[str, List[float]]:
    """From a MTL results dir, pull per-fold disjoint + geom_simple values.

    Mirrors the gather() path in summarize_tier_a1.py.
    """
    out = {
        "disjoint_cat_f1": [],
        "disjoint_reg_top10": [],
        "geom_cat_f1": [],
        "geom_reg_top10": [],
    }
    for fold in range(1, 6):
        cat_csv = run_dir / "metrics" / f"fold{fold}_next_category_val.csv"
        reg_csv = run_dir / "metrics" / f"fold{fold}_next_region_val.csv"
        if not cat_csv.exists() or not reg_csv.exists():
            return None
        cat_df = pd.read_csv(cat_csv)
        reg_df = pd.read_csv(reg_csv)
        cat_by_ep = {int(r.epoch): r for _, r in cat_df.iterrows()}
        reg_by_ep = {int(r.epoch): r for _, r in reg_df.iterrows()}
        # disjoint
        cat_best_ep = max(cat_by_ep, key=lambda e: cat_by_ep[e]["f1"])
        reg_best_ep = max(reg_by_ep, key=lambda e: reg_by_ep[e]["top10_acc_indist"])
        out["disjoint_cat_f1"].append(float(cat_by_ep[cat_best_ep]["f1"]) * 100)
        out["disjoint_reg_top10"].append(float(reg_by_ep[reg_best_ep]["top10_acc_indist"]) * 100)
        # geom_simple — joint over epochs both files share
        shared = sorted(set(cat_by_ep) & set(reg_by_ep))
        if not shared:
            return None
        def geom(ep):
            c = float(cat_by_ep[ep]["f1"])
            r = float(reg_by_ep[ep]["top10_acc_indist"])
            if c <= 0 or r <= 0:
                return 0
            return math.sqrt(c * r)
        gep = max(shared, key=geom)
        out["geom_cat_f1"].append(float(cat_by_ep[gep]["f1"]) * 100)
        out["geom_reg_top10"].append(float(reg_by_ep[gep]["top10_acc_indist"]) * 100)
    return out


def _find_run_dir(tier_b_root: Path, design: str, state: str) -> Path | None:
    cell_root = tier_b_root / design / state / "seed42"
    if not cell_root.exists():
        return None
    candidates = sorted(cell_root.glob("mtlnet_*"), key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--tier-b-root",
        default=str(REPO / "docs/results/substrate_protocol_cleanup/tier_b"),
    )
    ap.add_argument(
        "--designs",
        nargs="+",
        default=["check2hgi_design_b", "check2hgi_design_j", "check2hgi_design_l"],
    )
    ap.add_argument("--out", default=None, help="Optional markdown output path")
    args = ap.parse_args()

    tier_b_root = Path(args.tier_b_root)
    baselines = _load_canonical_baseline()

    rows = []
    for state in ("alabama", "arizona"):
        b = baselines[state]
        rows.append({
            "design": "canonical_baseline",
            "state": state,
            "mean_disjoint_reg": sum(b["disjoint_reg_top10"]) / 5,
            "mean_disjoint_cat": sum(b["disjoint_cat_f1"]) / 5,
            "mean_geom_reg": sum(b["geom_reg_top10"]) / 5,
            "mean_geom_cat": sum(b["geom_cat_f1"]) / 5,
            "delta_disjoint_reg": 0.0,
            "delta_disjoint_cat": 0.0,
            "wilcoxon_p": None,
            "verdict": "BASELINE",
        })
        for design in args.designs:
            run_dir = _find_run_dir(tier_b_root, design, state)
            if run_dir is None:
                rows.append({
                    "design": design, "state": state,
                    "mean_disjoint_reg": None, "mean_disjoint_cat": None,
                    "mean_geom_reg": None, "mean_geom_cat": None,
                    "delta_disjoint_reg": None, "delta_disjoint_cat": None,
                    "wilcoxon_p": None, "verdict": "MISSING",
                })
                continue
            v = _extract_per_fold_from_run(run_dir)
            if v is None or len(v["disjoint_reg_top10"]) != 5:
                rows.append({
                    "design": design, "state": state,
                    "mean_disjoint_reg": None, "mean_disjoint_cat": None,
                    "mean_geom_reg": None, "mean_geom_cat": None,
                    "delta_disjoint_reg": None, "delta_disjoint_cat": None,
                    "wilcoxon_p": None, "verdict": "INCOMPLETE",
                })
                continue
            deltas = [v["disjoint_reg_top10"][i] - b["disjoint_reg_top10"][i] for i in range(5)]
            try:
                w_stat = wilcoxon(deltas, alternative="greater")
                p = float(w_stat.pvalue)
            except Exception:
                p = None
            d_reg = sum(deltas) / 5
            d_cat = (sum(v["disjoint_cat_f1"]) / 5) - (sum(b["disjoint_cat_f1"]) / 5)
            if p is not None and p <= 0.05 and d_cat >= -0.5:
                verdict = "PROMOTE"
            elif p is not None:
                verdict = "NULL" if d_reg >= 0 else "FALSIFIED"
            else:
                verdict = "INDETERMINATE"
            rows.append({
                "design": design, "state": state,
                "mean_disjoint_reg": sum(v["disjoint_reg_top10"]) / 5,
                "mean_disjoint_cat": sum(v["disjoint_cat_f1"]) / 5,
                "mean_geom_reg": sum(v["geom_reg_top10"]) / 5,
                "mean_geom_cat": sum(v["geom_cat_f1"]) / 5,
                "delta_disjoint_reg": d_reg,
                "delta_disjoint_cat": d_cat,
                "wilcoxon_p": p,
                "verdict": verdict,
                "per_fold_deltas": deltas,
            })

    # Print markdown table
    lines = []
    lines.append("| design | state | disjoint reg | disjoint cat | geom reg | geom cat | Δreg pp | Δcat pp | p (1-sided) | verdict |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---|")
    def fmt(v, dp=2):
        return f"{v:.{dp}f}" if isinstance(v, (int, float)) else "—"
    for r in rows:
        lines.append(
            f"| {r['design']} | {r['state']} | "
            f"{fmt(r['mean_disjoint_reg'])} | {fmt(r['mean_disjoint_cat'])} | "
            f"{fmt(r['mean_geom_reg'])} | {fmt(r['mean_geom_cat'])} | "
            f"{fmt(r['delta_disjoint_reg'])} | {fmt(r['delta_disjoint_cat'])} | "
            f"{fmt(r['wilcoxon_p'], 6) if r['wilcoxon_p'] is not None else '—'} | "
            f"{r['verdict']} |"
        )
    md = "\n".join(lines) + "\n"
    print(md)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(md)
        print(f"wrote {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
