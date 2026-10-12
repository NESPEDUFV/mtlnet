#!/usr/bin/env bash
# F53 — category_weight sensitivity sweep at FL.
# 6 runs: {H3-alt, P1=no_crossattn} × {cw=0.25, 0.50, 0.75}
# All clean (per-fold log_T). 5f×50ep × bs=2048 ≈ 19 min each → ~115 min total.
#
# Hypothesis: if lowering cw unlocks cross-attn (P1 grows toward H3-alt as cw drops),
# absorption mechanism is hyperparameter-confirmed. If P1 ≈ H3-alt at all cw, the
# absorption is structural to the architecture, not balance-of-weights.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

base_fl=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight
    --scheduler constant
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# H3-alt sweep (cross-attn ON)
for cw in 0.25 0.50 0.75; do
    run "f53_h3alt_cw${cw}_fl" "${base_fl[@]}" --category-weight "${cw}"
done

# P1 sweep (cross-attn OFF, disable_cross_attn=true)
for cw in 0.25 0.50 0.75; do
    run "f53_p1_cw${cw}_fl" "${base_fl[@]}" \
        --category-weight "${cw}" \
        --model-param disable_cross_attn=true
done

echo "F53 sweep complete — extract from logs/f53_*.log + results/check2hgi/florida/"
