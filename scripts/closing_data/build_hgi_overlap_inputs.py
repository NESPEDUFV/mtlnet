#!/usr/bin/env python
"""Blocker 2 (Tbl 2) — build HGI-substrate category inputs under the OVERLAP windowing.

The Part-1 substrate table (Tbl 2: Check2HGI vs HGI category macro-F1) must live on ONE
windowing. The Check2HGI arm is already the board cat-STL ceiling under overlap
(`check2hgi_dk_ovl`); only the HGI arm under overlap is missing. This builds it.

Strategy (handoff §2.2, first recommendation — the bulletproof one):
  * REUSE the FROZEN `check2hgi_dk_ovl/<state>/temp/sequences_next.parquet` (stride-1,
    MIN_SEQ=10, emit_tail=False, gated). The windows are substrate-independent, so reusing
    the exact frozen sequences guarantees the HGI windows are BYTE-IDENTICAL to the
    Check2HGI arm — only the per-POI embedding lookup differs (HGI POI vector vs Check2HGI
    check-in vector). This is what the Tbl-2 contrast is supposed to isolate.
  * STREAM the output (NextInputStreamWriter, O(chunk) RAM). The legacy
    generate_next_input_from_poi accumulates all rows as a <U32 object array and would OOM
    on FL/CA/TX (~94-220 GB peak). Here the embedding gather is vectorised (E[idx_mat]) and
    only the per-row writer.add() buffers — peak RAM is O(chunk).

Output: output/hgi_dk_ovl/<state>/input/next.parquet  (+ symlinked HGI embeddings, + a
correct build-provenance sidecar so the board-overlap guard in folds.py passes under
MTL_STRICT=1).

Correctness gate (handoff §2.2): the produced row count MUST equal the Check2HGI-overlap
row count. By construction it equals the frozen sequence count; this script asserts it
against check2hgi_dk_ovl's next.parquet when that file is present (it was disk-reclaimed for
some big states — then the sequence count is the reference).

Usage:
  PYTHONPATH=src .venv/bin/python scripts/closing_data/build_hgi_overlap_inputs.py <state>
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm

from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR
from data.inputs.builders import _write_build_provenance
from data.inputs.core import (
    MISSING_CATEGORY_VALUE,
    NextInputStreamWriter,
    create_category_lookup,
)

HGI = EmbeddingEngine.HGI
C2H_OVL = EmbeddingEngine.CHECK2HGI_DK_OVL  # source of the frozen overlap windows
OVL = EmbeddingEngine.HGI_DK_OVL            # destination engine

CHUNK = 200_000  # rows per gather/write chunk (peak RAM ~ CHUNK * 576 * 4 bytes ~ 0.46 GB)


def _symlink(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src.resolve())
        print(f"  symlink {dst.name} -> {src}")
    else:
        print(f"  WARN: source missing, not symlinked: {src}")


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: build_hgi_overlap_inputs.py <state>")
    state = sys.argv[1]
    state_lc = state.lower()
    dst_dir = OUTPUT_DIR / OVL.value / state_lc
    print(f"=== build {OVL.value} category inputs for {state} "
          f"(reuse frozen {C2H_OVL.value} overlap sequences) ===")

    # 1. symlink HGI embeddings (windowing-independent) into the overlap engine dir.
    hgi_dir = OUTPUT_DIR / HGI.value / state_lc
    for f in ("embeddings.parquet", "region_embeddings.parquet"):
        _symlink(hgi_dir / f, dst_dir / f)

    # 2. load the FROZEN overlap sequences (the gated stride-1 windows; substrate-independent).
    seq_path = IoPaths.get_seq_next(state, C2H_OVL)
    if not seq_path.exists():
        raise SystemExit(f"frozen overlap sequences missing: {seq_path}")
    window_size = InputsConfig.SLIDE_WINDOW
    poi_cols = [f"poi_{i}" for i in range(window_size)]
    seq_df = pd.read_parquet(seq_path, columns=poi_cols + ["target_poi", "userid"])
    n_rows = len(seq_df)
    print(f"  frozen sequences: {seq_path}  rows={n_rows:,}")

    # 3. build a contiguous HGI embedding matrix + a poi_id -> row index map, with a
    #    dedicated zero PAD row at the end (covers padding -1 AND OOV POIs — matching the
    #    create_embedding_lookup .get(poi, zeros) semantics the Check2HGI/POI builders use).
    emb_df = IoPaths.load_embedd(state, HGI)
    numeric_cols = [c for c in emb_df.columns if c.isdigit()]
    embedding_dim = len(numeric_cols)
    assert embedding_dim == InputsConfig.EMBEDDING_DIM, (
        f"unexpected HGI embedding_dim {embedding_dim} != {InputsConfig.EMBEDDING_DIM}")
    ordered_cols = [str(i) for i in range(embedding_dim)]
    M = emb_df.set_index("placeid")[ordered_cols].to_numpy(dtype=np.float32)
    placeids = emb_df["placeid"].to_numpy()
    pad_row = M.shape[0]
    E = np.vstack([M, np.zeros((1, embedding_dim), dtype=np.float32)])  # (P+1, dim), pad at end
    id_to_row = dict(zip(placeids.tolist(), range(M.shape[0])))

    cat_lookup = create_category_lookup(IoPaths.load_city(state))

    # 4. vectorised gather indices: map every poi (and target) through id_to_row; -1/OOV -> pad.
    poi_mat = seq_df[poi_cols].to_numpy(dtype=np.int64)
    flat = pd.Series(poi_mat.ravel())
    idx_flat = flat.map(id_to_row)
    oov_hist = int(idx_flat.isna().sum())
    idx_mat = idx_flat.fillna(pad_row).to_numpy(dtype=np.int64).reshape(poi_mat.shape)
    # how many of the OOV are genuine pads (-1) vs unknown POIs?
    n_pad = int((poi_mat.ravel() == -1).sum())
    print(f"  history-POI gather: {oov_hist:,}/{poi_mat.size:,} -> pad row "
          f"({n_pad:,} are pad -1, {oov_hist - n_pad:,} are OOV-in-HGI)")

    tgt = seq_df["target_poi"].to_numpy(dtype=np.int64)
    cat_arr = np.array([cat_lookup.get(int(t), MISSING_CATEGORY_VALUE) for t in tgt], dtype=object)
    uid_arr = seq_df["userid"].to_numpy()

    # 5. stream chunks: vectorised gather E[idx] -> (chunk, 576) float32, write row-groups.
    num_features = window_size * embedding_dim
    out_path = IoPaths.get_next(state, OVL)
    writer = NextInputStreamWriter(out_path, num_features)
    for a in tqdm(range(0, n_rows, CHUNK), desc=f"{state} hgi-ovl"):
        b = min(a + CHUNK, n_rows)
        chunk = E[idx_mat[a:b]].reshape(b - a, num_features)  # float32 (nb, 576)
        cats = cat_arr[a:b]
        uids = uid_arr[a:b]
        for i in range(b - a):
            writer.add(chunk[i], cats[i], uids[i])
    n_written = writer.close()

    # 6. correct provenance sidecar (board-overlap guard reads stride/emit_tail/min_seq).
    _write_build_provenance(
        state, OVL, "next",
        min_sequence_length=10, stride=1, window_size=window_size, emit_tail=False,
    )

    # 7. row-count gate vs the Check2HGI-overlap arm.
    assert n_written == n_rows, f"row count drift: wrote {n_written} vs {n_rows} sequences"
    c2h_next = IoPaths.get_next(state, C2H_OVL)
    if c2h_next.exists():
        c2h_n = pd.read_parquet(c2h_next, columns=["userid"]).shape[0]
        status = "OK" if c2h_n == n_written else "MISMATCH"
        print(f"  [gate] hgi_dk_ovl rows={n_written:,} vs check2hgi_dk_ovl rows={c2h_n:,} -> {status}")
        if c2h_n != n_written:
            raise SystemExit("ROW-COUNT GATE FAILED — windowing desynced; stop.")
    else:
        print(f"  [gate] check2hgi_dk_ovl next.parquet absent (disk-reclaimed); "
              f"sequence count {n_rows:,} is the reference (matched by construction).")
    print(f"DONE: {OVL.value}/{state} next.parquet rows={n_written:,} -> {out_path}")


if __name__ == "__main__":
    main()
