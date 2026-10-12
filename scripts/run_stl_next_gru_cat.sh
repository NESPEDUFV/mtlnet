#!/usr/bin/env bash
# STL next_gru cat — matched-head STL baseline for B3 (post-F27).
#
# Motivation: MTL-B3 swapped task_a head from `next_mtl` → `next_gru` in F27
# (2026-04-24). The current STL cat baseline still uses `next_mtl` (matched
# with the PRE-F27 MTL config), which makes the MTL-over-STL cat comparison
# asterisked. This script runs STL with `next_gru` head so we can report
# MTL-B3 > matched-head STL without the architectural asterisk.
#
# Protocol: 5f × 50ep, seed 42, user-disjoint StratifiedGroupKFold,
# batch 2048, AdamW lr=1e-4 + OneCycleLR max_lr=3e-3 (matches MTL B3).
#
# Expected cost (MPS): AL ~30 min, AZ ~45 min, FL ~2 h.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/P1_5b_post_f27"
mkdir -p "${DEST}"

run() {
    local tag="$1" state="$2" folds="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state}, folds=${folds})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task next \
        --state "${state}" \
        --engine check2hgi \
        --model next_gru \
        --folds "${folds}" --epochs 50 --seed 42 \
        --batch-size 2048 \
        --max-lr 3e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

# Sequential: AL → AZ → FL (FL is 1-fold, aligned with current ablation
# tables; upgrade to 5f once F33 Colab lands).
run "stl_gru_cat_al" alabama 5
run "stl_gru_cat_az" arizona 5
run "stl_gru_cat_fl" florida 1

echo ""
echo "================================================================"
echo "=== STL next_gru cat complete at $(date)"
echo "=== Result JSONs land under:"
echo "===   results/check2hgi/<state>/next_lr1.0e-04_bs2048_ep50_*/summary/"
echo "=== Archive the summary.json to: ${DEST}/"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
