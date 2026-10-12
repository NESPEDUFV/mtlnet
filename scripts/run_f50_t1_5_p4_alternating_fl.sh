#!/usr/bin/env bash
# F50 T1.5-P4 — `--alternating-optimizer-step` on H3-alt MTL, FL 5f×50ep.
#
# Per-batch alternating-SGD: even batches update cat-side params from
# L_cat only; odd batches update reg-side params from L_reg only.
# Shared params see one task's gradient signal per batch (alternating).
#
# Tests: does fine-grained per-task alternation prevent the shared
# backbone from being hijacked by either loss? If P4 recovers FL Δm,
# the FL flaw is "joint backward overweights the larger-magnitude
# gradient signal", and alternation is the fix.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "=== [${tag}] start $(date) ==="
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --alternating-optimizer-step \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t1_5_p4_alternating_fl" florida 1e-3 3e-3 1e-3
