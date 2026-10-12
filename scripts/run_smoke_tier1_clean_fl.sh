#!/usr/bin/env bash
# Tier-1 verification smokes (1f×10ep each — ~3 min on RTX 4090).
# Per F50_T4_RERUN_DECISION.md these are *verification* smokes, not full
# 5-fold runs. Goals:
#   - PLE clean: confirm uniform-leak hypothesis (one architectural alt
#     should drop ~16 pp like H3-alt did)
#   - TGSTAN clean + leaky: quantify whether the per-sample gate
#     amplifies the leak BEYOND the α-only mechanism (audit's #2 flag)
# Reduced from 5f×50ep to 1f×10ep to keep this fast — total ~9 min vs
# 38 min sequential. We're testing magnitudes, not paper-grade Δs here.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

base_fl_smoke=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --mtl-loss static_weight --category-weight 0.75
    --cat-head next_gru
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 1 --epochs 10 --seed 42 --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --scheduler constant
    --min-best-epoch 3
    --no-checkpoints --no-folds-cache
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# 1. PLE-lite clean — uniform-leak confirmation
#    Pre-C4 leaky PLE @≥ep5: 74.97 (full 5f). Clean smoke should show
#    similar drop magnitude (~14 pp → expect ~60-61).
run "f50_p0e_ple_clean_smoke_fl" \
    "${base_fl_smoke[@]}" \
    --model mtlnet_ple \
    --reg-head next_getnext_hard \
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

# 2. TGSTAN clean (with --per-fold-transition-dir)
run "f50_p0d_tgstan_clean_smoke_fl" \
    "${base_fl_smoke[@]}" \
    --model mtlnet_crossattn \
    --reg-head next_tgstan \
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

# 3. TGSTAN leaky baseline — needed to compute the TGSTAN-specific Δ.
#    Audit's hypothesis: gate amplifies leak SELECTIVELY → leaky should
#    score MUCH higher (>16 pp gap to clean). If both numbers are
#    similar, gate doesn't matter; if leaky much higher, gate is
#    the second-most-likely C4-class leak.
run "f50_p0d_tgstan_leaky_smoke_fl" \
    "${base_fl_smoke[@]}" \
    --model mtlnet_crossattn \
    --reg-head next_tgstan
    # NOTE: deliberately NO --per-fold-transition-dir → uses full log_T

echo ""
echo "================================================================"
echo "=== Tier-1 smoke queue COMPLETE $(date) ==="
echo "================================================================"
