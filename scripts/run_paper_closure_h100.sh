#!/usr/bin/env bash
# Paper-closure run matrix for the check2hgi MTL study, on H100 80GB.
#
# Goal: cross-state P3 (CA, TX) + STL ceilings + FL STL reg multi-seed
# extension. 12 paper-grade runs total at 5f×50ep, leak-free per-fold log_T.
#
# Layout (2-way parallelism via simple job queue):
#   Group 1 — CA P3:           CA-B9 + CA-H3-alt        (~25-35 min/run)
#   Group 2 — TX P3:           TX-B9 + TX-H3-alt        (~20-30 min/run)
#   Group 3 — CA + TX STL cat: matched-head next_gru    (~10-15 min/run)
#   Group 4 — CA + TX STL reg: next_getnext_hard        (~15-20 min/run)
#   Group 5 — FL STL reg multi-seed: seeds {0,1,7,100}  (~8-12 min/run)
#
# Recipes:
#   B9      = H3-alt + alt-SGD + cosine + alpha-no-WD
#   H3-alt  = per-head LR (1e-3/3e-3/1e-3) + scheduler constant
#   STL cat = scripts/train.py --task next --model next_gru
#   STL reg = scripts/p1_region_head_ablation.py + per-fold-transition-dir

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"
PY="${PY:-python}"
MAX_JOBS="${MAX_JOBS:-2}"
cd "${WORKTREE}"
mkdir -p logs

# --- job queue limiter ---
wait_slot() {
    while [ "$(jobs -rp | wc -l)" -ge "${MAX_JOBS}" ]; do
        wait -n
    done
}

run_bg() {
    local tag="$1"; shift
    wait_slot
    (
        echo "================================================================"
        echo "=== [${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
        "$PY" -u "$@" >"logs/${tag}.log" 2>&1
        rc=$?
        echo "[${tag}] exit ${rc} at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    ) &
}

# Common MTL flags (B9 / H3-alt share these — recipe-specific bits added per call).
mtl_common_ca=(
    --task mtl --task-set check2hgi_next_region
    --state california --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/california/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/california"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
)
mtl_common_tx=(
    --task mtl --task-set check2hgi_next_region
    --state texas --engine check2hgi
    --model mtlnet_crossattn
    --cat-head next_gru --reg-head next_getnext_hard
    --reg-head-param d_model=256 --reg-head-param num_heads=8
    --reg-head-param "transition_path=${OUTPUT_DIR}/check2hgi/texas/region_transition_log.pt"
    --task-a-input-type checkin --task-b-input-type region
    --folds 5 --epochs 50 --seed 42
    --batch-size 2048
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    --gradient-accumulation-steps 1
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/texas"
    --no-checkpoints --no-folds-cache
    --min-best-epoch 5
    --mtl-loss static_weight --category-weight 0.75
)

# === Group 1 + 2: CA + TX MTL (B9 + H3-alt) ===
run_bg "paper_close_ca_b9" scripts/train.py \
    "${mtl_common_ca[@]}" \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

run_bg "paper_close_ca_h3alt" scripts/train.py \
    "${mtl_common_ca[@]}" \
    --scheduler constant --max-lr 3e-3

run_bg "paper_close_tx_b9" scripts/train.py \
    "${mtl_common_tx[@]}" \
    --alternating-optimizer-step \
    --scheduler cosine --max-lr 3e-3 \
    --alpha-no-weight-decay

run_bg "paper_close_tx_h3alt" scripts/train.py \
    "${mtl_common_tx[@]}" \
    --scheduler constant --max-lr 3e-3

# === Group 3: STL cat (next_gru) at CA + TX ===
for STATE in california texas; do
    run_bg "paper_close_${STATE}_stl_cat" scripts/train.py \
        --task next --state "${STATE}" --engine check2hgi \
        --model next_gru \
        --folds 5 --epochs 50 --seed 42 \
        --batch-size 2048 \
        --max-lr 3e-3 \
        --gradient-accumulation-steps 1 \
        --no-checkpoints
done

# === Group 4: STL reg (next_getnext_hard) at CA + TX, leak-free ===
for STATE in california texas; do
    run_bg "paper_close_${STATE}_stl_reg" scripts/p1_region_head_ablation.py \
        --state "${STATE}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --input-type region \
        --region-emb-source check2hgi \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
        --tag paper_close_stl_reg \
        --no-resume \
        --max-lr 1e-3
done

# === Group 5: FL STL reg multi-seed extension (seeds {0, 1, 7, 100}) ===
for SEED in 0 1 7 100; do
    run_bg "paper_close_fl_stl_reg_seed${SEED}" scripts/p1_region_head_ablation.py \
        --state florida --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed "${SEED}" --input-type region \
        --region-emb-source check2hgi \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
        --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
        --tag "paper_close_fl_stl_reg_seed${SEED}" \
        --no-resume \
        --max-lr 1e-3
done

# Drain heavy phase before bumping parallelism for small states.
wait
echo "=== Heavy phase (CA/TX/FL) done at $(date -u +%Y-%m-%dT%H:%M:%SZ); switching MAX_JOBS to 4 for AL+AZ"

# Small states (AL ~1109 regions, AZ ~1547 regions) — bump to 4-way parallel.
MAX_JOBS="${MAX_JOBS_SMALL:-4}"

# === Group 6 (P0): AL + AZ STL reg multi-seed (4 extra seeds × 2 states = 8 runs) ===
for STATE in alabama arizona; do
    for SEED in 0 1 7 100; do
        run_bg "paper_close_${STATE}_stl_reg_seed${SEED}" scripts/p1_region_head_ablation.py \
            --state "${STATE}" --heads next_getnext_hard \
            --folds 5 --epochs 50 --seed "${SEED}" --input-type region \
            --region-emb-source check2hgi \
            --override-hparams \
                d_model=256 num_heads=8 \
                "transition_path=${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log.pt" \
            --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
            --tag "paper_close_${STATE}_stl_reg_seed${SEED}" \
            --no-resume \
            --max-lr 1e-3
    done
done

# === Group 7 (P1): AL + AZ MTL B9 multi-seed (4 extra seeds × 2 states = 8 runs) ===
for STATE in alabama arizona; do
    for SEED in 0 1 7 100; do
        run_bg "paper_close_${STATE}_b9_seed${SEED}" scripts/train.py \
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
    done
done

wait
echo "================================================================"
echo "=== All paper-closure runs done at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "=== Logs in logs/paper_close_*.log; results under results/check2hgi/<state>/"
echo "================================================================"
