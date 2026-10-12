"""Layer 1 — raw check-ins to a per-visit representation.

    corpus.py    parquet -> sorted, encoded check-in table
    graph.py     consecutive-visit edges + the forward-only causality filter
    features.py  canonical 11 node features + v18's 4 elapsed-time columns

Nothing in `train/` imports this package. The two layers meet at a directory on disk described by a
manifest — see docs/ARCHITECTURE.md §1.1.
"""

from . import corpus, features, graph

__all__ = ["corpus", "graph", "features"]
