"""Next-region label derivation for the check2HGI MTL track.

Builds ``output/check2hgi/<state>/input/next_region.parquet`` from:

1. ``sequences_next.parquet`` produced by ``builders.generate_next_input_from_checkins``
   (written in the SAME pass as ``next.parquet`` — row-aligned by construction;
   pipeline_audit 2026-07-01: the old attribution to ``Check2HGIPreprocess``
   was stale, no such writer exists) — has per-row ``target_poi`` (POI index
   into ``poi_to_region``).
2. ``checkin_graph.pt`` produced by the same preprocessing — pickled
   dict with ``poi_to_region: np.ndarray[n_pois]`` mapping POI index →
   region index.
3. ``next.parquet`` (the check-in-level X sequences + userid + next_category
   label) — its rows are copied so next_region stays row-aligned with
   next.parquet (same userid/order; enforced at load by the C1 guard in
   ``folds.py``). NOTE: the copied X columns 0..575 are VESTIGIAL at MTL train
   time — the MTL loader picks each slot's own X (the region task consumes the
   region-embedding sequence, not these columns; see ``folds.py`` "each slot
   picks its own X"). They are kept only so the two parquets share a schema/row
   index, not because the region task reads them.

Output schema::

    col 0..575        — flattened 9-window of check2HGI check-in embeddings
                        (identical to next.parquet columns '0'..'575')
    region_idx        — int64 region index in ``[0, n_regions)``
    userid            — int64 user id (for StratifiedGroupKFold)
    last_region_idx   — int64 region index of the LAST observed POI in the
                        9-window (derived from ``poi_{0..8}`` via
                        ``placeid_to_idx`` + ``poi_to_region``). ``-1``
                        sentinel for rows with no valid POI in the window
                        (pad-only trajectories). Consumed by
                        ``next_getnext_hard`` head (faithful GETNext).

Fails loud on any target_poi that has no region assignment (should never
happen — every POI goes through spatial join in preprocessing — but we
assert it so a silent NaN never leaks into training).
"""

from __future__ import annotations

import pickle as pkl
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

from configs.paths import EmbeddingEngine, IoPaths


def _load_graph_maps(state: str) -> Tuple[dict, np.ndarray]:
    """Load ``placeid_to_idx`` + ``poi_to_region`` from the graph artifact.

    ``target_poi`` in ``sequences_next.parquet`` is a raw placeid (int),
    not a POI index — values like 25743 exceed ``n_pois=11848``. Resolve
    via ``placeid_to_idx`` before indexing ``poi_to_region``.
    """
    graph_path = IoPaths.CHECK2HGI.get_graph_data_file(state)
    with open(graph_path, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    return placeid_to_idx, np.asarray(poi_to_region, dtype=np.int64)


def _load_sequences(state: str) -> pd.DataFrame:
    """Load the per-row target_poi index from the preprocessing artifact."""
    seq_path = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    if not seq_path.exists():
        raise FileNotFoundError(
            f"sequences_next.parquet missing at {seq_path}. "
            f"Run pipelines/embedding/check2hgi.pipe.py for {state} first."
        )
    return pd.read_parquet(seq_path)


def build_next_region_frame(state: str) -> Tuple[pd.DataFrame, int]:
    """Build the next-region input DataFrame for ``state``.

    Returns ``(df, n_regions)``. ``df`` has the same row count as the
    check2HGI ``next.parquet`` and shares the X columns row-for-row —
    we assert that before joining the region label in.
    """
    next_df = IoPaths.load_next(state, EmbeddingEngine.CHECK2HGI)
    seq_df = _load_sequences(state)

    if len(next_df) != len(seq_df):
        raise ValueError(
            f"next.parquet rows ({len(next_df)}) and sequences_next.parquet "
            f"rows ({len(seq_df)}) disagree for {state}. Regenerate both "
            f"via the check2HGI pipeline in one pass."
        )
    # userid is stored as str in next.parquet and int64 in sequences_next.parquet
    # (they are produced by different code paths that disagree on the dtype,
    # not a semantic difference). Cast to str on both sides for the alignment
    # check so the string/int comparison doesn't silently fail.
    next_uid = next_df["userid"].astype(str).reset_index(drop=True)
    seq_uid = seq_df["userid"].astype(str).reset_index(drop=True)
    if not (next_uid == seq_uid).all():
        raise ValueError(
            f"userid columns of next.parquet and sequences_next.parquet "
            f"disagree for {state} — the two files are not row-aligned."
        )

    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1

    # target_poi is a raw placeid (stored as object/str); cast to int
    # and resolve through placeid_to_idx to get the POI index.
    target_placeid = seq_df["target_poi"].astype(np.int64).to_numpy()
    unmapped_mask = ~np.isin(target_placeid, list(placeid_to_idx.keys()))
    if unmapped_mask.any():
        sample = target_placeid[unmapped_mask][:10].tolist()
        raise ValueError(
            f"{int(unmapped_mask.sum())} target_poi values are not in "
            f"placeid_to_idx for {state}. Sample unmapped placeids: {sample}."
        )
    # Vectorised lookup: map once via pandas for speed; avoids a Python loop.
    poi_idx = pd.Series(target_placeid).map(placeid_to_idx).to_numpy(dtype=np.int64)

    region_idx = poi_to_region[poi_idx]
    if (region_idx < 0).any():
        bad_pois = poi_idx[region_idx < 0][:10].tolist()
        raise ValueError(
            f"{int((region_idx < 0).sum())} rows have no region assignment. "
            f"Sample unassigned POI indices: {bad_pois}."
        )

    # Compute last_region_idx from poi_{0..8}: last non-pad POI per row
    # mapped through placeid_to_idx + poi_to_region. Rows with no valid
    # POI (all-pad trajectories) get sentinel -1 — downstream heads
    # (e.g. next_getnext_hard) zero the graph prior for those rows.
    poi_cols = [f"poi_{i}" for i in range(9)]
    poi_mat = seq_df[poi_cols].astype(np.int64).to_numpy()  # [N, 9]
    valid = poi_mat >= 0
    # last-non-pad position per row; -1 if no valid POI
    last_pos = np.where(
        valid.any(axis=1),
        valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1),
        -1,
    )
    N = poi_mat.shape[0]
    last_poi = np.where(
        last_pos >= 0,
        poi_mat[np.arange(N), np.clip(last_pos, 0, None)],
        -1,
    )
    unmapped_valid = (last_poi >= 0) & ~np.isin(last_poi, list(placeid_to_idx.keys()))
    if unmapped_valid.any():
        bad = last_poi[unmapped_valid][:5].tolist()
        raise ValueError(
            f"{int(unmapped_valid.sum())} last_poi values (non-pad) unmapped "
            f"in placeid_to_idx for {state}. Sample: {bad}."
        )
    last_region_idx = np.full(N, -1, dtype=np.int64)
    valid_mask = last_poi >= 0
    if valid_mask.any():
        last_poi_idx = (
            pd.Series(last_poi[valid_mask])
            .map(placeid_to_idx)
            .to_numpy(dtype=np.int64)
        )
        last_region_idx[valid_mask] = poi_to_region[last_poi_idx]
        if (last_region_idx[valid_mask] < 0).any():
            raise ValueError(
                f"{int((last_region_idx[valid_mask] < 0).sum())} last_poi "
                f"entries resolve to unassigned regions for {state}."
            )

    out = next_df.drop(columns=["next_category"]).copy()
    out["region_idx"] = region_idx.astype(np.int64)
    out["last_region_idx"] = last_region_idx.astype(np.int64)
    return out, n_regions


def load_next_region_data(state: str, engine: EmbeddingEngine) -> pd.DataFrame:
    """Read a pre-built next_region.parquet. Fails if missing."""
    if engine != EmbeddingEngine.CHECK2HGI:
        raise ValueError(
            f"next_region only defined on CHECK2HGI (got {engine})."
        )
    return IoPaths.load_next_region(state, engine)


__all__ = [
    "build_next_region_frame",
    "load_next_region_data",
]
