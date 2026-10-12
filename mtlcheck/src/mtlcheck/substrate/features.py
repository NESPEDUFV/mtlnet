"""Node features: the canonical eleven, plus v18's four elapsed-time columns.

Layout, in order, giving ``in_channels = 15``:

    [0 .. C-1]   category one-hot            (C = 7 on Gowalla)
    [C .. C+3]   hour sin/cos, weekday sin/cos
    [C+4 .. C+7] elapsed time                (v18)

Everything in the elapsed-time block is measured **up to the visit itself**. The gap to the *target*
is never a feature — that would reintroduce the leak the forward-only graph exists to remove, in a
new form.

Why only elapsed time was added. Measured at Alabama against the forward-only baseline of 27.5127,
every other candidate hurt: place identity projected to 8 dims -0.41, standardized full 64 -1.74,
raw 64 -1.86, region identity projected to 8 -0.55; elapsed time +0.83, the only gain. The working
explanation is that the pretext discriminator's negatives are row-permuted node features, so any
block the graph can already anticipate from a neighbourhood becomes a shortcut — "real or shuffled?"
becomes answerable from that block alone, the pretext loss collapses, and downstream accuracy falls.
Elapsed time is the one tested feature barely above chance in neighbourhood predictability.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

from .corpus import Corpus, user_boundaries

logger = logging.getLogger(__name__)

SECONDS_PER_HOUR = 3600.0


@dataclass(frozen=True)
class NodeFeatures:
    matrix: np.ndarray            # [n, in_channels] float32
    layout: tuple[str, ...]       # block names, in order
    columns: tuple[str, ...]      # per-column names, for the manifest

    @property
    def in_channels(self) -> int:
        return int(self.matrix.shape[1])


def build(corpus: Corpus, *, continuous_time: bool = True) -> NodeFeatures:
    blocks = [_category_onehot(corpus), _cyclical_time(corpus)]
    layout = ["canonical_11"]
    columns = [f"category_{name}" for name in corpus.category_vocab]
    columns += ["hour_sin", "hour_cos", "dow_sin", "dow_cos"]

    if continuous_time:
        blocks.append(_elapsed_time(corpus))
        layout.append("continuous_time_4")
        columns += ["log1p_gap_hours/10", "log1p_since_first_hours/10",
                    "gap_clipped_24h/24", "gap_is_zero"]

    matrix = np.concatenate(blocks, axis=1).astype(np.float32)

    # A requested block that contributes zero columns is a silent no-op: the arm builds, trains and
    # scores, and is indistinguishable from its own baseline. That happened once in the reference
    # study and produced two void arms whose numbers were briefly read as a confirmation.
    for block, name in zip(blocks, layout):
        if block.shape[1] == 0:
            raise ValueError(f"feature block {name!r} contributed 0 columns")
    if matrix.shape[1] != len(columns):
        raise ValueError(f"layout says {len(columns)} columns, matrix has {matrix.shape[1]}")

    logger.info("node features: %d channels (%s)", matrix.shape[1], " + ".join(layout))
    return NodeFeatures(matrix=matrix, layout=tuple(layout), columns=tuple(columns))


def _category_onehot(corpus: Corpus) -> np.ndarray:
    out = np.zeros((corpus.n_checkins, corpus.n_categories), dtype=np.float32)
    out[np.arange(corpus.n_checkins), corpus.category_codes] = 1.0
    return out


def _cyclical_time(corpus: Corpus) -> np.ndarray:
    dt = corpus.frame["datetime"]
    hour = dt.dt.hour.to_numpy()
    dow = dt.dt.dayofweek.to_numpy()
    out = np.empty((len(dt), 4), dtype=np.float32)
    out[:, 0] = np.sin(2 * np.pi * hour / 24)
    out[:, 1] = np.cos(2 * np.pi * hour / 24)
    out[:, 2] = np.sin(2 * np.pi * dow / 7)
    out[:, 3] = np.cos(2 * np.pi * dow / 7)
    return out


def _elapsed_time(corpus: Corpus) -> np.ndarray:
    """The four v18 columns, vectorised over the sorted layout.

    The reference loops `for u in np.unique(userid)` with a `np.where` per user, which is O(U·N).
    Rows are already grouped and time-ordered, so the same values fall out of one diff plus one
    scatter of each user's first timestamp.
    """
    frame = corpus.frame
    n = len(frame)
    hours = frame["datetime"].to_numpy(dtype="datetime64[s]").astype(np.int64) / SECONDS_PER_HOUR

    same_user = user_boundaries(frame)             # [n-1]
    gap = np.zeros(n, dtype=np.float32)
    if n > 1:
        # Row i's gap is measured against row i-1 when they share a user; the first visit of every
        # user keeps 0.0.
        diffs = np.diff(hours)
        gap[1:] = np.where(same_user, diffs, 0.0)

    # Time since each user's first visit: broadcast the first timestamp of each run of equal users.
    starts = np.flatnonzero(np.concatenate(([True], ~same_user)))   # first row of each user
    run_id = np.zeros(n, dtype=np.int64)
    run_id[starts[1:]] = 1
    run_id = np.cumsum(run_id)
    since_first = (hours - hours[starts][run_id]).astype(np.float32)

    out = np.empty((n, 4), dtype=np.float32)
    out[:, 0] = np.log1p(np.clip(gap, 0, None)) / 10.0
    out[:, 1] = np.log1p(np.clip(since_first, 0, None)) / 10.0
    out[:, 2] = np.clip(gap, 0, 24.0) / 24.0
    # The reference build metadata names this column "is_first_visit", but the code computes
    # `gap == 0`, so simultaneous timestamps get 1.0 too — and the order among tied timestamps is
    # not stable. Reproduce the behaviour; the manifest records the honest name.
    out[:, 3] = (gap == 0).astype(np.float32)
    return out


__all__ = ["NodeFeatures", "build"]
