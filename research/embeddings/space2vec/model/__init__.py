"""
Space2Vec model components.

Exports the main model classes and dataset utilities.
"""

from embeddings.space2vec.model.SpaceEncoder import (
    SpaceContrastiveModel,
    GridCellSpatialRelationSpaceEncoder,
    GridCellSpatialRelationPositionEncoder,
    GridCellSpaceEncoderTorch,
    GridCellPositionEncoderTorch,
    SpaceEncoder,
    PositionEncoder,
)
from embeddings.space2vec.model.dataset import (
    SpatialContrastiveDataset,
    PairsMemmapDataset,
    build_pairs_memmap,
    spatial_proximity_pairs_kdtree_fast,
    to_xy_km,
    latlon_to_radians,
    EARTH_RADIUS_KM,
)
from embeddings.space2vec.model.components import (
    MultiLayerFeedForwardNN,
    SingleFeedForwardNN,
    get_activation_function,
    cal_freq_list,
)

__all__ = [
    # Encoders
    "SpaceContrastiveModel",
    "GridCellSpatialRelationSpaceEncoder",
    "GridCellSpatialRelationPositionEncoder",
    "GridCellSpaceEncoderTorch",
    "GridCellPositionEncoderTorch",
    "SpaceEncoder",
    "PositionEncoder",
    # Dataset
    "SpatialContrastiveDataset",
    "PairsMemmapDataset",
    "build_pairs_memmap",
    "spatial_proximity_pairs_kdtree_fast",
    "to_xy_km",
    "latlon_to_radians",
    "EARTH_RADIUS_KM",
    # Components
    "MultiLayerFeedForwardNN",
    "SingleFeedForwardNN",
    "get_activation_function",
    "cal_freq_list",
]
