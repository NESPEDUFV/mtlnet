#!/usr/bin/env bash
# F50 T3 / D34 — category_weight sensitivity sweep at FL.
#
# Tests mechanism α (loss-side scaling starves reg encoder): if reducing
# cat_weight unlocks reg performance, the absorption + reg-encoder-dead
# story is hyperparameter-confirmed, not architectural.
#
# Sweep: cat_weight ∈ {0.50, 0.25}. Baseline cat_weight=0.75 = CUDA H3-alt _0153.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" cw="$2"
    echo ""
    echo "=== [${tag}] start $(date) (cat_weight=${cw}) ==="
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state florida --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight "${cw}" \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t3_h3alt_cw0.50_fl" 0.50
run "f50_t3_h3alt_cw0.25_fl" 0.25
