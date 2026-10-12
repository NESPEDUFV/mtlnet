"""Check-in histories -> fixed-width prediction windows.

One window is nine historical visits plus the tenth as the target. The v18 protocol uses **stride 1
with the tail gate on**: windows start at every position where a full ten-visit run exists inside one
user's history, and no window is emitted once the slide walks off the end.

Two consequences of the gate worth stating, because both are easy to get wrong:

* **No padding is ever produced.** A window exists only where ten real visits do, so the pad value
  never appears at stride 1. The heads' padding logic (`x.abs().sum(-1) == 0`) and the GRU's
  `seq_lengths - 1` idiom both assume padding is strictly trailing; here there is none at all, which
  is why those two idioms agree on this data.
* **`min_sequence_length = 10` is implied, not enforced.** A user with nine or fewer visits cannot
  produce a window regardless. Measured at Alabama: `MIN_SEQ` 5 and 10 both yield exactly 96 326
  windows from 1 101 users. The pin still matters at other strides, so it stays configurable — but
  nobody should read the v18 numbers as depending on it.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

WINDOW = 9
PAD_VALUE = -1


@dataclass(frozen=True)
class Windows:
    """`history` is [N, 9] place ids, `target` is [N], `userid` is [N].

    `start` is the row of the source frame each window opens on, which is what lets a check-in-level
    embedding matrix be sliced into the same windows without re-deriving them.
    """

    history: np.ndarray
    target: np.ndarray
    userid: np.ndarray
    start: np.ndarray

    def __len__(self) -> int:
        return len(self.target)

    def to_frame(self) -> pd.DataFrame:
        """The reference on-disk layout: poi_0..poi_8, target_poi, userid."""
        out = {f"poi_{i}": self.history[:, i] for i in range(self.history.shape[1])}
        out["target_poi"] = self.target
        out["userid"] = self.userid
        return pd.DataFrame(out)


def build(frame: pd.DataFrame, *, window: int = WINDOW, stride: int = 1,
          min_sequence_length: int = 10, emit_tail: bool = False,
          place_column: str = "placeid") -> Windows:
    """Windows over a `(userid, datetime)`-sorted check-in frame.

    Vectorised. Because the frame is sorted, a window starting at row `i` lies entirely inside one
    user's history exactly when `userid[i] == userid[i + window]` — so the whole valid-start set is
    one comparison, and the windows themselves are a strided view. The reference implementation
    looped over users in Python and appended lists.
    """
    if emit_tail:
        raise NotImplementedError(
            "tail windows are not part of the v18 protocol. At stride 1 each user emits ~window of "
            "them, all targeting the SAME last visit on near-all-padding histories, which "
            "over-weights that target and injects trivial low-context rows."
        )
    if stride != 1:
        raise NotImplementedError("only stride 1 is used by v18; other strides need the tail rules")

    users = frame["userid"].to_numpy()
    places = frame[place_column].to_numpy()
    n = len(frame)
    span = window + 1                      # nine of history plus the target

    if n < span:
        empty_i = np.zeros((0, window), dtype=places.dtype)
        return Windows(empty_i, np.zeros(0, dtype=places.dtype), np.zeros(0, dtype=users.dtype),
                       np.zeros(0, dtype=np.int64))

    # A start is valid when the row `window` positions later still belongs to the same user; the
    # sort guarantees everything between them does too.
    valid = np.flatnonzero(users[: n - window] == users[window:])

    if min_sequence_length > span:
        # Only meaningful above the span the gate already requires. Drop users whose whole history
        # is shorter than the pin, rather than trimming their windows.
        sizes = frame.groupby("userid", sort=False).size()
        too_short = set(sizes.index[sizes < min_sequence_length])
        if too_short:
            valid = valid[~np.isin(users[valid], list(too_short))]

    strided = np.lib.stride_tricks.sliding_window_view(places, span)[valid]
    history = np.ascontiguousarray(strided[:, :window])
    target = np.ascontiguousarray(strided[:, window])

    logger.info("windows: %d from %d users (stride %d, gated tail)",
                len(target), len(np.unique(users[valid])), stride)
    return Windows(history=history, target=target, userid=users[valid],
                   start=valid.astype(np.int64))


def build_from(frame: pd.DataFrame, config) -> Windows:
    """Windows under a `DataConfig`. **Prefer this to `build`.**

    `build` takes loose keyword defaults, so a caller that forgot to pass the config got v18's shape
    by luck rather than by contract — which is how `min_sequence_length` and `stride` sat in
    `DataConfig` unread while every call site used the defaults. Same defect class as the decorative
    `repr_seed`, found one commit later by the round-2 audit.
    """
    return build(frame, window=config.window, stride=config.stride,
                 min_sequence_length=config.min_sequence_length)


__all__ = ["Windows", "build", "build_from", "WINDOW", "PAD_VALUE"]
