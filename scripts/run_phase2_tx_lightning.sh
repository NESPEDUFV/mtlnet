#!/usr/bin/env bash
# Phase 2 — TX grid on Lightning T4 (15 GB RAM, 15 GB VRAM).
# Runs: F40b cat STL ×2 + F40c reg STL ×2 (probes handled separately).
# Skips MTL CH18 (28 GiB RAM constraint, see PHASE2_TRACKER §7C).
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export OUTPUT_DIR=/teamspace/studios/this_studio/PoiMtlNet/output

mkdir -p logs/phase2_lightning

run_cat() {
    local STATE="$1" ENGINE="$2"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="STL_${UPSTATE}_${ENGINE}_cat_gru_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    python3 -u scripts/train.py \
        --task next --state "${STATE}" --engine "${ENGINE}" \
        --model next_gru \
        --folds 5 --epochs 50 --seed 42 --no-checkpoints \
        > "logs/phase2_lightning/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
}

run_reg() {
    local STATE="$1" ENGINE="$2"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="STL_${UPSTATE}_${ENGINE}_reg_gethard_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    python3 -u scripts/p1_region_head_ablation.py \
        --state "${STATE}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --input-type region \
        --region-emb-source "${ENGINE}" \
        --override-hparams d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
        --tag "${TAG}" \
        > "logs/phase2_lightning/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
}

STATE=texas
echo "######## Phase 2 ${STATE} grid start $(date) ########"
run_cat "$STATE" check2hgi
run_cat "$STATE" hgi
run_reg "$STATE" check2hgi
run_reg "$STATE" hgi
echo ""
echo "######## Phase 2 ${STATE} grid complete $(date) ########"
