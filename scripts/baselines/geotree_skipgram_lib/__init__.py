"""GeoTreeSkipGram — geographically-tree-regularized skip-gram, standalone per-POI 64-d substrate.

⚠ NOT POI2Vec (Feng et al., AAAI 2017) — see model.py for how it differs. The faithful
AAAI'17 POI2Vec is in ``scripts/baselines/poi2vec_lib/``. Also distinct from the in-repo
fclass-level HGI teacher ``research/embeddings/hgi/poi2vec.py`` (a Node2Vec teacher).
"""
from .model import GeoTreeSkipGram, build_geo_binary_tree

__all__ = ["GeoTreeSkipGram", "build_geo_binary_tree"]
