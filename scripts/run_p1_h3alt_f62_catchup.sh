#!/usr/bin/env bash
# Catch-up runs:
#   1. H3-alt + per-fold log_T — anchor the leak-free baseline (need this to
#      verify the +4.63 pp champion-vs-H3-alt claim survives the C4 fix)
#   2. F62 two-phase (mode=step) — was missed by the earlier queue
#      (committed AFTER watchdog launched)
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
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
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

# 1. H3-alt + per-fold log_T (leak-free baseline anchor)
#    NO alt-SGD, scheduler=constant. The "predecessor" champion of all F50.
run "f50_h3alt_clean_fl" \
    "${base_fl[@]}" \
    --mtl-loss static_weight --category-weight 0.75 \
    --scheduler constant \
    --min-best-epoch 5

# 2. F62 two-phase step-schedule (champion + temporal separation)
#    Stacks on alt-SGD + cosine but loss is now scheduled_static mode=step
run "f50_f62_two_phase_step_fl" \
    "${base_fl[@]}" \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --min-best-epoch 5 \
    --mtl-loss scheduled_static \
    --mtl-loss-param mode=step \
    --mtl-loss-param cat_weight_start=0.0 \
    --mtl-loss-param cat_weight_end=0.75 \
    --mtl-loss-param warmup_epochs=20 \
    --mtl-loss-param total_epochs=50

echo ""
echo "================================================================"
echo "=== Catch-up queue COMPLETE $(date) ==="
echo "================================================================"
