"""READERS for the two place-level spatial priors: POI2Vec and Delaunay edges.

⚠ This file used to open by calling these "the two artifacts the substrate cannot produce", from
the HGI engine, and calling that the reason mtlcheck was not self-contained. **That has not been
true since 2026-08-19.** `substrate/delaunay.py` and `substrate/poi2vec.py` build both from the
corpus, and `pipeline._scaffolding` calls them by default.

What lives here is only the FORMAT: `pois.csv` + `edges.csv` and the POI2Vec table. The functions
are agnostic about who wrote them — `delaunay.build()` moments ago into `<substrate>/temp/`, or the
old HGI engine years ago when `--delaunay-places`/`--poi2vec` point at banked files. That is the
whole point of routing both routes through one reader: the reproduction path and the from-scratch
path cannot drift.

Both are place-level spatial priors held FIXED across every arm of the study — they are not
per-fold, not per-seed, and not rebuilt when users are held out. That is a deliberate scope limit
inherited from the reference, and it means a fully inductive rebuild is still an open channel.

The reference loads both with a Python loop over every row and a dict lookup per edge (Alabama:
~70 k iterations; California: millions). Here the remap is a lookup array, which is the same function
of the same inputs and is verified against the reference's own output.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd
import torch

logger = logging.getLogger(__name__)

POI2VEC_DIM = 64


def _place_lookup(placeid_to_idx: dict, size_hint: int) -> tuple[np.ndarray, int]:
    """Turn the placeid → index dict into an array indexed by placeid. -1 marks unmapped."""
    keys = np.fromiter((int(k) for k in placeid_to_idx), dtype=np.int64, count=len(placeid_to_idx))
    values = np.fromiter((int(v) for v in placeid_to_idx.values()), dtype=np.int64,
                         count=len(placeid_to_idx))
    lookup = np.full(int(keys.max()) + 1 if len(keys) else 1, -1, dtype=np.int64)
    lookup[keys] = values
    return lookup, size_hint


def load_poi2vec(path: Path, num_places: int, placeid_to_idx: dict) -> torch.Tensor:
    """The frozen 64-d POI2Vec table, in the substrate's place-index space.

    Places absent from POI2Vec stay at zero — they are then pulled toward zero by the anchor term,
    which is worth knowing when reading the anchor loss on a state with poor coverage.
    """
    table = pd.read_csv(path)
    lookup, _ = _place_lookup(placeid_to_idx, num_places)

    placeids = table["placeid"].to_numpy(dtype=np.int64)
    # The lower bound matters: np.clip maps a negative id onto index 0, so without it a corrupt id
    # silently adopts whichever place happens to sit first in the table.
    within = (placeids >= 0) & (placeids < len(lookup))
    target = np.where(within, lookup[np.clip(placeids, 0, len(lookup) - 1)], -1)
    keep = target >= 0

    vectors = table[[str(i) for i in range(POI2VEC_DIM)]].to_numpy(dtype=np.float32)
    out = np.zeros((num_places, POI2VEC_DIM), dtype=np.float32)
    out[target[keep]] = vectors[keep]

    missing = num_places - int(keep.sum())
    if missing > 0:
        logger.warning("poi2vec: %d of %d places absent from the table, left at zero",
                       missing, num_places)
    return torch.from_numpy(out)


def load_delaunay(pois_path: Path, edges_path: Path, num_places: int,
                  placeid_to_idx: dict) -> tuple[torch.Tensor, torch.Tensor]:
    """HGI's Delaunay place graph, remapped and symmetrised.

    HGI's `edges.csv` names its endpoints by ROW NUMBER in its own `pois.csv`, not by placeid — so
    the remap is two hops: row → placeid → substrate index. An edge whose endpoint is not in the
    substrate's inventory is dropped.
    """
    hgi_places = pd.read_csv(pois_path)
    edges = pd.read_csv(edges_path)

    lookup, _ = _place_lookup(placeid_to_idx, num_places)
    row_placeids = hgi_places["placeid"].to_numpy(dtype=np.int64)
    row_to_index = np.where((row_placeids >= 0) & (row_placeids < len(lookup)),
                            lookup[np.clip(row_placeids, 0, len(lookup) - 1)], -1)

    src = row_to_index[edges["source"].to_numpy(dtype=np.int64)]
    dst = row_to_index[edges["target"].to_numpy(dtype=np.int64)]
    weight = edges["weight"].to_numpy(dtype=np.float32)

    keep = (src >= 0) & (dst >= 0)
    dropped = int((~keep).sum())
    src, dst, weight = src[keep], dst[keep], weight[keep]

    # Interleaved (a→b, b→a), which is the order the reference's append-append loop produces.
    edge_index = torch.from_numpy(
        np.stack([np.stack([src, dst]).T.reshape(-1), np.stack([dst, src]).T.reshape(-1)]))
    edge_weight = torch.from_numpy(np.repeat(weight, 2))

    logger.info("delaunay: %d edges (%d dropped as unmapped, from %d raw)",
                edge_index.shape[1], dropped, len(edges))
    return edge_index.long(), edge_weight.float()


def category_aggregate(node_features: np.ndarray, checkin_to_poi: np.ndarray,
                       num_places: int, target_dim: int) -> torch.Tensor:
    """Each place's mean over the FIRST `target_dim` node-feature columns — the masked-place target.

    A function of the encoder's own input, which is what makes the auxiliary add structure rather
    than information: the decoder must predict from neighbours something already present in `x`.

    ⚠ **`target_dim` is 8, and the eighth column is not a category.** The reference slices
    `len(CATEGORIES_MAP)` columns, and that map carries eight entries — seven real categories plus a
    sentinel `None` no corpus uses — while the feature matrix is `7 one-hot + hour_sin + hour_cos +
    ...`. So column 7 of the target is each place's mean **hour_sin**.

    This function took `num_categories` and produced a 7-column target, which is the INTENDED
    quantity and the wrong one: both banked substrates were built with 8, so a rebuild here was
    silently optimising a different objective than the artifact it would replace. Measured at
    Alabama, the two targets have mean cosine 0.8785 (5th pct 0.7193) — and the loss is a scaled
    cosine error, so that is a real difference, not rounding.

    The name of the parameter says what it is now: a width, not a category count.
    """
    if target_dim > node_features.shape[1]:
        raise ValueError(f"target_dim {target_dim} exceeds the {node_features.shape[1]} feature "
                         f"columns available")
    totals = np.zeros((num_places, target_dim), dtype=np.float32)
    counts = np.zeros(num_places, dtype=np.float32)
    np.add.at(totals, checkin_to_poi, node_features[:, :target_dim].astype(np.float32))
    np.add.at(counts, checkin_to_poi, 1.0)
    return torch.from_numpy(totals / np.clip(counts, 1.0, None)[:, None])


__all__ = ["load_poi2vec", "load_delaunay", "category_aggregate", "POI2VEC_DIM"]
