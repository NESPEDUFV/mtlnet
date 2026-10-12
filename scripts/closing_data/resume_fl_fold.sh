#!/usr/bin/env bash
# Resilient per-fold FL gate resume (survives the ~1-2h studio restarts).
# Runs each MISSING fold as --only-fold into its own rundir, then copies the produced
# fold CSV into the MASTER rundir's metrics/ so the master accumulates all 5 folds for scoring.
# Re-running after a crash skips folds already present in the master → idempotent resume.
# Usage: resume_fl_fold.sh <arm:bf16|fp32> <master_rundir> <cache_suffix>
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
ARM="$1"; MASTER="$2"; SUF="$3"
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export PYTHONPATH=src
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_${SUF}
if [ "$ARM" = "bf16" ]; then export MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1
elif [ "$ARM" = "fp32" ]; then export MTL_DISABLE_AMP=1
else echo "bad arm: $ARM"; exit 2; fi
# Isolate this arm's rundirs so the concurrent other arm can't race the "newest rundir" pick.
export RESULTS_ROOT="$PWD/results_resume_${ARM}"
mkdir -p "$RESULTS_ROOT"

for F in 1 2 3 4 5; do
  if [ -f "$MASTER/metrics/fold${F}_next_region_val.csv" ] && [ -f "$MASTER/metrics/fold${F}_next_category_val.csv" ]; then
    echo "[resume] fold $F already in master — skip"; continue
  fi
  # --only-fold is 0-INDEXED (train.py:2106): canonical fold F (1-indexed, the CSV name) ↔ --only-fold (F-1),
  # which loads fold{F}.pt and writes fold{F}_*.csv. Off-by-one here = a fold/log_T mismatch leak.
  OF=$((F-1))
  echo "[resume] running canonical fold $F ($ARM, --only-fold $OF) ..."
  python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
      --state florida --seed 0 --epochs 50 --only-fold $OF --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
      --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --compile --tf32 \
      --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/florida --no-checkpoints
  rc=$?
  if [ $rc -ne 0 ]; then echo "[resume] fold $F FAILED rc=$rc — stop"; exit $rc; fi
  # --only-fold runs a SINGLE fold and the storage RE-INDEXES it to fold1 (it's the only fold),
  # even though it used the canonical fold{F} split + fold{F}.pt log_T. So copy the run's fold1
  # CSV and RENAME it to fold{F} in the master. Fail loud if the source is missing.
  NEW=$(ls -dt "$RESULTS_ROOT"/check2hgi_dk_ovl/florida/mtlnet_* | head -1)
  mkdir -p "$MASTER/metrics"
  src_r="$NEW/metrics/fold1_next_region_val.csv"; src_c="$NEW/metrics/fold1_next_category_val.csv"
  if [ ! -f "$src_r" ] || [ ! -f "$src_c" ]; then
    echo "[resume] ERROR: expected fold1 CSVs in $NEW not found — abort"; exit 3; fi
  cp "$src_r" "$MASTER/metrics/fold${F}_next_region_val.csv"
  cp "$src_c" "$MASTER/metrics/fold${F}_next_category_val.csv"
  echo "[resume] fold $F done → copied (fold1→fold${F}) into master $MASTER"
done
echo "[resume] $ARM ALL FOLDS PRESENT in $MASTER"
echo "WALLCLOCK_END=$(date +%s)"
