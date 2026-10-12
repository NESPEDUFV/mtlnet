"""Layer 2 — substrate + check-ins to tensors and folds.

    sequences.py  check-in histories -> fixed-width prediction windows
    splits.py     the user-disjoint, category-stratified 5-fold split
    tensors.py    windows -> the two towers' input tensors
    loaders.py    device-resident batching, incl. the cross-task pairing invariant
    dataset.py    assembly: substrate files -> per-fold streams

Reads the substrate through files on disk; does not import `mtlcheck.substrate`.
"""

from . import dataset, loaders, sequences, splits, tensors

__all__ = ["sequences", "splits", "tensors", "loaders", "dataset"]
