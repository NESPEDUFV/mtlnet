"""Faithful POI2Vec (Feng et al., AAAI 2017; ref github.com/yongqyu/POI2Vec).

FIXED recursive rectangular midpoint tree + overlap-area phi + CBOW + hierarchical
softmax + negative-sampled user term. Per-POI 64-d substrate column for the matched
champion heads (built leak-safe per (state,seed,fold) by
``scripts/baselines/build_poi2vec_substrate.py``).

NOT the geotree_skipgram baseline (``scripts/baselines/geotree_skipgram_lib/``), which
gets all four of POI2Vec's defining mechanisms wrong. See model.py + README_poi2vec.md.
"""
from .model import (
    MidpointGeoTree,
    POI2VecAAAI,
    build_midpoint_tree,
    build_poi_routes,
)

__all__ = [
    "MidpointGeoTree",
    "POI2VecAAAI",
    "build_midpoint_tree",
    "build_poi_routes",
]
