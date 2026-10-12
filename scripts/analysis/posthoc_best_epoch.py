"""F50 T3 posthoc — apply correct (top10-aware, optionally delayed-min) best-epoch
selector to existing run dirs.

The trainer's `diagnostic_best_epochs` selects the best epoch by F1 (the per-task
primary metric) and reports OTHER metrics at THAT epoch. For top-K and MRR, the
F1-best epoch ≠ metric-best epoch, leading to systematic ~3.5 pp under-reporting
on FL MTL runs. F50 T3 §5.5 documents this.

This script reads each run's `metrics/fold{N}_next_{cat,region}_val.csv` and
re-aggregates with a user-chosen metric + epoch window.

USAGE:
    python scripts/analysis/posthoc_best_epoch.py <run_dir> \
        [--task next_region|next_category] \
        [--metric top10_acc_indist|mrr_indist|f1|...] \
        [--min-epoch N] \
        [--max-epoch N]

OUTPUT: one-line JSON per fold + aggregate summary.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path


def load_csv(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def best_in_window(rows: list[dict], key: str, min_epoch: int, max_epoch: int | None):
    """Return (best_value_pct, best_epoch) over rows where min_epoch ≤ ep ≤ max_epoch."""
    best, ep = -math.inf, None
    for r in rows:
        e = int(r["epoch"])
        if e < min_epoch:
            continue
        if max_epoch is not None and e > max_epoch:
            continue
        try:
            v = float(r[key])
        except (KeyError, ValueError):
            continue
        if math.isnan(v):
            continue
        if v > best:
            best, ep = v, e
    return (best * 100 if best > -math.inf else float("nan"), ep)


def f1_best_epoch(rows: list[dict]) -> int | None:
    """The trainer's selector — picks best F1 epoch."""
    best_f1, ep = -math.inf, None
    for r in rows:
        try:
            v = float(r["f1"])
        except (KeyError, ValueError):
            continue
        if v > best_f1:
            best_f1, ep = v, int(r["epoch"])
    return ep


def value_at_epoch(rows: list[dict], key: str, epoch: int):
    for r in rows:
        if int(r["epoch"]) == epoch:
            try:
                return float(r[key])
            except (KeyError, ValueError):
                return float("nan")
    return float("nan")


def aggregate(values: list[float]) -> dict:
    n = len(values)
    if n == 0:
        return {"mean": float("nan"), "std": float("nan"), "n": 0}
    m = sum(values) / n
    s = (sum((x - m) ** 2 for x in values) / (n - 1)) ** 0.5 if n > 1 else 0.0
    return {"mean": m, "std": s, "n": n, "values": values}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("run_dir", help="Path to results/check2hgi/<state>/<run_dir>")
    p.add_argument("--task", default="next_region", choices=("next_region", "next_category"))
    p.add_argument("--metric", default="top10_acc_indist",
                   help="Metric column in val CSV (default top10_acc_indist).")
    p.add_argument("--min-epoch", type=int, default=1, help="First epoch to consider (1-indexed).")
    p.add_argument("--max-epoch", type=int, default=None, help="Last epoch to consider (inclusive).")
    p.add_argument("--folds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    p.add_argument("--compare-f1-selector", action="store_true",
                   help="Also report metric value at F1-best epoch (the trainer's default) for comparison.")
    p.add_argument("--json", action="store_true", help="Emit JSON only (no headers).")
    args = p.parse_args()

    run = Path(args.run_dir)
    if not run.exists():
        print(f"ERROR: {run} not found", file=sys.stderr)
        sys.exit(2)

    metric_best, f1_best = [], []
    f1_best_epochs, metric_best_epochs = [], []
    f1_at_metric_best = []

    for fold in args.folds:
        csv_path = run / "metrics" / f"fold{fold}_{args.task}_val.csv"
        if not csv_path.exists():
            print(f"WARN: missing {csv_path}", file=sys.stderr)
            continue
        rows = load_csv(csv_path)

        v, ep = best_in_window(rows, args.metric, args.min_epoch, args.max_epoch)
        metric_best.append(v)
        metric_best_epochs.append(ep)

        if args.compare_f1_selector:
            f1_ep = f1_best_epoch(rows)
            f1_best_epochs.append(f1_ep)
            f1_metric_value = value_at_epoch(rows, args.metric, f1_ep) * 100 if f1_ep is not None else float("nan")
            f1_best.append(f1_metric_value)
            f1_at_metric_best.append(value_at_epoch(rows, "f1", ep) * 100 if ep is not None else float("nan"))

    summary = {
        "run_dir": str(run),
        "task": args.task,
        "metric": args.metric,
        "min_epoch": args.min_epoch,
        "max_epoch": args.max_epoch,
        f"{args.metric}_at_metric_best": aggregate(metric_best),
        "metric_best_epochs": metric_best_epochs,
    }
    if args.compare_f1_selector:
        summary[f"{args.metric}_at_f1_best"] = aggregate(f1_best)
        summary["f1_best_epochs"] = f1_best_epochs
        summary["selector_correction_pp"] = aggregate(metric_best)["mean"] - aggregate(f1_best)["mean"]

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"=== Posthoc best-epoch analysis ===")
        print(f"  run: {run.name}")
        print(f"  task={args.task}  metric={args.metric}  window=[{args.min_epoch}, {args.max_epoch or 'end'}]")
        print()
        agg = summary[f"{args.metric}_at_metric_best"]
        print(f"  {args.metric}-best ({args.min_epoch}≤ep≤{args.max_epoch or 'end'})")
        print(f"    mean = {agg['mean']:.2f} ± {agg['std']:.2f}  (n={agg['n']})")
        print(f"    per-fold values: {[f'{v:.2f}' for v in agg['values']]}")
        print(f"    per-fold best epochs: {metric_best_epochs}")
        if args.compare_f1_selector:
            f1_agg = summary[f"{args.metric}_at_f1_best"]
            print()
            print(f"  {args.metric} at F1-best (trainer's default selector)")
            print(f"    mean = {f1_agg['mean']:.2f} ± {f1_agg['std']:.2f}")
            print(f"    f1-best epochs: {f1_best_epochs}")
            print()
            print(f"  CORRECTION: {summary['selector_correction_pp']:+.2f} pp")
            print(f"  (positive = selector under-reported by this much)")


if __name__ == "__main__":
    main()
