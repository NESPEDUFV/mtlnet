#!/usr/bin/env bash
# Phase 1 Leg II — matched-head reg STL grid (next_getnext_hard, 5f×50ep, seed=42).
# Check2HGI side already done by F21c at AL+AZ (results/B3_baselines/stl_getnext_hard_*.json).
# This script lands the missing HGI side at AL+AZ.
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export DATA_ROOT=/Users/vitor/Desktop/mestrado/ingred
export OUTPUT_DIR=/Users/vitor/Desktop/mestrado/ingred/output
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1

mkdir -p logs

run() {
    local STATE="$1" SUBSTRATE="$2"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="STL_${UPSTATE}_${SUBSTRATE}_reg_gethard_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    caffeinate -s python3 scripts/p1_region_head_ablation.py \
        --state "${STATE}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --input-type region \
        --region-emb-source "${SUBSTRATE}" \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
        --tag "${TAG}" \
        > "logs/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
}

# Check2HGI side already done — only HGI runs needed
run alabama hgi
run arizona hgi
echo ""
echo "=== Phase 1 reg STL HGI grid complete at $(date)"
