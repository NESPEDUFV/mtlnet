#!/usr/bin/env bash
# F44-F47 — Clean budget / LR-schedule tests to disambiguate F42's inverted
# finding (150ep + OneCycleLR stretched hurt: reg Acc@10 59.60 → 56.14).
#
# F42 confounded "more epochs" with "stretched OneCycleLR schedule": at 150ep
# the max_lr=3e-3 peak migrated from ep15 to ep45, and the model's best
# shifted from ep34-46 (50ep annealing phase) to ep20-27 (150ep warmup).
#
# F44: 150ep + max_lr=1e-3     — lower peak, gentler OneCycleLR
# F45: 150ep + constant LR=3e-3 — no warmup/anneal, "more epochs" in isolation
# F46: 50ep  + pct_start=0.1   — peak at ep5, leaves 45 ep for annealing
# F47: 75ep  + max_lr=3e-3     — intermediate budget (interpolates F31 and F42)
#
# Both AL and AZ — tests if the trend is state-scale-dependent.
#
# Baselines to compare against:
#   B3 AL 50ep (F31):    59.60 ± 4.09 reg Acc@10
#   B3 AZ 50ep (F27):    53.82 ± 3.11
#   F42 AL 150ep (default): 56.14 ± 4.00
#   STL F21c AL:         68.37 ± 2.66 (ceiling)
#   STL F21c AZ:         66.74 ± 2.11
#
# Cost estimate: AL ~85 min + AZ ~170 min = ~4.3 h sequential.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

# Common B3 config, parametric over epochs/lr/scheduler/pct_start.
run() {
    local tag="$1" state="$2" epochs="$3" max_lr="$4" scheduler="$5" pct_start="$6"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} eps=${epochs} lr=${max_lr} sched=${scheduler} pct=${pct_start})"
    echo "================================================================"
    # Build extra args as a string to dodge `set -u` + empty array issue
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

# AL first (cheaper, ~85 min total)
run "f44_al" alabama 150 1e-3 onecycle default
run "f45_al" alabama 150 3e-3 constant default
run "f46_al" alabama 50  3e-3 onecycle 0.1
run "f47_al" alabama 75  3e-3 onecycle default

# AZ next (~170 min total)
run "f44_az" arizona 150 1e-3 onecycle default
run "f45_az" arizona 150 3e-3 constant default
run "f46_az" arizona 50  3e-3 onecycle 0.1
run "f47_az" arizona 75  3e-3 onecycle default

echo ""
echo "================================================================"
echo "=== F44-F47 AL + AZ complete at $(date)"
echo "=== JSONs under results/check2hgi/<state>/mtlnet_*_<ts>/summary/"
echo "=== Compare reg top10_acc_indist mean + σ to B3 50ep baseline"
echo "================================================================"
