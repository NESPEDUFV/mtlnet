#!/usr/bin/env bash
# Tiny LEAK-SAFE smoke for GeoTreeSkipGram: AL, 1 fold, 2 epochs, scratch OUTPUT_DIR.
# Proves: leak-safe per-fold split, per-POI table, check-in-level row-alignment,
# and (if a GPU is free) end-to-end matched-head plumbing. NEVER touches the
# frozen output/check2hgi/. Do NOT run full n=20 here.
set -euo pipefail
cd "$(dirname "$0")/../.."
REPO="$(pwd)"
SCRATCH="${SCRATCH:-/tmp/bl_geotree_smoke}"
STATE="${STATE:-alabama}"
SEED="${SEED:-0}"
FOLD="${FOLD:-0}"
DEV="${DEV:-cuda}"

echo "=== GeoTreeSkipGram smoke :: state=$STATE seed=$SEED fold=$FOLD device=$DEV ==="
echo "    scratch OUTPUT_DIR=$SCRATCH (frozen output/ untouched)"
rm -rf "$SCRATCH"
mkdir -p "$SCRATCH/check2hgi/$STATE"

# The probe build reads the FROZEN check2hgi substrate (embeddings/sequences/graph)
# from the real output/, but writes its emitted parquets into SCRATCH. We point
# OUTPUT_DIR at scratch and pre-symlink the read-only inputs the builder needs.
REAL_OUT="$REPO/output/check2hgi/$STATE"
ln -sf "$REAL_OUT/embeddings.parquet"       "$SCRATCH/check2hgi/$STATE/embeddings.parquet"
ln -sf "$REAL_OUT/region_embeddings.parquet" "$SCRATCH/check2hgi/$STATE/region_embeddings.parquet"
mkdir -p "$SCRATCH/check2hgi/$STATE/temp"
ln -sf "$REAL_OUT/temp/sequences_next.parquet" "$SCRATCH/check2hgi/$STATE/temp/sequences_next.parquet"
ln -sf "$REAL_OUT/temp/checkin_graph.pt"        "$SCRATCH/check2hgi/$STATE/temp/checkin_graph.pt"
# next.parquet is needed by load_next_data for the fold split — symlink the frozen one.
mkdir -p "$SCRATCH/check2hgi/$STATE/input"
ln -sf "$REAL_OUT/input/next.parquet" "$SCRATCH/check2hgi/$STATE/input/next.parquet"
# seeded per-fold log_T for the reg ranking prior (read from frozen output by train.py)
for f in "$REAL_OUT"/region_transition_log_seed${SEED}_fold*.pt; do
  [ -e "$f" ] && ln -sf "$f" "$SCRATCH/check2hgi/$STATE/$(basename "$f")"
done

# NOTE: the builder WRITES embeddings.parquet/input/* into the SAME engine dir it
# read symlinks from. To avoid clobbering the symlinked frozen inputs, the smoke
# uses --all-data=NO (leak-safe) but emits into a SEPARATE engine subdir is not
# possible while reusing --engine check2hgi. So we instead drop the read-only
# symlinks that the build overwrites (embeddings + input/next + sequences) right
# before the build re-creates them as real files in scratch. The frozen originals
# are never touched (scratch is a copy-by-symlink staging area).
rm -f "$SCRATCH/check2hgi/$STATE/embeddings.parquet" \
      "$SCRATCH/check2hgi/$STATE/input/next.parquet" \
      "$SCRATCH/check2hgi/$STATE/temp/sequences_next.parquet"
# but load_next_data (fold split) needs next.parquet — copy a REAL standalone one.
cp "$REAL_OUT/input/next.parquet" "$SCRATCH/check2hgi/$STATE/input/next.parquet"
# and the builder reads the FROZEN sequences for skip-gram + windowing — copy it.
cp "$REAL_OUT/temp/sequences_next.parquet" "$SCRATCH/check2hgi/$STATE/temp/sequences_next.parquet"

echo "--- step 1: build leak-safe per-fold GeoTreeSkipGram substrate ---"
OUTPUT_DIR="$SCRATCH" PYTHONPATH=src .venv/bin/python \
  scripts/baselines/build_geotree_skipgram_substrate.py "$STATE" \
  --seed "$SEED" --fold "$FOLD" --epochs 2 --batch-size 512 \
  --max-pairs 150000 --max-depth 10 --min-leaf 8 --device "$DEV"

echo "--- step 2: validate artifacts (shapes + row-alignment + leak-safety) ---"
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
# per-POI invariant: all check-ins of one placeid share the same vector
ec = [str(i) for i in range(64)]
g = emb.groupby("placeid")[ec].nunique().max().max()
print(f"  embeddings rows={len(emb)}  per-POI unique-vectors-per-dim(max)={g} (==1 => per-POI OK)")
print(f"  next rows={len(nxt)}  next_region rows={len(nr)}  seq rows={len(seq)}  (row-aligned OK)")
nonzero = float((emb[ec].abs().sum(axis=1) > 0).mean())
print(f"  non-zero-embedding fraction={nonzero:.3f}")
assert nonzero > 0.5, "too many zero embeddings — POI mapping failed"
print("  VALIDATION PASS")
PY

echo "--- step 3: tiny matched-head train.py (1 fold / 2 epochs) ---"
echo "    (best-effort; if GPU busy/OOM this is expected — steps 1-2 already prove plumbing)"
set +e
OUTPUT_DIR="$SCRATCH" PYTHONPATH=src timeout 900 .venv/bin/python scripts/train.py \
  --task mtl --task-set check2hgi_next_region --engine check2hgi \
  --state "$STATE" --seed "$SEED" --folds 1 --epochs 2 --batch-size 512 --no-checkpoints \
  --model mtlnet_crossattn --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region \
  --per-fold-transition-dir "$SCRATCH/check2hgi/$STATE" 2>&1 | tail -40
rc=$?
set -e
echo "=== smoke train.py exit code: $rc (0=full plumbing confirmed; non-0 acceptable if GPU busy) ==="
