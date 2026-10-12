"""The check-in graph: consecutive visits by the same user, and the causality filter.

This module owns the single change that defines v18.

The canonical preprocessor emits BOTH directions of every consecutive-visit edge. A visit's
representation is therefore convolved over a neighbourhood containing the visit that came *after*
it — so the category head reads a feature of the very target it is asked to predict. Measured at
Alabama on the reported dedicated model, that is worth **28.63 macro-F1 points** (28.23 honest vs
56.86 leaked).

Keeping only ``src < tgt`` removes it. That test is valid because `corpus.load` sorted check-ins into
``(userid, datetime)`` order, so a node's id IS its position in its user's history.

What this does NOT make causal, so that nobody over-reads it: the pretext training signal still sees
the future through other routes (POI pooling aggregates a place's future visits, the reconstruction
target is a corpus-wide category distribution, edge-weight normalisation is fit on the whole corpus),
and the region tower consumes fully bidirectional embeddings from a separate substrate.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .corpus import Corpus, user_boundaries

logger = logging.getLogger(__name__)

# Exponential decay applied to the seconds between consecutive visits: w = exp(-gap / decay).
#
# 3600, not 86400. Verified against the frozen graph the v18 substrate was built from
# (`output/check2hgi/alabama/temp/checkin_graph.pt`): at 3600 the weights match to 6e-8; at 86400
# they diverge by up to 0.835. The corroborating detail is that 46.8% of Alabama's edges fall below
# weight 0.01 — a figure the reference cites about its own graph, and one that is arithmetically
# impossible under a 24-hour decay.
TEMPORAL_DECAY_SECONDS = 3600.0


@dataclass(frozen=True)
class CheckinGraph:
    """A check-in graph. `edge_index` is [2, E]; `edge_weight` is [E]."""

    edge_index: np.ndarray
    edge_weight: np.ndarray
    n_nodes: int
    forward_only: bool
    edges_before_filter: int

    @property
    def n_edges(self) -> int:
        return int(self.edge_index.shape[1])

    @property
    def dropped_backward(self) -> int:
        return self.edges_before_filter - self.n_edges


def build(corpus: Corpus, *, forward_only: bool = True,
          temporal_decay: float = TEMPORAL_DECAY_SECONDS) -> CheckinGraph:
    """Build the consecutive-visit graph.

    Vectorised: consecutive visits by one user are adjacent rows, so the whole edge set is one
    boolean mask over `arange(n-1)`. The reference implementation looped over `groupby('userid')`
    in Python and appended to two lists.
    """
    frame = corpus.frame
    n = len(frame)
    if n < 2:
        empty = np.zeros((2, 0), dtype=np.int64)
        return CheckinGraph(empty, np.zeros(0, dtype=np.float32), n, forward_only, 0)

    same_user = user_boundaries(frame)
    src = np.flatnonzero(same_user)          # row i, where i and i+1 share a user
    tgt = src + 1

    seconds = frame["datetime"].to_numpy(dtype="datetime64[s]").astype(np.int64)
    gap = (seconds[tgt] - seconds[src]).astype(np.float64)
    weight = np.exp(-gap / temporal_decay).astype(np.float32)

    n_forward = len(src)
    if forward_only:
        edge_index = np.stack([src, tgt]).astype(np.int64)
        edge_weight = weight
        edges_before = n_forward * 2         # what the bidirectional build would have produced
    else:
        edge_index = np.stack([
            np.concatenate([src, tgt]),
            np.concatenate([tgt, src]),
        ]).astype(np.int64)
        edge_weight = np.concatenate([weight, weight])
        edges_before = n_forward * 2

    edge_weight = _normalize(edge_weight)

    logger.info(
        "graph: %d nodes · %d edges (%s)%s",
        n, edge_index.shape[1], "forward-only" if forward_only else "bidirectional",
        f" · dropped {edges_before - edge_index.shape[1]} backward" if forward_only else "",
    )
    return CheckinGraph(
        edge_index=edge_index,
        edge_weight=edge_weight,
        n_nodes=n,
        forward_only=forward_only,
        edges_before_filter=edges_before,
    )


def _normalize(weight: np.ndarray) -> np.ndarray:
    """Min-max the edge weights to [0, 1].

    Fit on the whole corpus, which is what the reference does. Recorded rather than fixed: it is one
    of the routes by which the pretext objective still sees information from outside a given visit's
    past, and changing it would move every number.
    """
    if weight.size == 0:
        return weight
    lo, hi = float(weight.min()), float(weight.max())
    return (weight - lo) / (hi - lo) if hi > lo else weight


def forward_only_filter(edge_index: np.ndarray, edge_weight: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Drop backward edges from an existing bidirectional graph.

    Kept as a standalone function because it is the operation the reference applies to a graph it
    built bidirectionally, and the equivalence test compares against exactly that path.
    """
    keep = edge_index[0] < edge_index[1]
    return edge_index[:, keep], edge_weight[keep]


def expected_forward_edges(frame: pd.DataFrame) -> int:
    """How many forward edges a corpus should yield — derivable without building the graph.

    `n_checkins - n_users_with_at_least_two_visits`. Users with a single check-in are still nodes;
    they simply have no consecutive pair. Alabama: 113 846 - 1 088 singleton visits - 2 770 users
    with >= 2 = 109 988, which is the audited count exactly.
    """
    sizes = frame.groupby("userid").size()
    return int((sizes[sizes >= 2] - 1).sum())


__all__ = ["CheckinGraph", "build", "forward_only_filter", "expected_forward_edges",
           "TEMPORAL_DECAY_SECONDS"]
