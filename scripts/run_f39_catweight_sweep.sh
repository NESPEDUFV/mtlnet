#!/usr/bin/env bash
# F39 — Exp B: cat_weight sweep on MTL-B3 to isolate Fator 1 (loss-weight) of CH18.
#
# B3 currently uses static_weight(cat=0.75) → reg gets effective weight 0.25.
# Hypothesis: decreasing cat_weight (more gradient budget to reg) should lift
# reg Acc@10 toward the STL matched-head ceiling (68.37 AL / 66.74 AZ).
#
# Configurations (AL + AZ, 5f × 50ep each):
#   cat_w=0.25 (reg-heavy)    → expect cat F1 dip, reg Acc@10 rise
#   cat_w=0.50 (equal)         → neutral point
# Reference: cat_w=0.75 is the current B3 (F31/F27-validation 5f).
#
# Pass (Fator 1 is load-bearing):  reg Acc@10 rises ≥ +3 pp as cat_w drops, σ-clean.
# Fail (Fator 1 not load-bearing): reg Acc@10 flat within σ → attribution shifts to Fator 3.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F39_catweight"
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

# AL first (cheap, ~45 min × 2 weights = ~1.5 h)
run "f39_al_cat025" alabama 0.25
run "f39_al_cat050" alabama 0.50

# AZ next (~1h × 2 = ~2 h)
run "f39_az_cat025" arizona 0.25
run "f39_az_cat050" arizona 0.50

echo ""
echo "================================================================"
echo "=== F39 cat_weight sweep complete at $(date)"
echo "=== JSONs land under results/check2hgi/<state>/mtlnet_*_<ts>/summary/"
echo "=== Archive the 4 summaries to: ${DEST}/"
echo "=== Compare reg top10_acc_indist vs B3@cat=0.75 (AL 59.60, AZ 53.82)"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
