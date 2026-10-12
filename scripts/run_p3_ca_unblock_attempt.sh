#!/usr/bin/env bash
# P3 unblock attempt: CA MTL CH18 on RunPod 4090 (was BLOCKED on Lightning A100
# due to 15 GB RAM ceiling; this env has 503 GB RAM). Tests:
#   1. Whether 24 GB GPU can hold CA's ~8050 region head + cross-attn + heads.
#   2. Whether CPU/RAM-side blocker is just the Lightning quota (resolved here).
#
# Recipe: B9 champion (alt-SGD + Cosine + alpha-no-WD + per-head LR + cw=0.75
# + clean per-fold log_T + min-best-epoch=5). FL paper-headline recipe.
#
# 5f×50ep × bs=2048. ETA depends on CA region count (8050+ vs FL 4702 = ~70%
# more output-space compute). Estimate 30-50 min on 4090.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

# Pre-flight: data must exist; build per-fold log_T if missing.
CA_DIR="${OUTPUT_DIR}/check2hgi/california"
if [[ ! -f "${CA_DIR}/embeddings.parquet" ]]; then
    echo "[ERROR] CA data not fetched yet at ${CA_DIR}. Run runpod_fetch_data.sh california first."
    exit 1
fi
if [[ ! -f "${CA_DIR}/region_transition_log_fold1.pt" ]]; then
    echo "[per-fold log_T] building for CA…"
    "$PY" scripts/compute_region_transition.py \
        --state california --per-fold \
        2>&1 | tee logs/ca_per_fold_logT.log
fi

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# B9 champion at CA. Targeted for A100 (40-80 GB) where the train-side
# logit catting at line mtl_cv.py:541 (CA 8501 regions × ~280K rows × fp32
# = ~9 GB on top of model state) fits comfortably.
run "p3_ca_b9_champion" \
    --task mtl --task-set check2hgi_next_region \
    --state california --engine check2hgi \
    --model mtlnet_crossattn \
    --cat-head next_gru --reg-head next_getnext_hard \
    --reg-head-param d_model=256 --reg-head-param num_heads=8 \
    --reg-head-param "transition_path=${CA_DIR}/region_transition_log.pt" \
    --task-a-input-type checkin --task-b-input-type region \
    --folds 5 --epochs 50 --seed 42 \
    --batch-size 2048 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --gradient-accumulation-steps 1 \
    --per-fold-transition-dir "${CA_DIR}" \
    --no-checkpoints --no-folds-cache \
    --min-best-epoch 5 \
    --mtl-loss static_weight --category-weight 0.75 \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

echo "P3 CA done — extract from results/check2hgi/california/"
