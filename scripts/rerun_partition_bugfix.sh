#!/usr/bin/env bash
# Partition-bug re-run launcher (alongside Aligned-MTL / CAGrad / DB-MTL probe)
#
# Reruns the 6 contaminated configs listed in
# docs/issues/check2hgi/MTL_PARAM_PARTITION_BUG.md §Re-run triage,
# plus a bounded optimizer probe on the A7 champion config
# (dselectk + MTLoRA r=8, AL 5f×50ep) testing Aligned-MTL / CAGrad / DB-MTL
# against the PCGrad baseline.
#
# Usage:
#   STATE=alabama WORKTREE=$(pwd) DATA_ROOT=/Volumes/Vitor\'s\ SSD/ingred/data \
#     OUTPUT_DIR=/Volumes/Vitor\'s\ SSD/ingred/output \
#     PY=/Volumes/Vitor\'s\ SSD/ingred/.venv/bin/python \
#     bash scripts/rerun_partition_bugfix.sh > rerun_partition.log 2>&1 &
#
# Budget: ~6 contaminated reruns + 3 new optimizer probes on A7 = 9 runs.
# At ~25-40 min/run on MPS ≈ 4-6h sequential. Parallelise across the two
# machines in scripts/p7_launcher.sh if needed.

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

# --- 6 contaminated reruns (from MTL_PARAM_PARTITION_BUG.md §Re-run triage) ---

# 1. A7 / B11 champion — dselectk + pcgrad + MTLoRA r=8, AL 5f×50ep
run "A7_mtlora_r8_al_pcgrad" alabama "ablation_04_mtlora_r8_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 2. MTLoRA r=16
run "mtlora_r16_al_pcgrad" alabama "ablation_04_mtlora_r16_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=16 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 3. MTLoRA r=32
run "mtlora_r32_al_pcgrad" alabama "ablation_04_mtlora_r32_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=32 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 4. AdaShare on mtlnet baseline, AL 5f×50ep + pcgrad
run "adashare_mtlnet_al_pcgrad" alabama "ablation_05_adashare_mtlnet_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet --model-param use_adashare=true \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 5. AZ replication of A7 (MTLoRA r=8)
run "A7_mtlora_r8_az_pcgrad" arizona "az2_mtlora_r8_fairlr_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 6. R4 fair-LR rerun
run "R4_mtlora_r8_al_fairlr" alabama "rerun_R4_mtlora_r8_fairlr_al_5f50ep_postfix" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss pcgrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# --- Bounded optimizer probe: A7 config × {Aligned-MTL, CAGrad, DB-MTL} ---
# User-requested cross-optimizer comparison. Only on the AL champion config
# (dselectk+MTLoRA r=8) to keep the probe bounded (~2h).

# 7. Aligned-MTL on A7
run "A7_mtlora_r8_al_alignedmtl" alabama "probe_mtlora_r8_al_5f50ep_alignedmtl" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss aligned_mtl --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 8. CAGrad on A7
run "A7_mtlora_r8_al_cagrad" alabama "probe_mtlora_r8_al_5f50ep_cagrad" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss cagrad --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

# 9. DB-MTL on A7 — scalar-backward path, was never affected by the
#    partition bug but included here as an apples-to-apples optimizer
#    comparison point.
run "A7_mtlora_r8_al_dbmtl" alabama "probe_mtlora_r8_al_5f50ep_dbmtl" \
    --task mtl --task-set check2hgi_next_region --engine check2hgi \
    --folds 5 --epochs 50 --seed 42 \
    --task-a-input-type checkin --task-b-input-type region \
    --model mtlnet_dselectk --model-param lora_rank=8 \
    --mtl-loss db_mtl --max-lr 0.003 \
    --gradient-accumulation-steps 1 --no-checkpoints

echo ""
echo "================================================================"
echo "=== partition bugfix rerun complete at $(date)"
echo "=== results in ${DEST}/"
echo "================================================================"
ls -la "${DEST}/"*.json 2>/dev/null || echo "[BUGFIX] no archived JSONs found"
