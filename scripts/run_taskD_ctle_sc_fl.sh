#!/usr/bin/env bash
# Task D — CTLE-SC @ FL (UNGATED by the M4 diagnosis). CORRECTED: build_ctle_substrate emits to a
# SINGLE dir (output/check2hgi_ctle/florida/, overwritten per fold), but mac_baseline_compare --baseline
# ctle reads 5 SEPARATE staged cells at output/board_baselines/ctle/florida/s0_f{f}/. So we build each
# fold's leak-safe cell, STAGE it to s0_f{f}/ before the next fold overwrites, then compare.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_RAM_HEADROOM_GB=4
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export BASELINE_PY="$(which python)"

CELLS=output/board_baselines/ctle/florida
echo "=== [Task D] build + stage 5 leak-safe CTLE cells (stride-1) $(date -u) ==="
for f in 0 1 2 3 4; do
  echo "--- build_ctle_substrate fold $f ---"
  python scripts/baselines/build_ctle_substrate.py --state florida --seed 0 --fold "$f" --stride 1 \
    || { echo "[Task D] cell fold $f BUILD FAILED"; continue; }
  mkdir -p "$CELLS/s0_f$f"
  cp output/check2hgi_ctle/florida/embeddings.parquet "$CELLS/s0_f$f/embeddings.parquet"
  cp output/check2hgi_ctle/florida/CTLE_FOLD.txt      "$CELLS/s0_f$f/LEAK_MARKER.txt" 2>/dev/null || true
  echo "  staged -> $CELLS/s0_f$f/embeddings.parquet"
done

echo "=== [Task D] matched-head compare $(date -u) ==="
python scripts/closing_data/mac_baseline_compare.py --state florida --baseline ctle \
    --cells-root output --folds 5 --heads cat reg \
  && echo "[Task D] OK $(date -u)" || echo "[Task D] compare FAILED $(date -u)"
ls -la docs/results/closing_data/baseline_compare/florida_ctle.json 2>/dev/null
