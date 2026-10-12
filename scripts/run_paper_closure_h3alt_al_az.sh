#!/usr/bin/env bash
# Paper-closure gap-fix: AL + AZ MTL H3-alt multi-seed.
#
# AL/AZ have B9 multi-seed from the 2026-05-01 paper-closure but no leak-free
# H3-alt — F49-era H3-alt at AL/AZ used the legacy log_T. This closes the
# B9 vs H3-alt recipe-comparison gap at AL+AZ for symmetric multi-seed
# Wilcoxon vs F51's FL multi-seed result.
#
# 4 seeds × 2 states = 8 runs. Small states (AL ~1109, AZ ~1547) — 4-way
# parallel safe on H100 80GB. ETA ~15-20 min.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
PY="${PY:-python}"
MAX_JOBS="${MAX_JOBS:-4}"
cd "${WORKTREE}"
mkdir -p logs

wait_slot() {
    while [ "$(jobs -rp | wc -l)" -ge "${MAX_JOBS}" ]; do
        wait -n
    done
}
run_bg() {
    local tag="$1"; shift
    wait_slot
    (
        echo "==[${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u scripts/train.py "$@" >"logs/${tag}.log" 2>&1
        echo "[${tag}] exit $? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

# H3-alt = B9 minus --alternating-optimizer-step, --alpha-no-weight-decay,
# scheduler constant instead of cosine. Per `research/F51_MULTI_SEED_FINDINGS.md`.
for STATE in alabama arizona; do
    SDIR="${OUTPUT_DIR}/check2hgi/${STATE}"
    for SEED in 0 1 7 100; do
        run_bg "paper_close_${STATE}_h3alt_seed${SEED}" \
            --task mtl --task-set check2hgi_next_region \
            --state "${STATE}" --engine check2hgi \
            --model mtlnet_crossattn \
            --cat-head next_gru --reg-head next_getnext_hard \
            --reg-head-param d_model=256 --reg-head-param num_heads=8 \
            --reg-head-param "transition_path=${SDIR}/region_transition_log.pt" \
            --task-a-input-type checkin --task-b-input-type region \
            --folds 5 --epochs 50 --seed "${SEED}" \
            --batch-size 2048 \
            --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
            --gradient-accumulation-steps 1 \
            --per-fold-transition-dir "${SDIR}" \
            --no-checkpoints --no-folds-cache \
            --min-best-epoch 5 \
            --mtl-loss static_weight --category-weight 0.75 \
            --scheduler constant --max-lr 3e-3
    done
done

wait
echo "============================================================"
echo "=== AL+AZ H3-alt multi-seed done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "============================================================"
