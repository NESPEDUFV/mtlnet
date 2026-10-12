#!/usr/bin/env bash
# F2 — FL-hard training-pathology diagnosis (north-star re-evaluation gate)
#
# See docs/studies/check2hgi/FOLLOWUPS_TRACKER.md §F2
# See docs/review/2026-04-23_critical_review.md §1.5
#
# Four sequential FL 1-fold × 50-epoch runs with `next_getnext_hard`:
#   A  : PCGrad baseline + checkpoints (extract final α)
#   B1 : static_weight, category_weight = 0.25 (reg-heavy, tests "does cat still starve even without PCGrad?")
#   B2 : static_weight, category_weight = 0.50 (equal-weight, the user-specified rescue point)
#   B3 : static_weight, category_weight = 0.75 (cat-heavy, tests rescue saturation)
#
# Runtime expectation: ~48 min each × 4 = ~3.2 h on M4 Pro MPS.
#
# Acceptance: if any static_weight variant restores cat F1 ≥ 60 while
# keeping reg Acc@5 ≥ +8 pp over soft (i.e., ≥ 44), north-star choice
# re-opens. Otherwise soft stays and hard is explained in the paper as
# a ≤1.5K-region-scale ablation.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F2_fl_diagnostic"
mkdir -p "${DEST}"

archive_latest_run() {
    local dest_name="$1"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/florida/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        # Also save the run dir path for α inspection (Phase A only)
        echo "${latest}" > "${DEST}/${dest_name}.run_dir"
        echo "[F2] saved → ${DEST}/${dest_name}.json (run dir: ${latest})"
    else
        echo "[F2] WARNING: no summary JSON found for ${dest_name}"
    fi
}

run() {
    local tag="$1" dest_name="$2"; shift 2
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$PY" -u scripts/train.py --state florida "$@"
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && archive_latest_run "${dest_name}"
}

COMMON_ARGS=(
    --task mtl --task-set check2hgi_next_region --engine check2hgi
    --folds 1 --epochs 50 --seed 42
    --task-a-input-type checkin --task-b-input-type region
    --model mtlnet_crossattn
    --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param transition_path="${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --max-lr 0.003 --gradient-accumulation-steps 1
)

# --- Phase A: PCGrad baseline + checkpoints (α inspection) ---
run "F2_A_pcgrad_ckpt" "fl_1f50ep_hard_pcgrad_ckpt" \
    "${COMMON_ARGS[@]}" --mtl-loss pcgrad
    # NOTE: --no-checkpoints is intentionally OMITTED here so α is saved

# --- Phase B1: static_weight, category=0.25 ---
run "F2_B1_static_cat0.25" "fl_1f50ep_hard_static_cat0.25" \
    "${COMMON_ARGS[@]}" --mtl-loss static_weight --category-weight 0.25 --no-checkpoints

# --- Phase B2: static_weight, category=0.50 (user-specified rescue point) ---
run "F2_B2_static_cat0.50" "fl_1f50ep_hard_static_cat0.50" \
    "${COMMON_ARGS[@]}" --mtl-loss static_weight --category-weight 0.50 --no-checkpoints

# --- Phase B3: static_weight, category=0.75 ---
run "F2_B3_static_cat0.75" "fl_1f50ep_hard_static_cat0.75" \
    "${COMMON_ARGS[@]}" --mtl-loss static_weight --category-weight 0.75 --no-checkpoints

echo ""
echo "================================================================"
echo "=== F2 FL-hard diagnostic complete at $(date)"
echo "=== results in ${DEST}/"
echo "=== Next: inspect α from Phase A checkpoint, compare cat F1 across"
echo "=== Phases B1/B2/B3 vs soft baseline (66.01) and hard baseline (55.43)."
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
