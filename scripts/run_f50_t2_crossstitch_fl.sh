#!/usr/bin/env bash
# F50 T2 — Cross-Stitch (mtlnet_crossstitch) at FL 5f×50ep with H3-alt-style per-head LR.
#
# Tests "learned-vs-forced sharing" hypothesis. Two variants:
#   default (alpha=[[0.9, 0.1], [0.1, 0.9]] init, no detach) — cross-stream
#     gradient flow exists (F49 mechanism in milder form). Tests "learned
#     sharing fraction" hypothesis directly.
#   With env DETACH=1 — uses --model-param detach_cross_stream=true to sever
#     off-diagonal gradient path. Tests "explicit task-specific structure
#     with NO F49 leakage" hypothesis (cleaner than default).
#
# Param count ~6.88M (-13% vs cross-attn 7.9M; alpha matrices are tiny).

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

DETACH_FLAG=""
TAG_SUFFIX=""
if [[ "${DETACH:-0}" == "1" ]]; then
    DETACH_FLAG="--model-param detach_cross_stream=true"
    TAG_SUFFIX="_detach"
fi

run() {
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "=== [${tag}] start $(date) ==="
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossstitch \
        ${DETACH_FLAG} \
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
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t2_crossstitch_fl${TAG_SUFFIX}" florida 1e-3 3e-3 1e-3
