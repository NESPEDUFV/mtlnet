#!/usr/bin/env bash
# CA + TX STL ceiling multi-seed launcher for §0.1 architectural-Δ upgrade.
#
# Runs:
#   STL cat next_gru      — CA + TX, seeds {0,1,7,100}  (8 runs, 4-way pool)
#   STL reg next_getnext_hard — CA + TX, seeds {0,1,7,100} (8 runs, 2-way per seed pair)
#
# MTL B9 at CA/TX seeds {0,1,7,100} already done (recipe-selection runs).
# Per-fold log_T for CA/TX seeds {0,1,7,100} already built.
#
# After all runs complete, update scripts/analysis/arch_delta_wilcoxon.py
# and run it to get §0.1 CA/TX Wilcoxon results.

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
STATES=(california texas)

echo "================================================================"
echo "=== CA+TX STL arch-Δ ceiling launcher started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== GPU before launch:"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"

# ── Phase 1: STL cat next_gru (8 runs, pool ≤4 concurrent) ─────────────────
echo ""
echo "--- Phase 1: STL cat next_gru (CA+TX, seeds {0,1,7,100}) ---"

MAX_JOBS_CAT=4
pids_cat=()

for SEED in "${SEEDS[@]}"; do
    for STATE in "${STATES[@]}"; do
        tag="arch_delta_${STATE}_stl_cat_seed${SEED}"
        "$PY" -u scripts/train.py \
            --task next --state "${STATE}" --engine check2hgi \
            --model next_gru \
            --folds 5 --epochs 50 --seed "${SEED}" \
            --batch-size 2048 \
            --max-lr 3e-3 \
            --gradient-accumulation-steps 1 \
            --no-checkpoints \
            >"logs/${tag}.log" 2>&1 &
        pid=$!
        pids_cat+=("$pid:$tag")
        echo "  Launched ${tag} pid=${pid}"

        # Throttle to MAX_JOBS_CAT concurrent
        while [ "${#pids_cat[@]}" -ge "${MAX_JOBS_CAT}" ]; do
            new_pids=()
            for entry in "${pids_cat[@]}"; do
                p="${entry%%:*}"; t="${entry##*:}"
                if kill -0 "$p" 2>/dev/null; then
                    new_pids+=("$entry")
                else
                    wait "$p"; rc=$?
                    echo "  [cat] ${t} exit=${rc} at $(date -u +%H:%M:%SZ)"
                fi
            done
            pids_cat=("${new_pids[@]+"${new_pids[@]}"}")
            [ "${#pids_cat[@]}" -ge "${MAX_JOBS_CAT}" ] && sleep 30
        done
    done
done

# Wait for remaining cat jobs
for entry in "${pids_cat[@]+"${pids_cat[@]}"}"; do
    p="${entry%%:*}"; t="${entry##*:}"
    wait "$p"; rc=$?
    echo "  [cat] ${t} exit=${rc} at $(date -u +%H:%M:%SZ)"
done

echo ""
echo "--- Phase 1 complete: STL cat at $(date -u +%Y-%m-%dT%H:%M:%SZ) ---"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv

# ── Phase 2: STL reg next_getnext_hard (2-way: CA+TX per seed) ─────────────
echo ""
echo "--- Phase 2: STL reg next_getnext_hard (CA+TX, seeds {0,1,7,100}) ---"

for SEED in "${SEEDS[@]}"; do
    echo ""
    echo "  Seed=${SEED}: launching CA + TX in parallel"
    pids_reg=()
    for STATE in "${STATES[@]}"; do
        tag="arch_delta_${STATE}_stl_reg_seed${SEED}"
        STATE_UPPER="${OUTPUT_DIR}/check2hgi/${STATE}"
        "$PY" -u scripts/p1_region_head_ablation.py \
            --state "${STATE}" \
            --heads next_getnext_hard \
            --folds 5 --epochs 50 --seed "${SEED}" \
            --input-type region \
            --region-emb-source check2hgi \
            --override-hparams \
                d_model=256 num_heads=8 \
                "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
            --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
            --tag "paper_close_${STATE}_stl_reg_seed${SEED}" \
            --no-resume \
            --max-lr 1e-3 \
            >"logs/${tag}.log" 2>&1 &
        pid=$!
        pids_reg+=("$pid:$tag")
        echo "    Launched ${tag} pid=${pid}"
    done

    nvidia-smi --query-gpu=memory.used,memory.free,utilization.gpu --format=csv

    for entry in "${pids_reg[@]}"; do
        p="${entry%%:*}"; t="${entry##*:}"
        wait "$p"; rc=$?
        echo "  [reg] ${t} exit=${rc} at $(date -u +%H:%M:%SZ)"
        if [ "$rc" -ne 0 ]; then
            echo "  ERROR: ${t} failed — stopping. Check logs/${t}.log"
            exit 1
        fi
    done
done

echo ""
echo "================================================================"
echo "=== All CA+TX STL runs done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== STL cat logs: logs/arch_delta_*_stl_cat_*.log"
echo "=== STL reg logs: logs/arch_delta_*_stl_reg_*.log"
echo "=== STL reg JSONs: docs/results/P1/region_head_*paper_close*stl_reg_seed*.json"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"
