#!/usr/bin/env python3
"""STL CAT ceiling scorer — macro-F1 at f1-best epoch, fold-mean, from a `--task next` rundir.

The matched MTL scorer (h100_score_matched.py) reads `metrics/fold*_next_category_val.csv`, but a
single-task `--task next` (next_gru) run writes `metrics/fold*_next_val.csv` with an `f1` (macro) column.
This mirrors the cat half of the matched method for those STL ceiling runs. cat is precision-insensitive
(fp16-eval OK per RUN_MATRIX_REDUCE) → REUSE existing artifacts.

Usage: python scripts/closing_data/score_stl_cat_ceiling.py <rundir> [--tag T]
"""
import argparse, csv, glob, json, statistics as st
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("rundir")
ap.add_argument("--tag", default=None)
args = ap.parse_args()
rundir = Path(args.rundir).resolve()

vals, eps = [], []
files = sorted(glob.glob(str(rundir / "metrics/fold*_next_val.csv")))
for f in files:
    rows = [r for r in csv.DictReader(open(f)) if r.get("f1")]
    if not rows:
        continue
    best = max(rows, key=lambda r: float(r["f1"]))
    vals.append(float(best["f1"]) * 100.0)
    eps.append(int(float(best["epoch"])))

if not vals:
    raise SystemExit(f"no fold*_next_val.csv with f1 in {rundir}")

mean = st.mean(vals)
std = st.pstdev(vals) if len(vals) > 1 else 0.0
out = {
    "rundir": str(rundir), "tag": args.tag, "metric": "STL cat ceiling = macro-F1 (f1 col) at f1-best epoch, fold-mean",
    "n_folds": len(vals), "cat_macro_f1_mean": round(mean, 4), "cat_macro_f1_std": round(std, 4),
    "cat_per_fold": [round(v, 4) for v in vals], "cat_best_epochs": eps,
}
print(f"=== STL cat ceiling: {rundir.name} ===")
print(f"  n_folds={len(vals)}  cat macro-F1 = {mean:.4f} ± {std:.4f}  per-fold={out['cat_per_fold']}  epochs={eps}")
sidecar = rundir / "stl_cat_ceiling_score.json"
sidecar.write_text(json.dumps(out, indent=2))
print(f"  wrote {sidecar}")
