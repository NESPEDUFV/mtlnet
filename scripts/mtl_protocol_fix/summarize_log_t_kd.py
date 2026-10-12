"""Summarise log_T-KD sweep results into a three-frontier table.

Reads per-fold val CSVs from results/check2hgi/{state}/<latest run dir>
for each --log-t-kd-weight setting and reports MTL @ disjoint, @ geom_simple,
and @ b9 selectors. Aggregates the 4-weight sweep into one markdown table.

Usage:
    python scripts/mtl_protocol_fix/summarize_log_t_kd.py --state alabama
"""
from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
WEIGHTS = ["0.0", "0.05", "0.1", "0.2"]
CAT = "next_category"
REG = "next_region"


def _per_fold_selectors(run_dir: Path, n_folds: int = 5) -> dict:
    """For each fold, pick cat-best ep, reg-best ep, geom_simple ep, b9 ep,
    and report metrics."""
    rows = []
    for k in range(1, n_folds + 1):
        cat_p = run_dir / "metrics" / f"fold{k}_{CAT}_val.csv"
        reg_p = run_dir / "metrics" / f"fold{k}_{REG}_val.csv"
        if not (cat_p.exists() and reg_p.exists()):
            raise FileNotFoundError(f"missing val CSVs at fold {k}: {cat_p} / {reg_p}")
        cat = pd.read_csv(cat_p)
        reg = pd.read_csv(reg_p)
        epochs = sorted(set(cat["epoch"]) & set(reg["epoch"]))
        cat_by = {int(e): cat[cat["epoch"] == e].iloc[0] for e in epochs}
        reg_by = {int(e): reg[reg["epoch"] == e].iloc[0] for e in epochs}

        cat_best_ep = max(epochs, key=lambda e: cat_by[e]["f1"])
        reg_best_ep = max(epochs, key=lambda e: reg_by[e]["top10_acc_indist"])

        def _geom_simple(e):
            cf = float(cat_by[e]["f1"])
            rt = float(reg_by[e]["top10_acc_indist"])
            return math.sqrt(max(cf, 0.0) * max(rt, 0.0))

        def _b9(e):
            cf = float(cat_by[e]["f1"])
            rf = float(reg_by[e].get("macro_f1", reg_by[e]["f1"]))
            return 0.5 * (cf + rf)

        geom_ep = max(epochs, key=_geom_simple)
        b9_ep = max(epochs, key=_b9)

        rows.append({
            "fold": k,
            # disjoint
            "disjoint_cat_f1": float(cat_by[cat_best_ep]["f1"]),
            "disjoint_reg_top10": float(reg_by[reg_best_ep]["top10_acc_indist"]),
            "disjoint_cat_ep": cat_best_ep,
            "disjoint_reg_ep": reg_best_ep,
            # geom_simple
            "geom_cat_f1": float(cat_by[geom_ep]["f1"]),
            "geom_reg_top10": float(reg_by[geom_ep]["top10_acc_indist"]),
            "geom_ep": geom_ep,
            # b9 (legacy)
            "b9_cat_f1": float(cat_by[b9_ep]["f1"]),
            "b9_reg_top10": float(reg_by[b9_ep]["top10_acc_indist"]),
            "b9_ep": b9_ep,
        })
    return rows


def _latest_run_dir(state: str, before_ts: str | None = None) -> Path:
    base = REPO / "results" / "check2hgi" / state
    if not base.exists():
        raise FileNotFoundError(f"no run dirs under {base}")
    cands = sorted([p for p in base.iterdir() if p.is_dir() and p.name.startswith("mtlnet_")])
    if not cands:
        raise FileNotFoundError(f"no mtlnet_* dirs under {base}")
    return cands[-1]


def _find_run_dirs(state: str, log_dir: Path) -> dict[str, Path]:
    """Match each per-weight log to the corresponding run dir by reading
    the FIRST timestamped train.py log line within the run log (which
    is emitted right at training start and matches the run-dir name).
    Falls back to chronological order when no timestamp match is found."""
    out: dict[str, Path] = {}
    base = REPO / "results" / "check2hgi" / state
    all_dirs = sorted(
        [p for p in base.iterdir() if p.is_dir() and p.name.startswith("mtlnet_")],
        key=lambda p: p.stat().st_mtime,
    )

    # Pull the start timestamp from each run log via the FOLD 1 header
    # which prints the start time; or use the file's mtime as a fallback.
    log_paths = []
    for w in WEIGHTS:
        tag = f"w{w.replace('.', '')}"
        log_p = log_dir / f"run_{tag}.log"
        if log_p.exists():
            log_paths.append((w, log_p))

    # Pair each log (in order) with the N most-recent run dirs of matching count.
    n = len(log_paths)
    if n == 0:
        return out
    # Take the N most recent run dirs in chronological order; map to weights.
    matched_dirs = all_dirs[-n:]
    for (w, _log_p), run_dir in zip(log_paths, matched_dirs):
        out[w] = run_dir
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument(
        "--out-dir",
        default=str(REPO / "docs" / "results" / "mtl_protocol_fix" / "phase3_rank1_log_t_kd"),
    )
    args = ap.parse_args()

    log_dir = Path(args.out_dir) / args.state
    if not log_dir.exists():
        raise FileNotFoundError(f"no log dir: {log_dir}")

    run_dirs = _find_run_dirs(args.state, log_dir)
    print(f"Found {len(run_dirs)}/{len(WEIGHTS)} run dirs for {args.state}")

    summary = {"state": args.state, "weights": {}}
    md_rows = []
    md_rows.append("| log_T-KD weight | MTL @ disjoint reg | MTL @ geom_simple reg | MTL @ b9 reg | disjoint cat | geom cat |")
    md_rows.append("|---|---:|---:|---:|---:|---:|")
    for w in WEIGHTS:
        if w not in run_dirs:
            md_rows.append(f"| {w} | (run missing) | | | | |")
            continue
        rows = _per_fold_selectors(run_dirs[w])
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
            "run_dir": str(run_dirs[w].relative_to(REPO)),
        }
        summary["weights"][w] = d
        md_rows.append(
            f"| {w} | {d['disjoint_reg_top10_mean']:.2f} ± {d['disjoint_reg_top10_std']:.2f} "
            f"| {d['geom_reg_top10_mean']:.2f} ± {d['geom_reg_top10_std']:.2f} "
            f"| {d['b9_reg_top10_mean']:.2f} ± {d['b9_reg_top10_std']:.2f} "
            f"| {d['disjoint_cat_f1_mean']:.2f} ± {d['disjoint_cat_f1_std']:.2f} "
            f"| {d['geom_cat_f1_mean']:.2f} ± {d['geom_cat_f1_std']:.2f} |"
        )

    # Wilcoxon vs baseline (w=0.0) on disjoint reg.
    try:
        from scipy.stats import wilcoxon
        base_rows = _per_fold_selectors(run_dirs["0.0"]) if "0.0" in run_dirs else None
        if base_rows is not None:
            base_reg = np.array([r["disjoint_reg_top10"] for r in base_rows])
            for w in WEIGHTS:
                if w == "0.0" or w not in run_dirs:
                    continue
                w_rows = _per_fold_selectors(run_dirs[w])
                w_reg = np.array([r["disjoint_reg_top10"] for r in w_rows])
                # one-sided: w_reg > base_reg
                stat, p = wilcoxon(w_reg, base_reg, alternative="greater", zero_method="wilcox")
                summary["weights"][w]["wilcoxon_disjoint_reg_p"] = float(p)
                summary["weights"][w]["mean_delta_pp"] = float((w_reg - base_reg).mean() * 100)
    except Exception as e:
        summary["wilcoxon_error"] = str(e)

    out_json = log_dir / f"{args.state}_summary.json"
    out_md = log_dir / f"{args.state}_summary.md"
    out_json.write_text(json.dumps(summary, indent=2))
    out_md.write_text(
        f"# log_T-KD sweep — {args.state}\n\n"
        f"Single-seed=42, 5 folds, 50 epochs. Baseline (w=0.0) vs supervisory log_T KD at w ∈ {{0.05, 0.1, 0.2}}.\n\n"
        + "\n".join(md_rows)
        + "\n\n"
        + ("**Wilcoxon (one-sided, w>baseline) on disjoint reg:**\n"
           + "\n".join(
               f"- w={w}: Δ={summary['weights'][w].get('mean_delta_pp', float('nan')):+.2f} pp, "
               f"p={summary['weights'][w].get('wilcoxon_disjoint_reg_p', float('nan')):.4f}"
               for w in WEIGHTS if w != "0.0" and w in summary['weights']
           )
           if "wilcoxon_error" not in summary
           else f"_Wilcoxon error: {summary['wilcoxon_error']}_")
        + "\n"
    )
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    print()
    print("\n".join(md_rows))


if __name__ == "__main__":
    main()
