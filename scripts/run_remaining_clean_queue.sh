#!/usr/bin/env bash
# Relaunch the 5 runs that died when output/ was wiped:
#   1. STL F37 clean (P1 ablation script)
#   2. F62 two-phase clean
#   3. PLE clean smoke (1f×10ep)
#   4. TGSTAN clean smoke (1f×10ep)
#   5. TGSTAN leaky smoke (1f×10ep)
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    echo "================================================================"
    "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# ---------------------------------------------------------------------------
# 1. STL F37 clean
# ---------------------------------------------------------------------------
run "f50_stl_clean_fl" \
    "$PY" -u scripts/p1_region_head_ablation.py \
        --state florida --heads next_getnext_hard \
        --folds 5 --epochs 50 \
        --batch-size 2048 --seed 42 --input-type region \
        --override-hparams d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
        --tag c4_clean --no-resume \
        --max-lr 1e-3 \
        --region-emb-source check2hgi \
        --mtl-preencoder --preenc-hidden 256 --preenc-layers 2 --preenc-dropout 0.1

# ---------------------------------------------------------------------------
# Common base flags for the rest (MTL training)
# ---------------------------------------------------------------------------
mtl_base=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --cat-head next_gru
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --no-checkpoints --no-folds-cache
)

# ---------------------------------------------------------------------------
# 2. F62 two-phase step-schedule (full 5f×50ep)
# ---------------------------------------------------------------------------
run "f50_f62_clean_fl" \
    "$PY" -u scripts/train.py \
        "${mtl_base[@]}" \
        --reg-head next_getnext_hard \
        --model mtlnet_crossattn \
        --folds 5 --epochs 50 --seed 42 --batch-size 2048 \
        --scheduler cosine --max-lr 3e-3 \
        --min-best-epoch 5 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
        --mtl-loss scheduled_static \
        --mtl-loss-param mode=step \
        --mtl-loss-param cat_weight_start=0.0 \
        --mtl-loss-param cat_weight_end=0.75 \
        --mtl-loss-param warmup_epochs=20 \
        --mtl-loss-param total_epochs=50

# ---------------------------------------------------------------------------
# 3-5. Tier-1 verification smokes (1f × 10ep each)
# ---------------------------------------------------------------------------
smoke_base=(
    "${mtl_base[@]}"
    --mtl-loss static_weight --category-weight 0.75
    --folds 1 --epochs 10 --seed 42 --batch-size 2048
    --scheduler constant
    --min-best-epoch 3
)

# 3. PLE-lite clean — uniform-leak architectural verification
run "f50_p0e_ple_clean_smoke_fl" \
    "$PY" -u scripts/train.py \
        "${smoke_base[@]}" \
        --model mtlnet_ple --reg-head next_getnext_hard \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

# 4. TGSTAN clean (with per-fold log_T)
run "f50_p0d_tgstan_clean_smoke_fl" \
    "$PY" -u scripts/train.py \
        "${smoke_base[@]}" \
        --model mtlnet_crossattn --reg-head next_tgstan \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"

# 5. TGSTAN leaky baseline (NO per-fold-transition-dir)
run "f50_p0d_tgstan_leaky_smoke_fl" \
    "$PY" -u scripts/train.py \
        "${smoke_base[@]}" \
        --model mtlnet_crossattn --reg-head next_tgstan

echo ""
echo "================================================================"
echo "=== Remaining-clean queue COMPLETE $(date) ==="
echo "================================================================"
