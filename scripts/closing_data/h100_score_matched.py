#!/usr/bin/env python3
"""A40 board lane — matched-metric scorer for ONE MTL rundir (Task 1 A/B + Task 2).

Applies the validated r0_matched_rescore.py METHOD to a single rundir (that script
itself is hardwired to multi-state manifests). Per-task DIAGNOSTIC-BEST, fold-paired:

  reg FULL top10_acc = top10_acc_indist * (1 - ood_fraction)   at the indist-best epoch
                       (full=indist*(1-ood); validated vs B-A2 FL 72.95 vs 72.93)
  cat macro-F1       = the `f1` column (macro)                  at the f1-best epoch

Both read from metrics/fold*_next_{region,category}_val.csv (the per-epoch source that
carries ood_fraction), meaned over folds. Prints to 4dp and writes a committable JSON
sidecar (C28: commit result JSONs) into the rundir.

Usage: PYTHONPATH=src .venv/bin/python scripts/closing_data/a40_score_matched.py <rundir> [--seed N] [--tag T]
"""
import argparse
import csv
import glob
import json
import statistics as st
from pathlib import Path


def _per_fold(rundir: Path, head: str, metric: str):
    """Return (per_fold_value, per_fold_epoch) picking the epoch that maximizes `metric`."""
    vals, eps = [], []
    for f in sorted(glob.glob(str(rundir / f"metrics/fold*_next_{head}_val.csv"))):
        rows = list(csv.DictReader(open(f)))
        if not rows:
            continue
        best = max(rows, key=lambda r: float(r[metric]))
        if head == "region":
            v = float(best["top10_acc_indist"]) * (1.0 - float(best["ood_fraction"])) * 100.0
        else:  # category
            v = float(best["f1"]) * 100.0
        vals.append(v)
        eps.append(int(float(best["epoch"])))
    return vals, eps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundir")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--tag", type=str, default=None)
    args = ap.parse_args()

    rundir = Path(args.rundir).resolve()
    if not rundir.exists():
        raise SystemExit(f"rundir not found: {rundir}")

    reg_full, reg_eps = _per_fold(rundir, "region", "top10_acc_indist")
    cat_f1, cat_eps = _per_fold(rundir, "category", "f1")

    def ms(x):
        return (st.mean(x), (st.pstdev(x) if len(x) > 1 else 0.0), len(x)) if x else (float("nan"), 0.0, 0)

    cm, cs, cn = ms(cat_f1)
    rm, rs, rn = ms(reg_full)

    print(f"=== A40 matched-metric score: {rundir.name} ===")
    if args.seed is not None:
        print(f"  seed={args.seed}  tag={args.tag}")
    print(f"  cat macro-F1 (diag-best)      = {cm:.4f} ± {cs:.4f}  (n={cn})  per-fold={[round(x,4) for x in cat_f1]}  epochs={cat_eps}")
    print(f"  reg FULL top10_acc (indist-best) = {rm:.4f} ± {rs:.4f}  (n={rn})  per-fold={[round(x,4) for x in reg_full]}  epochs={reg_eps}")

    out = {
        "rundir": str(rundir.relative_to(Path(__file__).resolve().parents[2])) if str(rundir).startswith(str(Path(__file__).resolve().parents[2])) else str(rundir),
        "seed": args.seed,
        "tag": args.tag,
        "method": "reg full=top10_acc_indist*(1-ood_frac) at indist-best epoch; cat=macro-f1 at f1-best epoch; per-task diagnostic-best, fold-mean",
        "cat_macro_f1_mean": round(cm, 4), "cat_macro_f1_std": round(cs, 4), "cat_per_fold": [round(x, 4) for x in cat_f1], "cat_best_epochs": cat_eps,
        "reg_full_top10_mean": round(rm, 4), "reg_full_top10_std": round(rs, 4), "reg_per_fold": [round(x, 4) for x in reg_full], "reg_best_epochs": reg_eps,
        "n_folds": rn,
    }
    sidecar = rundir / "h100_matched_score.json"
    sidecar.write_text(json.dumps(out, indent=2))
    print(f"  wrote {sidecar}")


if __name__ == "__main__":
    main()
