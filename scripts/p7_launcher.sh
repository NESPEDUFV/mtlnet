#!/usr/bin/env bash
# P7 launcher — runs the 5 headline experiments for one state.
#
# Usage:
#   STATE=florida WORKTREE=$(pwd) DATA_ROOT=/path/to/data OUTPUT_DIR=/tmp/check2hgi_data PY=/path/to/python \
#     bash scripts/p7_launcher.sh > p7_florida.log 2>&1 &
#
# Preconditions:
#   - Check2HGI embeddings exist at ${OUTPUT_DIR}/check2hgi/${STATE}/input/next_region.parquet
#     (see docs/studies/check2hgi/phases/P7_headline_states.md §1 for how to generate)
#   - ${WORKTREE} contains the check2hgi-mtl branch checkout (commit 8674656 or later)
#   - ${PY} is a venv with pytorch+mps/cuda, cvxpy, fvcore (optional)

set -u
STATE="${STATE:?set STATE=florida|california|texas}"
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python}"

cd "${WORKTREE}"

DEST="${WORKTREE}/docs/results/P4"
mkdir -p "${DEST}"

archive_summary() {
    local dest_name="$1"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/${STATE}/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "[P7] saved → ${DEST}/${dest_name}.json"
    else
        echo "[P7] WARNING: no summary JSON found for ${dest_name}"
    fi
}

run_with_retry() {
    local tag="$1" dest_name="$2"; shift 2
    for attempt in 1 2 3; do
        echo ""
        echo "================================================================"
        echo "=== [${tag}] attempt ${attempt} at $(date) ==="
        echo "================================================================"
        "$PY" -u scripts/train.py "$@"
        rc=$?
        echo "[${tag}] exit ${rc} at $(date)"
        if [ $rc -eq 0 ]; then
            archive_summary "${dest_name}"
            return 0
        fi
        sleep 30
    done
    echo "[${tag}] FAILED 3x — continuing to next experiment"
}

echo "================================================================"
echo "=== P7 launcher for STATE=${STATE} starting at $(date) ==="
echo "=== WORKTREE=${WORKTREE}"
echo "=== DATA_ROOT=${DATA_ROOT}"
echo "=== OUTPUT_DIR=${OUTPUT_DIR}"
echo "=== PY=${PY}"
echo "================================================================"

# ========== 2.1 Simple baselines (CPU-only, fast) ==========
echo ""
echo "=== Simple baselines at $(date) ==="
"$PY" scripts/compute_simple_baselines.py --state "${STATE}" --task next_region || echo "[WARN] region baselines failed"
"$PY" scripts/compute_simple_baselines.py --state "${STATE}" --task next_category || echo "[WARN] category baselines failed"

# ========== 2.2 STL next-category 5f x 50ep ==========
# Uses --task next with default next_mtl head (transformer) for next-category
# prediction over the 9-step window. max_lr=0.01 is the STL cat tuning.
run_with_retry "${STATE}_STL_cat" "${STATE}_stl_cat_fairlr_5f50ep" \
    --task next --engine check2hgi \
    --state "${STATE}" \
    --folds 5 --epochs 50 --seed 42 \
    --task-input-type checkin \
    --max-lr 0.01 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ========== 2.3 STL reg GRU 5f x 50ep ==========
run_with_retry "${STATE}_STL_reg" "${STATE}_stl_reg_gru_fairlr_5f50ep" \
    --task next --engine check2hgi \
    --state "${STATE}" \
    --folds 5 --epochs 50 --seed 42 \
    --task-input-type region \
    --next-head next_gru \
    --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ========== 2.4 MTL cross-attn + pcgrad 5f x 50ep (HEADLINE) ==========
run_with_retry "${STATE}_MTL_crossattn" "${STATE}_mtl_crossattn_pcgrad_fairlr_5f50ep" \
    --task mtl --task-set check2hgi_next_region \
    --state "${STATE}" --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_crossattn --mtl-loss pcgrad \
    --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ========== 2.5 MTL lambda=0 cross-attn decomposition 5f x 50ep ==========
run_with_retry "${STATE}_MTL_lambda0" "${STATE}_mtl_crossattn_lambda0_fairlr_5f50ep" \
    --task mtl --task-set check2hgi_next_region \
    --state "${STATE}" --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.0 \
    --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

echo ""
echo "================================================================"
echo "=== P7 ${STATE} complete at $(date) ==="
echo "=== Result JSONs in ${DEST}/"
echo "================================================================"
ls -la "${DEST}/${STATE}_"*.json 2>/dev/null || echo "[P7] no archived JSONs found — check results/check2hgi/${STATE}/ manually"
