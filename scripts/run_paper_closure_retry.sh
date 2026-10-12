#!/usr/bin/env bash
# Paper-closure recovery script for the 17 runs that failed in the
# 2026-05-01 attempt. Two failure modes were diagnosed:
#   1. CA + TX MTL pairs OOM'd on H100 (~40 GB each + 9 GB train-side
#      logit cat spike). Fix: serialize big-state MTL.
#   2. p1_region_head_ablation.py expected legacy unseeded log_T.
#      Fix: patched script to use seeded naming with legacy fallback.
#
# Already-completed runs (do NOT re-run, would overwrite results):
#   - paper_close_ca_h3alt
#   - paper_close_california_stl_cat / paper_close_texas_stl_cat
#   - paper_close_alabama_b9_seed{0,1,7,100}
#   - paper_close_arizona_b9_seed{0,1,7,100}
#
# Reruns (17 total):
#   3 MTL CA/TX (serial, big state OOM-safe)
#   2 STL reg CA/TX
#   4 FL STL reg multi-seed
#   4 AL STL reg multi-seed
#   4 AZ STL reg multi-seed

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
# Memory pressure mitigation per the OOM error suggestion.
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
PY="${PY:-python}"
cd "${WORKTREE}"
mkdir -p logs

run_fg() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    "$PY" -u "$@" >"logs/${tag}.log" 2>&1
    rc=$?
    echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

wait_slot() {
    while [ "$(jobs -rp | wc -l)" -ge "${MAX_JOBS}" ]; do
        wait -n
    done
}

run_bg() {
    local tag="$1"; shift
    wait_slot
    (
        echo "================================================================"
        echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u "$@" >"logs/${tag}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

# ============================================================
# PHASE A — MTL CA/TX SERIAL (3 runs, 60-90 min total)
# ============================================================
mtl_common_state() {
    local STATE="$1"
    local SDIR="${OUTPUT_DIR}/check2hgi/${STATE}"
    cat <<EOF
--task mtl --task-set check2hgi_next_region
--state ${STATE} --engine check2hgi
--model mtlnet_crossattn
--cat-head next_gru --reg-head next_getnext_hard
--reg-head-param d_model=256 --reg-head-param num_heads=8
--reg-head-param transition_path=${SDIR}/region_transition_log.pt
--task-a-input-type checkin --task-b-input-type region
--folds 5 --epochs 50 --seed 42
--batch-size 2048
--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
--gradient-accumulation-steps 1
--per-fold-transition-dir ${SDIR}
--no-checkpoints --no-folds-cache
--min-best-epoch 5
--mtl-loss static_weight --category-weight 0.75
EOF
}

# CA-B9
run_fg "paper_close_ca_b9_retry" scripts/train.py \
    $(mtl_common_state california) \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

# TX-B9
run_fg "paper_close_tx_b9_retry" scripts/train.py \
    $(mtl_common_state texas) \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

# TX-H3-alt
run_fg "paper_close_tx_h3alt_retry" scripts/train.py \
    $(mtl_common_state texas) \
    --scheduler constant --max-lr 3e-3

echo "=== Phase A (MTL retries) done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# ============================================================
# PHASE B — STL reg retries (small models, parallel)
# 14 runs total: CA + TX (seed 42), FL × 4 seeds, AL × 4 seeds, AZ × 4 seeds.
# STL reg uses just the head — ~5-8 GB GPU each. 4-way parallel safe.
# ============================================================
MAX_JOBS=4

stl_reg() {
    local STATE="$1" SEED="$2" TAG="$3"
    local SDIR="${OUTPUT_DIR}/check2hgi/${STATE}"
    run_bg "${TAG}" scripts/p1_region_head_ablation.py \
        --state "${STATE}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed "${SEED}" --input-type region \
        --region-emb-source check2hgi \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${SDIR}/region_transition_log.pt" \
        --per-fold-transition-dir "${SDIR}" \
        --tag "${TAG}" \
        --no-resume \
        --max-lr 1e-3
}

# CA + TX seed=42
stl_reg california 42 paper_close_california_stl_reg_retry
stl_reg texas      42 paper_close_texas_stl_reg_retry

# FL multi-seed extension
for SEED in 0 1 7 100; do
    stl_reg florida "${SEED}" "paper_close_fl_stl_reg_seed${SEED}_retry"
done

# AL + AZ multi-seed
for STATE in alabama arizona; do
    for SEED in 0 1 7 100; do
        stl_reg "${STATE}" "${SEED}" "paper_close_${STATE}_stl_reg_seed${SEED}_retry"
    done
done

wait
echo "================================================================"
echo "=== All retries done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
