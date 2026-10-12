"""Extract the learned `alpha` scalar from a next_getnext(_hard) MTL checkpoint.

Usage:
    PYTHONPATH=src python scripts/analysis/extract_alpha.py <checkpoint_dir_or_file>

Accepts either a single .pt file or a checkpoint directory — in the latter case
the highest-epoch checkpoint is picked. Prints α + head class + any sibling
scalars that live on the head.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import torch


def resolve_ckpt(path_arg: str) -> Path:
    p = Path(path_arg)
    if p.is_file():
        return p
    if not p.is_dir():
        raise SystemExit(f"Not a file or directory: {p}")
    candidates = sorted(
        p.glob("checkpoint_epoch_*.pt"),
        key=lambda f: int(re.search(r"checkpoint_epoch_(\d+)\.pt", f.name).group(1)),
    )
    if not candidates:
        raise SystemExit(f"No checkpoint_epoch_*.pt in {p}")
    return candidates[-1]  # highest epoch = latest best


def find_scalar_params(state_dict: dict) -> list[tuple[str, torch.Tensor]]:
    """Return (key, tensor) for every 0-dim or 1-element scalar parameter."""
    out = []
    for k, v in state_dict.items():
        if not isinstance(v, torch.Tensor):
            continue
        if v.numel() == 1:
            out.append((k, v))
    return out


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    ckpt_path = resolve_ckpt(sys.argv[1])
    print(f"Loading: {ckpt_path}")
    obj = torch.load(ckpt_path, map_location="cpu", weights_only=False)

    # ModelCheckpoint wraps in a dict with 'state_dict', 'epoch', 'metrics', etc.
    if isinstance(obj, dict) and "state_dict" in obj:
        sd = obj["state_dict"]
        epoch = obj.get("epoch", "?")
        metrics = obj.get("metrics", {})
        print(f"Epoch: {epoch}")
        if metrics:
            print("Saved-at metrics:")
            for k, v in sorted(metrics.items()):
                if isinstance(v, (int, float)):
                    print(f"  {k}: {v:.6f}")
    else:
        sd = obj
        print("Raw state_dict (no epoch metadata)")

    # Look specifically for alpha
    alpha_keys = [k for k in sd if k.endswith(".alpha") or k == "alpha"]
    print("\n=== Alpha parameters ===")
    if not alpha_keys:
        print("No keys ending in '.alpha' found.")
    for k in alpha_keys:
        v = sd[k]
        if isinstance(v, torch.Tensor):
            print(f"  {k} = {v.item():.6f}  (initial: 0.1 if default)")
        else:
            print(f"  {k} = {v}")

    # Dump all scalar params as diagnostic
    print("\n=== All scalar (1-element) parameters ===")
    for k, v in find_scalar_params(sd):
        try:
            val = v.item()
            print(f"  {k} = {val:.6f}")
        except Exception as e:
            print(f"  {k} = <tensor> ({e})")

    # Useful summary: head-related keys for verification
    print("\n=== Head-related key prefixes (for sanity check) ===")
    head_prefixes = set()
    for k in sd:
        if any(t in k for t in ["head", "getnext", "stan"]):
            parts = k.rsplit(".", 1)
            head_prefixes.add(parts[0] if len(parts) > 1 else k)
    for p in sorted(head_prefixes)[:25]:
        print(f"  {p}")
    if len(head_prefixes) > 25:
        print(f"  ... ({len(head_prefixes)-25} more)")


if __name__ == "__main__":
    main()
