#!/usr/bin/env bash
# F50 T3 Tier A — 7 CLI-only hyperparameter tests.
# Total ~2.2h compute (7 runs × 19 min) on RTX 4090.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

# Common flags shared across all Tier-A runs (the H3-alt baseline)
common_flags=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --mtl-loss static_weight --category-weight 0.75
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size "${BATCH_SIZE:-2048}"
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --no-checkpoints --no-folds-cache
)

run() {
    local tag="$1"; shift
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$PY" -u scripts/train.py "${common_flags[@]}" "$@" 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

# A1 — OneCycleLR scheduler
run "f50_t3_A1_onecycle50_fl" \
    --scheduler onecycle --max-lr 3e-3

# A3 — alpha_init=2.0 (skip α growth phase entirely)
run "f50_t3_A3_alpha_init_2.0_fl" \
    --scheduler constant \
    --reg-head-param alpha_init=2.0

# A5 — Stacked: OneCycle + alpha_init=2.0
run "f50_t3_A5_onecycle_alpha2_fl" \
    --scheduler onecycle --max-lr 3e-3 --pct-start 0.4 \
    --reg-head-param alpha_init=2.0

# A2 — Cosine scheduler (decay only, no warmup)
run "f50_t3_A2_cosine50_fl" \
    --scheduler cosine --max-lr 3e-3

# A6 — Combined: cw=0.25 + OneCycle
run "f50_t3_A6_cw0.25_onecycle_fl" \
    --category-weight 0.25 \
    --scheduler onecycle --max-lr 3e-3

# A4 — 100 epochs constant (sanity check that more wall time doesn't help)
# Note: 100 epochs ~38 min/run × 5 = 190 min just for this one. Defer; queue last.
run "f50_t3_A4_epochs100_constant_fl" \
    --epochs 100 \
    --scheduler constant

# A7 — Seed sanity (rerun H3-alt with seed=0 to bound seed noise)
# Skip A7 default for now — only run if A1-A6 are inconclusive.
# run "f50_t3_A7_seed0_fl" \
#     --scheduler constant --seed 0

echo ""
echo "================================================================"
echo "=== F50 T3 Tier A COMPLETE at $(date)"
echo "================================================================"
