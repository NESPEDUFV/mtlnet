"""
Input generation builders for MTL tasks.

This module contains the business logic for generating category and next-POI inputs
from embeddings. These are pure transformation functions used by pipeline orchestration.

Moved from pipelines/create_inputs.pipe.py to follow the pattern where pipes only
handle orchestration and modules contain business logic.
"""
from typing import Optional
import json
import subprocess
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from tqdm import tqdm

from configs.paths import IoPaths, EmbeddingEngine
from configs.model import InputsConfig

# Engines that produce check-in-level embeddings (one per visit, not per POI).
# Category task requires POI-level embeddings (one per POI).
_CHECKIN_LEVEL_ENGINES = {
    EmbeddingEngine.CHECK2HGI,
    EmbeddingEngine.CHECK2HGI_POI2VEC,
    EmbeddingEngine.C2HGI_HGI_CONCAT,  # Design A: 128-dim late concat (per-step, NOT POI-level)
    EmbeddingEngine.CHECK2HGI_DESIGN_E,
    EmbeddingEngine.CHECK2HGI_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_DESIGN_H,
    EmbeddingEngine.CHECK2HGI_DESIGN_D,
    EmbeddingEngine.CHECK2HGI_DESIGN_I,
    EmbeddingEngine.CHECK2HGI_DESIGN_J,
    EmbeddingEngine.CHECK2HGI_DESIGN_M,
    EmbeddingEngine.CHECK2HGI_DESIGN_L,
    EmbeddingEngine.CHECK2HGI_LEVER4_CANONICAL,
    EmbeddingEngine.CHECK2HGI_LEVER4_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_RESLN,
    EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_B,
    EmbeddingEngine.CHECK2HGI_RESLN_DESIGN_J,
    EmbeddingEngine.TIME2VEC,
}

from .core import (
    generate_sequences,
    create_embedding_lookup,
    create_category_lookup,
    convert_sequences_to_poi_embeddings,
    convert_user_checkins_to_sequences,
    save_next_input_dataframe,
    save_parquet,
    get_zero_embedding,
    NextInputStreamWriter,
    check_next_build_ram,
    NEXT_BUILD_CHUNK_ROWS,
    PADDING_VALUE,
    DEFAULT_BATCH_SIZE,
    MISSING_CATEGORY_VALUE,
    MIN_SEQUENCE_LENGTH,
)


def _resolve_emit_tail(emit_tail: Optional[bool], stride: Optional[int]) -> bool:
    """Resolve the AUTO (``None``) emit_tail policy from the stride.

    AUTO ⇒ emit tail windows at the default/non-overlap stride (byte-identical
    legacy behaviour) but GATE them at ``stride==1`` (the M1 last-POI-target
    skew fix — the overlap board's only use of stride-1). An explicit bool wins.
    """
    if emit_tail is not None:
        return emit_tail
    return stride != 1


def _git_sha() -> str:
    """Best-effort current git commit hash; 'unknown' if unavailable."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
    except Exception:
        return "unknown"


def _write_build_provenance(
    state: str,
    engine: EmbeddingEngine,
    task: str,
    *,
    min_sequence_length: int,
    stride: Optional[int],
    window_size: int,
    emit_tail: Optional[bool] = None,
) -> None:
    """Write an additive build-provenance sidecar next to the task's input parquet.

    Path: ``<engine_dir>/input/<task>_build_provenance.json``. This NEVER gates
    anything — it only records how the windowing-dependent inputs were built so a
    later reviewer can tell a stride-1/min_seq-10 board build apart from the frozen
    stride-9/min_seq-5 default build. ``stride=None`` means non-overlapping
    (step == window_size), matching the default code path.
    """
    try:
        # Anchor the sidecar to the same input dir the next parquet lives in.
        next_path = IoPaths.get_next(state, engine)
        sidecar = next_path.parent / f"{task}_build_provenance.json"
        payload = {
            "task": task,
            "engine": engine.value,
            "state": state,
            "min_sequence_length": min_sequence_length,
            # JSON-friendly: record the effective step explicitly too.
            "stride": stride,
            "effective_step": stride if stride is not None else window_size,
            "window_size": window_size,
            "emit_tail": emit_tail,
            "git_sha": _git_sha(),
            "utc": datetime.now(tz=timezone.utc).isoformat(),
        }
        sidecar.parent.mkdir(parents=True, exist_ok=True)
        sidecar.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        # Provenance is best-effort and must never break a build.
        pass


class _SequenceStreamWriter:
    """Memory-bounded writer for the intermediate POI-sequence parquet.

    Mirrors the legacy single-shot build exactly: ``pd.DataFrame(all_sequences,
    columns=seq_cols)`` with every ``poi_*``/``target_poi`` column cast to ``str``
    (object dtype), ``userid`` left as-is. Streams row-group chunks so peak RAM is
    O(chunk) instead of O(N). Schema is pinned from the first chunk so per-chunk
    object→arrow inference stays consistent.
    """

    def __init__(self, output_path, seq_cols, poi_cols, chunk_rows: int = None):
        from pathlib import Path as _P

        self.output_path = _P(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.seq_cols = list(seq_cols)
        self.poi_cols = set(poi_cols)
        self.chunk_rows = chunk_rows or NEXT_BUILD_CHUNK_ROWS
        self._buf = []
        self._writer = None
        self._schema = None

    def add(self, seq_row) -> None:
        self._buf.append(seq_row)
        if len(self._buf) >= self.chunk_rows:
            self._flush()

    def _flush(self) -> None:
        if not self._buf:
            return
        import pyarrow as pa
        import pyarrow.parquet as pq

        df = pd.DataFrame(self._buf, columns=self.seq_cols)
        for col in self.seq_cols:
            if col in self.poi_cols:
                df[col] = df[col].astype(str)
        table = pa.Table.from_pandas(df, preserve_index=False)
        if self._writer is None:
            self._schema = table.schema
            self._writer = pq.ParquetWriter(str(self.output_path), self._schema)
        else:
            table = table.cast(self._schema)
        self._writer.write_table(table)
        self._buf.clear()

    def close(self) -> None:
        self._flush()
        if self._writer is not None:
            self._writer.close()
        else:
            empty = pd.DataFrame(columns=self.seq_cols)
            for col in self.seq_cols:
                if col in self.poi_cols:
                    empty[col] = empty[col].astype(str)
            empty.to_parquet(self.output_path, index=False)


def generate_category_input(state: str, engine: EmbeddingEngine) -> None:
    """
    Generate category task input from embeddings.

    Simply copies embeddings with placeid as index.
    Rejects check-in-level engines (Time2Vec, Check2HGI) — category task
    requires one embedding per POI.

    Args:
        state: State name (e.g., 'alabama')
        engine: Embedding engine

    Raises:
        ValueError: If engine produces check-in-level embeddings.
    """
    if engine in _CHECKIN_LEVEL_ENGINES:
        raise ValueError(
            f"Engine {engine.value} produces check-in-level embeddings, which are "
            f"invalid for the category task (requires one embedding per POI). "
            f"Use a POI-level engine (HGI, DGI, Space2Vec, POI2HGI, HMRM) or "
            f"fusion mode with POI-level category embeddings."
        )

    embeddings_df = IoPaths.load_embedd(state, engine)
    output_path = IoPaths.get_category(state, engine)

    # Simple copy with placeid as index
    output_df = embeddings_df.copy()
    save_parquet(output_df, output_path)


def generate_next_input_from_poi(
    state: str,
    engine: EmbeddingEngine,
    batch_size: int = DEFAULT_BATCH_SIZE,
    stride: Optional[int] = None,
    min_sequence_length: int = MIN_SEQUENCE_LENGTH,
    emit_tail: Optional[bool] = None,
) -> None:
    """
    Generate next-POI input from POI-level embeddings.

    Uses embeddings that are constant per POI (e.g., HGI, Space2Vec, DGI).

    Args:
        state: State name
        engine: Embedding engine
        batch_size: Batch size for processing sequences
        stride: Step between sequence starts. ``None`` (default) → step ==
            window_size (non-overlapping), byte-identical to the legacy path.
        min_sequence_length: Minimum user check-ins to emit any sequence.
            Default == MIN_SEQUENCE_LENGTH (5) → legacy behaviour preserved.
        emit_tail: Whether to emit OOB tail windows (see ``generate_sequences``).
            ``None`` (default) → AUTO: emit at the default/non-overlap stride,
            but GATE (skip) them at ``stride==1`` (the M1 last-POI-target skew
            fix). Pass an explicit bool to override. AUTO at non-overlap keeps
            the legacy byte-identical behaviour.
    """
    emit_tail = _resolve_emit_tail(emit_tail, stride)
    # Load data
    embeddings_df = IoPaths.load_embedd(state, engine)
    checkins_df = IoPaths.load_city(state)

    # Build lookups — infer dimension from the embedding artifact
    numeric_cols = [c for c in embeddings_df.columns if c.isdigit()]
    embedding_dim = len(numeric_cols)
    embedding_lookup = create_embedding_lookup(embeddings_df, embedding_dim)
    category_lookup = create_category_lookup(checkins_df)

    # Generate sequences per user
    # M2 (2026-06-20): stable sort so datetime ties break deterministically
    # (numpy quicksort is non-deterministic run-to-run; an unstable order would
    # make the chronological "next" target ambiguous under same-timestamp ties).
    # Byte-identical where no ties exist (e.g. alabama: 0 ties).
    checkins_df = checkins_df.sort_values(['userid', 'datetime'], kind='mergesort')
    user_sequences = checkins_df.groupby('userid')['placeid'].apply(
        lambda places: generate_sequences(
            places.tolist(),
            stride=stride,
            min_sequence_length=min_sequence_length,
            emit_tail=emit_tail,
        )
    )

    # Flatten sequences into DataFrame
    sequences_data = []
    for userid, seqs in user_sequences.items():
        for seq in seqs:
            sequences_data.append(seq + [userid])

    window_size = InputsConfig.SLIDE_WINDOW
    seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
    sequences_df = pd.DataFrame(sequences_data, columns=seq_cols)

    # Save intermediate sequences
    sequences_path = IoPaths.get_seq_next(state, engine)
    save_parquet(sequences_df, sequences_path)

    # Convert sequences to embeddings using shared logic
    all_results = convert_sequences_to_poi_embeddings(
        sequences_df, embedding_lookup, category_lookup,
        window_size, embedding_dim, batch_size
    )

    # Save output
    save_next_input_dataframe(all_results, window_size, embedding_dim, state, engine)

    # Additive build-provenance sidecar (never gates anything)
    _write_build_provenance(
        state, engine, "next",
        min_sequence_length=min_sequence_length,
        stride=stride,
        window_size=window_size,
        emit_tail=emit_tail,
    )


def generate_next_input_from_checkins(
    state: str,
    engine: EmbeddingEngine,
    batch_size: int = DEFAULT_BATCH_SIZE,
    stride: int = None,
    min_sequence_length: int = MIN_SEQUENCE_LENGTH,
    emit_tail: Optional[bool] = None,
) -> None:
    """
    Generate next-POI input from check-in-level embeddings.

    Uses embeddings that vary per check-in (e.g., Time2Vec).
    Each check-in already has its contextual embedding.

    Memory-bounded build (default-preserving): rows are streamed to parquet in
    row-group chunks instead of accumulating all N rows in RAM. The legacy path
    held the per-row ``<U32`` list (``N × 578 × 128`` bytes) *plus* the
    ``np.array(results)`` copy in ``save_next_input_dataframe`` — peak ≈ 2× the
    ``<U32`` payload (~86× the output parquet, measured on alabama). At stride=1
    on a large state (CA, ~3M rows) that is ~440 GB and OOM-kills the box. Here
    each user's ``<U32`` rows are immediately converted to float32 + split off
    metadata and streamed out, so peak RAM is O(chunk) (~0.46 GB at the 200k-row
    default). The output parquet is byte-identical to the legacy single-shot
    write (same schema / column order / dtypes / row order). See
    ``core.NextInputStreamWriter`` and ``core.check_next_build_ram``.

    Args:
        state: State name
        engine: Embedding engine
        batch_size: Batch size for processing sequences (unused, kept for API compatibility)
        stride: Step between sequence starts. ``None`` (default) → step ==
            window_size (non-overlapping), byte-identical to the legacy path.
        min_sequence_length: Minimum user check-ins to emit any sequence.
            Default == MIN_SEQUENCE_LENGTH (5) → legacy behaviour preserved.
        emit_tail: Whether to emit OOB tail windows (see ``generate_sequences``).
            ``None`` (default) → AUTO: emit at the default/non-overlap stride,
            GATE at ``stride==1`` (the M1 skew fix). Explicit bool overrides.
    """
    emit_tail = _resolve_emit_tail(emit_tail, stride)
    # Load data
    embeddings_df = IoPaths.load_embedd(state, engine)

    # Embeddings are already at check-in level with category
    # No need for separate category lookup

    # Sort by user and time to ensure chronological order
    # M2 (2026-06-20): stable sort (see generate_next_input_from_poi) — deterministic
    # under datetime ties; byte-identical where none exist.
    embeddings_df = embeddings_df.sort_values(['userid', 'datetime'], kind='mergesort')

    # Detect embedding dimension from data
    numeric_cols = [c for c in embeddings_df.columns if c.isdigit()]
    embedding_dim = len(numeric_cols)
    emb_cols = [str(i) for i in range(embedding_dim)]
    window_size = InputsConfig.SLIDE_WINDOW
    num_features = window_size * embedding_dim

    # CPU-RAM guard: estimate the legacy-equivalent peak and (for the streaming
    # path) WARN if it would have blown the box; never raises here because the
    # streaming writer below keeps peak at O(chunk). For an exact pre-count we'd
    # have to materialise sequences, so we use a cheap upper bound: at stride=1
    # the row count is <= number of check-ins; at the default stride it is far
    # smaller. Use the check-in count as a conservative n_rows estimate.
    _est_rows = len(embeddings_df)
    check_next_build_ram(_est_rows, num_features, streaming=True)

    # Streaming writers — peak RAM is O(chunk), not O(N).
    next_writer = NextInputStreamWriter(
        IoPaths.get_next(state, engine), num_features
    )
    seq_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi', 'userid']
    poi_cols = [f'poi_{i}' for i in range(window_size)] + ['target_poi']
    seq_writer = _SequenceStreamWriter(
        IoPaths.get_seq_next(state, engine), seq_cols, poi_cols
    )

    for userid, user_df in tqdm(embeddings_df.groupby('userid'), desc="Processing users"):
        user_df = user_df.reset_index(drop=True)

        results, sequences = convert_user_checkins_to_sequences(
            user_df, emb_cols, window_size, embedding_dim,
            stride=stride, min_sequence_length=min_sequence_length,
            emit_tail=emit_tail,
        )

        # Convert this user's small <U32 batch to float32 + metadata immediately,
        # then stream out. The float32 round-trip of the string repr is lossless
        # (numpy's str repr of a float32 round-trips exactly), so the parquet is
        # byte-identical to save_next_input_dataframe's float32 cast.
        for row in results:
            next_writer.add(
                np.asarray(row[:num_features], dtype=np.float32),
                row[num_features],
                row[num_features + 1],
            )
        for seq in sequences:
            seq_writer.add(seq)
        # Free this user's batch before the next group accumulates.
        del results, sequences

    seq_writer.close()
    next_writer.close()

    # Additive build-provenance sidecar (never gates anything)
    _write_build_provenance(
        state, engine, "next",
        min_sequence_length=min_sequence_length,
        stride=stride,
        window_size=window_size,
        emit_tail=emit_tail,
    )
