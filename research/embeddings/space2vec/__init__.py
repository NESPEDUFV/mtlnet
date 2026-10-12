"""
Space2Vec: Spatial contrastive learning for location embeddings.

This module provides tools for learning dense location embeddings using
self-supervised contrastive learning on spatial proximity.
"""

from embeddings.space2vec.space2vec import create_embedding
from embeddings.space2vec.model.SpaceEncoder import SpaceContrastiveModel
from embeddings.space2vec.model.dataset import (
    SpatialContrastiveDataset,
    PairsMemmapDataset,
    build_pairs_memmap,
    to_xy_km,
)

__all__ = [
    "create_embedding",
    "SpaceContrastiveModel",
    "SpatialContrastiveDataset",
    "PairsMemmapDataset",
    "build_pairs_memmap",
    "to_xy_km",
]
