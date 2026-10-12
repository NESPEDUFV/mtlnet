"""Summarise Rank 2 balanced-sampler compare into a three-frontier table.

Two arms (baseline vs --reg-balanced-sampler); Wilcoxon paired vs baseline.

Usage:
    python scripts/mtl_protocol_fix/summarize_balanced_sampler.py --state alabama
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

# Reuse the Rank 1 per-fold selector helper.
import sys
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "mtl_protocol_fix"))
from summarize_log_t_kd import _per_fold_selectors  # type: ignore

ARMS = ["baseline", "balanced"]


def _find_run_dirs(state: str, log_dir: Path) -> dict[str, Path]:
    base = REPO / "results" / "check2hgi" / state
    all_dirs = sorted(
        [p for p in base.iterdir() if p.is_dir() and p.name.startswith("mtlnet_")],
        key=lambda p: p.stat().st_mtime,
    )
    log_paths = [
        (a, log_dir / f"run_{a}.log")
        for a in ARMS
        if (log_dir / f"run_{a}.log").exists()
    ]
    n = len(log_paths)
    if n == 0:
        return {}
    matched_dirs = all_dirs[-n:]
    return {a: d for (a, _), d in zip(log_paths, matched_dirs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument(
        "--out-dir",
        default=str(REPO / "docs" / "results" / "mtl_protocol_fix" / "phase3_rank2_balanced_sampler"),
    )
    args = ap.parse_args()

    log_dir = Path(args.out_dir) / args.state
    if not log_dir.exists():
        raise FileNotFoundError(f"no log dir: {log_dir}")

    run_dirs = _find_run_dirs(args.state, log_dir)
    print(f"Found {len(run_dirs)}/{len(ARMS)} run dirs for {args.state}")

    summary = {"state": args.state, "arms": {}}
    md_rows = []
    md_rows.append("| arm | disjoint reg | geom_simple reg | b9 reg | disjoint cat | geom cat |")
    md_rows.append("|---|---:|---:|---:|---:|---:|")
    arm_to_rows: dict[str, list] = {}
    for arm in ARMS:
        if arm not in run_dirs:
            md_rows.append(f"| {arm} | (missing) | | | | |")
            continue
        rows = _per_fold_selectors(run_dirs[arm])
        arm_to_rows[arm] = rows
        import pandas as pd
        df = pd.DataFrame(rows)
        d = {
            "disjoint_reg_top10_mean": float(df["disjoint_reg_top10"].mean() * 100),
            "disjoint_reg_top10_std": float(df["disjoint_reg_top10"].std() * 100),
            "geom_reg_top10_mean": float(df["geom_reg_top10"].mean() * 100),
            "geom_reg_top10_std": float(df["geom_reg_top10"].std() * 100),
            "b9_reg_top10_mean": float(df["b9_reg_top10"].mean() * 100),
            "b9_reg_top10_std": float(df["b9_reg_top10"].std() * 100),
            "disjoint_cat_f1_mean": float(df["disjoint_cat_f1"].mean() * 100),
            "disjoint_cat_f1_std": float(df["disjoint_cat_f1"].std() * 100),
            "geom_cat_f1_mean": float(df["geom_cat_f1"].mean() * 100),
            "geom_cat_f1_std": float(df["geom_cat_f1"].std() * 100),
            "n_folds": len(df),
            "run_dir": str(run_dirs[arm].relative_to(REPO)),
        }
        summary["arms"][arm] = d
        md_rows.append(
            f"| {arm} | {d['disjoint_reg_top10_mean']:.2f} ± {d['disjoint_reg_top10_std']:.2f} "
            f"| {d['geom_reg_top10_mean']:.2f} ± {d['geom_reg_top10_std']:.2f} "
            f"| {d['b9_reg_top10_mean']:.2f} ± {d['b9_reg_top10_std']:.2f} "
            f"| {d['disjoint_cat_f1_mean']:.2f} ± {d['disjoint_cat_f1_std']:.2f} "
            f"| {d['geom_cat_f1_mean']:.2f} ± {d['geom_cat_f1_std']:.2f} |"
        )

    wcx_line = ""
    if "baseline" in arm_to_rows and "balanced" in arm_to_rows:
        try:
            from scipy.stats import wilcoxon
            base_reg = np.array([r["disjoint_reg_top10"] for r in arm_to_rows["baseline"]])
            bal_reg = np.array([r["disjoint_reg_top10"] for r in arm_to_rows["balanced"]])
            stat, p = wilcoxon(bal_reg, base_reg, alternative="greater", zero_method="wilcox")
            delta = (bal_reg - base_reg).mean() * 100
            summary["wilcoxon_disjoint_reg_p"] = float(p)
            summary["mean_delta_pp"] = float(delta)
            wcx_line = (
                f"**Wilcoxon (one-sided, balanced > baseline) on disjoint reg**: "
                f"Δ={delta:+.2f} pp, p={p:.4f}\n"
            )
        except Exception as e:
            summary["wilcoxon_error"] = str(e)
            wcx_line = f"_Wilcoxon error: {e}_\n"

    out_json = log_dir / f"{args.state}_summary.json"
    out_md = log_dir / f"{args.state}_summary.md"
    out_json.write_text(json.dumps(summary, indent=2))
    out_md.write_text(
        f"# Rank 2 balanced-sampler compare — {args.state}\n\n"
        f"Single-seed=42, 5 folds, 50 epochs. baseline (weighted-CE) vs --reg-balanced-sampler (WeightedRandomSampler on reg only).\n\n"
        + "\n".join(md_rows)
        + "\n\n"
        + wcx_line
    )
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print()
    print("\n".join(md_rows))
    if wcx_line:
        print(wcx_line)


if __name__ == "__main__":
    main()
