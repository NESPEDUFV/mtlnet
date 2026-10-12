"""F50 follow-ups paired analysis (B2/F64 + F52 + F65 + F53).

Compares each new run vs the B9 champion clean baseline using paired
Wilcoxon signed-rank on per-fold reg top10_acc_indist @≥ep5. Emits a
markdown summary to stdout.

Usage:
    python scripts/analysis/f50_b2_f52_f65_f53_analysis.py \\
        --b9-run results/check2hgi/florida/<b9_clean_run> \\
        --b2-run results/check2hgi/florida/<b2_run> \\
        --f52-run results/check2hgi/florida/<f52_run> \\
        --f65-run results/check2hgi/florida/<f65_run> \\
        --f53-h3-runs results/check2hgi/florida/<h3_cw0.25>,<h3_cw0.50>,<h3_cw0.75> \\
        --f53-p1-runs results/check2hgi/florida/<p1_cw0.25>,<p1_cw0.50>,<p1_cw0.75>

Each run directory must contain ``metrics/fold{i}_next_region_val.csv``
and ``metrics/fold{i}_next_category_val.csv`` for folds 1..5. ``min_best_epoch``
is fixed at 5 to mirror the F50 T4 paper-grade selection rule.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

try:
    from scipy.stats import wilcoxon
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


REG_METRIC_KEYS = ("top10_acc_indist", "mrr_indist", "f1")
CAT_METRIC_KEYS = ("f1", "accuracy", "f1_weighted")


def per_fold_best(
    run_dir: Path, task: str, metric: str, min_epoch: int = 5,
) -> list[float]:
    """Return list of fold-best values @≥ep min_epoch for the given metric."""
    out: list[float] = []
    for fold in (1, 2, 3, 4, 5):
        csv = run_dir / "metrics" / f"fold{fold}_{task}_val.csv"
        if not csv.exists():
            continue
        df = pd.read_csv(csv)
        if metric not in df.columns:
            return []
        # min_epoch is 1-indexed (epoch 1 is first row, epoch=df['epoch'])
        masked = df[df["epoch"] >= min_epoch]
        if masked.empty:
            return []
        out.append(float(masked[metric].max()))
    return out


def paired_test(arm_vals: list[float], ref_vals: list[float]) -> dict:
    """Paired Wilcoxon vs ref. Returns {n, mean_arm, mean_ref, delta_pp,
    n_positive, n_negative, p_value, sigma_pooled}."""
    if not arm_vals or not ref_vals or len(arm_vals) != len(ref_vals):
        return {"valid": False}
    a = np.array(arm_vals, dtype=float)
    r = np.array(ref_vals, dtype=float)
    diffs = a - r
    n_positive = int((diffs > 0).sum())
    n_negative = int((diffs < 0).sum())
    out = {
        "valid": True,
        "n": len(a),
        "mean_arm": float(a.mean()),
        "std_arm": float(a.std(ddof=1)) if len(a) > 1 else 0.0,
        "mean_ref": float(r.mean()),
        "std_ref": float(r.std(ddof=1)) if len(r) > 1 else 0.0,
        "delta_pp": float((a.mean() - r.mean()) * 100),
        "n_positive": n_positive,
        "n_negative": n_negative,
    }
    if HAS_SCIPY and len(a) >= 4 and not np.allclose(diffs, 0):
        try:
            stat = wilcoxon(diffs, zero_method="wilcox", alternative="two-sided")
            out["p_value"] = float(stat.pvalue)
        except ValueError:
            out["p_value"] = None
    else:
        out["p_value"] = None
    return out


def fmt_paired(d: dict) -> str:
    if not d.get("valid"):
        return "n/a (missing folds)"
    sig = ""
    if d["p_value"] is not None:
        sig = f" p={d['p_value']:.4f}"
    return (f"Δ={d['delta_pp']:+.2f} pp{sig} "
            f"({d['n_positive']}/{d['n']}+ {d['n_negative']}/{d['n']}-)")


def analyze_arm(run_dir: Path, ref_dir: Path, label: str, min_epoch: int = 5) -> dict:
    out = {"label": label, "run_dir": str(run_dir)}
    for task_kind, task_id, metrics in [
        ("reg", "next_region", REG_METRIC_KEYS),
        ("cat", "next_category", CAT_METRIC_KEYS),
    ]:
        for metric in metrics:
            arm_v = per_fold_best(run_dir, task_id, metric, min_epoch=min_epoch)
            ref_v = per_fold_best(ref_dir, task_id, metric, min_epoch=min_epoch)
            out[f"{task_kind}.{metric}"] = paired_test(arm_v, ref_v)
            out[f"{task_kind}.{metric}.values"] = arm_v
            out[f"{task_kind}.{metric}.ref_values"] = ref_v
    return out


def print_arm(report: dict) -> None:
    print(f"\n### {report['label']}  (`{Path(report['run_dir']).name}`)\n")
    print("| task | metric | mean_arm | mean_ref | Δ paired Wilcoxon |")
    print("|---|---|---:|---:|---|")
    for task_kind, metrics in [("reg", REG_METRIC_KEYS), ("cat", CAT_METRIC_KEYS)]:
        for metric in metrics:
            d = report[f"{task_kind}.{metric}"]
            if not d.get("valid"):
                print(f"| {task_kind} | {metric} | — | — | n/a |")
                continue
            print(f"| {task_kind} | {metric} | {d['mean_arm']*100:.2f} ± "
                  f"{d['std_arm']*100:.2f} | {d['mean_ref']*100:.2f} ± "
                  f"{d['std_ref']*100:.2f} | {fmt_paired(d)} |")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--b9-run", type=Path, required=True,
                    help="B9 champion (clean) reference run dir")
    ap.add_argument("--b2-run", type=Path, default=None)
    ap.add_argument("--f52-run", type=Path, default=None)
    ap.add_argument("--f65-run", type=Path, default=None)
    ap.add_argument("--f53-h3-runs", type=str, default="",
                    help="Comma-separated H3-alt cw sweep run dirs (cw=0.25,0.50,0.75)")
    ap.add_argument("--f53-p1-runs", type=str, default="",
                    help="Comma-separated P1 (no_crossattn) cw sweep run dirs")
    ap.add_argument("--min-epoch", type=int, default=5)
    ap.add_argument("--output-json", type=Path, default=None)
    args = ap.parse_args()

    if not args.b9_run.exists():
        raise SystemExit(f"B9 reference run dir does not exist: {args.b9_run}")

    print(f"# F50 follow-ups paired analysis (vs B9 clean champion)\n")
    print(f"Reference: `{args.b9_run.name}`  | min_best_epoch = {args.min_epoch}\n")

    reports: list[dict] = []

    if args.b2_run and args.b2_run.exists():
        reports.append(analyze_arm(
            args.b2_run, args.b9_run, "B2/F64 — warmup-decay reg_head LR",
            min_epoch=args.min_epoch,
        ))
    if args.f52_run and args.f52_run.exists():
        reports.append(analyze_arm(
            args.f52_run, args.b9_run, "F52 — identity-crossattn (P5)",
            min_epoch=args.min_epoch,
        ))
    if args.f65_run and args.f65_run.exists():
        reports.append(analyze_arm(
            args.f65_run, args.b9_run, "F65 — min_size_truncate joint loader",
            min_epoch=args.min_epoch,
        ))

    # F53 sweep — compare each cw value vs B9.
    for label_prefix, runs_csv in [
        ("F53 H3-alt", args.f53_h3_runs),
        ("F53 P1 (no_crossattn)", args.f53_p1_runs),
    ]:
        if not runs_csv:
            continue
        for run_str in runs_csv.split(","):
            run_str = run_str.strip()
            if not run_str:
                continue
            p = Path(run_str)
            if not p.exists():
                print(f"\n[skip] {run_str} does not exist")
                continue
            # Try to extract cw from path or just label by directory name.
            label = f"{label_prefix} (`{p.name}`)"
            reports.append(analyze_arm(
                p, args.b9_run, label, min_epoch=args.min_epoch,
            ))

    # Print all arm tables.
    for r in reports:
        print_arm(r)

    # Write structured JSON for downstream scripts.
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        # Strip out the long lists for compactness.
        compact = []
        for r in reports:
            row = {"label": r["label"], "run_dir": r["run_dir"]}
            for k, v in r.items():
                if k.endswith(".values") or k.endswith(".ref_values"):
                    continue
                if isinstance(v, dict):
                    row[k] = v
            compact.append(row)
        args.output_json.write_text(json.dumps(compact, indent=2))
        print(f"\nWrote structured JSON: {args.output_json}")

    # Headline (best-of-arm by Δreg).
    print("\n## Headline ranking (Δreg top10_acc_indist vs B9)\n")
    rows = []
    for r in reports:
        d = r.get("reg.top10_acc_indist", {})
        if d.get("valid"):
            rows.append((r["label"], d["delta_pp"], d.get("p_value"),
                         d["n_positive"], d["n"]))
    rows.sort(key=lambda x: -x[1])
    print("| arm | Δreg pp | p | n+ / n |")
    print("|---|---:|---|---|")
    for label, delta, p, np_, n in rows:
        psig = f"{p:.4f}" if p is not None else "n/a"
        print(f"| {label} | {delta:+.2f} | {psig} | {np_}/{n} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
