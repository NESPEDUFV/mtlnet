#!/usr/bin/env bash
# Round 3 — try alternative MTL backbones with `next_stan` reg head.
# Cross-attn forces shared representation, hurting reg below STL ceiling.
# MoE-family architectures (MMoE/PLE/CGC) keep task-specific experts and let
# each task gate its own combination — canonical fix for negative transfer.
# Cross-Stitch learns a 2×2 mixing matrix between task streams (lighter
# coupling than full cross-attn).
#
# Configs (all at AZ, 5f×50ep, seed 42, PCGrad, OneCycleLR(max-lr=3e-3),
# bias_init=gaussian, d_model=256, num_heads=8):
#   M1: mtlnet_mmoe        — Multi-gate MoE (Ma 2018)
#   M2: mtlnet_ple         — Progressive Layered Extraction (Tang 2020)
#   M3: mtlnet_cgc         — Customized Gate Control (PLE precursor)
#   M4: mtlnet_crossstitch — Cross-Stitch (Misra 2016)
#
# Reference: A baseline (mtlnet_crossattn + next_stan + PCGrad) reg=41.52,
# cat=49.09. STL ceiling reg=52.24.

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
    --mtl-loss pcgrad
)

run_bg "stan_mtl_az_M1_mmoe"        scripts/train.py "${common[@]}" --model mtlnet_mmoe
run_bg "stan_mtl_az_M2_ple"         scripts/train.py "${common[@]}" --model mtlnet_ple
run_bg "stan_mtl_az_M3_cgc"         scripts/train.py "${common[@]}" --model mtlnet_cgc
run_bg "stan_mtl_az_M4_crossstitch" scripts/train.py "${common[@]}" --model mtlnet_crossstitch

wait
echo "=== Round 3 AZ done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
