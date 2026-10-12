"""Raw corpus -> the check-in table every later step indexes into.

The ordering established here is load-bearing far downstream. Check-ins are sorted by
``(userid, datetime)`` and re-indexed from zero, which makes a node's id its position in its user's
visit sequence. That is what licenses the forward-only edge filter to be the two-character test
``src < tgt`` (recorded as structural fact F1 in the reference study). Change the sort and the
causality fix becomes wrong without any error being raised.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .. import paths

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = ("userid", "placeid", "datetime", "category", "latitude", "longitude")

#: The OSM fine-grained venue class. NOT required — the check-in substrate never reads it — but the
#: Delaunay/POI2Vec scaffolding does, and it is the ONLY source of `fclass`. Left out of the required
#: list, this column was silently absent and the Delaunay builder substituted `category` for it:
#: 7 symbols where the reference has 284, which is the entire vocabulary of the POI2Vec code book.
OPTIONAL_COLUMNS = ("spot",)


@dataclass(frozen=True)
class Corpus:
    """A state's check-ins, sorted and encoded.

    `frame` is indexed 0..n-1 in visit order. `category_codes` and `category_vocab` come from a
    corpus-fit encoder — note that the reference build metadata claims these codes come from a fixed
    `CATEGORIES_MAP`, which is not what the code does. Reproduce the behaviour, not the label.
    """

    frame: pd.DataFrame
    category_codes: np.ndarray      # [n] int64
    category_vocab: tuple[str, ...]

    @property
    def has_fclass(self) -> bool:
        """Whether the corpus carries the OSM venue class the spatial scaffolding needs."""
        return "spot" in self.frame.columns

    @property
    def n_checkins(self) -> int:
        return len(self.frame)

    @property
    def n_users(self) -> int:
        return int(self.frame["userid"].nunique())

    @property
    def n_places(self) -> int:
        return int(self.frame["placeid"].nunique())

    @property
    def n_categories(self) -> int:
        return len(self.category_vocab)


def load(state: str, *, path=None) -> Corpus:
    """Load one state's check-ins, sorted into visit order and category-encoded."""
    source = path or paths.state_checkins(state)
    available = set(pd.read_parquet(source, columns=[]).columns) or set(
        __import__("pyarrow.parquet", fromlist=["parquet"]).ParquetFile(source).schema.names)
    wanted = list(REQUIRED_COLUMNS) + [c for c in OPTIONAL_COLUMNS if c in available]
    frame = pd.read_parquet(source, columns=wanted)

    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns: {missing}")

    frame = frame.sort_values(["userid", "datetime"], kind="stable").reset_index(drop=True)

    # A corpus-fit encoder over the sorted, filled category column. `sort=True` (pandas default for
    # `factorize` is False, so this is explicit) keeps the code assignment a pure function of the
    # category *names*, not of their order of appearance — otherwise two states, or the same state
    # after a row-order change, would silently disagree about which integer means "Food".
    filled = frame["category"].fillna("Unknown")
    vocab = tuple(sorted(filled.unique()))
    lookup = {name: i for i, name in enumerate(vocab)}
    codes = filled.map(lookup).to_numpy(dtype=np.int64)

    logger.info(
        "%s: %d check-ins · %d users · %d places · %d categories",
        state, len(frame), frame["userid"].nunique(), frame["placeid"].nunique(), len(vocab),
    )
    return Corpus(frame=frame, category_codes=codes, category_vocab=vocab)


def user_boundaries(frame: pd.DataFrame) -> np.ndarray:
    """Boolean mask, length n-1: True where row i and row i+1 belong to the SAME user.

    The one primitive the sorted layout buys us. Consecutive-visit edges, elapsed-time gaps and
    per-user first-visit markers are all expressible through it without a groupby loop — the
    reference implementation iterated `groupby('userid')` in Python for each of the three.
    """
    users = frame["userid"].to_numpy()
    return users[:-1] == users[1:]


__all__ = ["Corpus", "load", "user_boundaries", "REQUIRED_COLUMNS"]
