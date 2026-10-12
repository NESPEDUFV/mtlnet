#!/usr/bin/env bash
# F48-H3-alt — inverse of F48-H3: shared throttled to 1e-3 instead of
# 3e-3. Tests the cleaner disjoint-regimes hypothesis after H3 reproduced
# F45 (cat collapsed regardless of cat encoder LR because shared at
# sustained 3e-3 destabilized cat path upstream).
#
# Discriminator: does reg lift come from α growth alone (α lives in
# next_getnext_hard.head, in `reg_specific_parameters`), or does it
# require shared cross-attn co-evolution at high LR?
#
# Config: cat=1e-3, reg=3e-3, shared=1e-3 — all constant.
#   * α gets sustained 3e-3 (in reg group) → can grow per F45 mechanism
#   * reg encoder gets 3e-3 → reg loss reduced aggressively
#   * shared cross-attn at 1e-3 → doesn't disrupt cat path
#   * cat encoder at 1e-3 → cat preserved (per F48-H1 evidence)
#
# Acceptance:
#   cat F1 ≥ 35 AND reg Acc@10 ≥ 65   → α-growth alone explains lift,
#                                        cat is preservable, paper recipe
#   cat preserved but reg flat ~60    → reg lift REQUIRES shared updating
#                                        at high LR; cat-vs-reg tradeoff
#                                        is structural to shared cross-
#                                        attn (different paper finding)
#
# Cost: AL ~10 min + AZ ~20 min = ~30 min sequential on MPS.

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

# H3-alt: shared at 1e-3 (not 3e-3) — protects cat path, lets α grow
# in reg head independently.
run "f48_h3alt_al" alabama 1e-3 3e-3 1e-3
run "f48_h3alt_az" arizona 1e-3 3e-3 1e-3

echo ""
echo "================================================================"
echo "=== F48-H3-alt sweep COMPLETE at $(date)"
echo "=== Compare cat F1 to B3 (42.71 AL / 45.81 AZ) and to F48-H3 (collapsed)"
echo "=== Compare reg Acc@10 to STL F21c (68.37 AL / 66.74 AZ)"
echo "================================================================"
