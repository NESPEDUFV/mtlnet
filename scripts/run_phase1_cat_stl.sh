#!/usr/bin/env bash
# Phase 1 Leg II — matched-head cat STL grid (next_gru head, 5f×50ep, seed=42).
# AL × {check2hgi, hgi}  +  AZ × {check2hgi, hgi}  =  4 cells.
#
# AL check2hgi already completed by the time this script ran; can be re-run safely.
# Each AL cell ≈ 3 min, each AZ cell ≈ 6–8 min on M4 Pro MPS.
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export DATA_ROOT=/Users/vitor/Desktop/mestrado/ingred
export OUTPUT_DIR=/Users/vitor/Desktop/mestrado/ingred/output
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1

mkdir -p logs

run() {
    local STATE="$1" ENGINE="$2"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="STL_${UPSTATE}_${ENGINE}_cat_gru_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    caffeinate -s python3 scripts/train.py \
        --task next --state "${STATE}" --engine "${ENGINE}" \
        --model next_gru \
        --folds 5 --epochs 50 --seed 42 --no-checkpoints \
        > "logs/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && grep -E "next.*F1:" "logs/${TAG}.log" | tail -1
}

run alabama check2hgi
run alabama hgi
run arizona check2hgi
run arizona hgi
echo ""
echo "================================================================"
echo "=== Phase 1 cat STL grid complete at $(date)"
echo "================================================================"
