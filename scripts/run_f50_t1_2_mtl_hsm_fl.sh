#!/usr/bin/env bash
# F50 T1.2-mtl — H3-alt MTL with HSM reg head, FL 5f×50ep.
#
# Tests whether the hierarchical-additive softmax reg head closes the FL
# architectural gap when used inside the MTL-H3-alt champion configuration.
# Comparison points:
#   STL flat next_getnext_hard FL = 82.44 ± 0.38  (matched-head ceiling)
#   MTL H3-alt FL (flat reg)      = 71.96 ± 0.68  (current MTL champion)
#   STL HSM FL                    = (T1.2-stl, in flight)
# Acceptance: MTL with HSM FL reg Acc@10 ≥ 75.0 closes ≥3 pp of the
# 8.78 pp gap between MTL H3-alt and STL ceiling.
#
# Config matches H3-alt verbatim except --reg-head next_getnext_hard_hsm
# and --reg-head-param hierarchy_path=...
#
# Batch size:
#   - CUDA (default 2048): matches NORTH_STAR.md / H3-alt champion.
#   - MPS (M4 Pro): `BATCH_SIZE=1024 bash scripts/run_f50_t1_2_mtl_hsm_fl.sh`.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

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
        --reg-head next_getnext_hard_hsm \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --reg-head-param "hierarchy_path=${OUTPUT_DIR}/check2hgi/${state}/region_hierarchy.pt" \
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

run "f50_t1_2_mtl_hsm_fl" florida 1e-3 3e-3 1e-3

echo ""
echo "================================================================"
echo "=== F50 T1.2-mtl HSM MTL FL COMPLETE at $(date)"
echo "=== Compare reg Acc@10 to:"
echo "===   STL flat FL = 82.44 ± 0.38  (matched-head ceiling)"
echo "===   MTL H3-alt flat FL = 71.96 ± 0.68  (current champion)"
echo "===   STL HSM FL = (from T1.2-stl)"
echo "=== Acceptance: MTL HSM FL reg Acc@10 >= 75.0 closes >= 3 pp"
echo "================================================================"
