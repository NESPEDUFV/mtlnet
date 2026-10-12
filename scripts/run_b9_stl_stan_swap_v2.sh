#!/usr/bin/env bash
# v2 diagnostic — first attempt collapsed because B9's optimizer ingredients
# (alt-SGD + cosine + per-head LR + α-no-WD) were tuned around
# `next_getnext_hard`'s α scalar; `next_stan` has no α, so alt-SGD halves
# its update steps for nothing and cosine + low base LR starve it.
#
# Two configs × {AZ, FL}:
#
#   A "canonical MTL+STAN"  — match working `MTL_WITH_STAN_HEAD.md` config:
#       pcgrad, OneCycleLR(max-lr=3e-3), no per-head LRs, no alt-SGD,
#       no cosine, no α-no-WD, cw not relevant under pcgrad. This is
#       the known-good baseline at AL/AZ.
#
#   B "B9 loss + clean optimizer" — B9's loss (static_weight cw=0.75) +
#       OneCycleLR + uniform LR. Isolates whether the cw=0.75 task-weight
#       (the B9 *loss* component) survives the head swap when the B9
#       *optimizer* ingredients are removed.
#
# Both configs use bias_init=gaussian (legacy STAN default that the working
# AL/AZ MTL+STAN runs used; current `next_stan` default switched to alibi
# on 2026-04-22). Reverting to gaussian rules out alibi as a confound.

set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-python}"
mkdir -p logs

run_bg() {
    local tag="$1"; shift
    (
        echo "================================================================"
        echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u "$@" >"logs/${tag}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

common=(
    --task mtl --task-set check2hgi_next_region
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_stan
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param bias_init=gaussian
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --gradient-accumulation-steps 1
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --max-lr 3e-3
)

# Config A: canonical MTL+STAN (matches MTL_WITH_STAN_HEAD.md AL/AZ baseline)
run_bg "b9stan_v2_canonical_az" scripts/train.py \
    "${common[@]}" --state arizona --engine check2hgi \
    --mtl-loss pcgrad

run_bg "b9stan_v2_canonical_fl" scripts/train.py \
    "${common[@]}" --state florida --engine check2hgi \
    --mtl-loss pcgrad

# Config B: B9 loss component (cw=0.75) but clean optimizer
run_bg "b9stan_v2_cw075_az" scripts/train.py \
    "${common[@]}" --state arizona --engine check2hgi \
    --mtl-loss static_weight --category-weight 0.75

run_bg "b9stan_v2_cw075_fl" scripts/train.py \
    "${common[@]}" --state florida --engine check2hgi \
    --mtl-loss static_weight --category-weight 0.75

wait
echo "=== v2 swap done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
