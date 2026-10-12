#!/usr/bin/env bash
# Brief experiment: B9 canonical recipe with --engine hgi instead of check2hgi.
# Tests whether the MTL recipe transfers across substrate.
#
# Pairs with existing Check2HGI baseline (AZ multi-seed) from Step 3.
# Per-fold log_T is engine-agnostic (region transitions depend on check-in
# sequence, not embeddings) — reuses the existing check2hgi-built files.
#
# Single seed for brevity: ~5 min AL + ~12 min AZ ≈ ~17 min total.

set -u
WORKTREE="$(pwd)"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-${WORKTREE}/.venv/bin/python}"
LOGDIR="${WORKTREE}/docs/studies/mtl-exploration/logs"
mkdir -p "${LOGDIR}"

run_state() {
    local state="$1"; local seed="${2:-42}"
    local tag="hgi_b9_${state}_seed${seed}_5f25ep"
    echo "=== [${tag}] start $(date +%H:%M:%S)"
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine hgi \
        --model mtlnet_crossattn \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 25 \
        --batch-size 2048 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${state}" \
        --no-checkpoints --no-folds-cache \
        --min-best-epoch 5 \
        --mtl-loss static_weight --category-weight 0.75 \
        --seed "${seed}" \
        --alternating-optimizer-step \
        --scheduler cosine --max-lr 3e-3 \
        --alpha-no-weight-decay \
        2>&1 | tee "${LOGDIR}/${tag}.log"
    local rc="${PIPESTATUS[0]}"
    echo "[${tag}] exit ${rc} at $(date +%H:%M:%S)"
    return "${rc}"
}

run_state alabama 42 || exit $?
run_state arizona 42 || exit $?
echo "HGI_DONE" > "${LOGDIR}/_hgi_substrate_done.flag"
echo "Both runs complete at $(date +%H:%M:%S)"
