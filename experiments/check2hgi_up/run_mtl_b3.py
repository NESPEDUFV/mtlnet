"""Run MTL-B3 (post-F27 champion config) on a state with a swapped Check2HGI substrate.

B3 config (post-F27, per docs/archive/check2hgi-post-paper-closure-2026-05-01/SESSION_HANDOFF_2026-04-24.md):
    mtlnet_crossattn + static_weight(category_weight=0.75)
    + cat-head=next_gru (task_a)
    + reg-head=next_getnext_hard d=256, 8h (task_b)

Swap procedure:
  1. Backup `output/check2hgi/{state}/embeddings.parquet` if not already
  2. Copy variant embedding into that path
  3. Regenerate `next.parquet` + `sequences_next.parquet`
     (note: `region_transition_log.pt` does not depend on embeddings —
      it is reused as-is.)
  4. Run scripts/train.py --task mtl ...
  5. Restore baseline embedding + regenerate next.parquet so a downstream
     scripts/train.py invocation doesn't accidentally use the variant data.
"""

from __future__ import annotations

import argparse
import os
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
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--source_dir", default="docs/results/UP1")
    ap.add_argument("--source_epochs", type=int, default=200)
    ap.add_argument("--cat_head", default="next_gru",
                    help="Post-F27 default. Use 'default' to skip the flag (pre-F27 B3).")
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
        print(f"[backup] already exists at {backup}")

    print(f"[swap] {src} -> {target}")
    shutil.copy2(src, target)

    print("[regen] generate_next_input_from_checkins ...")
    from configs.paths import EmbeddingEngine
    from data.inputs.builders import generate_next_input_from_checkins
    generate_next_input_from_checkins(args.state, EmbeddingEngine.CHECK2HGI)

    transition_path = (_root / "output" / "check2hgi" / state_lower /
                       "region_transition_log.pt")
    if not transition_path.exists():
        sys.exit(f"region_transition_log.pt not found at {transition_path}; "
                 f"run scripts/compute_region_transition.py --state {state_lower}")

    cmd = [
        sys.executable, "-u", "scripts/train.py",
        "--state", state_lower,
        "--task", "mtl",
        "--task-set", "check2hgi_next_region",
        "--engine", "check2hgi",
        "--folds", str(args.folds),
        "--epochs", str(args.epochs),
        "--seed", "42",
        "--task-a-input-type", "checkin",
        "--task-b-input-type", "region",
        "--model", "mtlnet_crossattn",
        "--mtl-loss", "static_weight",
        "--category-weight", "0.75",
        "--reg-head", "next_getnext_hard",
        "--reg-head-param", "d_model=256",
        "--reg-head-param", "num_heads=8",
        "--reg-head-param", f"transition_path={transition_path}",
        "--max-lr", "0.003",
        "--gradient-accumulation-steps", "1",
        "--no-checkpoints",
    ]
    if args.cat_head != "default":
        cmd.extend(["--cat-head", args.cat_head])

    print("[train] " + " ".join(cmd))
    rc = subprocess.call(cmd)
    print(f"[train] returncode={rc}")

    print(f"[restore] {backup} -> {target}")
    shutil.copy2(backup, target)
    print("[restore] regenerating next.parquet from restored embedding ...")
    generate_next_input_from_checkins(args.state, EmbeddingEngine.CHECK2HGI)
    print("[done]")
    return rc


if __name__ == "__main__":
    sys.exit(main())
