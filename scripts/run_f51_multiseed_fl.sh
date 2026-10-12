#!/usr/bin/env bash
# F51 — Tier 1 multi-seed validation of the B9 champion vs H3-alt anchor.
#
# Mission (from F50_NORTH_STAR_DEEP_EXPLORATION_PROMPT.md §3 Tier 1):
#   - Run B9 at seed ∈ {0, 1, 7, 100} on FL (seed 42 already exists)
#   - Run H3-alt anchor at the same 4 new seeds
#   - 5 folds × 50 epochs each, paired analysis downstream
#
# 2026-04-30 fix — per-fold log_T MUST match the trainer's --seed. Earlier
# version of this script used the legacy unseeded log_T file built at
# seed=42, which leaked ~80% of val transitions when the trainer ran at any
# other seed (silently inflated absolute reg by ~10 pp; paired Δs survived
# under the uniform-leak property but absolute numbers were wrong). Fix:
# rebuild per-fold log_T at the trainer's seed before each seed's runs.
#
# ETA on 24 GB 4090: ~30 sec/seed log_T build + ~17 min/run × 8 runs ≈ 2.3 h.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

base_fl=(
    --task mtl --task-set check2hgi_next_region
    --state florida --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
)

run() {
    local tag="$1"; shift
    echo "================================================================"
    echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "================================================================"
    "$PY" -u scripts/train.py "$@" 2>&1 | tee "logs/${tag}.log"
    local rc="${PIPESTATUS[0]}"
    echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    return "$rc"
}

ensure_per_fold_logT() {
    local s="$1"
    local need=0
    for f in 1 2 3 4 5; do
        [ -f "${OUTPUT_DIR}/check2hgi/florida/region_transition_log_seed${s}_fold${f}.pt" ] || need=1
    done
    if [ "$need" -eq 1 ]; then
        echo "[per-fold log_T] building for seed=${s}"
        "$PY" -u scripts/compute_region_transition.py \
            --state florida --per-fold --seed "$s" 2>&1 | tee -a "logs/f51_per_fold_logT_build.log"
    else
        echo "[per-fold log_T] seed=${s} already built"
    fi
}

# All 5 seeds — need clean per-fold log_T at each.
SEEDS=(42 0 1 7 100)

# Step 1: ensure per-fold log_T exists for every seed.
for s in "${SEEDS[@]}"; do
    ensure_per_fold_logT "$s"
done

# Step 2: B9 champion arm. seed=42 is included in the rerun for parity
# with the original handover bundle's clean reference; the new run lives
# alongside as an env-B confirmation point.
SEEDS_NEW=(0 1 7 100)  # seed=42 has env-B 5x50ep already pinned (run _0522)
for s in "${SEEDS_NEW[@]}"; do
    run "f51_b9_seed${s}_fl" \
        "${base_fl[@]}" \
        --seed "${s}" \
        --alternating-optimizer-step \
        --scheduler cosine --max-lr 3e-3 \
        --alpha-no-weight-decay
done

# Step 3: H3-alt anchor arm. seed=42 anchor is in the handover bundle
# (run _1921); we still rerun the 4 new seeds in env-B with proper
# per-fold log_T per seed.
for s in "${SEEDS_NEW[@]}"; do
    run "f51_h3alt_seed${s}_fl" \
        "${base_fl[@]}" \
        --seed "${s}" \
        --scheduler constant
done

echo ""
echo "================================================================"
echo "=== F51 multi-seed sweep COMPLETE $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "================================================================"
