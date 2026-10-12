#!/usr/bin/env bash
# RunPod-side wrapper around scripts/run_f48_h3alt_fl.sh.
#
# Why a wrapper:
#   - The original launcher exports MPS-only env vars and requires the caller
#     to set DATA_ROOT/OUTPUT_DIR. On a fresh RunPod pod neither is true.
#   - This script provides sane CUDA defaults, then delegates to the
#     canonical launcher unchanged.
#
# Usage:
#   bash scripts/runpod_train_fl_h3alt.sh           # 5f x 50ep, seed 42
#   FOLDS=1 EPOCHS=2 bash scripts/runpod_train_fl_h3alt.sh   # smoke test
#
# Output: results/check2hgi/florida/<run_dir>/

set -euo pipefail

WORKTREE="${WORKTREE:-$(pwd)}"
cd "${WORKTREE}"

export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTHONPATH="${PYTHONPATH:-src}"
mkdir -p "${DATA_ROOT}" "${OUTPUT_DIR}"

# Pick venv python if available, else system python.
if [[ -x "${WORKTREE}/.venv/bin/python" ]]; then
    export PY="${WORKTREE}/.venv/bin/python"
else
    export PY="${PY:-python3}"
fi

echo "[runpod-train] DATA_ROOT  = ${DATA_ROOT}"
echo "[runpod-train] OUTPUT_DIR = ${OUTPUT_DIR}"
echo "[runpod-train] PY         = ${PY} ($(${PY} --version 2>&1))"
"${PY}" -c "import torch; print(f'[runpod-train] torch={torch.__version__} cuda={torch.cuda.is_available()}')"

# Required artefacts (a missing file → silent crash inside the trainer).
required=(
    "${OUTPUT_DIR}/check2hgi/florida/embeddings.parquet"
    "${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    "${OUTPUT_DIR}/check2hgi/florida/input/next.parquet"
    "${OUTPUT_DIR}/check2hgi/florida/input/next_region.parquet"
    "${OUTPUT_DIR}/check2hgi/florida/temp/sequences_next.parquet"
)
missing=0
for f in "${required[@]}"; do
    if [[ ! -f "$f" ]]; then
        echo "[runpod-train] MISSING: $f"
        missing=1
    fi
done
if [[ $missing -eq 1 ]]; then
    echo "[runpod-train] Run: bash scripts/runpod_fetch_data.sh florida"
    exit 1
fi

# Allow quick override via env.
FOLDS="${FOLDS:-5}"
EPOCHS="${EPOCHS:-50}"
SEED="${SEED:-42}"
# Default 2048 matches NORTH_STAR.md (`docs/NORTH_STAR.md`).
# On MPS, override with BATCH=1024 to avoid unified-memory pressure.
BATCH="${BATCH:-2048}"
TAG="${TAG:-baseline}"
EXTRA_FLAGS="${EXTRA_FLAGS:-}"

echo "[runpod-train] tag=${TAG} folds=${FOLDS} epochs=${EPOCHS} seed=${SEED} batch=${BATCH}"
echo "[runpod-train] extra flags = ${EXTRA_FLAGS:-(none)}"
echo "[runpod-train] launching H3-alt FL run ..."
echo ""

# shellcheck disable=SC2086
"${PY}" -u scripts/train.py \
    --task mtl \
    --task-set check2hgi_next_region \
    --state florida --engine check2hgi \
    --model mtlnet_crossattn \
    --mtl-loss static_weight \
    --category-weight 0.75 \
    --cat-head next_gru \
    --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --task-a-input-type checkin --task-b-input-type region \
    --folds "${FOLDS}" --epochs "${EPOCHS}" --seed "${SEED}" \
    --batch-size "${BATCH}" \
    --scheduler constant \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --gradient-accumulation-steps 1 \
    --no-checkpoints --no-folds-cache \
    ${EXTRA_FLAGS}
rc=$?

echo ""
echo "[runpod-train] exit=${rc} at $(date)"
if [[ $rc -eq 0 ]]; then
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/florida/"*_lr*_bs*_ep*_* 2>/dev/null | head -1)
    if [[ -n "$latest" ]]; then
        # Tag the run dir so comparison drivers can find variants.
        echo "${TAG}" > "${latest}/.runpod_tag"
        echo "[runpod-train] run dir: ${latest}"
        echo "[runpod-train] tag file: ${latest}/.runpod_tag = ${TAG}"
    fi
fi
exit $rc
