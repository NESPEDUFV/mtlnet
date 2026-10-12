#!/usr/bin/env bash
# Generic resilient per-fold champion-G MTL resume (survives ~1-2h studio restarts).
# Runs each MISSING canonical fold as --only-fold into an isolated rundir, copies its
# (re-indexed fold1) CSVs into the MASTER as fold{F}. Idempotent across restarts.
# Usage: resume_mtl_fold.sh <state> <arm:bf16|fp32> <master_rundir> <cache_suffix>
# Compile/memory knobs are INHERITED from the caller's env (so you can set
# MTL_GPU_HEADROOM_GB / MTL_COMPILE_MODE / MTL_COMPILE_DYNAMIC / MTL_DATASET_GPU per run).
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
STATE="$1"; ARM="$2"; MASTER="$3"; SUF="$4"
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1
export MTL_COMPILE_DYNAMIC="${MTL_COMPILE_DYNAMIC:-1}"   # default dynamic; caller may set 0 for reduce-overhead
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export PYTHONPATH=src
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_${SUF}
if [ "$ARM" = "bf16" ]; then export MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1
elif [ "$ARM" = "fp32" ]; then export MTL_DISABLE_AMP=1
else echo "bad arm: $ARM"; exit 2; fi
export RESULTS_ROOT="$PWD/results_resume_${STATE}_${ARM}"
mkdir -p "$RESULTS_ROOT" "$MASTER/metrics"
V14=output/check2hgi_design_k_resln_mae_l0_1/${STATE}

for F in 1 2 3 4 5; do
  if [ -f "$MASTER/metrics/fold${F}_next_region_val.csv" ] && [ -f "$MASTER/metrics/fold${F}_next_category_val.csv" ]; then
    echo "[resume] fold $F already in master — skip"; continue
  fi
  OF=$((F-1))   # --only-fold is 0-INDEXED: canonical fold F ↔ --only-fold (F-1), loads fold{F}.pt
  echo "[resume] $STATE $ARM canonical fold $F (--only-fold $OF) | headroom=${MTL_GPU_HEADROOM_GB:-auto} mode=${MTL_COMPILE_MODE:-default} dyn=${MTL_COMPILE_DYNAMIC} ..."
  python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
      --state "$STATE" --seed 0 --epochs 50 --only-fold $OF --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
      --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --compile --tf32 \
      --per-fold-transition-dir "$V14" --no-checkpoints
  rc=$?
  if [ $rc -ne 0 ]; then echo "[resume] fold $F FAILED rc=$rc — stop"; exit $rc; fi
  NEW=$(ls -dt "$RESULTS_ROOT"/check2hgi_dk_ovl/${STATE}/mtlnet_* | head -1)
  src_r="$NEW/metrics/fold1_next_region_val.csv"; src_c="$NEW/metrics/fold1_next_category_val.csv"
  if [ ! -f "$src_r" ] || [ ! -f "$src_c" ]; then echo "[resume] ERROR: fold1 CSVs missing in $NEW"; exit 3; fi
  cp "$src_r" "$MASTER/metrics/fold${F}_next_region_val.csv"
  cp "$src_c" "$MASTER/metrics/fold${F}_next_category_val.csv"
  echo "[resume] fold $F done → copied (fold1→fold${F}) into master"
done
echo "[resume] $STATE $ARM ALL FOLDS PRESENT in $MASTER"
echo "WALLCLOCK_END=$(date +%s)"
