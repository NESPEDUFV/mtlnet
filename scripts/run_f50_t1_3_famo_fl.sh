#!/usr/bin/env bash
# F50 T1.3 — FAMO drop-in replacement of static_weight, FL 5f×50ep.
#
# Tests whether FAMO (NeurIPS 2023) gradient-balancing handles the FL
# negative-transfer regime better than the H3-alt champion's
# static_weight(category_weight=0.75). Per F50 plan §5 + F50 findings:
# H3-alt MTL loses to STL on FL by −8.78 pp paired Wilcoxon p=0.0312;
# T1.3 acceptance criterion is FAMO MTL FL reg Acc@10 ≥ 75.0 (closes
# ≥ 3 pp of the 8.78 pp gap).
#
# DOMAIN-GAP CAVEAT: FAMO's reported wins are on NYUv2/CityScapes/CelebA/QM9
# — none are long-tail multi-class with 4.7K-class softmax. Treat T1.3
# outcome as exploratory.
#
# All other config matches H3-alt (per-head LR, scheduler=constant,
# 50 epochs, seed=42, 5 folds).
#
# Batch size:
#   - CUDA (default 2048): matches NORTH_STAR.md / H3-alt champion. ~19 min
#     per 5f×50ep on RTX 4090 (RunPod). The original 1024 here was an
#     MPS-only carryover from F48-FL legacy; same fix as run_f48_h3alt_fl.sh.
#   - MPS (M4 Pro): `BATCH_SIZE=1024 bash scripts/run_f50_t1_3_famo_fl.sh`.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1" state="$2" cat_lr="$3" reg_lr="$4" shared_lr="$5"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state} cat=${cat_lr} reg=${reg_lr} shared=${shared_lr})"
    echo "================================================================"
    "$PY" -u scripts/train.py \
        --task mtl \
        --task-set check2hgi_next_region \
        --state "${state}" --engine check2hgi \
        --model mtlnet_crossattn \
        --mtl-loss famo \
        --cat-head next_gru \
        --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size "${BATCH_SIZE:-2048}" \
        --scheduler constant \
        --cat-lr "${cat_lr}" --reg-lr "${reg_lr}" --shared-lr "${shared_lr}" \
        --gradient-accumulation-steps 1 \
        --no-checkpoints --no-folds-cache 2>&1 | tee "logs/${tag}.log"
    rc=${PIPESTATUS[0]}
    echo "[${tag}] exit ${rc} at $(date)"
}

run "f50_t1_3_famo_fl" florida 1e-3 3e-3 1e-3

echo ""
echo "================================================================"
echo "=== F50 T1.3 FAMO FL COMPLETE at $(date)"
echo "=== Compare reg Acc@10 to:"
echo "===   STL F21c FL = 82.44 ± 0.38  (matched-head ceiling)"
echo "===   MTL H3-alt FL = 71.96 ± 0.68  (current champion)"
echo "=== Acceptance: FAMO MTL FL reg Acc@10 >= 75.0 closes >=3 pp"
echo "================================================================"
