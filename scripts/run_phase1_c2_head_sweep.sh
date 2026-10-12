#!/usr/bin/env bash
# C2 — head-agnostic probe at AL+AZ.
# We already have:
#   - linear probe (head-free) — Leg I
#   - next_gru (matched head) — Leg II.1
# This script adds two probe heads: next_single (the existing P1_5b CH16 head)
# and next_lstm (a second sequential head). Sign(Δ_substrate) consistency
# across {linear, next_gru, next_single, next_lstm} closes C2.
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export DATA_ROOT=/Users/vitor/Desktop/mestrado/ingred
export OUTPUT_DIR=/Users/vitor/Desktop/mestrado/ingred/output
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1

mkdir -p logs

run() {
    local STATE="$1" ENGINE="$2" HEAD="$3"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="STL_${UPSTATE}_${ENGINE}_cat_${HEAD}_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    caffeinate -s python3 scripts/train.py \
        --task next --state "${STATE}" --engine "${ENGINE}" \
        --model "${HEAD}" \
        --folds 5 --epochs 50 --seed 42 --no-checkpoints \
        > "logs/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
}

# AL — both substrates × 2 heads
for HEAD in next_single next_lstm; do
    run alabama check2hgi $HEAD
    run alabama hgi       $HEAD
done

# AZ — both substrates × 2 heads
for HEAD in next_single next_lstm; do
    run arizona check2hgi $HEAD
    run arizona hgi       $HEAD
done

echo ""
echo "=== Phase 1 C2 head sweep complete at $(date)"
