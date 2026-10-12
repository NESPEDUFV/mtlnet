#!/usr/bin/env bash
# Multi-seed extension of the mtl-exploration factorial.
#   AL × 4 seeds × {baseline D, linear C, linear+LN E} = 12 runs
#   AZ × 4 seeds × {linear+LN E}                       =  4 runs
# Pairs with already-completed AZ × {D, C} multi-seed for the full factorial.
#
# Each run: 5 folds × 25 epochs, per-fold seed-tagged log_T.

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

SEEDS=(0 1 7 100)

ensure_per_fold_logT() {
    local state="$1"; local s="$2"
    local need=0
    for f in 1 2 3 4 5; do
        [ -f "${OUTPUT_DIR}/check2hgi/${state}/region_transition_log_seed${s}_fold${f}.pt" ] || need=1
    done
    if [ "$need" -eq 1 ]; then
        echo "[per-fold log_T] building for ${state} seed=${s}"
        "$PY" -u scripts/compute_region_transition.py \
            --state "${state}" --per-fold --seed "$s" 2>&1 \
          | tee -a "${LOGDIR}/_per_fold_logT_build_${state}.log"
    else
        echo "[per-fold log_T] ${state} seed=${s} already built"
    fi
}

run_state() {
    local state="$1"; local seed="$2"; local arm="$3"
    local extra_args=()
    case "${arm}" in
        baseline) extra_args=() ;;
        linear)   extra_args=(--model-param shared_layer_size=256 --model-param linear_encoders=true) ;;
        linear_ln) extra_args=(--model-param shared_layer_size=256 --model-param linear_ln_encoders=true) ;;
        *) echo "unknown arm: ${arm}"; return 2 ;;
    esac
    local tag="ms_${arm}_${state}_seed${seed}_5f25ep"
    echo "=== [${tag}] start $(date +%H:%M:%S)"
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        ${extra_args[@]+"${extra_args[@]}"} \
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

# Phase 1: build per-seed log_T at AL for {0,1,7,100} (AZ already built)
for s in "${SEEDS[@]}"; do
    ensure_per_fold_logT alabama "$s"
done

# Phase 2: AL × 3 arms × 4 seeds — interleave per seed to keep MPS warm
for s in "${SEEDS[@]}"; do
    run_state alabama "$s" baseline   || exit $?
    run_state alabama "$s" linear     || exit $?
    run_state alabama "$s" linear_ln  || exit $?
done

# Phase 3: AZ × E × 4 seeds (D and C already done)
for s in "${SEEDS[@]}"; do
    run_state arizona "$s" linear_ln  || exit $?
done

echo "MS_V2_DONE" > "${LOGDIR}/_ms_v2_done.flag"
echo "All runs complete at $(date +%H:%M:%S)"
