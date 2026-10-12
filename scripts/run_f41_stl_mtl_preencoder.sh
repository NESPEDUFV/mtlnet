#!/usr/bin/env bash
# F41 — Exp D: STL next_getnext_hard with MTL pre-encoder.
#
# Goal: isolate Fator 3 (upstream architecture interference) from the
# CH18 STL-vs-MTL reg gap. The pre-encoder (Linear+ReLU+LN+Dropout stack,
# 64 → 256) mirrors MTLnet's next_encoder without cross-attn or shared-
# backbone. If the gap closes meaningfully here, the bottleneck is the
# embed_dim projection + MLP regularization. If not, the cross-attn
# blocks themselves (still absent in this variant) are the culprit and a
# follow-up D-2 is needed.
#
# Configs:
#   D-base  : pure STL (for reproducing F21c; optional sanity)
#   D-preenc: STL + pre-encoder (new)
#
# Compare to F21c (STL baseline): AL 68.37 Acc@10 / AZ 66.74.
# Compare to B3 (MTL post-F27): AL 59.60 / AZ 53.82.
#
# If D-preenc ≈ F21c → pre-encoder alone is not load-bearing.
# If D-preenc ≈ B3   → upstream MLP 64→256 IS load-bearing; cross-attn not needed.
# If D-preenc in between → partial contribution; need cross-attn Exp D-2.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/F41_preencoder"
mkdir -p "${DEST}"

archive_latest() {
    local state="$1" dest_name="$2"
    local src="${WORKTREE}/docs/results/P1/region_head_${state}_region_5f_50ep_${dest_name}.json"
    if [ -f "${src}" ]; then
        cp "${src}" "${DEST}/${dest_name}.json"
        echo "[F41] saved → ${DEST}/${dest_name}.json"
    else
        echo "[F41] WARNING: expected output at ${src} not found"
    fi
}

run() {
    local tag="$1" state="$2" dest_name="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state})"
    echo "================================================================"
    "$PY" -u scripts/p1_region_head_ablation.py \
        --state "${state}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --input-type region \
        --mtl-preencoder \
        --preenc-hidden 256 --preenc-layers 2 --preenc-dropout 0.1 \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --tag "${dest_name}"
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && archive_latest "${state}" "${dest_name}"
}

# AL first (cheap, ~30 min)
run "f41_al" alabama "stl_gethard_preenc"

# AZ next (~1.5 h)
run "f41_az" arizona "stl_gethard_preenc"

echo ""
echo "================================================================"
echo "=== F41 AL + AZ complete at $(date)"
echo "=== Compare reg Acc@10 to F21c (AL 68.37 / AZ 66.74) and B3 (AL 59.60 / AZ 53.82)"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
