"""Centralized RNG seeding for reproducibility."""

import random

import numpy as np
import torch


def seed_everything(seed: int) -> None:
    """Seed all RNGs for deterministic execution.

    Call once at program startup before any model or data operations.
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)
