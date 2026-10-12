"""Identifier coercion — one function, because the same defect appeared three times.

The reference artifacts do not agree with themselves about how identifiers are stored. Measured,
all three within one state's files:

| identifier | `next.parquet` | `sequences_next.parquet` | `checkin_graph.pt` |
|---|---|---|---|
| `userid`   | **string**     | int64                    | —                  |
| `placeid`  | —              | **string**               | int keys           |

Same values, different types. Every one of these is a silent failure mode rather than a loud one:

* Grouping the CV split on string user ids sorts them lexicographically ('10' before '2'), so the
  group-aware splitter visits users in a different order and produces a perfectly valid split that
  is not THE split — all four reporting seeds diverged from the reference at fold 1.
* Looking up string place ids in an int-keyed map misses **every** row, which at least fails loudly —
  but the mirror case (int ids against a string-keyed map) fails the same way, and a `.get(pid, 0)`
  anywhere along that path would have turned it into "every visit is in region 0".

The reference defends against the first with an uncommented `.astype(int)` inside a loader. There is
no defence against the second; the code that needs it happens to receive the right type today.

So: identifiers cross every boundary through this function, and the boundary says which identifier it
is, so a failure names the column instead of producing a stack trace about dtypes.
"""

from __future__ import annotations

import logging

import numpy as np

logger = logging.getLogger(__name__)


def as_int64(values, *, name: str) -> np.ndarray:
    """Coerce an identifier column to int64, whatever the artifact chose to store it as."""
    arr = np.asarray(values)
    if arr.dtype == np.int64:
        return arr
    if arr.dtype.kind in "iu":
        return arr.astype(np.int64)
    if arr.dtype.kind in "US" or arr.dtype == object:
        try:
            out = arr.astype(np.int64)
        except (TypeError, ValueError) as exc:
            raise TypeError(
                f"identifier {name!r} is stored as {arr.dtype} and does not convert to int: {exc}"
            ) from exc
        logger.debug("identifier %r arrived as %s; coerced to int64", name, arr.dtype)
        return out
    if arr.dtype.kind == "f":
        # A float id means something upstream introduced NaN — usually a failed join. Refuse, rather
        # than truncate a NaN into a valid-looking index.
        if not np.isfinite(arr).all():
            raise ValueError(f"identifier {name!r} contains non-finite values (a failed join?)")
        rounded = arr.astype(np.int64)
        if not np.array_equal(rounded.astype(arr.dtype), arr):
            raise ValueError(f"identifier {name!r} is float and not integral")
        return rounded
    raise TypeError(f"identifier {name!r} has unsupported dtype {arr.dtype}")


def as_int_keys(mapping: dict, *, name: str) -> dict[int, int]:
    """Same, for the key side of a lookup dict."""
    if not mapping:
        return {}
    sample = next(iter(mapping))
    if isinstance(sample, (int, np.integer)):
        return mapping
    logger.debug("map %r has %s keys; coercing to int", name, type(sample).__name__)
    return {int(k): v for k, v in mapping.items()}


__all__ = ["as_int64", "as_int_keys"]
