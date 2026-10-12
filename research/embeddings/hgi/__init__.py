"""HGI (Hierarchical Graph Infomax) embedding module."""

from embeddings.hgi.hgi import create_embedding, run_pipeline, train_hgi
from embeddings.hgi.preprocess import preprocess_hgi, HGIPreprocess
from embeddings.hgi.poi2vec import POI2Vec, train_poi2vec
from embeddings.hgi.model import (
    HierarchicalGraphInfomax,
    POIEncoder,
    POI2Region,
    PMA,
    MAB,
    SAB,
    corruption,
)

__all__ = [
    # Main entry point
    "create_embedding",
    "run_pipeline",  # Backwards compatibility alias
    "train_hgi",
    # Preprocessing
    "preprocess_hgi",
    "HGIPreprocess",
    # POI2Vec
    "POI2Vec",
    "train_poi2vec",
    # Model components
    "HierarchicalGraphInfomax",
    "POIEncoder",
    "POI2Region",
    "PMA",
    "MAB",
    "SAB",
    "corruption",
]
