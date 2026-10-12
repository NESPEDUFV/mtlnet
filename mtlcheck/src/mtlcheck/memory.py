"""Memory estimation and a guard proportional to what is actually needed.

The reference refuses to load when free memory is below a **fixed 16 GB**, regardless of the dataset:
it correctly estimates that Alabama needs 0.4 GB and refuses anyway, so no machine with less than
16 GB free can run any state. Its message then blames "an oversized stride-1 large-state build",
which is misleading when the data in question wants 0.4 GB.

The fix is not to remove the guard — that trades "refuses when it shouldn't" for "no warning when it
should". It is to make the margin a function of the requirement.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

BYTES_PER_FLOAT32 = 4
# Working headroom beyond the tensors themselves: the parquet reader's buffers, the fold slices, and
# whatever else is resident. Multiplicative because it scales with the data, plus a floor for the
# interpreter and libraries.
OVERHEAD_FACTOR = 1.6
FLOOR_GB = 1.0


def tensor_bytes(n_rows: int, window: int, embed_dim: int, towers: int = 1) -> int:
    """Bytes for `towers` float32 tensors of shape [n_rows, window, embed_dim]."""
    return n_rows * window * embed_dim * BYTES_PER_FLOAT32 * towers


def available_bytes() -> int | None:
    """Free host memory, or None when it cannot be determined."""
    try:
        import psutil
        return int(psutil.virtual_memory().available)
    except Exception:
        return None


def check(required: int, *, where: str, strict: bool = False) -> None:
    """Warn — or refuse, under `strict` — when the requirement does not fit.

    The threshold is `required * OVERHEAD_FACTOR + FLOOR_GB`, so a small dataset asks for a small
    margin. Unknown availability warns once and proceeds: refusing on an unmeasurable condition is
    the reference's failure mode in a different costume.
    """
    available = available_bytes()
    if available is None:
        logger.debug("%s: cannot read available memory; proceeding", where)
        return

    needed = int(required * OVERHEAD_FACTOR + FLOOR_GB * 2**30)
    if available >= needed:
        return

    message = (
        f"{where}: needs about {required / 2**30:.2f} GB of tensors "
        f"({needed / 2**30:.2f} GB with working overhead) and {available / 2**30:.2f} GB is free. "
        f"Expect swapping or an out-of-memory kill."
    )
    if strict:
        raise MemoryError(message)
    logger.warning(message)


__all__ = ["tensor_bytes", "available_bytes", "check", "OVERHEAD_FACTOR", "FLOOR_GB"]
