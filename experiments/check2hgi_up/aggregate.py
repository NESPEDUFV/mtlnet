"""Aggregate all variant runs + anchor baselines into a single table."""

from __future__ import annotations

import argparse
import glob
import json
import statistics as st
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results_dir", default="docs/results/UP1")
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rdir = Path(args.results_dir)

    # Load anchors
    anc_path = rdir / f"anchors_{args.state}.json"
    anchors = None
    if anc_path.exists():
        anchors = json.load(open(anc_path))

    # Load all variant runs
    runs = []
    for p in sorted(glob.glob(str(rdir / f"{args.state}_*_seed*_ep*.json"))):
        # exclude summary files
        if "summary" in Path(p).name or "anchors" in Path(p).name:
            continue
        d = json.load(open(p))
        runs.append(d)

    # Group by variant
    variants = {}
    for d in runs:
        variants.setdefault(d["variant"], []).append(d)

    # Compute stats
    rows = []
    base_f1 = None
    for v, seeds in sorted(variants.items(), key=lambda x: x[0]):
        f1s = [d["linear_probe"]["f1_mean"] for d in seeds]
        accs = [d["linear_probe"]["acc_mean"] for d in seeds]
        losses = [d["best_loss"] for d in seeds]
        times = [d["train_time_s"] for d in seeds]
        n_params = seeds[0]["n_params"]
        row = {
            "variant": v,
            "n_seeds": len(seeds),
            "f1_mean": st.mean(f1s),
            "f1_std": st.stdev(f1s) if len(f1s) > 1 else 0.0,
            "acc_mean": st.mean(accs),
            "acc_std": st.stdev(accs) if len(accs) > 1 else 0.0,
            "best_loss_mean": st.mean(losses),
            "n_params": n_params,
            "avg_train_s": st.mean(times),
        }
        rows.append(row)
        if v == "baseline":
            base_f1 = row["f1_mean"]

    # Sort by F1 mean descending
    rows.sort(key=lambda r: r["f1_mean"], reverse=True)

    # Print anchor block
    print(f"\n=== Check2HGI-up · Alabama · Linear Probe (next-category) ===\n")
    if anchors:
        for name, key in [("majority", "majority"), ("raw-features", "raw_features")]:
            a = anchors[key]
            print(f"{'anchor/'+name:<22} n=1   f1={a['f1_mean']:.4f}±{a['f1_std']:.4f}  "
                  f"acc={a['acc_mean']:.4f}±{a['acc_std']:.4f}")
    print()

    # Print variant table
    header = f"{'Variant':<22} {'Seeds':<5} {'F1-macro':<20} {'Acc':<20} {'Loss':<10} {'Params':<10} {'Δvs base'}"
    print(header); print("-" * len(header))
    for r in rows:
        delta = f"+{(r['f1_mean']-base_f1)*100:.2f} pp" if base_f1 is not None else "—"
        if r["variant"] == "baseline":
            delta = "(ref)"
        print(f"{r['variant']:<22} {r['n_seeds']:<5} "
              f"{r['f1_mean']:.4f}±{r['f1_std']:.4f}  "
              f"{r['acc_mean']:.4f}±{r['acc_std']:.4f}  "
              f"{r['best_loss_mean']:.4f}   {r['n_params']:<10} "
              f"{delta}")

    # Save
    out = args.out or (rdir / f"AGGREGATE_{args.state}.json")
    with open(out, "w") as f:
        json.dump({
            "state": args.state,
            "anchors": anchors,
            "variants": rows,
            "baseline_f1": base_f1,
        }, f, indent=2)
    print(f"\nSaved to {out}")


if __name__ == "__main__":
    main()
