#!/usr/bin/env bash
# F42 — Exp E: B3 AL epoch-budget sweep to test the premature-termination
# hypothesis for CH18.
#
# User observation (2026-04-24): the B3 AL 5f σ (4-5 pp) on reg Acc@10 is
# ~2x STL F21c σ (2.66). Per-fold best_epoch analysis shows several folds
# peaking at epochs 44-48 of 50 — OneCycleLR tail clipping. Hypothesis:
# MTL converges slower than STL because the shared backbone has to
# coordinate two gradients + late-stage handover consumes 40+ epochs, but
# MTL is evaluated with the same 50-epoch budget as STL → unfair comparison.
#
# State-scale note: AL has only ~5 batches/epoch (12.7K rows / 2048 batch)
# vs FL's ~62 batches/epoch (127K rows / 2048 batch). Per-state epoch
# budgets should scale inversely with batches/epoch. AL is the most
# step-starved state; test there first.
#
# Acceptance:
#   σ tight (≤2.5 pp) + reg Acc@10 rises ≥3 pp  → CH18 partially closed by training budget
#   σ tight but reg Acc@10 flat at 59.60        → training was converged at 50ep; σ was noise
#   σ still wide + reg Acc@10 jumps             → still premature at 150, go higher
#
# Start: AL 5f × 150 epochs (single run, ~30 min on MPS).
# If the peak is clearly within 150ep, project to AZ and then FL.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F42_epoch_sweep"
mkdir -p "${DEST}"

run() {
    local tag="$1" state="$2" epochs="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state}, epochs=${epochs})"
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
        --folds 5 --epochs "${epochs}" --seed 42 \
        --batch-size 2048 --max-lr 3e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

# AL 5f × 150 ep — first test point
run "f42_al_150ep" alabama 150

echo ""
echo "================================================================"
echo "=== F42 AL 150ep complete at $(date)"
echo "=== Inspect per-fold best_epoch via fold_info.json; compare σ vs B3@50ep (4.16)"
echo "=== JSONs land under results/check2hgi/alabama/mtlnet_*/summary/"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
