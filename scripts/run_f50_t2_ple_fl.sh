#!/usr/bin/env bash
# F50 T2 — PLE-lite (mtlnet_ple) at FL 5f×50ep with H3-alt-style per-head LR.
#
# CAVEATS DOCUMENTED IN src/models/mtl/mtlnet_ple/model.py + MTL_FLAWS_AND_FIXES.md §3.1:
#  - "PLE-lite" — per-task-input adaptation, NOT canonical Tang 2020 PLE.
#  - Side effect (positive for our hypothesis): NO F49 Layer 2 leakage.
#  - PLE-lite is essentially stacked CGC (no inter-level shared-gate chain).
#  - Param count ~8.25M ≈ cross-attn 7.9M (+4%) — capacity-comparable.
#
# Acceptance: reg top10_acc_indist (per-task-best) ≥ 76.61 closes ≥ 3 pp of
# the 8.78 pp gap to STL ceiling. Compare to:
#   CUDA H3-alt FL = 73.61 ± 0.83 (per-task-best, substrate-matched)
#   STL FL ceiling = 82.44 ± 0.38 (matched-head GETNext-hard)

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "=== [${tag}] start $(date) ==="
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_ple \
        --mtl-loss static_weight --category-weight 0.75 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t2_ple_fl" florida 1e-3 3e-3 1e-3
