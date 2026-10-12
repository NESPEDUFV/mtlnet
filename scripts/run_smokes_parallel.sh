#!/usr/bin/env bash
# 3 smokes in parallel with STL clean in tmux 'reclean'.
# Each smoke ~30 sec at 1f×10ep bs=2048 (≈4 GB GPU mem); STL clean uses
# ~4 GB → total 8 GB / 24 GB. Safe co-residence.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$@" 2>&1 | tee "logs/${tag}_par.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

base=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --mtl-loss static_weight --category-weight 0.75
    --cat-head next_gru
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 1 --epochs 10 --seed 42 --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --scheduler constant
    --min-best-epoch 3
    --no-checkpoints --no-folds-cache
)

run "f50_p0e_ple_clean_smoke_par" \
    "$PY" -u scripts/train.py \
        "${base[@]}" \
        --model mtlnet_ple --reg-head next_getnext_hard \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

run "f50_p0d_tgstan_clean_smoke_par" \
    "$PY" -u scripts/train.py \
        "${base[@]}" \
        --model mtlnet_crossattn --reg-head next_tgstan \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

run "f50_p0d_tgstan_leaky_smoke_par" \
    "$PY" -u scripts/train.py \
        "${base[@]}" \
        --model mtlnet_crossattn --reg-head next_tgstan
echo "Smokes done"
