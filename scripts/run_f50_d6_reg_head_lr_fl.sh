#!/usr/bin/env bash
# F50 D6 — H3-alt MTL with reg_head_lr=3e-2 (10x reg_lr) at FL 5f×50ep.
# Boosts LR for next_poi params (where α scalar lives in next_getnext_hard).
# Tests if α growth is the FL bottleneck per the D1 + cat_weight finding:
#   STL α=0 → 72.61 ≈ MTL → 73.61. STL α-trainable → 82.44.
#   The prior is functionally disabled in MTL → α isn't growing under
#   joint-loss training. Boosting reg_head_lr should let α grow.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" rh_lr="$2"
    echo ""
    echo "=== [${tag}] start $(date) (reg_head_lr=${rh_lr}) ==="
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state florida --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --reg-head-lr "${rh_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_d6_reg_head_lr_3e-2_fl" 3e-2
run "f50_d6_reg_head_lr_1e-1_fl" 1e-1
