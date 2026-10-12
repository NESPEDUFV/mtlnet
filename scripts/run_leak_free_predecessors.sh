#!/usr/bin/env bash
# Re-run the predecessor champions with --per-fold-transition-dir so we can
# verify the relative ordering survives the C4 correction. Without these,
# the leak-free champion verdict (B9 +0.24 vs P0-A) is ungrounded relative
# to the broader study.
#
# Recipes (each ~19 min on CUDA):
#   1. P4 alt-SGD alone (constant scheduler) — predecessor before P4+Cosine
#   2. P4 + OneCycle — the "max-reg" alternative that was Pareto-trade
#
# Both stack the same per-fold log_T fix.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

base_fl=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --mtl-loss static_weight --category-weight 0.75
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --alternating-optimizer-step
    --min-best-epoch 5
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# 1. P4 alt-SGD alone, leak-free (predecessor — before cosine was added)
#    Uses constant scheduler.
run "f50_p4_alone_clean_fl" \
    "${base_fl[@]}" \
    --scheduler constant

# 2. P4 + OneCycle, leak-free (the reg-only-optimal alt that was Pareto-trade)
run "f50_p4_onecycle_clean_fl" \
    "${base_fl[@]}" \
    --scheduler onecycle --max-lr 3e-3 --pct-start 0.4

echo ""
echo "================================================================"
echo "=== Predecessor leak-free queue COMPLETE $(date) ==="
echo "================================================================"
