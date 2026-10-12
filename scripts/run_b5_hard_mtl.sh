#!/usr/bin/env bash
# B5 — faithful GETNext with hard last_region_idx, 5f × 50ep on AL + AZ.
#
# Paired against the soft-probe champion (commit b-M6b / b-M9b in
# RESULTS_TABLE.md) using the SAME seed, same optimizer, same head hparams
# — only the head family swaps (next_getnext -> next_getnext_hard).
#
# Expected: AL Acc@10 59-63 (from 56.38) ; AZ 50-54 (from 47.34).
# Wallclock budget: ~13 min AL + ~30 min AZ = ~45 min on MPS. FL 1f
# optional (another ~30 min) — add after AZ if time permits.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/B5"
mkdir -p "${DEST}"

archive_summary() {
    local state="$1" dest_name="$2"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/${state}/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "[B5] saved → ${DEST}/${dest_name}.json"
    else
        echo "[B5] WARNING: no summary JSON found for ${dest_name}"
    fi
}

run() {
    local tag="$1" state="$2" dest_name="$3"; shift 3
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state})"
    echo "================================================================"
    "$PY" -u scripts/train.py --state "${state}" "$@"
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && archive_summary "${state}" "${dest_name}"
}

# --- AL 5f × 50ep ---
run "b5_hard_al" alabama "al_5f50ep_next_getnext_hard" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_crossattn --mtl-loss pcgrad \
    --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param transition_path="${OUTPUT_DIR}/check2hgi/alabama/region_transition_log.pt" \
    --max-lr 0.003 --gradient-accumulation-steps 1 --no-checkpoints

# --- AZ 5f × 50ep ---
run "b5_hard_az" arizona "az_5f50ep_next_getnext_hard" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_crossattn --mtl-loss pcgrad \
    --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param transition_path="${OUTPUT_DIR}/check2hgi/arizona/region_transition_log.pt" \
    --max-lr 0.003 --gradient-accumulation-steps 1 --no-checkpoints

echo ""
echo "================================================================"
echo "=== B5 hard MTL complete at $(date)"
echo "=== results in ${DEST}/"
echo "================================================================"
ls -la "${DEST}/"*.json 2>/dev/null || echo "[B5] no archived JSONs found"
