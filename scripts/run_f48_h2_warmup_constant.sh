#!/usr/bin/env bash
# F48-H2 — warmup-then-plateau scheduler. Single LR (not per-head).
# Linear warmup ~50ep from 0.033*max_lr → max_lr, then plateau at max_lr
# for the remaining ~100ep. Total 150ep.
#
# Hypothesis: gentle ramp during warmup lets the 7-class cat head
# (next_gru) stabilise before hitting the lethal sustained 3e-3
# regime that collapses cat in F45/H3 (sh=3e-3). Reg gets 100ep
# of sustained 3e-3 in the plateau phase — enough for α (graph-prior
# weight in next_getnext_hard.head) to grow per F45 mechanism.
#
# Comparison points (single-LR family):
#   B3 50ep OneCycleLR max=3e-3:  AL cat 42.71 / reg 59.60   AZ 45.81 / 53.82
#   F45 const 3e-3 (no warmup):   AL cat 10.44 / reg 74.20   AZ 12.23 / 63.34
#   F48-H1 const 1e-3:            AL cat 40.99 / reg 61.43   AZ 45.34 / 50.68
#   F48-H3-alt per-head:          AL cat 42.22 / reg 74.62   AZ 45.11 / 63.45  (winning recipe)
#
# Acceptance:
#   cat F1 ≥ 35 AND reg Acc@10 ≥ 65 → warmup mechanism alone is sufficient
#                                      (alternative paper recipe, simpler
#                                      than per-head LR)
#   cat preserved AND reg flat ~60 → warmup buys nothing for reg; per-head
#                                    LR is the only fix
#   cat collapse → warmup insufficient; cat dies once it hits plateau

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

run() {
    local tag="$1" state="$2" max_lr="$3" pct="$4" batch="$5"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} max_lr=${max_lr} warmup_pct=${pct} batch=${batch})"
    echo "================================================================"
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
        --folds 5 --epochs 150 --seed 42 \
        --batch-size "${batch}" --max-lr "${max_lr}" \
        --scheduler warmup_constant --pct-start "${pct}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
}

# AL ~80 min + AZ ~150 min = ~3.8h sequential on MPS
run "f48_h2_al" alabama 3e-3 0.333 2048
run "f48_h2_az" arizona 3e-3 0.333 2048

echo ""
echo "================================================================"
echo "=== F48-H2 AL+AZ complete at $(date)"
echo "=== Compare cat F1 / reg Acc@10 to H3-alt and F45"
echo "================================================================"
