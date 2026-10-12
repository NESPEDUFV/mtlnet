"""
Shared synthetic data infrastructure for integration tests.

All integration tests use CPU-only, deterministic synthetic data.
No real data files required on a fresh checkout.
"""

import random

import numpy as np
import pytest
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset


# ---------------------------------------------------------------------------
# Constants (shared across all integration tests)
# ---------------------------------------------------------------------------
SEED = 42
NUM_CLASSES = 7
EMBED_DIM = 64
SEQ_LEN = 9
BATCH_SIZE = 64
NUM_TRAIN = 700   # 100 per class
NUM_VAL = 140     # 20 per class
DEVICE = torch.device("cpu")
INTEGRATION_EPOCHS = 3
INTEGRATION_FOLDS = 2


# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------
def seed_everything(seed: int = SEED) -> None:
    """Seed all RNGs for deterministic CPU execution."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.use_deterministic_algorithms(True, warn_only=True)


# ---------------------------------------------------------------------------
# Synthetic data generators
# ---------------------------------------------------------------------------
def make_category_data(n_per_class: int, embed_dim: int = EMBED_DIM,
                       seed: int = SEED):
    """Synthetic category data: class-specific centroid + noise.

    Returns (X, y) as torch tensors.
    """
    rng = np.random.RandomState(seed)
    xs, ys = [], []
    for c in range(NUM_CLASSES):
        centroid = np.zeros(embed_dim, dtype=np.float32)
        centroid[c * (embed_dim // NUM_CLASSES): (c + 1) * (embed_dim // NUM_CLASSES)] = 2.0
        noise = rng.randn(n_per_class, embed_dim).astype(np.float32) * 1.5
        xs.append(centroid + noise)
        ys.extend([c] * n_per_class)
    return torch.from_numpy(np.vstack(xs)), torch.tensor(ys, dtype=torch.long)


def make_next_data(n_per_class: int, embed_dim: int = EMBED_DIM,
                   seq_len: int = SEQ_LEN, seed: int = SEED):
    """Synthetic next-POI data: class-specific sequence patterns.

    Returns (X, y) as torch tensors with X shape (N, seq_len, embed_dim).
    """
    rng = np.random.RandomState(seed)
    xs, ys = [], []
    for c in range(NUM_CLASSES):
        centroid = np.zeros(embed_dim, dtype=np.float32)
        centroid[c * (embed_dim // NUM_CLASSES): (c + 1) * (embed_dim // NUM_CLASSES)] = 2.0
        for _ in range(n_per_class):
            seq = np.tile(centroid, (seq_len, 1))
            seq += rng.randn(seq_len, embed_dim).astype(np.float32) * 1.5
            xs.append(seq)
            ys.append(c)
    X = torch.from_numpy(np.stack(xs))
    y = torch.tensor(ys, dtype=torch.long)
    return X, y


def make_loaders(X_train, y_train, X_val, y_val, batch_size=BATCH_SIZE):
    """Create train/val DataLoaders with deterministic shuffling."""
    train_dl = DataLoader(
        TensorDataset(X_train, y_train),
        batch_size=batch_size,
        shuffle=True,
        generator=torch.Generator().manual_seed(SEED),
    )
    val_dl = DataLoader(
        TensorDataset(X_val, y_val),
        batch_size=batch_size,
    )
    return train_dl, val_dl
