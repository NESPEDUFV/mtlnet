"""Windows -> the two input tensors the heads consume.

The two task towers read different things, and this is the one place that difference is spelled out:

* **check-in tower** — the substrate's per-visit embedding for each of the nine historical visits.
  It arrives pre-materialised as 576 columns of `next.parquet`, laid out as 9 positions x 64 dims.
* **region tower** — the *region* embedding of the region each historical visit happened in, looked
  up through `place -> region`. Not stored anywhere: it is built here, from the sequences, the
  place/region maps, and a region-embedding table that comes from a **different substrate** than the
  check-in one.

That second tower is where the two substrates meet. In the reference the connection was a filesystem
symlink inside the engine directory; here it is an explicit argument, and the manifest records which
region substrate a run consumed.
"""

from __future__ import annotations

import logging
import pickle
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from .. import ids, memory

logger = logging.getLogger(__name__)

EMBED_DIM = 64
WINDOW = 9
PAD_PLACE = -1


@dataclass(frozen=True)
class PlaceRegionMaps:
    """`place id -> region index`, from the graph the substrate was built on.

    **This does not define the label space.** The reference derives the head's output width from the
    region label COLUMN of the input table — `max(region_idx) + 1` over all rows — not from the
    place/region map. The two coincide only when the highest-indexed region happens to appear as
    some window's target. At Alabama they do (1 109 either way);
    at a state where the top region is never a target they would not, and the head would be wider
    than the reference's, changing its parameter count and every ranking denominator.

    So the map exposes `n_regions_from_map` as a CROSS-CHECK, and `label_space` takes the labels.
    """

    place_to_region: pd.Series      # index: place id, value: region index
    n_regions_from_map: int         # max over ALL places — a cross-check, NOT the label space

    @classmethod
    def from_parquet(cls, directory: str | Path) -> "PlaceRegionMaps":
        """The same maps, from a substrate this package built.

        `from_graph` unpickles an artifact the OLD engine wrote, which meant a substrate built
        entirely by `mtlcheck check2hgi build` still could not feed its own region tower. The two
        parquets `export.py` already writes carry exactly the same information — this reads them.

        Four checks that dict and array semantics gave `from_graph` for free and a parquet does not:
        a duplicated `placeid` would make the join ambiguous, a duplicated `poi_idx` likewise, a
        `poi_idx` outside the region table would index past the end, and a negative region index
        would silently become a valid position from the other end of the array.
        """
        directory = Path(directory)
        places = pd.read_parquet(directory / "place_index.parquet")
        regions = pd.read_parquet(directory / "poi_to_region.parquet")

        placeid = ids.as_int64(places["placeid"], name="placeid")
        poi_idx = np.asarray(places["poi_idx"], dtype=np.int64)
        if len(np.unique(placeid)) != len(placeid):
            raise ValueError(f"{directory}: place_index.parquet has duplicate placeids; the "
                             f"place->region join would be ambiguous")
        if len(np.unique(regions["poi_idx"])) != len(regions):
            raise ValueError(f"{directory}: poi_to_region.parquet has duplicate poi_idx")
        # CONTIGUOUS, because the lookup below is positional after the sort. A table missing poi_idx
        # 3 passes every other check and silently resolves place->poi 3 to poi 4's region.
        if not np.array_equal(np.sort(np.asarray(regions["poi_idx"], dtype=np.int64)),
                              np.arange(len(regions), dtype=np.int64)):
            raise ValueError(f"{directory}: poi_to_region.parquet must cover poi_idx 0..n-1 with no "
                             f"gaps; the region lookup is positional and a gap shifts every place "
                             f"after it onto the wrong region")

        table = np.asarray(regions.sort_values("poi_idx")["region_idx"], dtype=np.int64)
        if table.size == 0:
            raise ValueError(f"{directory}: poi_to_region.parquet is empty")
        if poi_idx.min() < 0 or poi_idx.max() >= table.size:
            raise ValueError(f"{directory}: place_index.parquet references poi_idx "
                             f"[{poi_idx.min()}, {poi_idx.max()}] against a region table of "
                             f"{table.size} rows")
        assert_region_table(table, f"{directory}: poi_to_region.parquet")

        return cls(place_to_region=pd.Series(table[poi_idx], index=placeid),
                   n_regions_from_map=int(table.max()) + 1)

    @classmethod
    def from_graph(cls, graph_path: str | Path) -> "PlaceRegionMaps":
        with open(graph_path, "rb") as fh:
            graph = pickle.load(fh)
        placeid_to_idx = ids.as_int_keys(graph["placeid_to_idx"], name="placeid_to_idx")
        poi_to_region = np.asarray(_to_numpy(graph["poi_to_region"]), dtype=np.int64)

        places = np.fromiter(placeid_to_idx.keys(), dtype=np.int64, count=len(placeid_to_idx))
        indices = np.fromiter(placeid_to_idx.values(), dtype=np.int64, count=len(placeid_to_idx))
        # The same guard `from_parquet` carries. A negative region index is the quiet one: it is a
        # valid position counted from the other end of the array, so it resolves to a real region
        # and nothing raises. The pickle path had no such check while the parquet path did, which
        # made the safer constructor the one nobody used.
        assert_region_table(poi_to_region, str(graph_path))
        series = pd.Series(poi_to_region[indices], index=places)
        return cls(place_to_region=series, n_regions_from_map=int(poi_to_region.max()) + 1)


def assert_region_table(table: np.ndarray, source: str) -> None:
    """A place->region table must be non-empty and non-negative, whatever wrote it."""
    table = np.asarray(table)
    if table.size == 0:
        raise ValueError(f"{source}: the poi->region table is empty")
    if table.min() < 0:
        raise ValueError(f"{source}: the poi->region table holds a negative region index; it would "
                         f"address the region table from the wrong end and resolve silently")


def label_space(region_labels) -> int:
    """The head's output width: `max(region_idx) + 1` over the region LABEL column.

    Not the count of distinct regions, and not a train-only count. Getting this from anywhere else
    changes the head's shape without changing anything that would raise.
    """
    labels = np.asarray(region_labels)
    if labels.size == 0:
        raise ValueError("cannot derive a label space from an empty column")
    return int(labels.max()) + 1


def _to_numpy(obj):
    return obj.cpu().numpy() if hasattr(obj, "cpu") else np.asarray(obj)


def checkin_tensor(source, *, window: int = WINDOW, embed_dim: int = EMBED_DIM) -> np.ndarray:
    """The [N, 9, 64] check-in tensor, from a DataFrame or straight from a parquet path.

    Columns are digit-named ('0'..'575'), position-major: position p occupies columns
    `p*64 .. p*64+63`. They are sorted NUMERICALLY — as strings the order would be 0, 1, 10, 100.

    Given a path, the file is read one position at a time into a preallocated array, so peak memory
    is the tensor plus one position rather than the tensor plus a full second copy. At Texas that is
    the difference between ~17 GB and ~8.8 GB.
    """
    if isinstance(source, (str, Path)):
        return _checkin_tensor_streamed(Path(source), window, embed_dim)

    columns = _embedding_columns(source.columns, window, embed_dim)
    flat = source[columns].to_numpy(dtype=np.float32)
    return flat.reshape(len(source), window, embed_dim)


def _embedding_columns(columns, window: int, embed_dim: int) -> list:
    ordered = sorted((c for c in columns if str(c).isdigit()), key=int)
    expected = window * embed_dim
    if len(ordered) != expected:
        raise ValueError(
            f"expected {expected} embedding columns ({window} x {embed_dim}), found {len(ordered)}"
        )
    return ordered


def _checkin_tensor_streamed(path: Path, window: int, embed_dim: int) -> np.ndarray:
    import pyarrow.parquet as pq

    handle = pq.ParquetFile(path)
    columns = _embedding_columns(handle.schema.names, window, embed_dim)
    n_rows = handle.metadata.num_rows

    memory.check(memory.tensor_bytes(n_rows, window, embed_dim),
                 where=f"checkin tensor for {path.name}")

    out = np.empty((n_rows, window, embed_dim), dtype=np.float32)
    for position in range(window):
        block = columns[position * embed_dim:(position + 1) * embed_dim]
        table = handle.read(columns=block)
        out[:, position, :] = np.column_stack(
            [column.to_numpy(zero_copy_only=False) for column in table.columns]
        ).astype(np.float32, copy=False)
        del table
    return out


def region_tensor(history: np.ndarray, maps: PlaceRegionMaps,
                  region_embeddings: pd.DataFrame) -> np.ndarray:
    """The [N, 9, 64] region tensor: each historical visit replaced by its region's embedding.

    Vectorised over the whole [N, 9] block. The reference loops over the nine positions with a
    `pd.Series.map` per position, once per cell, for every state and seed.

    Padded positions map to the zero vector, so the heads' `x.abs().sum(-1) == 0` padding test
    behaves exactly as it does on the check-in tower. At stride 1 no padding exists (every window has
    nine real visits), so that branch is unreachable on v18 data — implemented correctly anyway,
    because the invariant is what the heads rely on.
    """
    table = _region_embedding_matrix(region_embeddings)
    n, window = history.shape

    # The window columns arrive as strings in the reference artifacts while the map is int-keyed.
    # Without this every lookup misses; with a forgiving `.get(pid, 0)` upstream it would instead
    # have placed every visit in region 0. See mtlcheck.ids.
    flat = ids.as_int64(history.reshape(-1), name="placeid")
    valid = flat != PAD_PLACE

    regions = np.zeros(flat.shape, dtype=np.int64)
    mapped = maps.place_to_region.reindex(flat[valid])
    if mapped.isna().any():
        missing = int(mapped.isna().sum())
        raise KeyError(
            f"{missing} historical places are absent from the place->region map. The sequences and "
            f"the graph come from different builds."
        )
    regions[valid] = mapped.to_numpy(dtype=np.int64)

    out = np.zeros((flat.shape[0], table.shape[1]), dtype=np.float32)
    out[valid] = table[regions[valid]]
    return out.reshape(n, window, table.shape[1])


def _region_embedding_matrix(frame: pd.DataFrame) -> np.ndarray:
    """`region_embeddings.parquet` -> [n_regions, 64], row-indexed by region id."""
    key = next((c for c in ("region_id", "region_idx") if c in frame.columns), None)
    if key is None:
        raise ValueError(f"no region key column in {list(frame.columns)[:5]}")

    dims = sorted((c for c in frame.columns if str(c).startswith("reg_") and str(c)[4:].isdigit()),
                  key=lambda c: int(str(c)[4:]))
    if not dims:
        # The place table names its dimensions with bare digits; the region table uses reg_N. Both
        # conventions exist in the reference, and assuming the wrong one produced a ZERO-WIDTH block
        # that concatenated silently and made two experiment arms indistinguishable from their own
        # baselines.
        dims = sorted((c for c in frame.columns if str(c).isdigit()), key=int)
    if not dims:
        raise ValueError(f"no dimension columns in {list(frame.columns)[:6]}")

    ordered = frame.sort_values(key)
    region_ids = ordered[key].to_numpy(dtype=np.int64)
    if not np.array_equal(region_ids, np.arange(len(region_ids))):
        raise ValueError("region ids are not a contiguous 0..n-1 range; the row index would be wrong")
    return ordered[dims].to_numpy(dtype=np.float32)


def region_of(places, maps: PlaceRegionMaps) -> np.ndarray:
    """Region index of each place. Exposed because it is how the label columns are checked."""
    keys = ids.as_int64(places, name="placeid")
    mapped = maps.place_to_region.reindex(keys)
    if mapped.isna().any():
        raise KeyError(f"{int(mapped.isna().sum())} places are absent from the place->region map")
    return mapped.to_numpy(dtype=np.int64)


__all__ = ["PlaceRegionMaps", "checkin_tensor", "region_tensor", "region_of", "label_space",
           "EMBED_DIM", "WINDOW", "PAD_PLACE"]
