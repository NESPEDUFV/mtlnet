#!/usr/bin/env bash
# H100 camera-ready gap-fill — closes the last two compute gaps documented in
# docs/studies/check2hgi/H100_CAMERA_READY_GAPS_PROMPT.md:
#
#   Gap 1: CA + TX MTL multi-seed, B9 vs H3-alt   (16 runs)
#   Gap 2: AL + AZ + FL STL cat multi-seed         (12 runs)
#
# Total: 28 runs at 5f×50ep, leak-free per-fold log_T for MTL.
# Hardware: H100 80 GB.
#
# Concurrency budget (empirical):
#   - CA MTL `mtlnet_crossattn` + `next_getnext_hard` peaks ~40 GB/run.
#     Two CA MTL runs concurrently OOM (>80 GB). Run MTL strictly serial.
#   - STL cat `next_gru` is small (~3-5 GB/run on small states); run 4-way.
#   - Cross-phase: 1 MTL (≤40 GB) + up to 4 STL cat (≤20 GB) = ≤60 GB. Safe.
#
# Layout:
#   Background pool A — STL cat next_gru, AL/AZ/FL × seeds (12 runs, ≤4 concurrent)
#   Foreground       — MTL B9/H3-alt, CA/TX × seeds × recipes (16 runs, serial)

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

# --- helpers ---
stl_pool_jobs() {
    # count active STL cat background jobs (children of this shell tagged stl_pool)
    pgrep -P $$ -f "h100_gaps_stl_pool" 2>/dev/null | wc -l
}

# === Step 0: ensure per-fold log_T exists for CA/TX seeds {0,1,7,100} ===
ensure_per_fold_logT() {
    local state="$1"
    local seed="$2"
    local need=0
    for f in 1 2 3 4 5; do
        [ -f "${OUTPUT_DIR}/check2hgi/${state}/region_transition_log_seed${seed}_fold${f}.pt" ] || need=1
    done
    if [ "$need" -eq 1 ]; then
        echo "[per-fold log_T] building state=${state} seed=${seed}"
        "$PY" -u scripts/compute_region_transition.py \
            --state "${state}" --per-fold --seed "${seed}" \
            >>"logs/h100_gaps_per_fold_logT_build.log" 2>&1
    else
        echo "[per-fold log_T] state=${state} seed=${seed} already built"
    fi
}

echo "=== [step 0] building missing per-fold log_T for CA/TX seeds ==="
for STATE in california texas; do
    for SEED in "${SEEDS[@]}"; do
        ensure_per_fold_logT "${STATE}" "${SEED}"
    done
done
echo "=== [step 0] done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# === Background pool A: STL cat next_gru × {AL, AZ, FL} × 4 seeds (4-way) ===
STL_POOL_MAX=4
launch_stl_cat_bg() {
    local state="$1"; local seed="$2"
    local tag="h100_gaps_stl_pool_${state}_seed${seed}"
    while [ "$(stl_pool_jobs)" -ge "${STL_POOL_MAX}" ]; do
        sleep 5
    done
    (
        echo "[${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"logs/h100_camera_ready_gaps.master.log"
        "$PY" -u scripts/train.py \
            --task next --state "${state}" --engine check2hgi \
            --model next_gru \
            --folds 5 --epochs 50 --seed "${seed}" \
            --batch-size 2048 \
            --max-lr 3e-3 \
            --gradient-accumulation-steps 1 \
            --no-checkpoints >"logs/h100_gaps_stl_cat_${state}_seed${seed}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"logs/h100_camera_ready_gaps.master.log"
    ) &
}

echo "=== [Gap 2] launching STL cat next_gru pool (4-way) ==="
for STATE in alabama arizona florida; do
    for SEED in "${SEEDS[@]}"; do
        launch_stl_cat_bg "${STATE}" "${SEED}"
    done
done

# === Foreground: Gap 1 MTL — strictly serial to keep peak under 80 GB ===
run_mtl_serial() {
    local tag="$1"; shift
    echo "================================================================" >>"logs/h100_camera_ready_gaps.master.log"
    echo "[${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"logs/h100_camera_ready_gaps.master.log"
    "$PY" -u scripts/train.py "$@" >"logs/${tag}.log" 2>&1
    local rc=$?
    echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)" >>"logs/h100_camera_ready_gaps.master.log"
}

for STATE in california texas; do
    for SEED in "${SEEDS[@]}"; do
        # B9 = H3-alt + alt-SGD + cosine + alpha-no-WD
        run_mtl_serial "h100_gaps_${STATE}_b9_seed${SEED}" \
            --task mtl --task-set check2hgi_next_region \
            --state "${STATE}" --engine check2hgi \
            --model mtlnet_crossattn \
            --cat-head next_gru --reg-head next_getnext_hard \
            --reg-head-param d_model=256 --reg-head-param num_heads=8 \
            --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
            --task-a-input-type checkin --task-b-input-type region \
            --folds 5 --epochs 50 --seed "${SEED}" \
            --batch-size 2048 \
            --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
            --gradient-accumulation-steps 1 \
            --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
            --no-checkpoints --no-folds-cache \
            --min-best-epoch 5 \
            --mtl-loss static_weight --category-weight 0.75 \
            --alternating-optimizer-step \
            --scheduler cosine --max-lr 3e-3 \
            --alpha-no-weight-decay

        # H3-alt = constant scheduler
        run_mtl_serial "h100_gaps_${STATE}_h3alt_seed${SEED}" \
            --task mtl --task-set check2hgi_next_region \
            --state "${STATE}" --engine check2hgi \
            --model mtlnet_crossattn \
            --cat-head next_gru --reg-head next_getnext_hard \
            --reg-head-param d_model=256 --reg-head-param num_heads=8 \
            --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
            --task-a-input-type checkin --task-b-input-type region \
            --folds 5 --epochs 50 --seed "${SEED}" \
            --batch-size 2048 \
            --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
            --gradient-accumulation-steps 1 \
            --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
            --no-checkpoints --no-folds-cache \
            --min-best-epoch 5 \
            --mtl-loss static_weight --category-weight 0.75 \
            --scheduler constant --max-lr 3e-3
    done
done

echo "=== [Gap 1] CA/TX MTL serial pass done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"

# Wait for any STL cat stragglers
wait
echo "================================================================"
echo "=== All H100 camera-ready gap runs done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== Logs in logs/h100_gaps_*.log; results under results/check2hgi/<state>/"
echo "================================================================"
