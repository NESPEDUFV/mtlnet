#!/usr/bin/env bash
# TX MTL multi-seed 2-way parallel launcher.
# Picks up after CA finishes in run_h100_camera_ready_gaps.sh.
#
# TX has 6553 regions → peak ~29 GB/run → two concurrent runs ≈ 57 GB (fits H100 80 GB).
# Runs B9 and H3-alt for the same seed in parallel, then moves to next seed.
#
# 8 runs total: 4 seeds × 2 recipes at 5f × 50ep.
# Expected wall time: ~4 × ~30 min = ~2 h  (vs ~8 × ~30 min = ~4 h serial).

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

echo "================================================================"
echo "=== TX MTL 2-way parallel launcher started $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== GPU before launch:"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"

# Ensure per-fold log_T exists for TX (should already be built by the CA script, but guard)
for SEED in "${SEEDS[@]}"; do
    need=0
    for f in 1 2 3 4 5; do
        [ -f "${OUTPUT_DIR}/check2hgi/texas/region_transition_log_seed${SEED}_fold${f}.pt" ] || need=1
    done
    if [ "$need" -eq 1 ]; then
        echo "[per-fold log_T] building TX seed=${SEED}"
        "$PY" -u scripts/compute_region_transition.py \
            --state texas --per-fold --seed "${SEED}" \
            >>"logs/h100_tx_2way_logT_build.log" 2>&1
    else
        echo "[per-fold log_T] TX seed=${SEED} already built"
    fi
done

run_tx_pair() {
    local SEED="$1"
    local tag_b9="h100_gaps_texas_b9_seed${SEED}"
    local tag_h3="h100_gaps_texas_h3alt_seed${SEED}"

    echo "================================================================" | tee -a logs/h100_tx_2way.master.log
    echo "=== [TX seed=${SEED}] launching B9 + H3-alt in parallel at $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a logs/h100_tx_2way.master.log

    # B9
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state texas --engine check2hgi \
        --model mtlnet_crossattn \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/texas/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed "${SEED}" \
        --batch-size 2048 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/texas" \
        --no-checkpoints --no-folds-cache \
        --min-best-epoch 5 \
        --mtl-loss static_weight --category-weight 0.75 \
        --alternating-optimizer-step \
        --scheduler cosine --max-lr 3e-3 \
        --alpha-no-weight-decay \
        >"logs/${tag_b9}.log" 2>&1 &
    local pid_b9=$!

    # H3-alt
    "$PY" -u scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state texas --engine check2hgi \
        --model mtlnet_crossattn \
        --cat-head next_gru --reg-head next_getnext_hard \
        --reg-head-param d_model=256 --reg-head-param num_heads=8 \
        --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/texas/region_transition_log.pt" \
        --task-a-input-type checkin --task-b-input-type region \
        --folds 5 --epochs 50 --seed "${SEED}" \
        --batch-size 2048 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --gradient-accumulation-steps 1 \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/texas" \
        --no-checkpoints --no-folds-cache \
        --min-best-epoch 5 \
        --mtl-loss static_weight --category-weight 0.75 \
        --scheduler constant --max-lr 3e-3 \
        >"logs/${tag_h3}.log" 2>&1 &
    local pid_h3=$!

    echo "[TX seed=${SEED}] B9 pid=${pid_b9}  H3-alt pid=${pid_h3}" | tee -a logs/h100_tx_2way.master.log

    # Wait for both to finish before next seed pair
    wait $pid_b9; local rc_b9=$?
    wait $pid_h3; local rc_h3=$?

    echo "[TX seed=${SEED}] B9 exit=${rc_b9}  H3-alt exit=${rc_h3} at $(date -u +%Y-%m-%dT%H:%M:%SZ)" | tee -a logs/h100_tx_2way.master.log

    # Hard stop if either failed
    if [ "$rc_b9" -ne 0 ] || [ "$rc_h3" -ne 0 ]; then
        echo "ERROR: TX seed=${SEED} had a failure — stopping. Check logs/${tag_b9}.log and logs/${tag_h3}.log" | tee -a logs/h100_tx_2way.master.log
        nvidia-smi --query-gpu=memory.used,memory.free --format=csv
        exit 1
    fi
}

for SEED in "${SEEDS[@]}"; do
    run_tx_pair "${SEED}"
done

echo "================================================================"
echo "=== All TX MTL 2-way runs done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== Logs: logs/h100_gaps_texas_*.log"
echo "=== Results: results/check2hgi/texas/"
nvidia-smi --query-gpu=memory.used,memory.free --format=csv
echo "================================================================"
