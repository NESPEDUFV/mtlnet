#!/usr/bin/env bash
# F51 Tier 2 — encoder/backbone capacity smoke.
#
# Mission (from F50_NORTH_STAR_DEEP_EXPLORATION_PROMPT.md §3 Tier 2):
# "Reg-side encoder saturation (D5 finding) is partly a capacity bottleneck.
#  Larger reg encoder might delay saturation."
#
# IMPORTANT: smoke uses 5 folds × 30 ep, NOT 1 fold × 50 ep.
# Reason: --folds 1 triggers n_splits=max(2, 1)=2 in the trainer, which
# uses a different fold split than the 5-fold per-fold log_T we built
# (region_transition_log_seed42_fold{N}.pt is 5-fold-keyed). Running smokes
# at --folds 1 would silently re-introduce a partial C4 leak (the same
# class of bug F51 just fixed). Smokes therefore use 5 folds × 30 ep
# (~10 min/smoke) so the per-fold log_T matches the trainer's fold split.
#
# Promote to 5-fold × 50 ep paper-grade only if a knob shifts reg-best
# epoch past ep 5–6 OR raises reg @≥ep5 by >0.5 pp vs B9 seed=42 ref
# (reg 63.47 ± 0.75 over 5 folds at 50 ep).
#
# Sweep: 7 capacity knobs × ~3 levels each = ~21 smokes × ~10 min ≈ 3.5 h.
# Run when GPU is free.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

# Base B9 recipe at FL, 5 folds × 30 ep, seed=42 (the reference seed).
# 5 folds is required so the per-fold log_T (5-fold-keyed) matches the
# trainer's fold split. 30 ep captures the reg-best window (typically
# ep 5–10 under B9) without paying the full 50-ep cost; cat continues
# improving past 30 but cat is locked at 68.6 across seeds anyway and
# isn't the smoke decision metric.
base_b9_smoke=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 30 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
    --alternating-optimizer-step
    --scheduler cosine --max-lr 3e-3
    --alpha-no-weight-decay
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "================================================================"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# 1. encoder_layer_size sweep — current 256 → {128, 384, 512}
for v in 128 384 512; do
    run "f51_t2_encoder_layer_size_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "encoder_layer_size=${v}"
done

# 2. num_encoder_layers sweep — current 2 → {1, 3, 4}
for v in 1 3 4; do
    run "f51_t2_num_encoder_layers_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "num_encoder_layers=${v}"
done

# 3. encoder_dropout sweep — current 0.1 → {0.05, 0.2, 0.3}
for v in 0.05 0.2 0.3; do
    run "f51_t2_encoder_dropout_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "encoder_dropout=${v}"
done

# 4. shared_layer_size sweep — current 256 → {128, 384, 512}.
# NOTE: must match encoder_layer_size for the cross-attn block dim alignment.
for v in 128 384 512; do
    run "f51_t2_shared_layer_size_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "shared_layer_size=${v}" \
        --model-param "encoder_layer_size=${v}"
done

# 5. num_crossattn_blocks sweep — current 2 → {1, 3, 4}.
# F52 said cross-attn mixing is dead at FL → expect tied with B9.
for v in 1 3 4; do
    run "f51_t2_num_crossattn_blocks_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "num_crossattn_blocks=${v}"
done

# 6. num_crossattn_heads sweep — current 4 → {2, 8, 16}
for v in 2 8 16; do
    run "f51_t2_num_crossattn_heads_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "num_crossattn_heads=${v}"
done

# 7. crossattn_ffn_dim sweep — current 256 → {128, 512, 1024}.
# F52 said FFN+LN is the productive part — does width help?
for v in 128 512 1024; do
    run "f51_t2_crossattn_ffn_dim_${v}" \
        "${base_b9_smoke[@]}" \
        --model-param "crossattn_ffn_dim=${v}"
done

echo ""
echo "================================================================"
echo "=== F51 Tier 2 capacity smoke COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "================================================================"
