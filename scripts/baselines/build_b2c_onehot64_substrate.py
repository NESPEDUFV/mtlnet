#!/usr/bin/env python
"""B2c — one-hot-POI 64-d (zero-training floor) probe-engine substrate builder.

SPEC (board baseline B2c):
    A FIXED 64-d deterministic random projection of the POI id (seeded), emitted as
    the substrate column parquet for a probe-engine, then run UNDER the matched
    champion heads (cat=next_gru, reg=next_stan_flow_dualtower) via train.py --engine.

    NO training.  The 64-d vector for a POI is a pure, seeded function of its placeid:
        emb[placeid] = G[ rank(placeid) ]        where  G ~ N(0, 1/sqrt(64)) seeded
    This is the *dense random-projection* relaxation of a one-hot-POI table (a true
    one-hot of ~12k POIs is 12k-d; the standard zero-training floor projects it to a
    fixed 64-d random subspace — the Johnson-Lindenstrauss / random-features trick).

WHY this is the trivial absolute-zero floor:
  * NO pretraining of any kind → there is NOTHING to overfit on the val users
    → it is LEAK-SAFE BY CONSTRUCTION (see section "LEAK-SAFETY" below). It does not
    even read fold indices: the same fixed table is reused for every state/seed/fold.
  * Windowing-INDEPENDENT: the per-POI vector does not depend on sequences, so the
    same embeddings.parquet feeds stride-9 (now) and stride-1 (P3) builds unchanged.
  * Fully REUSABLE: one table per (state) — not per (state, seed, fold).

It is the integration TEMPLATE for the class-(A) SC-SUBSTRATE-COLUMN baselines: it
mirrors scripts/mtl_improvement/build_overlap_probe_engine.py exactly, except the
embeddings.parquet *values* are the seeded projection instead of symlinked from a
trained substrate.

Artifacts emitted under  $OUTPUT_DIR/baseline_b2c_onehot64/<state>/ :
    embeddings.parquet            (userid, placeid, category, datetime, "0".."63")
    input/next.parquet            (built by generate_next_input_from_checkins)
    temp/sequences_next.parquet   (built by generate_next_input_from_checkins)
    input/next_region.parquet     (built by build_next_region_for)
    region_embeddings.parquet     (SYMLINK from check2hgi — shared geographic partition)
    poi_embeddings.parquet        (SYMLINK from check2hgi — optional, shared graph)

The region label space + poi_to_region map + per-fold seeded log_T are the SHARED
CHECK2HGI geographic artifacts (substrate-independent), so B2c reuses
output/check2hgi/<state>/temp/checkin_graph.pt and the region_transition_log_*.pt
files via --per-fold-transition-dir output/check2hgi/<state> at train time.

Usage:
    PYTHONPATH=src OUTPUT_DIR=output \
      .venv/bin/python scripts/baselines/build_b2c_onehot64_substrate.py <state> [seed] [stride]

  seed   : RNG seed for the fixed projection (default 1234; the SUBSTRATE seed, NOT
           the fold seed — the floor is the same table for all fold seeds, so leave
           it at the default for the scored board).
  stride : window stride passed to the builder (default None = canonical stride-9;
           pass 1 for the P3 overlapping-window paper build).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR
from data.inputs.builders import generate_next_input_from_checkins

# the canonical source substrate we borrow ROW ORDER + the shared region/graph from
SRC = EmbeddingEngine.CHECK2HGI
B2C = EmbeddingEngine.BASELINE_B2C_ONEHOT64

EMB_DIM = 64
DEFAULT_SUBSTRATE_SEED = 1234


def _symlink(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src.resolve())
        print(f"  symlink {dst.name} -> {src}")
    else:
        print(f"  WARN: source missing, no symlink: {src}")


def build_pojection_table(placeids: np.ndarray, seed: int) -> np.ndarray:
    """FIXED, seeded 64-d Gaussian random projection of each distinct POI id.

    Deterministic in (sorted-unique placeids, seed). NO data is fit. Each distinct
    POI gets one fixed N(0, 1/sqrt(D)) row; the projection is L2-normalised so the
    scale matches a typical trained substrate (keeps the heads' LayerNorm happy).
    """
    uniq = np.unique(placeids)
    rng = np.random.default_rng(seed)
    G = rng.standard_normal((len(uniq), EMB_DIM)).astype(np.float32)
    G /= np.sqrt(EMB_DIM)                       # JL-style scaling
    # L2-normalise per POI (unit sphere) — stable, scale-free floor
    norms = np.linalg.norm(G, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    G = G / norms
    return uniq, G


def build_b2c_embeddings(state: str, seed: int) -> pd.DataFrame:
    """Replace the check2hgi embedding columns with the B2c fixed projection,
    keeping the EXACT check-in rows (userid, placeid, category, datetime) and order
    so generate_next_input_from_checkins row-aligns with the matched-head inputs."""
    src = IoPaths.load_embedd(state, SRC)
    meta_cols = [c for c in ("userid", "placeid", "category", "datetime") if c in src.columns]
    assert "placeid" in meta_cols, f"check2hgi embeddings missing 'placeid': {src.columns.tolist()}"

    placeids = src["placeid"].to_numpy()
    uniq, table = build_pojection_table(placeids, seed)
    # map each check-in row -> its POI's fixed vector
    pos = {int(p): i for i, p in enumerate(uniq)}
    idx = np.fromiter((pos[int(p)] for p in placeids), count=len(placeids), dtype=np.int64)
    emb = table[idx]                            # [n_checkins, 64], POI-constant

    out = src[meta_cols].copy().reset_index(drop=True)
    emb_df = pd.DataFrame(emb, columns=[str(i) for i in range(EMB_DIM)])
    out = pd.concat([out, emb_df], axis=1)
    return out


def build_next_region_for(state: str, engine: EmbeddingEngine):
    """Identical to build_overlap_probe_engine.build_next_region_for: derive
    region_idx / last_region_idx from THIS engine's sequences using the SHARED
    check2hgi graph maps (poi_to_region)."""
    from data.inputs.region_sequence import _load_graph_maps
    next_df = IoPaths.load_next(state, engine)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    assert len(next_df) == len(seq_df), (len(next_df), len(seq_df))
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1
    tgt = seq_df["target_poi"].astype(np.int64).to_numpy()
    poi_idx = pd.Series(tgt).map(placeid_to_idx).to_numpy(dtype=np.int64)
    region_idx = poi_to_region[poi_idx]
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
          f"pad={(last_region < 0).mean() * 100:.1f}%)")


def main():
    state = sys.argv[1] if len(sys.argv) > 1 else "alabama"
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_SUBSTRATE_SEED
    stride = int(sys.argv[3]) if len(sys.argv) > 3 else None
    src_dir = OUTPUT_DIR / SRC.value / state.lower()
    dst_dir = OUTPUT_DIR / B2C.value / state.lower()
    print(f"=== build B2c one-hot-POI-64 probe engine {B2C.value} for {state} "
          f"(substrate_seed={seed}, stride={stride}) ===")

    # 1. emit the FIXED-projection embeddings.parquet (row-aligned with check2hgi)
    emb = build_b2c_embeddings(state, seed)
    dst_dir.mkdir(parents=True, exist_ok=True)
    emb_path = IoPaths.get_embedd(state, B2C)
    emb.to_parquet(emb_path, index=False)
    print(f"  embeddings.parquet -> {emb_path}  "
          f"(rows={len(emb):,}, distinct_pois={emb['placeid'].nunique():,}, dim={EMB_DIM})")

    # 2. symlink the SHARED (substrate-independent) region/poi artifacts from check2hgi
    for f in ("region_embeddings.parquet", "poi_embeddings.parquet"):
        _symlink(src_dir / f, dst_dir / f)

    # 3. build next.parquet + sequences_next.parquet from the B2c embeddings
    print(f"  building next.parquet + sequences (stride={stride})...")
    generate_next_input_from_checkins(state, B2C, stride=stride)

    # 4. build next_region.parquet (region labels from the SHARED graph maps)
    build_next_region_for(state, B2C)

    n = len(IoPaths.load_next(state, B2C))
    print(f"DONE: {B2C.value}/{state} next.parquet rows={n:,}")


if __name__ == "__main__":
    main()
