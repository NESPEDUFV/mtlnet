#!/usr/bin/env python
"""Build the isolated OVERLAP probe-engine dir (CHECK2HGI_DK_OVL) for the real-pipeline validation.

v14 (design_k) embeddings, re-windowed at stride=1 (overlapping). embeddings/region/poi are symlinked
from v14 (identical); ONLY the windowing differs. Frozen v14 substrate is untouched. The real trainers
(train.py / p1 / MTL) then read this engine to confirm the overlap lift the isolated harness found
(cat AL +9.50, reg AL +4.97) in the actual pipeline.

Usage: PYTHONPATH=src .venv/bin/python scripts/mtl_improvement/build_overlap_probe_engine.py <state> [stride]
"""
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR
from data.inputs.builders import generate_next_input_from_checkins

V14 = EmbeddingEngine.CHECK2HGI_DESIGN_K_RESLN_MAE_L0_1
OVL = EmbeddingEngine.CHECK2HGI_DK_OVL


def _symlink(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src.resolve())
        print(f"  symlink {dst.name} -> {src}")


def build_next_region_for(state: str, engine: EmbeddingEngine):
    """Engine-aware next_region build: replicate build_next_region_frame on THIS engine's
    next.parquet + sequences (overlapping), using check2hgi graph maps for poi->region."""
    from data.inputs.region_sequence import _load_graph_maps
    next_df = IoPaths.load_next(state, engine)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    assert len(next_df) == len(seq_df), (len(next_df), len(seq_df))
    # pipeline_audit 2026-07-01 (V7) — row-count parity is NOT sufficient: a
    # stale seq file with equal per-user counts would silently mis-pair every
    # (X, region-label) row. Mirror the canonical per-row userid content guard
    # (next_region.py:87-103 / folds._load_and_validate_check2hgi_data).
    _next_uids = next_df["userid"].astype(str).to_numpy()
    _seq_uids = seq_df["userid"].astype(str).to_numpy()
    assert (_next_uids == _seq_uids).all(), (
        f"next.parquet and sequences_next.parquet userids are not row-aligned "
        f"for {state}/{engine.value} — stale/mixed build; rebuild both in one pass."
    )
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1
    tgt = seq_df["target_poi"].astype(np.int64).to_numpy()
    # M3 (2026-06-20): guard OOV target POIs. Without this, .map() returns NaN for
    # any target not in placeid_to_idx and .to_numpy(int64) silently coerces NaN to
    # a huge negative int, which then negative-indexes poi_to_region (wrong region)
    # or raises a cryptic IndexError. Mirror the last_region path's explicit guard.
    poi_idx_s = pd.Series(tgt).map(placeid_to_idx)
    oov = int(poi_idx_s.isna().sum())
    if oov:
        bad = sorted(set(tgt[poi_idx_s.isna().to_numpy()].tolist()))[:10]
        raise ValueError(
            f"{state}/{engine.value}: {oov} target_poi values are not in the "
            f"check2hgi placeid_to_idx vocabulary (e.g. {bad}). The probe engine's "
            f"sequences are out of sync with the check2hgi graph maps — rebuild the "
            f"engine's sequences against the same graph."
        )
    poi_idx = poi_idx_s.to_numpy(dtype=np.int64)
    region_idx = poi_to_region[poi_idx]
    # last_region_idx from poi_{0..8}
    poi_cols = [f"poi_{i}" for i in range(9)]
    poi_mat = seq_df[poi_cols].astype(np.int64).to_numpy()
    last_region = np.full(len(seq_df), -1, np.int64)
    for r in range(len(seq_df)):
        valid = np.where(poi_mat[r] >= 0)[0]
        if len(valid):
            pi = placeid_to_idx.get(int(poi_mat[r][valid[-1]]), None)
            if pi is not None:
                last_region[r] = poi_to_region[pi]
    out = next_df.copy()
    out["region_idx"] = region_idx
    out["last_region_idx"] = last_region
    dst = IoPaths.get_next_region(state, engine)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dst, index=False)
    print(f"  next_region -> {dst}  (rows={len(out)}, n_regions={n_regions}, "
          f"pad={(last_region<0).mean()*100:.1f}%)")


# Board overlap windowing = stride-1, GATED (emit_tail auto-off at stride==1), MIN_SEQ=10.
# min_seq defaults to 10 HERE (board value) rather than core.py's global 5 — the overlap
# engine is board-only, so this never touches the frozen non-overlap v11/v14 substrate
# (which must stay at the global MIN_SEQ=5 for §0.1 reproduction; see DEFAULTS_AND_GUARDS
# TRAP #1). Override with argv[3].
BOARD_MIN_SEQ = 10


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "alabama"
    stride = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    min_seq = int(sys.argv[3]) if len(sys.argv) > 3 else BOARD_MIN_SEQ
    src_dir = OUTPUT_DIR / V14.value / state.lower()
    dst_dir = OUTPUT_DIR / OVL.value / state.lower()
    print(f"=== build overlap probe engine {OVL.value} for {state} "
          f"(stride={stride}, min_seq={min_seq}) ===")
    # 1. symlink the shared (windowing-independent) artifacts from v14
    for f in ("embeddings.parquet", "region_embeddings.parquet", "poi_embeddings.parquet"):
        _symlink(src_dir / f, dst_dir / f)
    # 2. build overlapping next.parquet + sequences_next.parquet into the probe dir
    print("  building overlapping next.parquet + sequences "
          "(stride=%d, min_seq=%d)..." % (stride, min_seq))
    generate_next_input_from_checkins(state, OVL, stride=stride, min_sequence_length=min_seq)
    # 3. build overlapping next_region.parquet
    build_next_region_for(state, OVL)
    n = len(IoPaths.load_next(state, OVL))
    print(f"DONE: {OVL.value}/{state} next.parquet rows={n:,}")


if __name__ == "__main__":
    main()
