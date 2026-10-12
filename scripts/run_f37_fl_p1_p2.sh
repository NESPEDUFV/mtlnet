#!/usr/bin/env bash
# F37 FL — STL next_gru cat (P1) + STL next_getnext_hard reg (P2) on Florida.
#
# Note: AL and AZ STL next_gru cat 5f are already done in Phase-1
# (results/phase1_perfold/{AL,AZ}_check2hgi_cat_gru_5f50ep.json).
# F21c AL and AZ for reg also done (results/B3_baselines/stl_getnext_hard_{al,az}_5f50ep.json).
# This launcher fills in the FL gap for both P1 (cat) and P2 (reg).
#
# P1 (FL cat) closes the cat-side matched-head STL story at FL.
# P2 (FL reg) closes F49 Layer 3 — absolute architectural Δ vs STL ceiling at FL.
#
# Cost on M4 Pro MPS (estimates from prior runs):
#   - FL cat 5f × 50ep: ~3-4h (cat-only is cheap)
#   - FL reg 5f × 50ep: ~5-6h (4702 regions; getnext-hard graph prior is heavier)
#   - Total: ~8-10h sequential.
#
# To run in background:
#   WORKTREE=$(pwd) DATA_ROOT=/Volumes/Vitor\'s\ SSD/ingred/data \
#     OUTPUT_DIR=/Volumes/Vitor\'s\ SSD/ingred/output \
#     bash scripts/run_f37_fl_p1_p2.sh > /tmp/f37_fl.log 2>&1 &
#
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

DEST_P1="${WORKTREE}/docs/results/P1_5b_post_f27"
DEST_P2="${WORKTREE}/docs/results/B3_baselines"
mkdir -p "${DEST_P1}" "${DEST_P2}"

START_TIME=$(date +%s)
echo "================================================================"
echo "=== F37 FL P1+P2 launcher — $(date)"
echo "=== WORKTREE=${WORKTREE}"
echo "=== DATA_ROOT=${DATA_ROOT}"
echo "=== OUTPUT_DIR=${OUTPUT_DIR}"
echo "================================================================"

# ────────────────────────────────────────────────────────────────────────────
# P1 — FL STL next_gru cat 5f
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== [P1] FL STL next_gru cat 5f start $(date)"
"$PY" -u scripts/train.py \
    --task next \
    --state florida \
    --engine check2hgi \
    --model next_gru \
    --folds 5 --epochs 50 --seed 42 \
    --batch-size 2048 \
    --max-lr 3e-3 \
    --gradient-accumulation-steps 1 \
    --no-checkpoints
P1_RC=$?
echo "[P1] exit ${P1_RC} at $(date)"

if [ ${P1_RC} -ne 0 ]; then
    echo "[P1] FAILED — retrying with batch-size 1024 (FL 4702-region OOM mitigation)"
    "$PY" -u scripts/train.py \
        --task next \
        --state florida \
        --engine check2hgi \
        --model next_gru \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size 1024 \
        --max-lr 3e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints
    P1_RC=$?
    echo "[P1 retry] exit ${P1_RC} at $(date)"
fi

# ────────────────────────────────────────────────────────────────────────────
# P2 — FL STL next_getnext_hard reg 5f
# ────────────────────────────────────────────────────────────────────────────
echo ""
echo "=== [P2] FL STL next_getnext_hard reg 5f start $(date)"
"$PY" -u scripts/p1_region_head_ablation.py \
    --state florida --heads next_getnext_hard \
    --folds 5 --epochs 50 --seed 42 --input-type region \
    --override-hparams \
        d_model=256 num_heads=8 \
        "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --tag stl_gethard
P2_RC=$?
echo "[P2] exit ${P2_RC} at $(date)"

# Archive P2 if successful
if [ ${P2_RC} -eq 0 ]; then
    P2_SRC="${WORKTREE}/docs/results/P1/region_head_florida_region_5f_50ep_stl_gethard.json"
    if [ -f "${P2_SRC}" ]; then
        cp "${P2_SRC}" "${DEST_P2}/stl_getnext_hard_fl_5f50ep.json"
        echo "[P2] archived → ${DEST_P2}/stl_getnext_hard_fl_5f50ep.json"
    else
        echo "[P2] WARNING: expected output at ${P2_SRC} not found"
    fi
fi

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
echo ""
echo "================================================================"
echo "=== F37 FL P1+P2 complete at $(date)"
echo "=== Elapsed: ${ELAPSED}s ($((ELAPSED / 3600))h $(((ELAPSED % 3600) / 60))m)"
echo "=== P1 exit: ${P1_RC}  P2 exit: ${P2_RC}"
echo "================================================================"
echo ""
echo "P1 result JSON: results/check2hgi/florida/next_lr1.0e-04_bs*_ep50_*/summary/full_summary.json"
echo "P2 result JSON: ${DEST_P2}/stl_getnext_hard_fl_5f50ep.json"
echo ""
echo "Next: re-run scripts/analysis/p4_p5_wilcoxon_offline.py with FL F21c per-fold"
echo "      to close F49 Layer 3 (absolute architectural Δ vs STL on FL)."
