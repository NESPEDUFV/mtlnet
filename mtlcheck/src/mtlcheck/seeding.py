"""Seeding — and the one contract that makes a fold independent of the folds before it.

The reference implementation seeds two different ways. `train.py` seeds once per run, so fold k's
weights depend on how much randomness folds 0..k-1 consumed. `p1_region_head_ablation.py` reseeds
inside each fold with `seed + fold_idx`, which is what makes its `--only-fold` fan-out reproduce a
sequential run exactly.

This project adopts the per-fold reseed for every family. That is a deliberate behaviour change for
the category and joint families. **The A/B that would quantify it has NOT been run** — the A40 is
occupied and no multi-seed comparison exists yet. Until it does, this is an accepted change, not a
measured one. Tracked in `studies/porting_validation/STATE.md`.

**What it does NOT touch: the split.** Fold membership comes from `StratifiedGroupKFold(random_state=seed)`
computed once, before any training. Reseeding inside a fold changes weight initialisation and batch
shuffling only.
"""

from __future__ import annotations

import hashlib
import os
import random

import numpy as np
import torch


def seed_everything(seed: int) -> None:
    """Seed Python, NumPy and torch (all devices)."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def fold_seed(seed: int, fold: int, *, decorrelated: bool = False) -> int:
    """The seed a given fold trains under.

    `decorrelated=False` reproduces the reference contract exactly: `seed + fold`. It has a known
    wart — the streams collide across cells, so (seed 0, fold 1) and (seed 1, fold 0) share one
    stream, mildly correlating cells the statistics treat as independent replicates.

    `decorrelated=True` derives the stream from a hash of the pair instead, which removes the
    collision but breaks byte-identity with the reference. It is opt-in for exactly that reason:
    the break has to be a decision, not a side effect.
    """
    if not decorrelated:
        return seed + fold
    digest = hashlib.sha256(f"{seed}:{fold}".encode()).digest()
    return int.from_bytes(digest[:4], "big")


def split_seed(seed: int) -> int:
    """The seed that determines fold MEMBERSHIP.

    Deliberately its own function, and deliberately not `fold_seed`. Fold membership is a property
    of the run, not of the fold, and conflating the two is how a "harmless" seeding change silently
    redraws a frozen split.
    """
    return seed


__all__ = ["seed_everything", "fold_seed", "split_seed"]
