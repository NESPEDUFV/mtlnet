#!/usr/bin/env bash
# B3 — multi-state 5-fold validation of the F2-identified candidate north-star.
#
# Config: cross-attn + static_weight(category_weight=0.75) + next_getnext_hard d=256, 8h
#
# Runs sequentially on AL (cheap ≈1h) → AZ (≈1.5h) → FL (≈5-6h) so a broken
# cheap run skips expensive downstream runs.
#
# See docs/findings/B5_FL_TASKWEIGHT.md for the F2 outcome
# that motivated this validation and NORTH_STAR.md §Re-evaluation triggers
# for the pass criteria.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/B3_validation"
mkdir -p "${DEST}"

archive_latest() {
    local state="$1" dest_name="$2"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/${state}/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "${latest}" > "${DEST}/${dest_name}.run_dir"
        echo "[B3] saved → ${DEST}/${dest_name}.json"
    else
        echo "[B3] WARNING: no summary JSON for ${dest_name}"
    fi
}

run() {
    local tag="$1" state="$2" dest_name="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state})"
    echo "================================================================"
    "$PY" -u scripts/train.py --state "${state}" \
        --task mtl --task-set check2hgi_next_region --engine check2hgi \
        --folds 5 --epochs 50 --seed 42 \
        --task-a-input-type checkin --task-b-input-type region \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param transition_path="${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --max-lr 0.003 --gradient-accumulation-steps 1 --no-checkpoints
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    if [ $rc -eq 0 ]; then
        archive_latest "${state}" "${dest_name}"
    else
        echo "[B3] ABORT — non-zero exit on ${tag}; downstream states will be skipped"
        exit $rc
    fi
}

# --- AL 5f × 50ep (F18, cheapest — should be ~1h) ---
run "b3_al" alabama "al_5f50ep_b3"

# --- AZ 5f × 50ep (F19 — ~1.5h) ---
run "b3_az" arizona "az_5f50ep_b3"

# --- FL 5f × 50ep (F17 — ~5-6h, the binding dominance check) ---
run "b3_fl" florida "fl_5f50ep_b3"

echo ""
echo "================================================================"
echo "=== B3 multi-state validation complete at $(date)"
echo "================================================================"
ls -la "${DEST}/"*.json 2>/dev/null
