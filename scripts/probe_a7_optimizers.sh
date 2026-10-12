#!/usr/bin/env bash
# A7 optimizer probe — champion config (dselectk + MTLoRA r=8, 5f×50ep)
# swept across {pcgrad, aligned_mtl, cagrad, db_mtl}.
#
# Purpose:
#   1. Verify the MTL_PARAM_PARTITION_BUG fix — rerun the A7 config under
#      PCGrad and see whether the MTLoRA lift survives now that LoRA
#      actually trains.
#   2. Test the three optimizers the user asked for (Aligned-MTL, CAGrad,
#      DB-MTL) on the same config, as apples-to-apples comparison points.
#
# Usage:
#   STATE=alabama bash scripts/probe_a7_optimizers.sh
#   STATE=arizona bash scripts/probe_a7_optimizers.sh
#
# Expected runtime: 4 runs × ~40min/run on MPS ≈ 2.7h (AL scale).
# AZ is ~2x AL, so ~5-6h.

set -u

STATE="${STATE:-alabama}"
STATE_SHORT="${STATE_SHORT:-}"
if [ -z "${STATE_SHORT}" ]; then
    case "${STATE}" in
        alabama)  STATE_SHORT="al" ;;
        florida)  STATE_SHORT="fl" ;;
        arizona)  STATE_SHORT="az" ;;
        *)        STATE_SHORT="${STATE}" ;;
    esac
fi

WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-$WORKTREE/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-$WORKTREE/output}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

DEST="${WORKTREE}/docs/results/P5_bugfix"
mkdir -p "${DEST}"

archive_summary() {
    local dest_name="$1"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/${STATE}/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "[PROBE] saved → ${DEST}/${dest_name}.json"
    else
        echo "[PROBE] WARNING: no summary JSON found for ${dest_name}"
    fi
}

run() {
    local tag="$1" dest_name="$2"; shift 2
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${STATE})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl --engine check2hgi --state "${STATE}" \
        --task-set check2hgi_next_region \
        --task-a-input-type checkin --task-b-input-type region \
        --model mtlnet_dselectk --model-param lora_rank=8 \
        --max-lr 0.003 \
        --folds 5 --epochs 50 --seed 42 \
        --gradient-accumulation-steps 1 --no-checkpoints \
        "$@"
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    if [ $rc -eq 0 ]; then
        archive_summary "${dest_name}"
    fi
}

echo "================================================================"
echo "=== A7 optimizer probe starting $(date) — STATE=${STATE}"
echo "================================================================"

run "a7_pcgrad_${STATE_SHORT}_postfix"      "a7_mtlora_r8_${STATE_SHORT}_5f50ep_postfix_pcgrad"      --mtl-loss pcgrad
run "a7_aligned_mtl_${STATE_SHORT}_postfix" "a7_mtlora_r8_${STATE_SHORT}_5f50ep_postfix_aligned_mtl" --mtl-loss aligned_mtl
run "a7_cagrad_${STATE_SHORT}_postfix"      "a7_mtlora_r8_${STATE_SHORT}_5f50ep_postfix_cagrad"      --mtl-loss cagrad
run "a7_db_mtl_${STATE_SHORT}_postfix"      "a7_mtlora_r8_${STATE_SHORT}_5f50ep_postfix_db_mtl"      --mtl-loss db_mtl

echo ""
echo "================================================================"
echo "=== A7 probe complete at $(date) — STATE=${STATE}"
echo "=== results in ${DEST}/"
echo "================================================================"
ls -la "${DEST}/a7_mtlora_r8_${STATE_SHORT}_5f50ep_postfix_"*.json 2>/dev/null || echo "[PROBE] no archived JSONs found"
