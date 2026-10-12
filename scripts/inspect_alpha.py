"""Inspect learned α (and α_cluster) from MTL GETNext/TGSTAN/STA-Hyper checkpoints.

Reads the latest fold checkpoint in a given results dir and prints the
learned graph-prior mixing coefficient(s). Expects the MTL model to have
``next_poi`` as the region head with an ``alpha`` attribute (and
``alpha_cluster`` for STA-Hyper).

Usage::

    python scripts/inspect_alpha.py --run-dir results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_YYYYMMDD_HHMM
    python scripts/inspect_alpha.py --glob 'results/check2hgi/*/mtlnet_*20260421*'
"""

from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import torch


def find_best_ckpt(run_dir: Path) -> Path | None:
    # ModelCheckpoint saves under run_dir/fold_X/model_*.pt
    candidates = sorted(run_dir.glob("fold_*/*.pt"))
    if not candidates:
        candidates = sorted(run_dir.glob("**/*.pt"))
    return candidates[0] if candidates else None


def inspect(run_dir: Path) -> None:
    ckpt = find_best_ckpt(run_dir)
    if ckpt is None:
        print(f"[{run_dir.name}] No checkpoint found")
        return
    sd = torch.load(ckpt, map_location="cpu", weights_only=False)
    if isinstance(sd, dict) and "state_dict" in sd:
        sd = sd["state_dict"]
    elif isinstance(sd, dict) and "model_state_dict" in sd:
        sd = sd["model_state_dict"]
    # Search for alpha-like keys
    found = {}
    for key, val in sd.items():
        if "alpha" in key.lower() and val.numel() <= 4:
            found[key] = val.detach().cpu().tolist()
    if not found:
        print(f"[{run_dir.name}] No α-like parameters found in {ckpt.name}")
        print(f"  Keys sampled: {list(sd.keys())[:10]}")
        return
    print(f"[{run_dir.name}] from {ckpt.name}")
    for k, v in found.items():
        print(f"  {k}: {v}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=str, default=None)
    parser.add_argument("--glob", type=str, default=None,
                        help="Glob pattern for multiple run dirs")
    args = parser.parse_args()

    if args.glob:
        dirs = [Path(p) for p in sorted(glob.glob(args.glob)) if Path(p).is_dir()]
    elif args.run_dir:
        dirs = [Path(args.run_dir)]
    else:
        parser.error("Pass --run-dir or --glob")

    for d in dirs:
        inspect(d)
        print()


if __name__ == "__main__":
    main()
