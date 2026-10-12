#!/usr/bin/env python3
"""Drive end-to-end MTL evaluation for each HGI-category-injection variant on AZ.

For each variant {baseline, A, B, C}:
  1. Generate input/category.parquet + input/next.parquet from the variant's embeddings.
  2. Freeze MTL fold indices (if not cached).
  3. Run scripts/train.py --task mtl --state arizona_cat{X} --engine hgi.
  4. Parse the resulting fold metrics and emit a per-variant JSON.

Final step: pull all per-variant fold metrics into a single comparison table.

Usage:
    PYTHONPATH=src:research python scripts/probe/run_mtl_category_variants.py \\
        [--variants baseline A B C] [--folds 5] [--epochs 30]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "research"))

from configs.paths import IoPaths, EmbeddingEngine  # noqa: E402
from data.inputs.builders import generate_category_input, generate_next_input_from_poi  # noqa: E402


def ensure_inputs(state: str) -> None:
    """Regenerate input/{category,next}.parquet from the variant's embeddings."""
    print(f"[{state}] regenerating MTL inputs ...")
    generate_category_input(state, EmbeddingEngine.HGI)
    generate_next_input_from_poi(state, EmbeddingEngine.HGI)


def freeze_folds(state: str) -> None:
    cache = IoPaths.HGI.get_state_dir(state) / "folds" / "fold_indices_mtl.pt"
    if cache.exists():
        print(f"[{state}] folds already frozen at {cache}")
        return
    print(f"[{state}] freezing MTL folds ...")
    # NB: freeze_folds.py crashes at the very end with a worktree-specific
    # relative_to() check, but writes the cache file before crashing. So we
    # tolerate non-zero exit if the .pt file landed.
    rc = subprocess.call([
        sys.executable, "scripts/study/freeze_folds.py",
        "--state", state, "--engine", "hgi", "--task", "mtl",
    ], cwd=str(REPO_ROOT))
    if not cache.exists():
        raise RuntimeError(f"freeze_folds did not produce cache: rc={rc}, missing {cache}")
    if rc != 0:
        print(f"[{state}] freeze_folds exited rc={rc} but cache file landed — proceeding.")


def run_mtl(state: str, folds: int, epochs: int) -> Path:
    """Run scripts/train.py and return the results directory."""
    print(f"[{state}] starting MTL training: --folds {folds} --epochs {epochs}")
    t0 = time.time()
    log_path = REPO_ROOT / f"/tmp/mtl_{state}.log"
    # Don't suppress output — capture stderr in case of crash.
    rc = subprocess.call([
        sys.executable, "scripts/train.py",
        "--task", "mtl", "--state", state, "--engine", "hgi",
        "--folds", str(folds), "--epochs", str(epochs),
    ], cwd=str(REPO_ROOT))
    dt = (time.time() - t0) / 60
    print(f"[{state}] MTL exit={rc}, wall={dt:.1f} min")
    results_dir = REPO_ROOT / "results" / "hgi" / state
    return results_dir


def parse_fold_metrics(state: str) -> dict:
    """Scan results/hgi/<state>/ for fold-level metrics and aggregate."""
    results_dir = REPO_ROOT / "results" / "hgi" / state
    if not results_dir.exists():
        return {"error": f"results dir missing: {results_dir}"}
    # Look for the canonical history.json or fold summary.
    candidates = list(results_dir.rglob("*.json")) + list(results_dir.rglob("*.csv"))
    print(f"[{state}] result files found: {[p.name for p in candidates[:10]]}")
    summary = {"state": state, "files": [str(p.relative_to(REPO_ROOT)) for p in candidates]}
    # Try to extract category F1 and next F1 from history.json patterns.
    for p in candidates:
        if p.suffix != ".json":
            continue
        try:
            with open(p) as f:
                obj = json.load(f)
        except Exception:
            continue
        if "category" in obj or "next" in obj or "folds" in obj:
            summary["raw"] = {k: obj[k] for k in ("category", "next", "folds", "summary")
                              if k in obj}
            break
    return summary


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variants", nargs="+", default=["baseline", "A", "B", "C"])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--out", type=str,
                    default="docs/studies/hgi_category_injection/HGI_CATEGORY_MTL.json")
    args = ap.parse_args()

    all_results = {}
    for v in args.variants:
        state = f"arizona_cat{v}"
        print("\n" + "=" * 80 + f"\n>>> {state}\n" + "=" * 80)
        ensure_inputs(state)
        freeze_folds(state)
        run_mtl(state, folds=args.folds, epochs=args.epochs)
        all_results[v] = parse_fold_metrics(state)

    out_path = REPO_ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump({"folds": args.folds, "epochs": args.epochs, "results": all_results}, f, indent=2)
    print(f"\nWrote MTL results map → {out_path}")


if __name__ == "__main__":
    main()
