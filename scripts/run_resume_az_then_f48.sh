#!/usr/bin/env bash
# Resume launcher — Path A (F44-F47 AZ side) then Path B (F48-H1 AL+AZ).
#
# Path A: F44-F47 AZ — completes the budget/LR sweep on AZ (AL was done
# in the previous session). ~170 min.
#
# Path B: F48-H1 — single design test. Constant LR=1e-3 (instead of 3e-3)
# for 150 ep, AL + AZ. Hypothesis: gentler constant LR preserves cat
# (avoids the F45 collapse from sustained 3e-3) while still extending the
# effective high-LR window enough to recover reg toward 65-74. If reg
# lands in [65, 74] with cat ≥ 35, we have a hybrid regime worth scaling.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

# Build extra-args via string to dodge `set -u` + empty-array bash gotcha.
run() {
    local tag="$1" state="$2" epochs="$3" max_lr="$4" scheduler="$5" pct_start="$6"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} eps=${epochs} lr=${max_lr} sched=${scheduler} pct=${pct_start})"
    echo "================================================================"
    local extra_args=""
    if [[ "${scheduler}" != "onecycle" ]]; then
        extra_args="${extra_args} --scheduler ${scheduler}"
    fi
    if [[ "${pct_start}" != "default" ]]; then
        extra_args="${extra_args} --pct-start ${pct_start}"
    fi
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight \
        --category-weight 0.75 \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs "${epochs}" --seed 42 \
        --batch-size 2048 --max-lr "${max_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache \
        ${extra_args}
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

echo "================================================================"
echo "=== PATH A: F44-F47 AZ side ($(date))"
echo "================================================================"

run "f44_az" arizona 150 1e-3 onecycle default
run "f45_az" arizona 150 3e-3 constant default
run "f46_az" arizona 50  3e-3 onecycle 0.1
run "f47_az" arizona 75  3e-3 onecycle default

echo ""
echo "================================================================"
echo "=== PATH B: F48-H1 — constant LR=1e-3 @ 150ep, AL + AZ ($(date))"
echo "================================================================"

run "f48_h1_al" alabama 150 1e-3 constant default
run "f48_h1_az" arizona 150 1e-3 constant default

echo ""
echo "================================================================"
echo "=== Resume sweep COMPLETE at $(date)"
echo "=== JSONs under results/check2hgi/<state>/mtlnet_*_<ts>/summary/"
echo "================================================================"
