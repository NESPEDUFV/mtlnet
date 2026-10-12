"""
Sphere2Vec contrastive dataset.

This module provides two equivalent dataset implementations:

1. ``ContrastiveSpatialDataset`` — verbatim port of the source notebook's
   per-item ``__getitem__`` (one Python random call + numpy.normal +
   3 tensor allocations per sample). Slow but bit-equivalent to the
   notebook under a shared global numpy RNG. Used by the equivalence test
   in ``tests/test_embeddings/test_sphere2vec.py``.

2. ``FastContrastiveSpatialDataset`` — vectorized rewrite that implements
   ``__getitems__(indices)`` (PyTorch ≥2.0). Generates an entire batch's
   worth of positives/negatives in a single tensor op. Produces the SAME
   statistical distribution of pairs (Bernoulli(0.5) positive/negative,
   Gaussian(0, pos_radius) noise, uniform negative-coord choice) but in a
   different sequence than the per-item version. Used by ``create_embedding``
   by default for ~5–10× faster epoch times.

Both classes use the global numpy RNG (matching the notebook), so seeding
``np.random.seed(...)`` before iteration gives reproducible runs.
"""

from typing import List, Tuple

import numpy as np
import torch
from torch.utils.data import Dataset


class ContrastiveSpatialDataset(Dataset):
    """
    Per-item dataset matching the source notebook bit-for-bit.

    Args:
        coords: ``np.ndarray`` of shape ``[N, 2]`` with ``(latitude, longitude)``
            in degrees.
        pos_radius: Standard deviation (in degrees) of the Gaussian noise applied
            to generate positive pairs. ``0.01`` ≈ 1.1 km.
    """

    def __init__(self, coords: np.ndarray, pos_radius: float = 0.01):
        self.coords = coords
        self.num_points = len(coords)
        self.pos_radius = pos_radius

    def __len__(self) -> int:
        return self.num_points

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        coord_i = self.coords[idx]

        if np.random.random() > 0.5:
            label = 1.0
            noise = np.random.normal(0, self.pos_radius, size=2)
            coord_j = coord_i + noise
        else:
            label = 0.0
            rand_idx = np.random.randint(0, self.num_points)
            coord_j = self.coords[rand_idx]

        return (
            torch.tensor(coord_i, dtype=torch.float32),
            torch.tensor(coord_j, dtype=torch.float32),
            torch.tensor(label, dtype=torch.float32),
        )


class FastContrastiveSpatialDataset(Dataset):
    """
    Vectorized batched version of ``ContrastiveSpatialDataset``.

    Implements ``__getitems__`` (PyTorch ≥2.0 batched fetch) so the
    DataLoader avoids per-item Python overhead and per-item tensor
    allocations. Pre-tensorizes the coordinate array once at construction
    time and uses tensor ops for the random pair generation.

    Statistically equivalent to ``ContrastiveSpatialDataset`` (same
    Bernoulli(0.5) positive/negative ratio, same Gaussian noise scale, same
    uniform negative sampling) but the per-batch sample sequence differs
    because the random calls are vectorized rather than per-item.

    Args:
        coords: ``np.ndarray`` of shape ``[N, 2]`` with ``(latitude, longitude)``
            in degrees.
        pos_radius: Standard deviation (in degrees) of the Gaussian noise applied
            to generate positive pairs.
    """

    def __init__(self, coords: np.ndarray, pos_radius: float = 0.01):
        # Pre-tensorize once — the per-item version pays this cost on every
        # __getitem__ call.
        self.coords_tensor = torch.from_numpy(np.ascontiguousarray(coords)).float()
        self.num_points = self.coords_tensor.shape[0]
        self.pos_radius = float(pos_radius)

    def __len__(self) -> int:
        return self.num_points

    def __getitem__(
        self, idx: int
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # Single-item path — only used when DataLoader collation falls back
        # to per-item fetch (very rare in practice). Delegates to the batched
        # path with one index.
        ci, cj, lb = self.__getitems__([idx])
        return ci[0], cj[0], lb[0]

    def __getitems__(
        self, indices: List[int]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        n = len(indices)
        idx_tensor = torch.as_tensor(indices, dtype=torch.long)

        coord_i = self.coords_tensor.index_select(0, idx_tensor)  # [n, 2]

        # Bernoulli(0.5) for positive vs negative — uses global numpy RNG
        # to match ContrastiveSpatialDataset's seeding convention.
        is_positive = np.random.random(n) > 0.5  # [n] bool

        # Positive pairs: coord_i + Gaussian noise
        noise = np.random.normal(0.0, self.pos_radius, size=(n, 2)).astype(np.float32)
        coord_j_pos = coord_i + torch.from_numpy(noise)

        # Negative pairs: random other coord (uniform with replacement)
        rand_idx = np.random.randint(0, self.num_points, size=n)
        coord_j_neg = self.coords_tensor.index_select(0, torch.as_tensor(rand_idx, dtype=torch.long))

        # Branchless select per row
        is_pos_t = torch.from_numpy(is_positive)  # [n] bool
        coord_j = torch.where(is_pos_t.unsqueeze(1), coord_j_pos, coord_j_neg)
        labels = is_pos_t.float()

        return coord_i, coord_j, labels
