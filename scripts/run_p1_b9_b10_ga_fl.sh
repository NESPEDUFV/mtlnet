#!/usr/bin/env bash
# Post-P0A queue: P1 runs (B9, B10) + cross-state validation (GA, AL, AZ).
# All recipes stack on the P4+Cosine champion.
# Run after P0-A completes.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

# Build per-fold log_T for cross-state runs (skip if already built or
# data missing). The C4 fix requires per-fold prior to avoid val→train
# leakage in the GETNext graph prior.
build_per_fold_logT() {
    local state="$1"
    if [ ! -f "${OUTPUT_DIR}/check2hgi/${state}/temp/sequences_next.parquet" ]; then
        echo "[skip-build] ${state} sequences_next missing — skip per-fold build"
        return 1
    fi
    if [ -f "${OUTPUT_DIR}/check2hgi/${state}/region_transition_log_fold5.pt" ]; then
        echo "[skip-build] ${state} per-fold log_T already exists"
        return 0
    fi
    echo "[build] per-fold log_T for ${state}"
    "$PY" scripts/compute_region_transition.py --state "${state}" --per-fold 2>&1 | tail -8
    return $?
}

build_per_fold_logT georgia
build_per_fold_logT alabama
build_per_fold_logT arizona

# Champion-recipe flags shared across all runs (state-overridden per call)
champion_flags() {
    local state="$1"
    cat <<EOF
--task mtl --task-set check2hgi_next_region
--state ${state} --engine check2hgi
--model mtlnet_crossattn
--mtl-loss static_weight --category-weight 0.75
--cat-head next_gru --reg-head next_getnext_hard
--reg-head-param d_model=256 --reg-head-param num_heads=8
--reg-head-param transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt
--task-a-input-type checkin --task-b-input-type region
--folds 5 --epochs 50 --seed 42
--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
--gradient-accumulation-steps 1
--alternating-optimizer-step
--scheduler cosine --max-lr 3e-3
--min-best-epoch 10
--per-fold-transition-dir ${OUTPUT_DIR}/check2hgi/${state}
--no-checkpoints --no-folds-cache
EOF
}

run() {
    local tag="$1"; shift
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# ---------------------------------------------------------------------------
# P1 — close the residual 6.37 pp gap on FL
# ---------------------------------------------------------------------------

# P1-A B9: exempt α from weight decay (champion + --alpha-no-weight-decay)
run "f50_p1a_b9_alpha_no_wd_fl" \
    $(champion_flags florida) --batch-size 2048 --alpha-no-weight-decay

# P1-C B10: 2× α steps via half batch (champion + bs=1024)
run "f50_p1c_b10_bs1024_fl" \
    $(champion_flags florida) --batch-size 1024

# ---------------------------------------------------------------------------
# P0-cross — champion at smaller-cardinality states (portability check)
# ---------------------------------------------------------------------------

# Georgia (2283 regions) — small, fast smoke (was substitute when AL/AZ blocked)
if [ -f "${OUTPUT_DIR}/check2hgi/georgia/region_transition_log_fold5.pt" ]; then
    run "f50_p0_cross_ga_champion" \
        $(champion_flags georgia) --batch-size 2048
fi

# Alabama (1109 regions) — canonical cross-state validation target
if [ -f "${OUTPUT_DIR}/check2hgi/alabama/region_transition_log_fold5.pt" ]; then
    run "f50_p0_cross_al_champion" \
        $(champion_flags alabama) --batch-size 2048
fi

# Arizona — pairs with AL for cross-cardinality story
if [ -f "${OUTPUT_DIR}/check2hgi/arizona/region_transition_log_fold5.pt" ]; then
    run "f50_p0_cross_az_champion" \
        $(champion_flags arizona) --batch-size 2048
fi

# ---------------------------------------------------------------------------
# F62 — two-phase via step-schedule (orthogonal mechanism vs P4)
# ---------------------------------------------------------------------------
# Tests temporal separation: reg-only for first 25 epochs (cw=0), then
# joint MTL for last 25 (cw=0.75). Different mechanism from P4 which
# does per-batch alternating. If F62 wins → mechanism is "reg gets
# pure training time"; if it ties P4 → either intervention sufficient;
# if it loses → P4's per-batch granularity is essential.
# Builds on the champion (cosine + alt-SGD + delayed-min).
run "f50_f62_two_phase_step_fl" \
    $(champion_flags florida | grep -v 'mtl-loss\|category-weight') \
    --batch-size 2048 \
    --mtl-loss scheduled_static \
    --mtl-loss-param mode=step \
    --mtl-loss-param cat_weight_start=0.0 \
    --mtl-loss-param cat_weight_end=0.75 \
    --mtl-loss-param warmup_epochs=20 \
    --mtl-loss-param total_epochs=50

echo ""
echo "================================================================"
echo "=== Post-P0A queue COMPLETE $(date) ==="
echo "================================================================"
