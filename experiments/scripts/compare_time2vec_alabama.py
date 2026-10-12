"""
A/B comparison: train MTLnet next-task on two Time2Vec embedding variants.

Variants (built by previous step into output/time2vec/alabama/.variants/):
  - ours_sub: our migrated embeddings, subset to 93,402 rows / 10,269 placeids
              that the reference also has
  - ref:      reference embeddings (from original notebook source)
              paired with our parquet's metadata via stable within-placeid sort

Both variants share IDENTICAL metadata (userid, datetime, placeid, category) so
the only thing that changes between runs is the 64-d embedding values. Any
difference in MTLnet F1 reflects a difference in embedding quality.

Outputs are saved to results/time2vec/alabama_{variant}/ for side-by-side
inspection.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from configs.paths import IoPaths, EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins

VARIANT_DIR = PROJECT_ROOT / "output" / "time2vec" / "alabama" / ".variants"
EMB_PATH = IoPaths.get_embedd("alabama", EmbeddingEngine.TIME2VEC)
RESULTS_BASE = PROJECT_ROOT / "results" / "time2vec"
INPUT_DIR = PROJECT_ROOT / "output" / "time2vec" / "alabama" / "input"
TEMP_DIR = PROJECT_ROOT / "output" / "time2vec" / "alabama" / "temp"
FOLDS_DIR = PROJECT_ROOT / "output" / "time2vec" / "alabama" / "folds"

VARIANTS = ["ours_sub", "ref"]


def swap_in(variant: str) -> None:
    src = VARIANT_DIR / f"embeddings_{variant}.parquet"
    if not src.exists():
        raise FileNotFoundError(f"Missing variant: {src}")
    print(f"  → swapping in {src.name}")
    shutil.copy(src, EMB_PATH)


def regenerate_inputs() -> None:
    """Regenerate next-task input from the swapped-in embedding file."""
    print("  → regenerating next-task input")
    # Wipe stale folds (they cache the old embeddings)
    if FOLDS_DIR.exists():
        shutil.rmtree(FOLDS_DIR)
    if INPUT_DIR.exists():
        shutil.rmtree(INPUT_DIR)
    if TEMP_DIR.exists():
        shutil.rmtree(TEMP_DIR)
    generate_next_input_from_checkins("alabama", EmbeddingEngine.TIME2VEC)


def train_mtlnet(epochs: int, folds: int) -> None:
    print(f"  → training MTLnet next-task (epochs={epochs}, folds={folds})")
    cmd = [
        sys.executable, "scripts/train.py",
        "--task", "next",
        "--state", "alabama",
        "--engine", "time2vec",
        "--epochs", str(epochs),
        "--folds", str(folds),
    ]
    subprocess.run(cmd, cwd=PROJECT_ROOT, check=True)


def archive_results(variant: str) -> None:
    src = RESULTS_BASE / "alabama"
    dst = RESULTS_BASE / f"alabama_{variant}"
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"  → archived to {dst}")


def main(epochs: int = 20, folds: int = 2) -> None:
    if not VARIANT_DIR.exists() or not list(VARIANT_DIR.glob("embeddings_*.parquet")):
        raise SystemExit(
            f"No variants in {VARIANT_DIR}. Run the variant builder first."
        )

    for variant in VARIANTS:
        print(f"\n{'='*72}\n  Variant: {variant}\n{'='*72}")
        swap_in(variant)
        regenerate_inputs()
        train_mtlnet(epochs=epochs, folds=folds)
        archive_results(variant)

    print(f"\n{'='*72}\n  Done. Results:")
    for variant in VARIANTS:
        print(f"    results/time2vec/alabama_{variant}/")
    print(f"{'='*72}")


if __name__ == "__main__":
    main()