#!/usr/bin/env bash
# Phase 2 MTL CH18 — CA + TX × {check2hgi, hgi} on Lightning T4.
# Uses the canonical MTL B3 north_star CLI per NORTH_STAR.md.
# Memory caveat: 5-fold pre-materialization in _create_check2hgi_mtl_folds
# may exceed Lightning's 15 GB RAM + 9 GB swap. CA (286k rows) likely fits;
# TX (460k rows) likely OOMs without C2 fold-loading patch.
# Order: CA first (smaller; if it OOMs, abort before TX).
set -u
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export OUTPUT_DIR=/teamspace/studios/this_studio/PoiMtlNet/output
# Memory notes (verified on Lightning T4 2026-04-29):
#   T4 (15 GB VRAM) cannot fit CA MTL at ANY tested batch size due to the
#   8497-region transition prior matrix (274 MB) + cross-attn buffers +
#   STAN backprop intermediates. Failures observed at bs={2048, 1024, 512}
#   all hitting ~14.3-14.5 GB peak with 5-25 MB free at OOM time.
#   Recommendation: L4/A10G (24 GB) or A100 — see docs.
# expandable_segments helps fragmentation (~300 MB recoverable) but is not
# sufficient on its own for CA on T4.
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Canonical batch size (per NORTH_STAR.md / FL B3 reference) is 2048.
# Override via MTL_BATCH_SIZE env var if running on a smaller GPU.
MTL_BS="${MTL_BATCH_SIZE:-2048}"

mkdir -p logs/phase2_lightning

run_mtl() {
    local STATE="$1" ENGINE="$2"
    local UPSTATE=$(echo "${STATE}" | tr '[:lower:]' '[:upper:]')
    local TAG="MTL_B3_${UPSTATE}_${ENGINE}_5f50ep"
    echo ""
    echo "================================================================"
    echo "=== [${TAG}] start $(date)"
    echo "================================================================"
    python3 -u scripts/train.py \
        --task mtl --state "${STATE}" --engine "${ENGINE}" \
        --task-set check2hgi_next_region \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --reg-head next_getnext_hard --cat-head next_gru \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
        --batch-size "${MTL_BS}" \
        --folds 5 --epochs 50 --seed 42 --no-checkpoints \
        > "logs/phase2_lightning/${TAG}.log" 2>&1
    rc=$?
    echo "[${TAG}] exit ${rc} at $(date)"
    return $rc
}

echo "######## Phase 2 MTL CH18 grid start $(date) ########"

# CA first (smaller; likely fits in RAM + swap).
echo "--- CA × c2hgi ---"
if ! run_mtl california check2hgi; then
    echo "[abort] CA × c2hgi failed (likely OOM). Skipping remaining cells."
    echo "######## Phase 2 MTL grid ABORTED $(date) ########"
    exit 1
fi

echo "--- CA × hgi ---"
run_mtl california hgi || echo "[warn] CA × hgi failed; continuing"

# TX (larger; may OOM without C2 patch).
echo "--- TX × c2hgi ---"
run_mtl texas check2hgi || echo "[warn] TX × c2hgi failed; continuing"

echo "--- TX × hgi ---"
run_mtl texas hgi || echo "[warn] TX × hgi failed; continuing"

echo ""
echo "######## Phase 2 MTL CH18 grid complete $(date) ########"
