#!/usr/bin/env bash
# Round 1 STAN×MTL optimization sweep at AZ. Pure-CLI variations off the
# canonical baseline (PCGrad + OneCycleLR + uniform LR + bias_init=gaussian
# = 41.52 ± 2.78 reg, 49.09 ± 0.93 cat at AZ).
#
# A = baseline (already done; PID 423286 — not relaunched here)
# B = bias_init=alibi  (recency-decay regularization; current default)
# C = mtl-loss=nashmtl (B9's original outer loop, replacing pcgrad)
# D = reg-lr=1.5e-3    (STAN wants gentler LR than max-lr=3e-3)
# E = mtl-loss=uncertainty_weighting (learnable per-task variance)

set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python}"
mkdir -p logs

run_bg() {
    local tag="$1"; shift
    (
        echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u "$@" >"logs/${tag}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

common=(
    --task mtl --task-set check2hgi_next_region
    --state arizona --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_stan
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --gradient-accumulation-steps 1
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --max-lr 3e-3
)

# B: bias_init=alibi
run_bg "stan_mtl_az_B_alibi" scripts/train.py \
    "${common[@]}" \
    --reg-head-param bias_init=alibi \
    --mtl-loss pcgrad

# C: nashmtl (B9's outer loop without alt-SGD/cosine/per-head LR)
run_bg "stan_mtl_az_C_nashmtl" scripts/train.py \
    "${common[@]}" \
    --reg-head-param bias_init=gaussian \
    --mtl-loss nashmtl

# D: reg-lr=1.5e-3 lower than peak max-lr=3e-3
run_bg "stan_mtl_az_D_reglrlow" scripts/train.py \
    "${common[@]}" \
    --reg-head-param bias_init=gaussian \
    --mtl-loss pcgrad \
    --cat-lr 3e-3 --reg-lr 1.5e-3 --shared-lr 3e-3

# E: uncertainty_weighting
run_bg "stan_mtl_az_E_uw" scripts/train.py \
    "${common[@]}" \
    --reg-head-param bias_init=gaussian \
    --mtl-loss uncertainty_weighting

wait
echo "=== round 1 AZ done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
