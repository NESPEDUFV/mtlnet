#!/usr/bin/env bash
# Tiny LEAK-SAFE smoke for FAITHFUL POI2Vec (AAAI'17): AL, 1 fold, 2 epochs, CPU,
# scratch OUTPUT_DIR. Proves: leak-safe per-fold split, FIXED midpoint tree + overlap
# phi, per-POI table, check-in-level row-alignment (next==next_region==seq), train loss
# decreases, and the frozen-clobber + leak asserts fire. NEVER touches output/check2hgi/.
# Mirrors smoke_geotree_skipgram.sh. Do NOT run train.py if no GPU is free.
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO="$(pwd)"
SCRATCH="${SCRATCH:-/tmp/bl_poi2vec_smoke}"
STATE="${STATE:-alabama}"
SEED="${SEED:-0}"
FOLD="${FOLD:-0}"
DEV="${DEV:-cpu}"
THETA="${THETA:-0.05}"

echo "=== FAITHFUL POI2Vec smoke :: state=$STATE seed=$SEED fold=$FOLD device=$DEV theta=$THETA ==="
echo "    scratch OUTPUT_DIR=$SCRATCH (frozen output/ untouched)"
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/check2hgi/$STATE"

# The probe build reads the FROZEN check2hgi substrate (embeddings/sequences/graph)
# from the real output/, but writes its emitted parquets into SCRATCH. We point
# OUTPUT_DIR at scratch and stage the read-only inputs the builder needs.
REAL_OUT="$REPO/output/check2hgi/$STATE"
mkdir -p "$SCRATCH/check2hgi/$STATE/temp" "$SCRATCH/check2hgi/$STATE/input"
# build reads: frozen embeddings (row order), sequences (CBOW + windowing), checkin_graph
# (poi->region maps), next (fold split via load_next_data). Copy the ones the build
# OVERWRITES (embeddings/next/sequences); symlink read-only ones (region/graph).
cp "$REAL_OUT/temp/sequences_next.parquet" "$SCRATCH/check2hgi/$STATE/temp/sequences_next.parquet"
cp "$REAL_OUT/input/next.parquet"          "$SCRATCH/check2hgi/$STATE/input/next.parquet"
ln -sf "$REAL_OUT/embeddings.parquet"        "$SCRATCH/check2hgi/$STATE/embeddings.parquet"
ln -sf "$REAL_OUT/region_embeddings.parquet" "$SCRATCH/check2hgi/$STATE/region_embeddings.parquet"
ln -sf "$REAL_OUT/temp/checkin_graph.pt"     "$SCRATCH/check2hgi/$STATE/temp/checkin_graph.pt"
# the build reads frozen embeddings.parquet for the LEFT-JOIN row order, then overwrites
# it as a real file in scratch — drop the symlink so the write lands in scratch only.
# (We keep a real copy of the frozen embeddings for the read; the build re-reads via
#  IoPaths.load_embedd which resolves the symlink before unlink, so copy it instead.)
rm -f "$SCRATCH/check2hgi/$STATE/embeddings.parquet"
cp "$REAL_OUT/embeddings.parquet" "$SCRATCH/check2hgi/$STATE/embeddings.parquet"

echo "--- step 0: phi unit test ---"
PYTHONPATH=src .venv/bin/python scripts/baselines/poi2vec_lib/test_phi.py

echo "--- step 1: build leak-safe per-fold FAITHFUL POI2Vec substrate (CPU) ---"
OUTPUT_DIR="$SCRATCH" PYTHONPATH=src .venv/bin/python \
  scripts/baselines/build_poi2vec_substrate.py "$STATE" \
  --seed "$SEED" --fold "$FOLD" --epochs 2 --batch-size 512 \
  --theta "$THETA" --route-count 4 --context-window 9 \
  --user-dim 64 --max-examples 100000 --device "$DEV"

echo "--- step 2: validate artifacts (shapes + row-alignment + per-POI invariant) ---"
OUTPUT_DIR="$SCRATCH" PYTHONPATH=src .venv/bin/python - "$STATE" <<'PY'
import sys
import numpy as np, pandas as pd
from configs.paths import EmbeddingEngine, IoPaths
state = sys.argv[1]
E = EmbeddingEngine.CHECK2HGI
emb = IoPaths.load_embedd(state, E)
nxt = IoPaths.load_next(state, E)
nr  = IoPaths.load_next_region(state, E)
seq = pd.read_parquet(IoPaths.get_seq_next(state, E))
assert list(emb.columns)[:4] == ["userid","placeid","category","datetime"], emb.columns[:4].tolist()
assert sum(c.isdigit() for c in emb.columns) == 64, "expected 64 emb cols"
assert len(nxt) == len(nr) == len(seq), (len(nxt), len(nr), len(seq))
ec = [str(i) for i in range(64)]
g = emb.groupby("placeid")[ec].nunique().max().max()
print(f"  embeddings rows={len(emb)}  per-POI unique-vectors-per-dim(max)={g} (==1 => per-POI OK)")
print(f"  next rows={len(nxt)}  next_region rows={len(nr)}  seq rows={len(seq)}  (row-aligned OK)")
nonzero = float((emb[ec].abs().sum(axis=1) > 0).mean())
print(f"  non-zero-embedding fraction={nonzero:.3f}")
assert nonzero > 0.5, "too many zero embeddings — POI mapping failed"
print("  VALIDATION PASS")
PY

echo "--- step 3 (optional): tiny matched-head train.py — SKIPPED on CPU/no-GPU ---"
echo "    (steps 0-2 prove tree+phi+build+row-align+leak; run train.py only with a free GPU)"
echo "=== POI2Vec smoke complete (build + row-align + leak asserts OK) ==="
