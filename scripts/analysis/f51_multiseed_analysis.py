"""F51 multi-seed paired-Wilcoxon analysis.

Compares B9 champion vs H3-alt anchor at each seed (5f x 50ep, FL, leak-free).
Reports per-seed paired Wilcoxon, then aggregates across seeds for a meta-test.

Usage:
    python scripts/analysis/f51_multiseed_analysis.py \
        --b9 seed=42:results/check2hgi/florida/...,seed=0:results/...,... \
        --h3alt seed=42:results/check2hgi/florida/...,seed=0:results/...,...

Output: a markdown table to stdout, plus optional JSON.

Decision rule (from F50_NORTH_STAR_DEEP_EXPLORATION_PROMPT.md §3 Tier 1):
- 4/5 seeds with Δreg ≥ +2.5 pp -> robust, paper claim holds.
- 2-3/5 seeds -> fragile, paper claim weakens to "FL-strong with seed-conditioning".
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

try:
    from scipy.stats import wilcoxon, combine_pvalues
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


REG_METRIC = "top10_acc_indist"
CAT_METRIC = "f1"
MIN_EPOCH = 5


def per_fold_best(run_dir: Path, task: str, metric: str, min_epoch: int = MIN_EPOCH) -> list[float]:
    out: list[float] = []
    for fold in (1, 2, 3, 4, 5):
        csv = run_dir / "metrics" / f"fold{fold}_{task}_val.csv"
        if not csv.exists():
            return []
        df = pd.read_csv(csv)
        if metric not in df.columns:
            return []
        masked = df[df["epoch"] >= min_epoch]
        if masked.empty:
            return []
        out.append(float(masked[metric].max()))
    return out


def paired(arm: list[float], ref: list[float]) -> dict:
    if not arm or len(arm) != len(ref):
        return {"valid": False}
    a, r = np.array(arm), np.array(ref)
    diffs = a - r
    out = {
        "valid": True,
        "n": len(a),
        "mean_arm_pp": float(a.mean() * 100),
        "std_arm_pp": float(a.std(ddof=1) * 100),
        "mean_ref_pp": float(r.mean() * 100),
        "std_ref_pp": float(r.std(ddof=1) * 100),
        "delta_pp": float((a.mean() - r.mean()) * 100),
        "n_pos": int((diffs > 0).sum()),
        "n_neg": int((diffs < 0).sum()),
        "p_value": None,
    }
    if HAS_SCIPY and len(a) >= 4 and not np.allclose(diffs, 0):
        try:
            stat = wilcoxon(diffs, zero_method="wilcox", alternative="greater")
            out["p_value"] = float(stat.pvalue)
        except ValueError:
            pass
    return out


def parse_seed_run_pairs(spec: str) -> dict[int, Path]:
    """Parse 'seed=42:path,seed=0:path,...' -> {seed: Path}."""
    out: dict[int, Path] = {}
    for tok in spec.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if not tok.startswith("seed="):
            raise SystemExit(f"Bad spec '{tok}': expected 'seed=N:path'")
        seed_part, _, path_part = tok.partition(":")
        seed = int(seed_part[len("seed="):])
        out[seed] = Path(path_part)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b9", required=True,
                    help="Comma-separated seed=N:path pairs for B9 runs")
    ap.add_argument("--h3alt", required=True,
                    help="Comma-separated seed=N:path pairs for H3-alt runs")
    ap.add_argument("--output-json", type=Path, default=None)
    args = ap.parse_args()

    b9_runs = parse_seed_run_pairs(args.b9)
    h3_runs = parse_seed_run_pairs(args.h3alt)
    seeds = sorted(set(b9_runs) & set(h3_runs))
    if not seeds:
        raise SystemExit("No overlapping seeds between --b9 and --h3alt")

    print("# F51 multi-seed paired-Wilcoxon analysis (B9 vs H3-alt, FL 5f×50ep, ≥ep5)\n")
    print(f"Seeds: {seeds}\n")
    print(f"Decision rule: 4/5 seeds with Δreg ≥ +2.5 pp → robust.\n")

    rows = []
    cat_rows = []
    for seed in seeds:
        b9_dir = b9_runs[seed]
        h3_dir = h3_runs[seed]
        b9_reg = per_fold_best(b9_dir, "next_region", REG_METRIC)
        h3_reg = per_fold_best(h3_dir, "next_region", REG_METRIC)
        b9_cat = per_fold_best(b9_dir, "next_category", CAT_METRIC)
        h3_cat = per_fold_best(h3_dir, "next_category", CAT_METRIC)
        rows.append({
            "seed": seed,
            "b9_dir": str(b9_dir),
            "h3_dir": str(h3_dir),
            "reg": paired(b9_reg, h3_reg),
            "cat": paired(b9_cat, h3_cat),
            "b9_reg_folds": b9_reg,
            "h3_reg_folds": h3_reg,
            "b9_cat_folds": b9_cat,
            "h3_cat_folds": h3_cat,
        })

    print("## 1 · Per-seed paired Wilcoxon (Δ B9 − H3-alt)\n")
    print("| seed | B9 reg ± σ | H3-alt reg ± σ | Δreg | p_reg | n+/n | "
          "B9 cat ± σ | H3-alt cat ± σ | Δcat | p_cat |")
    print("|---:|---:|---:|---:|---|---|---:|---:|---:|---|")
    for r in rows:
        rd = r["reg"]
        cd = r["cat"]
        if not rd.get("valid"):
            print(f"| {r['seed']} | (missing folds) |")
            continue
        p_r = f"{rd['p_value']:.4f}" if rd["p_value"] is not None else "n/a"
        p_c = f"{cd['p_value']:.4f}" if cd["p_value"] is not None else "n/a"
        print(f"| {r['seed']} | {rd['mean_arm_pp']:.2f} ± {rd['std_arm_pp']:.2f} | "
              f"{rd['mean_ref_pp']:.2f} ± {rd['std_ref_pp']:.2f} | "
              f"{rd['delta_pp']:+.2f} | {p_r} | {rd['n_pos']}/{rd['n']} | "
              f"{cd['mean_arm_pp']:.2f} ± {cd['std_arm_pp']:.2f} | "
              f"{cd['mean_ref_pp']:.2f} ± {cd['std_ref_pp']:.2f} | "
              f"{cd['delta_pp']:+.2f} | {p_c} |")

    print()
    print("## 2 · Across-seed summary\n")
    valid = [r for r in rows if r["reg"].get("valid")]
    deltas_reg = [r["reg"]["delta_pp"] for r in valid]
    deltas_cat = [r["cat"]["delta_pp"] for r in valid]
    n_seeds_pos = sum(1 for d in deltas_reg if d > 0)
    n_seeds_robust = sum(1 for d in deltas_reg if d >= 2.5)
    n_seeds = len(valid)

    print(f"- Across {n_seeds} seeds:")
    print(f"  - Δreg mean ± σ: **{np.mean(deltas_reg):+.2f} ± {np.std(deltas_reg, ddof=1):.2f} pp**  "
          f"(range [{min(deltas_reg):+.2f}, {max(deltas_reg):+.2f}])")
    print(f"  - Δcat mean ± σ: **{np.mean(deltas_cat):+.2f} ± {np.std(deltas_cat, ddof=1):.2f} pp**  "
          f"(range [{min(deltas_cat):+.2f}, {max(deltas_cat):+.2f}])")
    print(f"  - Seeds with Δreg > 0: **{n_seeds_pos}/{n_seeds}**")
    print(f"  - Seeds with Δreg ≥ +2.5 pp (paper-grade threshold): **{n_seeds_robust}/{n_seeds}**")

    # Pool all 5 folds × N seeds = 5N paired observations and run a single
    # paired Wilcoxon. This is the most powerful test if seeds are exchangeable.
    pooled_b9 = []
    pooled_h3 = []
    for r in valid:
        pooled_b9.extend(r["b9_reg_folds"])
        pooled_h3.extend(r["h3_reg_folds"])
    pooled = paired(pooled_b9, pooled_h3)
    if pooled.get("valid") and pooled["p_value"] is not None:
        print(f"  - **Pooled paired Wilcoxon (5×N folds): Δ={pooled['delta_pp']:+.2f} pp, "
              f"p={pooled['p_value']:.4g}, {pooled['n_pos']}/{pooled['n']} positive folds**")

    # Combine per-seed p-values via Fisher (each seed contributes p=0.0312 if 5/5+).
    if HAS_SCIPY:
        per_seed_ps = [r["reg"]["p_value"] for r in valid if r["reg"]["p_value"] is not None]
        if len(per_seed_ps) >= 2:
            fisher_stat, fisher_p = combine_pvalues(per_seed_ps, method="fisher")
            print(f"  - Fisher-combined p across seeds: **p={fisher_p:.4g}** (stat={fisher_stat:.2f})")

    # Verdict
    if n_seeds_robust >= 4:
        verdict = "✅ **ROBUST** — 4/5+ seeds with Δreg ≥ +2.5 pp. Paper claim holds."
    elif n_seeds_robust >= 2:
        verdict = "⚠ **FRAGILE** — 2-3/5 seeds robust. Paper claim weakens to FL-strong with seed-conditioning."
    else:
        verdict = "❌ **REJECTED** — fewer than 2 seeds robust."
    print(f"\n## 3 · Verdict\n\n{verdict}\n")

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        compact = []
        for r in rows:
            compact.append({
                "seed": r["seed"],
                "b9_dir": r["b9_dir"],
                "h3_dir": r["h3_dir"],
                "reg": r["reg"],
                "cat": r["cat"],
                "b9_reg_folds": r["b9_reg_folds"],
                "h3_reg_folds": r["h3_reg_folds"],
                "b9_cat_folds": r["b9_cat_folds"],
                "h3_cat_folds": r["h3_cat_folds"],
            })
        args.output_json.write_text(json.dumps({
            "rows": compact,
            "summary": {
                "n_seeds": n_seeds,
                "n_seeds_pos": n_seeds_pos,
                "n_seeds_robust": n_seeds_robust,
                "delta_reg_mean": float(np.mean(deltas_reg)),
                "delta_reg_std": float(np.std(deltas_reg, ddof=1)),
                "delta_cat_mean": float(np.mean(deltas_cat)),
                "delta_cat_std": float(np.std(deltas_cat, ddof=1)),
                "pooled": pooled,
            },
        }, indent=2))
        print(f"Wrote JSON: {args.output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
