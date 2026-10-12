#!/usr/bin/env bash
# F50 D8 — MTL pipeline with category_weight=0.0 at FL 5f×50ep.
# Limit case: if cw=0 → STL ceiling (82.44), the only issue was loss-side
# scaling and the MTL pipeline is fine. If cw=0 → ~75, there's an additional
# factor (e.g., dataloader cycling, scheduler interaction). Combined with
# D1+D6+cat_weight sweep, this maps the full mechanism-α picture.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

echo "=== [D8 cw=0] start $(date) ==="
"$PY" -u scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state florida --engine check2hgi \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.0 \
    --cat-head next_gru --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --task-a-input-type checkin --task-b-input-type region \
    --folds 5 --epochs 50 --seed 42 \
    --batch-size "${BATCH_SIZE:-2048}" \
    --scheduler constant \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --gradient-accumulation-steps 1 \
    --no-checkpoints --no-folds-cache 2>&1 | tee "logs/f50_d8_cw0_fl.log"
rc=${PIPESTATUS[0]}
echo "[D8] exit ${rc} at $(date)"
