#!/usr/bin/env bash
# Resume launcher for rerun_partition_bugfix.sh — runs the 4 remaining
# configs after (a) our local crash on 2026-04-22 at 12:55 (SIGBUS after
# completing run 1 of 9) and (b) the M2 Pro's parallel probe_a7_optimizers.sh
# which covered runs 7-9 (Aligned-MTL / CAGrad / DB-MTL on the A7 config).
#
# Skipped:
#   - Run 1 (A7 MTLoRA r=8 AL pcgrad)   — done locally, see P5_bugfix/ablation_04_*.json
#   - Run 6 (R4 MTLoRA r=8 AL fair-LR)  — command is identical to run 1, duplicate
#   - Runs 7-9 (A7 × Aligned/CAGrad/DB) — done on M2 Pro, see P5_bugfix/a7_*.json
#
# What this resume script does:
#   - Run 2: MTLoRA r=16 AL pcgrad  (crashed at fold 5 epoch 7 in prior pass)
#   - Run 3: MTLoRA r=32 AL pcgrad
#   - Run 4: AdaShare mtlnet AL pcgrad
#   - Run 5: A7 MTLoRA r=8 AZ pcgrad (cross-state replication)
#
# Budget: ~35-40 min/run × 4 = 2h20m–2h40m on MPS.
#
# Launched via `caffeinate -s` to prevent system sleep (which triggered
# SIGBUS on the prior attempt).
#
# Usage:
#   WORKTREE=$(pwd) DATA_ROOT=/tmp/check2hgi_data OUTPUT_DIR=/tmp/check2hgi_data \
#     PY=/Volumes/Vitor\'s\ SSD/ingred/.venv/bin/python \
#     caffeinate -s bash scripts/rerun_partition_bugfix_resume.sh \
#     > /tmp/stan_logs/rerun_partition_resume.log 2>&1 &

set -u

WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT to the path holding checkins + miscellaneous}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR to the path holding output/check2hgi/*/input/next_region.parquet}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"

DEST="${WORKTREE}/docs/results/P5_bugfix"
mkdir -p "${DEST}"

archive_summary() {
    local state="$1" dest_name="$2"
    local latest
    latest=$(ls -dt "${WORKTREE}/results/check2hgi/${state}/"*_lr*_bs*_ep50_* 2>/dev/null | head -1)
    if [ -n "${latest}" ] && [ -f "${latest}/summary/full_summary.json" ]; then
        cp "${latest}/summary/full_summary.json" "${DEST}/${dest_name}.json"
        echo "[BUGFIX] saved → ${DEST}/${dest_name}.json"
    else
        echo "[BUGFIX] WARNING: no summary JSON found for ${dest_name}"
    fi
}

run() {
    local tag="$1" state="$2" dest_name="$3"; shift 3
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state})"
    echo "================================================================"
    "$PY" -u scripts/train.py --state "${state}" "$@"
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    if [ $rc -eq 0 ]; then
        archive_summary "${state}" "${dest_name}"
    fi
}

# ---- Run 2: MTLoRA r=16 AL pcgrad (crashed prior pass) ----
run "mtlora_r16_al_pcgrad" alabama "ablation_04_mtlora_r16_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=16 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ---- Run 3: MTLoRA r=32 AL pcgrad ----
run "mtlora_r32_al_pcgrad" alabama "ablation_04_mtlora_r32_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=32 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ---- Run 4: AdaShare mtlnet AL pcgrad ----
run "adashare_mtlnet_al_pcgrad" alabama "ablation_05_adashare_mtlnet_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet --model-param use_adashare=true \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# ---- Run 5: A7 MTLoRA r=8 AZ pcgrad (cross-state replication) ----
run "A7_mtlora_r8_az_pcgrad" arizona "az2_mtlora_r8_fairlr_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

echo ""
echo "================================================================"
echo "=== resume complete at $(date)"
echo "=== results in ${DEST}/"
echo "================================================================"
ls -la "${DEST}/"*.json 2>/dev/null || echo "[BUGFIX] no archived JSONs found"
