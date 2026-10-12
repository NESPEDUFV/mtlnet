#!/usr/bin/env bash
# F50 D5 — encoder weight-trajectory diagnostic. Two paired 1-fold runs at
# FL with per-fold log_T (clean):
#   1. H3-alt baseline — the predecessor MTL recipe (no P4)
#   2. B9 champion — P4 + Cosine + alpha-no-WD
#
# Both runs log per-epoch Frobenius norm + drift of `next_encoder` and
# `category_encoder`. Hypothesis: reg-side drift saturates earlier than
# cat-side under joint training, paralleling reg-best epoch ~5 vs cat-best
# epoch ~16. Total wall-clock: ~6 min on 4090 (1 fold × 50 ep × bs=2048).
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
    --folds 1 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# 1. H3-alt baseline — no alt-SGD, scheduler=constant.
run "f50_d5_h3alt_traj_fl" \
    "${base_fl[@]}" \
    --mtl-loss static_weight --category-weight 0.75 \
    --scheduler constant

# 2. B9 champion — alt-SGD + Cosine + alpha-no-WD.
run "f50_d5_b9_traj_fl" \
    "${base_fl[@]}" \
    --mtl-loss static_weight --category-weight 0.75 \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

echo "Done — extract trajectories from results/check2hgi/florida/*/diagnostics/"
