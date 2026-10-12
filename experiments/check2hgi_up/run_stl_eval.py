"""Run STL next-category training for one variant on AL.

This is the headline eval — the linear probe is just a fast proxy. Here we
plug a variant's embeddings into the actual MTLnet pipeline and run the same
single-task training that produced the published 38.58 ± 1.23 baseline.

Strategy:
  1. Backup current `output/check2hgi/{state}/embeddings.parquet`
  2. Copy variant embeddings into that path
  3. Regenerate `next.parquet` via `generate_next_input_from_checkins(...)`
  4. Run `scripts/train.py --task next --engine check2hgi --state {state} --folds 5 --epochs 50`
  5. Restore backup

Designed to be re-runnable (each call backs up only if a backup doesn't exist).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--state", default="Alabama")
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--source_dir", default="docs/results/UP1")
    ap.add_argument("--source_epochs", type=int, default=200)
    args = ap.parse_args()

    state_lower = args.state.lower()
    src = Path(args.source_dir) / f"{state_lower}_{args.variant}_seed{args.seed}_ep{args.source_epochs}_emb.parquet"
    if not src.exists():
        sys.exit(f"variant embedding not found: {src}")

    target = _root / "output" / "check2hgi" / state_lower / "embeddings.parquet"
    backup = target.with_suffix(".parquet.bak_orig")

    if not backup.exists():
        print(f"[backup] {target} -> {backup}")
        shutil.copy2(target, backup)
    else:
        print(f"[backup] already exists at {backup}, leaving alone")

    print(f"[swap] {src} -> {target}")
    shutil.copy2(src, target)

    # Regenerate next.parquet
    print("[regen] generate_next_input_from_checkins ...")
    from configs.paths import EmbeddingEngine
    from data.inputs.builders import generate_next_input_from_checkins
    generate_next_input_from_checkins(args.state, EmbeddingEngine.CHECK2HGI)

    # Run STL next training
    cmd = [
        sys.executable, "scripts/train.py",
        "--task", "next",
        "--engine", "check2hgi",
        "--state", state_lower,
        "--folds", str(args.folds),
        "--epochs", str(args.epochs),
        "--no-checkpoints",
    ]
    print("[train] " + " ".join(cmd))
    rc = subprocess.call(cmd)
    print(f"[train] returncode={rc}")

    # Restore embedding + regenerate next.parquet so subsequent plain
    # scripts/train.py invocations don't accidentally use the variant's
    # cached next.parquet.
    print(f"[restore] {backup} -> {target}")
    shutil.copy2(backup, target)
    print("[restore] regenerating next.parquet from restored embedding ...")
    generate_next_input_from_checkins(args.state, EmbeddingEngine.CHECK2HGI)
    print("[done]")
    return rc


if __name__ == "__main__":
    sys.exit(main())
