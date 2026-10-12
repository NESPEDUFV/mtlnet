#!/usr/bin/env bash
# FL MTL B9 multi-seed launcher — closes §0.1 FL cat-side n=5 gap.
#
# Runs MTL B9 at seeds {0,1,7,100} for Florida (5f × 50ep).
# STL cat next_gru seeds {0,1,7,100} already done (Gap 2, gap_fill_wilcoxon.py).
# After completion, extend arch_delta_wilcoxon.py to add FL paired Wilcoxon (n=20).
#
# Estimated runtime: ~20 min per run, 2-way parallel → ~40 min total.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"
PY="${PY:-python}"
cd "${WORKTREE}"
mkdir -p logs

SEEDS=(0 1 7 100)
MAX_JOBS=4

echo "================================================================"
echo "=== FL MTL B9 multi-seed launcher started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"

pids=()

for SEED in "${SEEDS[@]}"; do
    tag="fl_mtl_b9_seed${SEED}"
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state florida --engine check2hgi \
        --model mtlnet_crossattn \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed "${SEED}" \
        --batch-size 2048 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
        --no-checkpoints --no-folds-cache \
        --min-best-epoch 5 \
        --mtl-loss static_weight --category-weight 0.75 \
        --alternating-optimizer-step \
        --scheduler cosine --max-lr 3e-3 \
        --alpha-no-weight-decay \
        >"logs/${tag}.log" 2>&1 &
    pid=$!
    pids+=("$pid:$tag")
    echo "  Launched ${tag} pid=${pid}"

    # Throttle to MAX_JOBS concurrent
    while [ "${#pids[@]}" -ge "${MAX_JOBS}" ]; do
        new_pids=()
        for entry in "${pids[@]}"; do
            p="${entry%%:*}"; t="${entry##*:}"
            if kill -0 "$p" 2>/dev/null; then
                new_pids+=("$entry")
            else
                wait "$p"; rc=$?
                echo "  [done] ${t} exit=${rc} at $(date -u +%H:%M:%SZ)"
                if [ "$rc" -ne 0 ]; then
                    echo "  ERROR: ${t} failed — check logs/${t}.log"
                fi
            fi
        done
        pids=("${new_pids[@]+"${new_pids[@]}"}")
        [ "${#pids[@]}" -ge "${MAX_JOBS}" ] && sleep 30
    done
done

# Wait for remaining
for entry in "${pids[@]+"${pids[@]}"}"; do
    p="${entry%%:*}"; t="${entry##*:}"
    wait "$p"; rc=$?
    echo "  [done] ${t} exit=${rc} at $(date -u +%H:%M:%SZ)"
    [ "$rc" -ne 0 ] && echo "  ERROR: ${t} failed — check logs/${t}.log"
done

echo ""
echo "================================================================"
echo "=== All FL MTL B9 seeds done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"
