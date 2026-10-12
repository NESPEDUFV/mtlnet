#!/usr/bin/env bash
# F43 — MTL-B3 with cat_weight ≈ 0 (reg-only loss).
#
# Follow-up to F41 AL finding: the upstream MLP pre-encoder by itself does NOT
# depress reg (F41 matched STL F21c within σ). The remaining MTL-specific
# components are (a) cross-attention blocks and (b) joint training dynamics.
#
# F43 tests (b): keep full B3 architecture (cross-attn + shared encoders),
# but set the cat loss weight to ~0 so only reg loss drives backward.
# Implementation: --category-weight 0.01 (epsilon instead of 0.0 to avoid
# degenerate optimizer behaviour where cat_encoder gradients are exactly 0).
#
# The cat encoder and cat head still receive forward passes (their output
# flows through cross-attn into the reg stream), but no cat-loss-side
# gradient signal pollutes the shared params. Cross-attn params still
# update from reg-loss backward.
#
# Acceptance:
#   reg Acc@10 ≈ STL F21c (68.37 AL)  → joint-training signal is the culprit;
#                                        cross-attn itself is fine
#   reg Acc@10 ≈ B3 56.33              → cross-attn architecture is the
#                                        culprit (independent of cat loss)
#   reg Acc@10 in between              → partial contribution from each
#
# Cost: 1 AL run 5f × 50ep ≈ 10 min. Launch after F41 AZ finishes.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F43_cat_zero"
mkdir -p "${DEST}"

run() {
    local tag="$1" state="$2" cat_w="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state}, cat_weight=${cat_w})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight \
        --category-weight "${cat_w}" \
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

# AL cat=0.01 — reg-dominant, cat kept barely in the graph
run "f43_al_cat001" alabama 0.01

echo ""
echo "================================================================"
echo "=== F43 AL complete at $(date)"
echo "=== Compare reg Acc@10 to STL F21c (68.37) and B3 baseline (59.60)"
echo "=== If ≥ 66: cross-attn OK, joint-signal is the culprit"
echo "=== If ≤ 60: cross-attn arch is the culprit"
echo "================================================================"
