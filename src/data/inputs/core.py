"""
Pure logic functions for MTL input generation (no I/O).

This module contains stateless, testable functions extracted from create_input.py.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from configs.model import InputsConfig

logger = logging.getLogger(__name__)

# Constants
PADDING_VALUE = -1
MIN_SEQUENCE_LENGTH = 5
DEFAULT_BATCH_SIZE = 100000
MISSING_CATEGORY_VALUE = "None"

# Number of output rows held in RAM per parquet row-group during the streaming
# next-input build (see ``NextInputStreamWriter``). 200k rows × 578 float32 ≈
# ~0.46 GB/chunk — small relative to the box, large enough for good parquet
# compression. Overridable via env for tuning / tests.
NEXT_BUILD_CHUNK_ROWS = int(os.environ.get("MTL_NEXT_BUILD_CHUNK_ROWS", "200000"))

# Default head-room (GB) subtracted from psutil-available RAM before the build
# RAM estimate is compared. Overridable via MTL_RAM_HEADROOM_GB.
DEFAULT_RAM_HEADROOM_GB = float(os.environ.get("MTL_RAM_HEADROOM_GB", "16"))


def estimate_next_build_ram_gb(n_rows: int, num_features: int) -> float:
    """Estimate peak RAM (GB) of the *legacy* (non-streaming) next-input build.

    The legacy path holds, simultaneously, the per-row ``<U32`` accumulation list
    (``n_rows × (num_features + 2) × 128`` bytes) **and** the ``np.array(results)``
    copy of the same — i.e. ~2× the ``<U32`` payload. This estimator returns that
    worst-case so callers can warn before a large build.
    """
    u32_payload = n_rows * (num_features + 2) * 128  # bytes, one <U32 matrix
    return 2 * u32_payload / (1024 ** 3)


def available_ram_gb() -> Optional[float]:
    """Available system RAM in GB, or ``None`` if psutil is unavailable or the
    query fails. macOS psutil can intermittently raise on
    ``host_statistics(HOST_VM_INFO)`` under memory pressure ("array not large
    enough"); since this guard is advisory (the streaming writer bounds peak RAM
    regardless) a transient query failure must not crash the build — fall back to
    ``None``, which every caller already handles."""
    try:
        import psutil
        return psutil.virtual_memory().available / (1024 ** 3)
    except Exception:  # pragma: no cover - psutil missing OR transient syscall failure
        return None


def check_next_build_ram(
    n_rows: int,
    num_features: int,
    *,
    streaming: bool,
    headroom_gb: float = None,
) -> None:
    """Fail-loud / warn-loud CPU-RAM guard for the next-input build.

    With ``streaming=True`` (the chunked writer) peak RAM is O(chunk), so this
    only emits an informational WARN with the legacy-equivalent estimate — it
    never raises (the build is safe). With ``streaming=False`` (the legacy O(N)
    accumulation, used only by callers that still need the in-RAM list) it raises
    a clear ``MemoryError`` when the estimate would exceed available RAM, pointing
    at the chunked path, rather than letting the box OOM.
    """
    if headroom_gb is None:
        headroom_gb = DEFAULT_RAM_HEADROOM_GB
    est_gb = estimate_next_build_ram_gb(n_rows, num_features)
    avail = available_ram_gb()
    if streaming:
        # Streaming holds only ~chunk rows of float32 at once.
        chunk_gb = NEXT_BUILD_CHUNK_ROWS * num_features * 4 / (1024 ** 3)
        logger.info(
            "next-input streaming build: %d rows, legacy-equiv peak ~%.1f GB, "
            "streaming peak ~%.2f GB/chunk (chunk=%d rows)%s",
            n_rows, est_gb, chunk_gb, NEXT_BUILD_CHUNK_ROWS,
            "" if avail is None else f", avail={avail:.1f} GB",
        )
        if avail is not None and est_gb > (avail - headroom_gb):
            logger.warning(
                "next-input build would need ~%.1f GB in the LEGACY path "
                "(avail %.1f GB - headroom %.1f GB); using the streaming writer "
                "instead so peak stays ~%.2f GB/chunk.",
                est_gb, avail, headroom_gb, chunk_gb,
            )
        return
    # Non-streaming: this is the dangerous path.
    if avail is not None and est_gb > (avail - headroom_gb):
        raise MemoryError(
            f"next-input build needs ~{est_gb:.1f} GB peak RAM (n_rows={n_rows}, "
            f"num_features={num_features}) but only {avail:.1f} GB is available "
            f"(headroom {headroom_gb:.1f} GB). Use the streaming build path "
            f"(generate_next_input_from_checkins, which writes incrementally) or "
            f"a smaller config. Override headroom via MTL_RAM_HEADROOM_GB."
        )


class NextInputStreamWriter:
    """Incremental parquet writer for next-input rows (memory-bounded build).

    Accumulates rows in an in-RAM buffer and flushes a parquet **row-group**
    every ``chunk_rows`` rows, so peak RAM is O(chunk) instead of O(N). The
    produced file is byte-identical in *schema, column order, dtypes and row
    order* to the legacy ``save_next_input_dataframe`` single-shot write: each
    flushed chunk is materialised as the *same* pandas DataFrame the legacy path
    builds (float32 embedding matrix + object ``next_category`` + object
    ``userid``) and converted to Arrow via ``pyarrow.Table.from_pandas`` with the
    schema pinned from the first chunk.

    Usage::

        w = NextInputStreamWriter(out_path, num_features)
        for emb_f32, cat, uid in per_user_rows:   # emb_f32: (num_features,) float32
            w.add(emb_f32, cat, uid)
        w.close()
    """

    def __init__(self, output_path, num_features: int, chunk_rows: int = None):
        from pathlib import Path as _P

        self.output_path = _P(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.num_features = num_features
        self.cols = [str(i) for i in range(num_features)]
        self.chunk_rows = chunk_rows or NEXT_BUILD_CHUNK_ROWS
        self._buf_emb: List[np.ndarray] = []
        self._buf_cat: List = []
        self._buf_uid: List = []
        self._n_buf = 0
        self._writer = None  # pyarrow.parquet.ParquetWriter, lazily opened
        self._schema = None
        self._total = 0

    def add(self, emb_row: np.ndarray, cat, uid) -> None:
        self._buf_emb.append(emb_row)
        self._buf_cat.append(cat)
        self._buf_uid.append(uid)
        self._n_buf += 1
        if self._n_buf >= self.chunk_rows:
            self._flush()

    def _chunk_dataframe(self) -> pd.DataFrame:
        # Build EXACTLY the frame the legacy save_next_input_dataframe builds for
        # this slice: a contiguous float32 matrix + object metadata columns.
        mat = np.empty((self._n_buf, self.num_features), dtype=np.float32)
        for i, e in enumerate(self._buf_emb):
            mat[i] = e
        df = pd.DataFrame(mat, columns=self.cols)
        # ``.tolist()`` mirrors save_next_input_dataframe (object dtype columns).
        df["next_category"] = list(self._buf_cat)
        df["userid"] = list(self._buf_uid)
        return df

    def _flush(self) -> None:
        if self._n_buf == 0:
            return
        import pyarrow as pa
        import pyarrow.parquet as pq

        df = self._chunk_dataframe()
        table = pa.Table.from_pandas(df, preserve_index=False)
        if self._writer is None:
            self._schema = table.schema
            self._writer = pq.ParquetWriter(str(self.output_path), self._schema)
        else:
            # Pin every chunk to the first chunk's schema (object columns can
            # otherwise infer string vs large_string differently per chunk).
            table = table.cast(self._schema)
        self._writer.write_table(table)
        self._total += self._n_buf
        # Release the buffer for this chunk before the next one accumulates.
        self._buf_emb.clear()
        self._buf_cat.clear()
        self._buf_uid.clear()
        self._n_buf = 0

    def close(self) -> int:
        """Flush any remainder and finalise the file. Returns total rows written."""
        self._flush()
        if self._writer is not None:
            self._writer.close()
        else:
            # No rows at all: write an empty, correctly-typed parquet so the
            # output schema still matches the legacy empty-frame path.
            empty = pd.DataFrame(
                columns=self.cols + ["next_category", "userid"]
            )
            empty.to_parquet(self.output_path, index=False)
        return self._total


def generate_sequences(
    places_visited: List[int],
    window_size: int = InputsConfig.SLIDE_WINDOW,
    pad_value: int = PADDING_VALUE,
    stride: int = None,
    return_start_indices: bool = False,
    min_sequence_length: int = MIN_SEQUENCE_LENGTH,
    emit_tail: bool = True,
):
    """
    Generate sequences of fixed length for next-POI prediction.

    Each sequence contains:
    - First (window_size) positions: historical visits (padded if needed)
    - Final position: target POI to predict

    Args:
        places_visited: List of place IDs in chronological order
        window_size: Number of historical visits per sequence (default: SLIDE_WINDOW)
        pad_value: Value for padding short sequences (default: -1)
        stride: Step between sequence starts (default: window_size, i.e. non-overlapping)
        return_start_indices: If True, return List[Tuple[int, List[int]]] where each
            tuple is (start_idx, sequence). Needed for position-based embedding lookup
            in check-in-level conversion.
        min_sequence_length: Minimum number of check-ins a user must have for any
            sequence to be emitted; users with fewer are dropped (returns []).
            Default == the module constant MIN_SEQUENCE_LENGTH (5) so existing
            callers are byte-identical to the pre-parameterization behaviour.
        emit_tail: If True (default), emit the out-of-bounds "tail" windows where
            the sliding window walks off the end of the user's history and the
            last real visit is demoted to the target (history shifted). This is
            required at the non-overlapping default (stride=9) — it is how each
            user's FINAL window/last-POI target is produced. If False (the M1
            gate, used only at stride=1), these tail windows are skipped: at
            stride=1 each user emits ~window_size of them, all targeting the SAME
            last POI on near-all-padding histories, which over-weights the
            last-POI target and injects trivial low-context samples (a label-
            distribution skew, not a leak). Default True ⇒ byte-identical.

    Returns:
        If return_start_indices is False:
            List of sequences, each of length (window_size + 1).
        If return_start_indices is True:
            List of (start_idx, sequence) tuples.
        Empty list if insufficient data.
    """
    if not places_visited or len(places_visited) < min_sequence_length:
        return []

    sequences = []
    step = stride if stride is not None else window_size
    total_visits = len(places_visited)

    for start_idx in range(0, total_visits, step):
        # Extract history window (always window_size items, regardless of stride)
        history = places_visited[start_idx : start_idx + window_size]

        # Pad if history is shorter than window_size
        if len(history) < window_size:
            history = history + [pad_value] * (window_size - len(history))

        # Determine target POI (immediately after the history window)
        target_idx = start_idx + window_size
        if target_idx < total_visits:
            target_poi = places_visited[target_idx]
        elif not emit_tail:
            # M1 gate: skip the OOB tail window (no genuine next visit exists
            # past the history). Used at stride=1 to avoid the last-POI-target
            # skew. At the default emit_tail=True this branch is never taken.
            continue
        else:
            # Use last real visit as target, shift history
            for j in range(len(history) - 1, -1, -1):
                if history[j] != pad_value:
                    target_poi = history[j]
                    history = history[:j] + history[j + 1 :] + [pad_value]
                    break
            else:
                target_poi = pad_value

        # Skip all-padding sequences
        if all(x == pad_value for x in history) or target_poi == pad_value:
            continue

        seq = history + [target_poi]
        if return_start_indices:
            sequences.append((start_idx, seq))
        else:
            sequences.append(seq)

    return sequences


def create_embedding_lookup(
    embeddings_df: pd.DataFrame, embedding_dim: int
) -> Dict[int, np.ndarray]:
    """
    Build POI → embedding lookup dictionary.

    Consolidates patterns from:
    - create_input.py:360-372
    - embedding_fusion.py:413-417

    Args:
        embeddings_df: DataFrame with 'placeid' and embedding columns
        embedding_dim: Dimension of embeddings

    Returns:
        Dictionary mapping POI ID to embedding vector (np.ndarray)
    """
    emb_cols = [str(i) for i in range(embedding_dim)]

    # Set placeid as index if not already
    if "placeid" in embeddings_df.columns:
        emb_df = embeddings_df.set_index("placeid")[emb_cols]
    else:
        emb_df = embeddings_df[emb_cols]

    # Build lookup dictionary
    lookup = {
        poi_id: row.values.astype(np.float32) for poi_id, row in emb_df.iterrows()
    }

    # Add zero embedding for padding
    lookup[PADDING_VALUE] = np.zeros(embedding_dim, dtype=np.float32)

    return lookup


def create_category_lookup(
    checkins_df: pd.DataFrame, default_value: str = None
) -> Dict[int, str]:
    """
    Build POI → category lookup dictionary.

    Extracted from create_input.py:350-357
    Updated to support default value for missing categories.

    Args:
        checkins_df: DataFrame with 'placeid' and 'category' columns
        default_value: Value to use for missing categories (default: MISSING_CATEGORY_VALUE)

    Returns:
        Dictionary mapping POI ID to category label
    """
    if default_value is None:
        default_value = MISSING_CATEGORY_VALUE

    # Handle duplicate placeids by taking first occurrence
    unique_checkins = checkins_df.drop_duplicates(subset=["placeid"], keep="first")
    lookup = dict(zip(unique_checkins["placeid"], unique_checkins["category"]))

    # Add explicit padding entry
    lookup[PADDING_VALUE] = default_value

    return lookup


def get_zero_embedding(embedding_dim: int) -> np.ndarray:
    """
    Get zero embedding vector for padding.

    Centralizes pattern from lines 226, 373, 410, 449 across multiple files.

    Args:
        embedding_dim: Dimension of embedding

    Returns:
        Zero vector of specified dimension
    """
    return np.zeros(embedding_dim, dtype=np.float32)


def parse_and_sort_checkins(checkin_timestamps: List[str]) -> List:
    """
    Parse and sort checkin timestamps using vectorized operations.

    Extracted from create_input.py:19-29

    Args:
        checkin_timestamps: List of timestamp strings

    Returns:
        List of sorted datetime objects
    """
    return sorted(pd.to_datetime(checkin_timestamps))


def save_parquet(
    df: pd.DataFrame, output_path, create_dirs: bool = True, index: bool = False
) -> None:
    """
    Save DataFrame to parquet with automatic directory creation.

    Consolidates pattern from 5 locations across builders.py and fusion.py.

    Args:
        df: DataFrame to save
        output_path: Output file path (str or Path)
        create_dirs: If True, create parent directories
        index: If True, include index in output
    """
    from pathlib import Path

    path = Path(output_path)

    if create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(path, index=index)


def save_next_input_dataframe(
    results: List[np.ndarray], window_size: int, embedding_dim: int, state: str, engine
) -> None:
    """
    Save next-POI input results to parquet.

    Consolidates DataFrame creation and saving from:
    - builders.py:113-121 (generate_next_input_from_poi)
    - builders.py:196-209 (generate_next_input_from_checkins)
    - fusion.py:430-438 (_convert_sequences_to_fused_embeddings)

    Args:
        results: List of numpy arrays, each containing flattened embeddings
                + target category + userid
        window_size: Number of historical steps in sequence
        embedding_dim: Embedding dimension
        state: State name
        engine: Embedding engine (EmbeddingEngine enum)
    """
    from configs.paths import IoPaths

    num_features = window_size * embedding_dim
    emb_cols = list(map(str, range(num_features)))

    if results:
        # Each result row mixes float32 embeddings with a string category and userid,
        # forcing object dtype on the whole array. Building a DataFrame directly from
        # N object-dtype rows is slow (pandas does per-element type inference).
        # Splitting into a typed float32 matrix + metadata columns is much faster,
        # and matches the float32 precision already used everywhere else in the pipeline
        # (create_embedding_lookup, convert_user_checkins_to_sequences, load_next_data).
        arr = np.array(results)  # (N, num_features + 2), object dtype
        output_df = pd.DataFrame(
            arr[:, :num_features].astype(np.float32), columns=emb_cols
        )
        output_df["next_category"] = arr[:, num_features].tolist()
        output_df["userid"] = arr[:, num_features + 1].tolist()
    else:
        output_df = pd.DataFrame(columns=emb_cols + ["next_category", "userid"])

    output_path = IoPaths.get_next(state, engine)
    save_parquet(output_df, output_path)


def convert_sequences_to_poi_embeddings(
    sequences_df: pd.DataFrame,
    embedding_lookup: Dict[int, np.ndarray],
    category_lookup: Dict[int, str],
    window_size: int,
    embedding_dim: int,
    batch_size: int = None,
    show_progress: bool = True,
) -> List[np.ndarray]:
    """
    Convert POI sequences to flattened embedding sequences.

    Consolidates ~33 lines of duplicated logic from:
    - builders.py:89-111 (generate_next_input_from_poi)
    - fusion.py:403-428 (_convert_sequences_to_fused_embeddings)

    Process:
    1. For each sequence row: [poi_0, poi_1, ..., poi_8, target_poi, userid]
    2. Map each POI ID to its embedding vector via lookup
    3. Stack window embeddings: shape (window_size, embedding_dim)
    4. Flatten to 1D: shape (window_size * embedding_dim,)
    5. Append target category and userid

    **IMPORTANT**: This function is ONLY for POI-level embeddings (dictionary-based lookup).
    It is NOT used by generate_next_input_from_checkins which has a different algorithm
    for check-in-level embeddings.

    Args:
        sequences_df: DataFrame with columns [poi_0, ..., poi_N, target_poi, userid]
        embedding_lookup: POI ID → embedding vector (dictionary)
        category_lookup: POI ID → category label
        window_size: Number of POIs in history window
        embedding_dim: Dimension of each embedding
        batch_size: Batch size for progress bar (default: DEFAULT_BATCH_SIZE)
        show_progress: If True, show tqdm progress bar

    Returns:
        List of numpy arrays, each containing:
        [flattened_embeddings..., target_category, userid]
    """
    if batch_size is None:
        batch_size = DEFAULT_BATCH_SIZE

    from tqdm import tqdm

    all_results = []
    iterator = range(0, len(sequences_df), batch_size)

    if show_progress:
        iterator = tqdm(iterator, desc="Processing batches")

    for start_idx in iterator:
        batch = sequences_df.iloc[start_idx : start_idx + batch_size]

        for _, row in batch.iterrows():
            # Extract history POI IDs (first window_size columns)
            history_pois = row.iloc[:window_size].values.astype(int)
            target_poi = int(row.iloc[window_size])
            userid = row["userid"]

            # Build sequence embeddings using lookup
            sequence_embeddings = np.vstack(
                [
                    embedding_lookup.get(int(poi_id), embedding_lookup[PADDING_VALUE])
                    for poi_id in history_pois
                ]
            )

            # Flatten to 1D: [window_size × embedding_dim] features
            flattened = sequence_embeddings.ravel()

            # Get target category
            target_category = category_lookup.get(target_poi, MISSING_CATEGORY_VALUE)

            # Append target category and userid
            all_results.append(np.concatenate([flattened, [target_category, userid]]))

    return all_results


def convert_user_checkins_to_sequences(
    user_df: pd.DataFrame,
    embedding_cols: List[str],
    window_size: int,
    embedding_dim: int,
    stride: int = None,
    min_sequence_length: int = MIN_SEQUENCE_LENGTH,
    emit_tail: bool = True,
) -> Tuple[List[np.ndarray], List[List[int]]]:
    """
    Convert a single user's check-in DataFrame to embedding sequences using position-based lookup.

    This function handles check-in-level embeddings where each row in user_df corresponds
    to a specific check-in event. Unlike POI-level embeddings where same POI = same embedding,
    check-in-level embeddings (Time2Vec, Check2HGI) have unique embeddings per visit.

    The position-based lookup ensures that sequence N starts at position N * window_size
    in the user's chronological history, preserving the temporal context of each visit.

    Args:
        user_df: DataFrame for a single user, sorted by datetime, with reset index.
                 Must contain columns: userid, placeid, category, and all embedding_cols.
        embedding_cols: List of column names containing embedding values.
                       Example: ['0', '1', ..., '63'] or ['fused_0', 'fused_1', ..., 'fused_127']
        window_size: Number of historical check-ins per sequence.
        embedding_dim: Dimension of each embedding vector.

    Returns:
        Tuple of:
        - embedding_results: List of numpy arrays, each containing:
          [flattened_window_embeddings, target_category, userid]
        - poi_sequences: List of POI ID sequences (for intermediate file saving)
          Each sequence is [poi_0, ..., poi_{window-1}, target_poi, userid]

    Notes:
        - Uses non-overlapping windows: sequence N starts at position N * window_size
        - Padding positions (PADDING_VALUE) get zero embeddings
        - Target category uses position-based lookup with fallback to POI ID search
    """
    embedding_results = []
    poi_sequences = []

    # Get user ID (same for all rows in user_df)
    userid = user_df["userid"].iloc[0]

    # Pre-extract numpy arrays for fast indexed access (avoids slow iloc in loop)
    emb_matrix = user_df[embedding_cols].values.astype(np.float32)
    categories = user_df["category"].values
    placeids = user_df["placeid"].values
    n_rows = len(user_df)
    zero_emb = np.zeros(embedding_dim, dtype=np.float32)

    # Generate POI sequences using shared function (with start indices for position safety)
    places = placeids.tolist()
    sequences_with_idx = generate_sequences(
        places,
        window_size=window_size,
        stride=stride,
        return_start_indices=True,
        min_sequence_length=min_sequence_length,
        emit_tail=emit_tail,
    )

    if not sequences_with_idx:
        return [], []

    for history_start_idx, seq in sequences_with_idx:
        history_pois = seq[:window_size]
        target_poi = seq[window_size]

        # Save POI sequence for intermediate output
        poi_sequences.append(seq + [userid])

        # Build embeddings using POSITION-based lookup (not POI ID search)
        seq_embeddings = []
        for i, poi in enumerate(history_pois):
            if poi == PADDING_VALUE:
                seq_embeddings.append(zero_emb)
            else:
                row_idx = history_start_idx + i
                if row_idx < n_rows:
                    seq_embeddings.append(emb_matrix[row_idx])
                else:
                    seq_embeddings.append(zero_emb)

        # Get target category - try position first, fall back to POI ID lookup
        target_idx = history_start_idx + window_size
        if target_idx < n_rows:
            target_category = categories[target_idx]
        else:
            # Fallback: look up target POI's category by POI ID
            matches = np.where(placeids == target_poi)[0]
            target_category = (
                categories[matches[0]] if len(matches) > 0 else MISSING_CATEGORY_VALUE
            )

        # Flatten embeddings and append metadata
        flattened = np.vstack(seq_embeddings).ravel()
        embedding_results.append(np.concatenate([flattened, [target_category, userid]]))

    return embedding_results, poi_sequences
