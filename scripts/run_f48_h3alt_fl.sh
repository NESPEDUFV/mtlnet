#!/usr/bin/env bash
# F48-H3-alt FL — scale-stability validation of the per-head LR recipe
# that worked on AL (cat preserved + reg exceeded STL by +6.25 pp) and
# AZ (cat preserved + 75% gap closed).
#
# FL is the largest state: 4703 regions vs AL 1109 / AZ 1547. If H3-alt
# scales here, the recipe is paper-ready cross-state. If it degrades,
# we have scale-dependence to characterize.
#
# Same config as `run_f48_h3alt_per_head_lr.sh`:
#   --scheduler constant --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
#
# Cost estimate: FL has ~3x AZ rows + ~3x AZ regions, so ~10-15 min/fold
# × 5 folds = 50-75 min on MPS.
#
# Batch size:
#   - CUDA (default 2048): matches NORTH_STAR.md and reproduces the
#     published cat F1 67.92 ± 0.72. Verified on RTX 4090 (RunPod), 5f×50ep,
#     19 min wall time, see docs/results/perf_compare/.
#   - MPS (recommended 1024): the 24 GB unified-memory M4 Pro starts to
#     swap above ~1500 effective batch on this model; run with
#     `BATCH_SIZE=1024 bash scripts/run_f48_h3alt_fl.sh` on Mac.

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
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f48_h3alt_fl" florida 1e-3 3e-3 1e-3

echo ""
echo "================================================================"
echo "=== F48-H3-alt FL COMPLETE at $(date)"
echo "=== Compare cat F1 to past STL FL baselines (state-dependent)"
echo "=== Compare reg Acc@10 to STL F21c FL (TBD — F37 4050 will land)"
echo "================================================================"
