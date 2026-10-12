#!/usr/bin/env bash
# F50 T1.5-P2 — `--detach-crossattn-kv` on H3-alt MTL, FL 5f×50ep.
#
# Direct test of the F49 Layer 2 mechanism under full-MTL conditions:
# .detach() K/V in cross_ab/cross_ba so reg-loss gradients don't flow
# back through the cat encoder (and vice versa). If P2 recovers FL Δm
# vs CUDA H3-alt baseline (73.61 ± 0.83), the silent gradient leakage
# IS the FL flaw and we have a paper-headline minimal-edit fix.
#
# All other config matches H3-alt verbatim.
#
# Batch size:
#   - CUDA (default 2048): matches NORTH_STAR.md / H3-alt champion.
#   - MPS (M4 Pro): `BATCH_SIZE=1024 bash scripts/run_f50_t1_5_p2_detach_kv_fl.sh`.

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
        --model-param detach_crossattn_kv=true \
        --mtl-loss static_weight \
        --category-weight 0.75 \
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

run "f50_t1_5_p2_detach_kv_fl" florida 1e-3 3e-3 1e-3

echo ""
echo "================================================================"
echo "=== F50 T1.5-P2 detach-K/V FL COMPLETE at $(date)"
echo "=== Compare reg Acc@10_indist (per-task-best) to:"
echo "===   CUDA H3-alt FL = 73.61 ± 0.83  (substrate-matched baseline)"
echo "===   STL ceiling FL = 82.44 ± 0.38"
echo "=== Acceptance: detach-K/V reg top10 >= 76.61 closes >=3 pp"
echo "================================================================"
