#!/usr/bin/env bash
# F50 CHAMPION CANDIDATE — P4 alternating-SGD + OneCycleLR scheduler at FL 5f×50ep.
# Combines the two strongest signals from the F50 T3 work:
#   - P4 alternating-SGD: +3.83 pp Δreg with delayed-min selector (paired Wilcoxon p=0.0312)
#   - OneCycleLR: hypothesized to align peak LR with α-growth window (ep 15-20)
# If the two compose: expect +5-7 pp. If they don't: P4-alone recipe stands.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1"; shift
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
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
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --alternating-optimizer-step \
        --no-checkpoints --no-folds-cache \
        "$@" 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

# Champion candidate: P4 + OneCycle (with appropriate pct_start to peak around ep 15-20)
run "f50_champion_p4_onecycle_fl" \
    --scheduler onecycle --max-lr 3e-3 --pct-start 0.4

# Bonus: P4 + cosine (decay only — isolate warmup ramp from peak-LR effect)
run "f50_champion_p4_cosine_fl" \
    --scheduler cosine --max-lr 3e-3
