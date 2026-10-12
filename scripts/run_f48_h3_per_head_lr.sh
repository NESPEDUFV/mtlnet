#!/usr/bin/env bash
# F48-H3 — per-head LR test for the disjoint-regimes hypothesis from
# F44-F48. Cat needs gentle LR (≤ 1e-3); reg needs sustained high LR
# (≥ 2e-3 for 50+ ep). Single-LR scheduler can't serve both — F45
# constant 3e-3 lifted reg to 74 (AL) but cat collapsed to 10.
#
# Design: AdamW with three param groups built via
# `setup_per_head_optimizer`:
#   cat group    (category_encoder + category_poi)         lr=1e-3
#   reg group    (next_encoder + next_poi)                 lr=3e-3
#   shared group (crossattn_blocks + cat/next final_ln)    lr=3e-3
# Scheduler `constant` so per-group LRs survive (no overwrite).
#
# Why shared_lr = reg_lr (3e-3): the cross-attn blocks are in the reg
# gradient path (enc_next → blocks → next_final_ln → next_poi). Setting
# shared_lr=1e-3 throttles reg's gradient through the blocks and
# reproduces F44 (gentle peak hurt reg) instead of testing the
# disjoint-regimes hypothesis. Localize cat protection to cat-only
# params.
#
# Acceptance: cat F1 ≥ 35 AND reg Acc@10 ≥ 65 → disjoint-regimes
# hypothesis confirmed; clean paper recipe ("per-head LR with cat at
# gentle peak, reg at sustained max").
#
# Cost: AL ~10 min + AZ ~25 min = ~35 min sequential on MPS.
# Compare to:
#   B3 50ep default  AL 42.71/59.60   AZ 45.81/53.82
#   F45 const 3e-3   AL 10.44/74.20   AZ 12.23/63.34
#   F48-H1 const 1e-3 AL 40.99/61.43  AZ 45.34/50.68
#   STL F21c ceiling AL n/a/68.37     AZ n/a/66.74

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
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} cat=${cat_lr} reg=${reg_lr} shared=${shared_lr})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight \
        --category-weight 0.75 \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size 2048 \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

# Primary config: cat=1e-3 (preserves cat per F48-H1), reg=3e-3 (the
# F45 sweet spot for reg), shared=3e-3 (don't throttle reg gradient
# through cross-attn).
run "f48_h3_al" alabama 1e-3 3e-3 3e-3
run "f48_h3_az" arizona 1e-3 3e-3 3e-3

echo ""
echo "================================================================"
echo "=== F48-H3 sweep COMPLETE at $(date)"
echo "=== Compare cat F1 to B3 (42.71 AL / 45.81 AZ)"
echo "=== Compare reg Acc@10 to STL F21c (68.37 AL / 66.74 AZ)"
echo "================================================================"
