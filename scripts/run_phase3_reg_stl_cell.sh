#!/usr/bin/env bash
# Phase 3 Scope D — single reg STL cell with leakage-free per-fold transitions.
# Pins the cell to a specific GPU via CUDA_VISIBLE_DEVICES.
#
# Usage:
#   bash scripts/run_phase3_reg_stl_cell.sh STATE ENGINE GPU_ID
#
# Example:
#   bash scripts/run_phase3_reg_stl_cell.sh california check2hgi 0
#   bash scripts/run_phase3_reg_stl_cell.sh texas      hgi       3
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

# Per-fold transition dir (built by build_phase3_per_fold_transitions.sh).
# Same file lives under check2hgi/<state>/ regardless of engine — both engines
# share the same userid-based fold split and same raw transition trajectories.
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
TAG="STL_${UPSTATE}_${ENGINE}_reg_gethard_pf_5f50ep"
LOG="logs/phase3/${TAG}.log"
mkdir -p logs/phase3

echo "================================================================"
echo "[${TAG}] start $(date)"
echo "  STATE=$STATE  ENGINE=$ENGINE  GPU_ID=$GPU_ID"
echo "  per-fold-transition-dir=${PER_FOLD_DIR}"
echo "  log=$LOG"
echo "================================================================"

python3 -u scripts/p1_region_head_ablation.py \
    --state "$STATE" --heads next_getnext_hard \
    --folds 5 --epochs 50 --seed 42 --input-type region \
    --region-emb-source "$ENGINE" \
    --override-hparams d_model=256 num_heads=8 \
        "transition_path=${PER_FOLD_DIR}/region_transition_log.pt" \
    --per-fold-transition-dir "${PER_FOLD_DIR}" \
    --tag "$TAG" \
    > "$LOG" 2>&1
rc=$?

echo "[${TAG}] exit $rc at $(date)"
exit $rc
