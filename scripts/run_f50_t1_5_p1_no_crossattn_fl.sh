#!/usr/bin/env bash
# F50 T1.5-P1 — `--disable-cross-attn` on H3-alt MTL, FL 5f×50ep.
#
# Bypasses the entire crossattn_blocks loop in MTLnetCrossAttn — pure
# parallel encoders (cat / reg) → final LN → heads. Tests whether the
# cross-attn shared layer is contributing at FL or is null/hurting.
# If P1 ≈ H3-alt at FL within σ, the cross-attn shared layer is null
# and "two STLs in a trenchcoat" is equivalent.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} cat=${cat_lr} reg=${reg_lr} shared=${shared_lr})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --model-param disable_cross_attn=true \
        --mtl-loss static_weight \
        --category-weight 0.75 \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t1_5_p1_no_crossattn_fl" florida 1e-3 3e-3 1e-3
