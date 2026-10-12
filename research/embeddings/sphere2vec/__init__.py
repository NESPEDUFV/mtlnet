"""
Sphere2Vec (sphereM variant): Spherical-RBF location embeddings.

This module provides tools for learning dense location embeddings using
self-supervised contrastive learning over a fixed multi-scale RBF kernel
defined on the unit 3-sphere.

Reference: Mai et al., "Sphere2Vec: A General-Purpose Location Representation
Learning over a Spherical Surface for Large-Scale Geospatial Predictions"
(https://arxiv.org/abs/2306.17624)
"""

from embeddings.sphere2vec.sphere2vec import create_embedding
from embeddings.sphere2vec.model.Sphere2VecModule import (
    SphereLocationContrastiveModel,
    SphereLocationEncoder,
    SphereRBFPositionEncoder,
    SpherePositionEncoder,  # backward-compat alias for SphereRBFPositionEncoder
    SphereMixScalePositionEncoder,
    contrastive_bce,
)
from embeddings.sphere2vec.model.dataset import (
    ContrastiveSpatialDataset,
    FastContrastiveSpatialDataset,
)

__all__ = [
    "create_embedding",
    "SphereLocationContrastiveModel",
    "SphereLocationEncoder",
    "SphereRBFPositionEncoder",
    "SpherePositionEncoder",
    "SphereMixScalePositionEncoder",
    "ContrastiveSpatialDataset",
    "FastContrastiveSpatialDataset",
    "contrastive_bce",
]
