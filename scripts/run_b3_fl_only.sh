#!/usr/bin/env bash
# F17 re-launch — B3 on FL, 5f × 50ep.
# First attempt (2026-04-23 04:05) crashed at fold 2 ep 22; F20 per-fold
# persistence (commit landing 2026-04-23 ~06:35) now guarantees completed
# folds survive any mid-CV crash.

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
    local dest_name="$1"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/florida/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "${latest}" > "${DEST}/${dest_name}.run_dir"
        echo "[B3 FL] saved → ${DEST}/${dest_name}.json"
    else
        echo "[B3 FL] WARNING: no summary JSON for ${dest_name}"
        # On crash: still record the latest run dir so per-fold data is discoverable
        [ -n "${latest}" ] && echo "${latest}" > "${DEST}/${dest_name}.run_dir"
    fi
}

echo ""
echo "================================================================"
echo "=== [B3 FL re-launch] start $(date)"
echo "================================================================"
"$PY" -u scripts/train.py --state florida \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param transition_path="${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --max-lr 0.003 --gradient-accumulation-steps 1 --no-checkpoints
rc=$?
echo "[B3 FL] exit ${rc} at $(date)"

if [ $rc -eq 0 ]; then
    archive_latest "fl_5f50ep_b3"
else
    echo "[B3 FL] non-zero exit — per-fold data preserved under the latest fl run dir (F20)"
    archive_latest "fl_5f50ep_b3_partial"
fi
echo ""
echo "================================================================"
echo "=== B3 FL complete at $(date)"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
