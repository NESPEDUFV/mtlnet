"""Check-in embeddings + corpus -> the two input tables the training layer reads.

This is the seam between layer 1 and layer 2, and it is deliberately a **file on disk** rather than a
function call: a substrate is built once and read by dozens of cells, so the contract between them is
an artifact with a schema, not an import.

## The 576 columns

`next.parquet` is the nine history positions of a window, each a 64-dim check-in vector, flattened
position-major into columns `"0"`..`"575"`. Position-major, not dimension-major — column `j` belongs
to position `j // 64`. Getting that backwards scrambles every input while every shape stays valid,
which is why `tests/equivalence/test_assembly.py` asserts the layout against the raw columns rather
than trusting it.

## One divergence, deliberate

The reference copies all 576 embedding columns into `next_region.parquet` as well, and its own
docstring calls them "VESTIGIAL at MTL train time" — the region task reads the region-embedding
tower, not these. They exist so the two files share a schema. That is ~200 MB per state of duplicated
float for a column nobody reads; the reader here selects by name and needs four columns from that
file. So the region table is written without them.

A reader that selects by name is unaffected either way, and an old file still loads. What breaks is a
reader that assumes the two files are column-identical — of which there are none here.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from .sequences import PAD_VALUE, WINDOW, Windows

logger = logging.getLogger(__name__)


def next_table(windows: Windows, checkin_embeddings: np.ndarray,
               categories: np.ndarray) -> pd.DataFrame:
    """`next.parquet`: 576 embedding columns, `userid`, `next_category`.

    `checkin_embeddings` is [n_checkins, 64] in corpus row order, so a window's nine positions are
    rows `start .. start + 8` — no join, just a strided gather.
    """
    n, dim = len(windows.target), checkin_embeddings.shape[1]
    offsets = windows.start[:, None] + np.arange(WINDOW)[None, :]
    flat = checkin_embeddings[offsets].reshape(n, WINDOW * dim)

    frame = pd.DataFrame(flat, columns=[str(i) for i in range(WINDOW * dim)])
    frame["userid"] = windows.userid.astype(str)
    frame["next_category"] = categories[windows.start + WINDOW]
    logger.info("next table: %d rows x %d embedding columns", n, WINDOW * dim)
    return frame


def next_region_table(windows: Windows, categories: np.ndarray,
                      place_to_index: dict, poi_to_region: np.ndarray) -> tuple[pd.DataFrame, int]:
    """`next_region.parquet`: the region label, the last observed region, and the keys to align on.

    `last_region_idx` is the region of the ninth history visit. The reference derives it as "the last
    non-pad position", carrying a -1 sentinel for all-pad rows — but at stride 1 with the tail gate
    **no window contains padding at all**, so the sentinel is unreachable. It is asserted rather than
    assumed: a -1 here would mean the window builder changed under this code.
    """
    # Assert the no-padding property directly. It is what licenses reading the last history slot as
    # "the last observed place"; relying on the dict lookup two functions down to miss on -1 works,
    # but reports it as an unmapped place id, which sends the reader to the spatial join instead of
    # to the window builder.
    if (windows.history == PAD_VALUE).any():
        raise ValueError(
            f"{int((windows.history == PAD_VALUE).sum())} padded slots in the windows: the last "
            "history position is not necessarily the last observed place, so last_region_idx needs "
            "the reference's last-non-pad rule and a -1 sentinel")

    target_index = _to_index(windows.target, place_to_index, "target")
    region_idx = poi_to_region[target_index]

    last_index = _to_index(windows.history[:, -1], place_to_index, "last history position")
    last_region_idx = poi_to_region[last_index]

    if (region_idx < 0).any() or (last_region_idx < 0).any():
        raise ValueError("a place resolved to no region; the spatial join and the corpus disagree")

    frame = pd.DataFrame({
        "next_category": categories[windows.start + WINDOW],
        "userid": windows.userid.astype(str),
        "region_idx": region_idx.astype(np.int64),
        "last_region_idx": last_region_idx.astype(np.int64),
    })
    n_regions = int(poi_to_region.max()) + 1
    logger.info("next_region table: %d rows · %d regions", len(frame), n_regions)
    return frame, n_regions


def _to_index(placeids: np.ndarray, place_to_index: dict, where: str) -> np.ndarray:
    """Map raw place ids to substrate place indices, failing loudly on anything unmapped.

    The window builder works in raw place ids and the substrate works in dense indices; a place the
    spatial join dropped is present in one and absent from the other. Silently dropping those rows
    would change the row count and break the alignment the whole layer depends on.
    """
    lookup = pd.Series(place_to_index)
    mapped = pd.Series(placeids.astype(np.int64)).map(lookup)
    missing = int(mapped.isna().sum())
    if missing:
        sample = placeids[mapped.isna().to_numpy()][:5].tolist()
        raise ValueError(f"{missing} place ids at the {where} are not in the substrate index "
                         f"(sample: {sample})")
    return mapped.to_numpy(dtype=np.int64)


def sequences_table(windows: Windows) -> pd.DataFrame:
    """`temp/sequences_next.parquet`: the windows in place ids, kept as the alignment witness.

    Nothing trains on this. It exists so a later reader can prove that a row of `next.parquet`
    describes the window it thinks it does, which is the check that caught the userid dtype trap.
    """
    frame = windows.to_frame()
    frame["userid"] = windows.userid.astype(np.int64)
    return frame


__all__ = ["next_table", "next_region_table", "sequences_table"]
