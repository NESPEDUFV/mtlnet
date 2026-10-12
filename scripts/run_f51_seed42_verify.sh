#!/usr/bin/env bash
# F51 verification — re-run B9 at seed=42 with current code.
#
# Hypothesis test: did the multiple commits between 2026-04-29 18:13 (seed=42
# reference run `_1813`) and 2026-04-30 02:39 (multi-seed sweep launch) alter
# the B9-default code path?
#
# If the new fold-1 reg top10 @≥ep5 matches 63.53 (existing 1813 fold-1 max),
# the code is stable and seed=42 truly is a low-outlier partition. If it
# differs, we have a regression to investigate.
#
# 1 fold × 10 epochs ≈ 40 sec on the 4090 — enough to capture the reg-best
# epoch (which is ep 6 in the existing reference).

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

run_dir_target="logs/f51_seed42_verify.log"

echo "================================================================"
echo "=== [f51_seed42_verify] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"

"$PY" -u scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state florida --engine check2hgi \
    --model mtlnet_crossattn \
    --cat-head next_gru --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --task-a-input-type checkin --task-b-input-type region \
    --folds 1 --epochs 10 --seed 42 \
    --batch-size 2048 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --gradient-accumulation-steps 1 \
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
    --no-checkpoints --no-folds-cache \
    --min-best-epoch 5 \
    --mtl-loss static_weight --category-weight 0.75 \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay 2>&1 | tee "${run_dir_target}"

echo "[f51_seed42_verify] exit ${PIPESTATUS[0]} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
