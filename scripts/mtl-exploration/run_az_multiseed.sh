#!/usr/bin/env bash
# Step 2: multi-seed AZ for linear_encoders+d=256 (cell C) vs baseline (cell D).
# Seeds {0, 1, 7, 100} x 5 folds each x 2 arms = 8 runs of 5f x 25ep at AZ.
# Per-seed per-fold log_T must be built first.

set -u
WORKTREE="$(pwd)"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-${WORKTREE}/.venv/bin/python}"
LOGDIR="${WORKTREE}/docs/studies/mtl-exploration/logs"
STATE=arizona
SEEDS=(0 1 7 100)
mkdir -p "${LOGDIR}"

ensure_per_fold_logT() {
    local s="$1"
    local need=0
    for f in 1 2 3 4 5; do
        [ -f "${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log_seed${s}_fold${f}.pt" ] || need=1
    done
    if [ "$need" -eq 1 ]; then
        echo "[per-fold log_T] building for seed=${s}"
        "$PY" -u scripts/compute_region_transition.py \
            --state "${STATE}" --per-fold --seed "$s" 2>&1 \
          | tee -a "${LOGDIR}/_per_fold_logT_build_${STATE}.log"
    else
        echo "[per-fold log_T] seed=${s} already built"
    fi
}

run_state() {
    local seed="$1"; local variant="$2"
    local extra_args=()
    if [ "${variant}" = "linear" ]; then
        extra_args=(--model-param shared_layer_size=256 --model-param linear_encoders=true)
    fi
    local tag="ms_${variant}_${STATE}_seed${seed}_5f25ep"
    echo "=== [${tag}] start $(date +%H:%M:%S)"
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${STATE}" --engine check2hgi \
        --model mtlnet_crossattn \
        ${extra_args[@]+"${extra_args[@]}"} \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 25 \
        --batch-size 2048 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
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

# Step 2a: build per-seed log_T for {0,1,7,100}
for s in "${SEEDS[@]}"; do
    ensure_per_fold_logT "$s"
done

# Step 2b: 5-fold runs at each seed for both arms
for s in "${SEEDS[@]}"; do
    run_state "$s" baseline || exit $?
    run_state "$s" linear   || exit $?
done

echo "AZ_MS_DONE" > "${LOGDIR}/_az_ms_done.flag"
echo "All AZ multi-seed runs done at $(date +%H:%M:%S)"
