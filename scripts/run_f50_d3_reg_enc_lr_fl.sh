#!/usr/bin/env bash
# F50 D3 — H3-alt MTL with separate reg_encoder_lr (10x reg_lr).
# Tests mechanism α: if reg encoder is under-trained because loss-side
# cat_weight=0.75 scaling shrinks effective reg gradient by 4x.
# reg_encoder_lr=3e-2 (10x reg_lr=3e-3) compensates.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" reg_enc_lr="$2"
    echo ""
    echo "=== [${tag}] start $(date) (reg_encoder_lr=${reg_enc_lr}) ==="
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
        --reg-encoder-lr "${reg_enc_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

# Sweep two values: 3e-2 (10x) and 1e-2 (3.3x)
run "f50_d3_reg_enc_lr_3e-2_fl" 3e-2
run "f50_d3_reg_enc_lr_1e-2_fl" 1e-2
