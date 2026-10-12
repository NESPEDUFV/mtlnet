#!/usr/bin/env bash
# F27 — Cat-head ablation on MTL-B3, 1-fold × 50 epochs on AZ.
#
# Question: does the choice of task_a (cat) head materially change B3's
# joint-task numbers? B3's default head_factory=None → MTLnet falls back
# to NextHeadMTL (Transformer + sequence reduction). We sweep the 5
# sequence-compatible heads in the registry.
#
# AZ is chosen because (i) it's mid-scale (~25 min/fold), (ii) it's where
# we have the strongest existing B3 result (AZ B3 cat F1 = 43.62 ± 0.74),
# (iii) 1-fold is enough for a directional screen — if one head wins by
# > 2 pp we'd follow up with 5-fold.
#
# See docs/archive/check2hgi-post-paper-closure-2026-05-01/FOLLOWUPS_TRACKER.md §F27
# and docs/findings/F21C_FINDINGS.md for context.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F27_cathead_sweep"
mkdir -p "${DEST}"

archive_latest() {
    local dest_name="$1"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/arizona/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "${latest}" > "${DEST}/${dest_name}.run_dir"
        echo "[F27] saved → ${DEST}/${dest_name}.json"
    else
        echo "[F27] WARNING: no summary JSON for ${dest_name}"
    fi
}

# Common B3 args — everything except --cat-head fixed.
COMMON_ARGS=(
    --task mtl --task-set check2hgi_next_region --engine check2hgi
    --state arizona
    --folds 1 --epochs 50 --seed 42
    --task-a-input-type checkin --task-b-input-type region
    --model mtlnet_crossattn
    --mtl-loss static_weight --category-weight 0.75
    --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/arizona/region_transition_log.pt"
    --max-lr 0.003 --gradient-accumulation-steps 1 --no-checkpoints
)

run() {
    local tag="$1" cat_head="$2" dest_name="$3"; shift 3
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (cat-head=${cat_head})"
    echo "================================================================"
    if [ "${cat_head}" = "default" ]; then
        # No --cat-head → task_set preset default (None → NextHeadMTL)
        "$PY" -u scripts/train.py "${COMMON_ARGS[@]}"
    else
        "$PY" -u scripts/train.py "${COMMON_ARGS[@]}" --cat-head "${cat_head}"
    fi
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && archive_latest "${dest_name}"
}

# Control = default (None → NextHeadMTL, B3's actual head)
run "f27_default" "default"       "az_1f50ep_cathead_default"

# Sequence-compatible heads registered in models/next/
run "f27_next_mtl" "next_mtl"     "az_1f50ep_cathead_next_mtl"
run "f27_gru"     "next_gru"      "az_1f50ep_cathead_next_gru"
run "f27_lstm"    "next_lstm"     "az_1f50ep_cathead_next_lstm"
run "f27_stan"    "next_stan"     "az_1f50ep_cathead_next_stan"
run "f27_tcn"     "next_tcn_residual" "az_1f50ep_cathead_next_tcn_residual"
run "f27_tcnn"    "next_temporal_cnn" "az_1f50ep_cathead_next_temporal_cnn"

echo ""
echo "================================================================"
echo "=== F27 sweep complete at $(date)"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
