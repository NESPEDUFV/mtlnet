#!/usr/bin/env bash
# F49 — λ=0.0 isolation re-measurement under H3-alt (3-way decomposition)
#
# Two variants per state:
#   * loss-side  : --category-weight 0.0 only. Cat encoder still co-adapts
#                  as a reg-helper through cross_ba's K/V projections.
#   * frozen-cat : --category-weight 0.0 + --freeze-cat-stream. Cat encoder
#                  + cat head get requires_grad=False; the optimizer's
#                  requires_grad filter prevents AdamW silent decay.
#
# Combined with STL F21c (already have) and full MTL H3-alt (already have)
# gives the full 3-way decomposition:
#   full MTL − STL = (frozen_λ0 − STL) + (loss_λ0 − frozen_λ0) + (full − loss_λ0)
#                       architectural    cat-encoder co-adapt    cat-supervision transfer
#
# Plan: `docs/findings/F49_LAMBDA0_DECOMPOSITION_GAP.md`.
# Tracker: `docs/studies/check2hgi/FOLLOWUPS_TRACKER.md §F49`.
#
# Cost (MPS): AL ~30min × 2 + AZ ~60min × 2 = ~3h for the AL+AZ decision
# gate. FL ~4.3h × 2 = ~9h (gated on AL+AZ outcome; needs batch=1024).
#
# Usage:
#   # Smoke (1f × 2ep on AL, both variants — sanity check only)
#   MODE=smoke bash scripts/run_f49_lambda0_decomposition.sh
#
#   # AL+AZ both variants (decision gate, ~3h)
#   MODE=alaz bash scripts/run_f49_lambda0_decomposition.sh
#
#   # FL both variants (gated, ~9h, batch=1024)
#   MODE=fl bash scripts/run_f49_lambda0_decomposition.sh
#
#   # Single state + variant: STATE=alabama VARIANT=frozen bash …
#   STATE=alabama VARIANT=lossside bash scripts/run_f49_lambda0_decomposition.sh

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

# ----- helpers ----------------------------------------------------------------

# Run one F49 cell. Args: tag state variant folds epochs batch_size
# variant ∈ {lossside, frozen}
run_cell() {
    local tag="$1" state="$2" variant="$3"
    local folds="$4" epochs="$5" batch_size="$6"

    local extra_args=()
    if [[ "${variant}" == "frozen" ]]; then
        extra_args+=(--freeze-cat-stream)
    elif [[ "${variant}" != "lossside" ]]; then
        echo "[run_cell] unknown variant '${variant}', expected lossside|frozen" >&2
        return 2
    fi

    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) — state=${state} variant=${variant}"
    echo "===   folds=${folds} epochs=${epochs} batch=${batch_size}"
    echo "===   per-head LR: cat=1e-3 reg=3e-3 shared=1e-3 (constant)"
    echo "===   loss: static_weight category_weight=0.0"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight \
        --category-weight 0.0 \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds "${folds}" --epochs "${epochs}" --seed 42 \
        --batch-size "${batch_size}" \
        --scheduler constant \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        ${extra_args[@]+"${extra_args[@]}"} \
        --no-checkpoints --no-folds-cache
    local rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    return ${rc}
}

# ----- mode dispatch ----------------------------------------------------------

MODE="${MODE:-}"
STATE="${STATE:-}"
VARIANT="${VARIANT:-}"

case "${MODE}" in
    smoke)
        # 1f × 2ep on AL, both variants. Sanity check only.
        run_cell "f49_smoke_al_lossside" alabama lossside 1 2 2048
        run_cell "f49_smoke_al_frozen"   alabama frozen   1 2 2048
        ;;
    alaz)
        # Decision-gate runs: AL+AZ at 5f × 50ep, both variants.
        run_cell "f49_al_lossside" alabama lossside 5 50 2048
        run_cell "f49_al_frozen"   alabama frozen   5 50 2048
        run_cell "f49_az_lossside" arizona lossside 5 50 2048
        run_cell "f49_az_frozen"   arizona frozen   5 50 2048
        echo ""
        echo "================================================================"
        echo "=== F49 AL+AZ COMPLETE at $(date)"
        echo "=== Now compute the 3-way decomposition table and decide on FL."
        echo "================================================================"
        ;;
    fl)
        # FL runs: 5f × 50ep, both variants, batch=1024 (2048 OOMs at fold 2 ep 23
        # silently per F48-H3-alt — see SESSION_HANDOFF_2026-04-26.md).
        run_cell "f49_fl_lossside" florida lossside 5 50 1024
        run_cell "f49_fl_frozen"   florida frozen   5 50 1024
        echo ""
        echo "================================================================"
        echo "=== F49 FL COMPLETE at $(date)"
        echo "=== 3-way decomposition now has all 3 states. Write up results."
        echo "================================================================"
        ;;
    *)
        # Single STATE+VARIANT mode for ad-hoc reruns.
        if [[ -z "${STATE}" || -z "${VARIANT}" ]]; then
            echo "Usage: MODE=smoke|alaz|fl bash $0" >&2
            echo "   or: STATE=<state> VARIANT=lossside|frozen bash $0" >&2
            exit 2
        fi
        local_bs=2048
        if [[ "${STATE}" == "florida" ]]; then local_bs=1024; fi
        run_cell "f49_${STATE}_${VARIANT}" "${STATE}" "${VARIANT}" 5 50 "${local_bs}"
        ;;
esac
