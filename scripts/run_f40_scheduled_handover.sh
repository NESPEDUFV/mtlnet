#!/usr/bin/env bash
# F40 — Experiment C: scheduled cat_weight handover with B3 architecture.
#
# Loss: scheduled_static interpolates cat_weight linearly from 0.75 (ep 0)
# to 0.25 (ep 49). Cat converges early under high weight (matching B3),
# then gradient budget shifts to reg in the second half (matching F45's
# α-growth window).
#
# Architecture: B3 (mtlnet_crossattn + next_gru cat + next_getnext_hard reg).
# LR schedule: B3 default OneCycleLR max=3e-3, 50ep — isolates the
# loss-side change from the LR-side recipe (H3-alt).
#
# Comparison points:
#   B3 50ep static_weight cat=0.75:  AL cat 42.71 / reg 59.60   AZ 45.81 / 53.82
#   F39 cat=0.50/0.25 static (AL):   reg flat (refuted Fator 1 alone)
#   F48-H3-alt per-head (winner):    AL cat 42.22 / reg 74.62   AZ 45.11 / 63.45
#
# Acceptance (Pareto-lift):
#   cat F1 ≥ B3 - 1 pp AND reg Acc@10 > B3 + 3 pp
#   = AL cat ≥ 41.71 AND reg ≥ 62.60
#   = AZ cat ≥ 44.81 AND reg ≥ 56.82
#
# Cost: AL ~8 min + AZ ~15 min = ~25 min sequential on MPS.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

run() {
    local tag="$1" state="$2" cat_start="$3" cat_end="$4"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} cat_start=${cat_start} cat_end=${cat_end})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss scheduled_static \
        --mtl-loss-param "cat_weight_start=${cat_start}" \
        --mtl-loss-param "cat_weight_end=${cat_end}" \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size 2048 --max-lr 3e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

# Spec from tracker: cat_weight 0.75 → 0.25 over 50ep
run "f40_al" alabama 0.75 0.25
run "f40_az" arizona 0.75 0.25

echo ""
echo "================================================================"
echo "=== F40 sweep COMPLETE at $(date)"
echo "=== Compare to B3 baseline (Pareto-lift threshold)"
echo "================================================================"
