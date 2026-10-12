#!/usr/bin/env bash
# B3 + HGI leak-free at AL / AZ / FL, seed=42, 5-fold × 50 epochs.
#
# Discriminator experiment: the CH18-substrate "MTL+HGI catastrophic break
# (reg=29.95 at AL)" was measured 2026-04-27 under BOTH the C4 leak AND the
# B3 recipe. The HGI substrate experiment (2026-05-16, EXPERIMENT_HGI_SUBSTRATE.md)
# showed MTL+HGI ≡ STL+HGI under B9+leak-free — but did not isolate whether
# the disappearance of the catastrophic break was the leak fix or the recipe
# change (B3 → B9). This run isolates: B3 + HGI + leak-free.
#
# Predictions:
#   - If catastrophe was the leak: B3+HGI leak-free reg ≈ STL+HGI ceiling (~62 AL / ~53 AZ / ~73 FL).
#   - If catastrophe was B3 recipe instability: B3+HGI leak-free reg << STL+HGI ceiling.
#   - Mixed: somewhere in between.
#
# B3 recipe (from NORTH_STAR.md §Predecessor — B3):
#   - mtlnet_crossattn, static_weight cat=0.75
#   - cat-head next_gru, reg-head next_getnext_hard
#   - d_model=256, 8 heads
#   - max_lr=0.003 with OneCycleLR (no per-head LR, no cosine, no alt-SGD, no α-no-WD)
#   - batch=2048 (AL/AZ), batch=1024 (FL to avoid MPS OOM)
#   - 50 epochs, seed=42
#
# Wall-clock on MPS (estimated):
#   AL  ~12 min, AZ  ~25 min, FL  ~5 h (batch=1024)  →  total ~6 h.

set -u
WORKTREE="$(pwd)"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-${WORKTREE}/.venv/bin/python}"
LOGDIR="${WORKTREE}/docs/studies/mtl-exploration/logs"
mkdir -p "${LOGDIR}"

run_state() {
    local state="$1"; local bs="$2"
    local tag="b3_hgi_${state}_seed42_5f50ep"
    echo "=== [${tag}] start $(date +%H:%M:%S)"
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "${state}" --engine hgi \
        --model mtlnet_crossattn \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 \
        --batch-size "${bs}" \
        --max-lr 0.003 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${state}" \
        --no-checkpoints --no-folds-cache \
        --min-best-epoch 5 \
        --mtl-loss static_weight --category-weight 0.75 \
        --seed 42 \
        2>&1 | tee "${LOGDIR}/${tag}.log"
    local rc="${PIPESTATUS[0]}"
    echo "[${tag}] exit ${rc} at $(date +%H:%M:%S)"
    return "${rc}"
}

# Order small → large so AL/AZ land quickly for early signal
run_state alabama 2048 || exit $?
run_state arizona 2048 || exit $?
run_state florida 1024 || exit $?
echo "B3_HGI_DONE" > "${LOGDIR}/_b3_hgi_done.flag"
echo "All B3+HGI runs done at $(date +%H:%M:%S)"
