#!/usr/bin/env bash
# F51 Tier 3 — optimizer/scheduler hyperparameter sweep around B9 (FL).
#
# Phase 0 of the paper-closure plan. Reviewer-rebuttal insurance:
# bank a clean negative (or small positive) before the cross-state
# closure runs consume H100 budget.
#
# Recipe base: B9 champion at FL, 5 folds × 30 epochs, seed=42.
# 5 folds (not 1) because the per-fold log_T is 5-fold-keyed; --folds 1
# would silently re-introduce a partial C4 leak.
#
# Sweep matrix (15 smokes):
#   weight_decay   {0.0, 0.01, 0.1, 0.2}      [B9 default 0.05]
#   max_grad_norm  {0.5, 2.0, 5.0, 0.0}       [B9 default 1.0; 0 disables]
#   eta_min        {1e-5, 1e-4}               [B9 default 0; cosine floor]
#   pct_start      {0.1, 0.4, 0.5}            [requires --scheduler onecycle]
#   adam_eps       {1e-7, 1e-6}               [B9 default 1e-8]
#
# Promotion rule: if any smoke beats B9 reg-best by >0.5 pp at ≥ep5,
# promote to 5f×50ep paper-grade.
#
# Parallelism: 3-way on H100 (B9 ~6-10 GB/job, plenty of headroom on 80GB).
# ETA: ~50-60 min wall.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
PY="${PY:-python}"
MAX_JOBS="${MAX_JOBS:-3}"
cd "${WORKTREE}"
mkdir -p logs

wait_slot() {
    while [ "$(jobs -rp | wc -l)" -ge "${MAX_JOBS}" ]; do
        wait -n
    done
}

run_bg() {
    local tag="$1"; shift
    wait_slot
    (
        echo "================================================================"
        echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u scripts/train.py "$@" >"logs/${tag}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

# B9 base recipe at FL, 5f×30ep, seed=42 — recipe-specific knobs added per call.
b9_base=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 30 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
    --alternating-optimizer-step
    --alpha-no-weight-decay
)

# Default scheduler for non-pct_start sweeps: cosine + max_lr 3e-3.
b9_cosine=(--scheduler cosine --max-lr 3e-3)

# 1. weight_decay sweep (cosine base)
for v in 0.0 0.01 0.1 0.2; do
    run_bg "f51_t3_wd_${v}" \
        "${b9_base[@]}" "${b9_cosine[@]}" \
        --weight-decay "${v}"
done

# 2. max_grad_norm sweep (cosine base)
for v in 0.5 2.0 5.0 0.0; do
    run_bg "f51_t3_gradclip_${v}" \
        "${b9_base[@]}" "${b9_cosine[@]}" \
        --max-grad-norm "${v}"
done

# 3. eta_min sweep (cosine base — eta_min only matters for cosine)
for v in 1e-5 1e-4; do
    run_bg "f51_t3_etamin_${v}" \
        "${b9_base[@]}" "${b9_cosine[@]}" \
        --eta-min "${v}"
done

# 4. pct_start sweep (requires --scheduler onecycle, NOT cosine)
for v in 0.1 0.4 0.5; do
    run_bg "f51_t3_pctstart_${v}" \
        "${b9_base[@]}" \
        --scheduler onecycle --max-lr 3e-3 \
        --pct-start "${v}"
done

# 5. adam_eps sweep (cosine base)
for v in 1e-7 1e-6; do
    run_bg "f51_t3_adameps_${v}" \
        "${b9_base[@]}" "${b9_cosine[@]}" \
        --adam-eps "${v}"
done

wait
echo "================================================================"
echo "=== F51 Tier 3 sweep done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== Logs: logs/f51_t3_*.log"
echo "=== Summarize: grep -E 'reg.*best|reg @ep' logs/f51_t3_*.log"
echo "================================================================"
