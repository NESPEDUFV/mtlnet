#!/usr/bin/env python3
"""North-star evaluation for the HGI POI2Vec category-injection variants on AZ.

The merge_design study's load-bearing tasks are:
  - next-CATEGORY  via  --heads next_gru --input-type checkin
  - next-REGION    via  --heads next_getnext_hard --input-type region
                       (with per-fold leak-free GETNext transition logs)

For each variant {baseline, A, B, C}: run both heads with 5 folds × 30 epochs.
Per-fold transition logs are reused from output/check2hgi/arizona/.

Outputs land under docs/results/P1/ (the canonical location
p1_region_head_ablation.py writes to), tagged with the variant name so they
don't collide.

Usage:
    PYTHONPATH=src:research python scripts/probe/run_northstar_category_variants.py \\
        [--variants baseline A B C] [--folds 5] [--epochs 30]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


C2HGI_AZ_DIR = REPO_ROOT / "output" / "check2hgi" / "arizona"
TRANSITION_FOLD1 = C2HGI_AZ_DIR / "region_transition_log_seed42_fold1.pt"


def run_next_cat(state: str, folds: int, epochs: int) -> int:
    """next-CATEGORY via next_gru on check-in input sequences."""
    tag = f"NS_AZ_{state.split('_')[-1]}_nextcat_5f{epochs}ep"
    print(f"\n>>> [{state}] next-CATEGORY via next_gru, tag={tag}")
    cmd = [
        sys.executable, "scripts/p1_region_head_ablation.py",
        "--state", state,
        "--engine-override", "hgi",
        "--heads", "next_gru",
        "--input-type", "checkin",
        "--target", "category",
        "--folds", str(folds),
        "--epochs", str(epochs),
        "--seed", "42",
        "--tag", tag,
    ]
    print("  $", " ".join(cmd))
    t0 = time.time()
    rc = subprocess.call(cmd, cwd=str(REPO_ROOT))
    print(f"  rc={rc}, wall={(time.time()-t0)/60:.1f} min")
    return rc


def run_next_reg(state: str, folds: int, epochs: int) -> int:
    """next-REGION via next_getnext_hard on region-sequence input."""
    tag = f"NS_AZ_{state.split('_')[-1]}_nextreg_5f{epochs}ep"
    print(f"\n>>> [{state}] next-REGION via next_getnext_hard, tag={tag}")
    cmd = [
        sys.executable, "scripts/p1_region_head_ablation.py",
        "--state", state,
        "--engine-override", "hgi",
        "--region-emb-source", "hgi",
        "--heads", "next_getnext_hard",
        "--input-type", "region",
        "--folds", str(folds),
        "--epochs", str(epochs),
        "--seed", "42",
        "--override-hparams",
        "d_model=256", "num_heads=8",
        f"transition_path={TRANSITION_FOLD1}",
        "--per-fold-transition-dir", str(C2HGI_AZ_DIR),
        "--tag", tag,
    ]
    print("  $", " ".join(cmd))
    t0 = time.time()
    rc = subprocess.call(cmd, cwd=str(REPO_ROOT))
    print(f"  rc={rc}, wall={(time.time()-t0)/60:.1f} min")
    return rc


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variants", nargs="+", default=["baseline", "A", "B", "C"])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--skip-cat", action="store_true")
    ap.add_argument("--skip-reg", action="store_true")
    args = ap.parse_args()

    if not TRANSITION_FOLD1.exists():
        raise SystemExit(f"missing per-fold transition log: {TRANSITION_FOLD1}")

    summary: dict[str, dict] = {}
    for v in args.variants:
        state = f"arizona_cat{v}"
        summary[v] = {}
        if not args.skip_cat:
            summary[v]["next_cat_rc"] = run_next_cat(state, args.folds, args.epochs)
        if not args.skip_reg:
            summary[v]["next_reg_rc"] = run_next_reg(state, args.folds, args.epochs)

    print("\n" + "=" * 60 + "\nNorth-star run summary (rc=0 means OK):")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
