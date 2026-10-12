#!/usr/bin/env bash
# Phase 1 Leg III — MTL counterfactual: B3 north_star with HGI substrate.
# Tests "MTL Check2HGI > MTL HGI" — closes the substrate-claim loop.
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export DATA_ROOT=/Users/vitor/Desktop/mestrado/ingred
export OUTPUT_DIR=/Users/vitor/Desktop/mestrado/ingred/output
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1

mkdir -p logs

run() {
    local STATE="$1"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="MTL_B3_${UPSTATE}_hgi_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    caffeinate -s python3 scripts/train.py \
        --task mtl --state "${STATE}" --engine hgi \
        --task-set check2hgi_next_region \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --reg-head next_getnext_hard --cat-head next_gru \
        --folds 5 --epochs 50 --seed 42 --no-checkpoints \
        > "logs/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
}

run alabama
run arizona
echo ""
echo "=== Phase 1 MTL counterfactual complete at $(date)"
