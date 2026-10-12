#!/usr/bin/env bash
# Phase 3 Scope D — single MTL B9 cell with leakage-free per-fold transitions.
#
# B9 = F50 P4 (alternating-SGD) + Cosine(max_lr=3e-3) + per-head LR
#      (cat=1e-3, reg=3e-3, shared=1e-3) + alpha-no-weight-decay
#      + delayed-min selector (min_epoch=5).
#
# Per NORTH_STAR.md (2026-04-29 19:50 UTC C4 caveat): under leakage-free
# conditions, B9 is the committed champion (+3.34 pp paired Wilcoxon p=0.0312
# vs leak-free H3-alt). Phase 3 substrate comparison adopts B9 so the
# leakage-free comparison is at the post-leak frontier, not the predecessor B3.
#
# Pins the cell to a specific GPU via CUDA_VISIBLE_DEVICES.
#
# Usage:
#   bash scripts/run_phase3_mtl_cell.sh STATE ENGINE GPU_ID
#
# Example:
#   bash scripts/run_phase3_mtl_cell.sh california check2hgi 0
#   bash scripts/run_phase3_mtl_cell.sh texas      hgi       3
set -u
cd "$(dirname "$0")/.."

if [ "$#" -lt 3 ]; then
    echo "Usage: $0 STATE ENGINE GPU_ID"
    echo "  STATE   = alabama | arizona | florida | california | texas"
    echo "  ENGINE  = check2hgi | hgi"
    echo "  GPU_ID  = integer (0..N-1)"
    exit 1
fi

STATE="$1"
ENGINE="$2"
GPU_ID="$3"

export PYTHONPATH=src
export OUTPUT_DIR=$(pwd)/output
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export CUDA_VISIBLE_DEVICES="$GPU_ID"

# Canonical batch size. Override via MTL_BATCH_SIZE env var if needed.
MTL_BS="${MTL_BATCH_SIZE:-2048}"

# Per-fold transition dir — built by build_phase3_per_fold_transitions.sh.
# The c2hgi-side dir holds the matrices; both MTL+c2hgi and MTL+hgi runs use
# the same matrices because the user-disjoint fold splits + raw checkin
# trajectories are engine-independent.
PER_FOLD_DIR="${OUTPUT_DIR}/check2hgi/${STATE}"

# Verify per-fold matrices exist
for fold in 1 2 3 4 5; do
    f="${PER_FOLD_DIR}/region_transition_log_fold${fold}.pt"
    if [ ! -f "$f" ]; then
        echo "[error] per-fold matrix missing: $f"
        echo "  Build first: STATES=\"$STATE\" bash scripts/build_phase3_per_fold_transitions.sh"
        exit 1
    fi
done

UPSTATE=$(echo "$STATE" | tr '[:lower:]' '[:upper:]')
TAG="MTL_B9_${UPSTATE}_${ENGINE}_pf_5f50ep"
LOG="logs/phase3/${TAG}.log"
mkdir -p logs/phase3

echo "================================================================"
echo "[${TAG}] start $(date)"
echo "  STATE=$STATE  ENGINE=$ENGINE  GPU_ID=$GPU_ID  bs=$MTL_BS"
echo "  recipe=B9 (P4 alternating-SGD + Cosine max_lr=3e-3 + per-head LR + alpha-no-WD + min_ep=5)"
echo "  per-fold-transition-dir=${PER_FOLD_DIR}"
echo "  log=$LOG"
echo "================================================================"

python3 -u scripts/train.py \
    --task mtl --state "$STATE" --engine "$ENGINE" \
    --task-set check2hgi_next_region \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    --reg-head next_getnext_hard --cat-head next_gru \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${PER_FOLD_DIR}/region_transition_log.pt" \
    --per-fold-transition-dir "${PER_FOLD_DIR}" \
    --scheduler cosine --max-lr 3e-3 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --alternating-optimizer-step \
    --alpha-no-weight-decay \
    --min-best-epoch 5 \
    --gradient-accumulation-steps 1 \
    --batch-size "$MTL_BS" \
    --folds 5 --epochs 50 --seed 42 --no-checkpoints \
    > "$LOG" 2>&1
rc=$?

echo "[${TAG}] exit $rc at $(date)"
exit $rc
