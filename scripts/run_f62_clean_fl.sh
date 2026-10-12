#!/usr/bin/env bash
# F62 two-phase step-schedule with leak-free per-fold log_T.
# NOTE: --alternating-optimizer-step requires --mtl-loss static_weight, so
# F62 (which needs scheduled_static for the step schedule) cannot stack
# with P4. This is a DIFFERENT mechanism — pure temporal separation
# (cat_weight=0 ep 0-19, then 0.75 ep 20-49) without P4's per-batch
# alternation. Tests if temporal separation alone is sufficient.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

"$PY" -u scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state florida --engine check2hgi \
    --model mtlnet_crossattn \
    --cat-head next_gru --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --task-a-input-type checkin --task-b-input-type region \
    --folds 5 --epochs 50 --seed 42 --batch-size 2048 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --gradient-accumulation-steps 1 \
    --scheduler cosine --max-lr 3e-3 \
    --min-best-epoch 5 \
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
    --mtl-loss scheduled_static \
    --mtl-loss-param mode=step \
    --mtl-loss-param cat_weight_start=0.0 \
    --mtl-loss-param cat_weight_end=0.75 \
    --mtl-loss-param warmup_epochs=20 \
    --mtl-loss-param total_epochs=50 \
    --no-checkpoints --no-folds-cache \
    2>&1 | tee logs/f50_f62_clean_fl.log
