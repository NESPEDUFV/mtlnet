#!/usr/bin/env bash
# Task A (BASELINE_H100 §2): Check2HGI-SC comparand @ FL (seed0 x 5f).
# Step 1 (build_overlap_probe_engine) SKIPPED — already built (rowcount 1,274,418, Jun 22).
# Step 2: per-fold log_T for dk_ovl engine (leak-free train-only prior).
# Step 3: comparand training (cat + reg heads).
set -euo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
# fp32 (protocol §0) — the STL trainer/eval autocast fp16 has no GradScaler and NaN-collapses
# at FL scale on CUDA. DISABLE_AMP forces fp32, matching the Mac (MPS) board numbers.
export DISABLE_AMP=1 MTL_DISABLE_AMP=1

echo "=== [Task A] START $(date -u) ==="

echo "--- Step 2: per-fold log_T (florida / check2hgi_dk_ovl / seed0 / 5 folds) ---"
python scripts/compute_region_transition.py --state florida \
    --engine check2hgi_dk_ovl --per-fold --seed 0 --n-splits 5
echo "--- Step 2 DONE $(date -u) ---"

echo "--- Step 3: comparand_check2hgi_sc (florida, 5 folds, cat reg) ---"
python scripts/closing_data/comparand_check2hgi_sc.py \
    --state florida --folds 5 --heads cat reg
echo "--- Step 3 DONE $(date -u) ---"

echo "=== [Task A] COMPLETE $(date -u) ==="
echo "--- output json ---"
ls -la docs/results/closing_data/baseline_compare/florida_check2hgi_sc.json || echo "WARN: output json missing"
