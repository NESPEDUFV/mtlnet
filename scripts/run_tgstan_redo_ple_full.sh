#!/usr/bin/env bash
# After fixing the aux-side-channel bug for next_tgstan / next_stahyper /
# next_getnext (F50 T4 broader-leakage audit), re-run:
#   1. TGSTAN clean (1f×10ep) — true gate-amplifier verification
#   2. TGSTAN leaky (1f×10ep) — paired baseline for Δ
#   3. PLE-lite clean FULL 5f×50ep — preliminary smoke gave anomalous
#      75 reg vs H3-alt clean's 60; full run needed to confirm/refute
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

base=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --mtl-loss static_weight --category-weight 0.75
    --cat-head next_gru
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --scheduler constant
    --no-checkpoints --no-folds-cache
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# 1+2: TGSTAN smokes (with aux fix) — 1f×10ep
smoke_tgstan=(
    "${base[@]}" --model mtlnet_crossattn --reg-head next_tgstan
    --folds 1 --epochs 10 --seed 42 --batch-size 2048 --min-best-epoch 3
)

run "f50_p0d_tgstan_clean_smoke_v2" \
    "$PY" -u scripts/train.py "${smoke_tgstan[@]}" \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

run "f50_p0d_tgstan_leaky_smoke_v2" \
    "$PY" -u scripts/train.py "${smoke_tgstan[@]}"

# 3: PLE clean FULL 5f×50ep — confirm or refute the 75 anomaly
run "f50_p0e_ple_clean_full_fl" \
    "$PY" -u scripts/train.py \
        "${base[@]}" \
        --model mtlnet_ple --reg-head next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --batch-size 2048 --min-best-epoch 5 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

echo "Done"
