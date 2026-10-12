#!/usr/bin/env bash
# F50 B2/F64 + F52 + F65 — three follow-up paper-grade probes at FL clean.
#
# B2/F64 — warmup-decay LambdaLR on reg_head: tests whether late-window α
#          growth can be unlocked without sustained instability (D6's
#          failure mode). Stacks on B9 champion.
#
# F52    — identity-crossattn (P5 probe): zeros cross-attn output but keeps
#          per-task FFN+LN. Decomposes mixing vs FFN depth.
#
# F65    — joint-loader min_size_truncate: stops at shortest loader's end,
#          no cycling. Tests if reg saturation is driven by cycling pattern.
#
# Each at FL 5f×50ep × bs=2048 ≈ 19 min on 4090. Total ~57 min.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

# Anchor recipe = B9 champion (clean): per-fold log_T + alt-SGD + cosine
# + alpha-no-WD + per-head LR + cw=0.75 + min-best-epoch=5.
base_b9=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
    --alternating-optimizer-step
    --alpha-no-weight-decay
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date)"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit ${PIPESTATUS[0]} at $(date)"
}

# B2/F64 — warmup-decay reg_head LR (peak 10× over base reg_lr, ramps ep 0-5,
# plateau through ep 15, decay back through ep 50). Replaces cosine on the
# whole optimizer (cosine + reg_head warmup-decay is incompatible) — but the
# multiplier shape is reg-head-only; cat/reg_encoder/shared stay at base LR.
run "f50_b2_warmup_decay_fl" "${base_b9[@]}" \
    --scheduler reg_head_warmup_decay \
    --reg-head-warmup-decay-peak-mult 10.0 \
    --reg-head-warmup-decay-warmup-epochs 5 \
    --reg-head-warmup-decay-plateau-epochs 15

# F52 — identity-crossattn (replaces cosine with constant for clean test;
# absorption probes are typically run without cosine to avoid confounding).
run "f50_f52_identity_crossattn_fl" "${base_b9[@]}" \
    --scheduler cosine --max-lr 3e-3 \
    --model-param identity_cross_attn=true

# F65 — min_size_truncate joint-loader strategy. Other settings = B9.
run "f50_f65_min_size_truncate_fl" "${base_b9[@]}" \
    --scheduler cosine --max-lr 3e-3 \
    --joint-loader-strategy min_size_truncate

echo "B2/F52/F65 done — extract from results/check2hgi/florida/"
