#!/usr/bin/env bash
# NO-GIT TX MTL resume (folds 3,4,5). Decoupled from git because the environment's git
# commit is hanging (degraded FS/harness contention post-restart). Writes fold results to the
# master rundir + DEST + updates TX_CELL.md ON DISK (durable, filesystem persists). A separate
# git sync pushes them when the infra recovers. Eager (no --compile) + MTL_RAM_HEADROOM_GB=0.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
MASTER=results/check2hgi_dk_ovl/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260624_044542_126420
DEST=docs/results/closing_data/h100/texas_s0_mtl
TXDIR=output/check2hgi_dk_ovl/texas
export MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1
export MTL_RAM_HEADROOM_GB=0
export PYTHONPATH=src TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_tx_resume"
export RESULTS_ROOT="$PWD/results_resume_texas_bf16"
mkdir -p "$RESULTS_ROOT" "$DEST" "$HOME/.inductor_cache_tx_resume"

for F in 3 4 5; do
  if [ -f "$MASTER/metrics/fold${F}_next_region_val.csv" ] && [ -f "$MASTER/metrics/fold${F}_next_category_val.csv" ]; then
    echo "[tx-nogit] fold $F already in master — skip"; continue
  fi
  OF=$((F-1))
  echo "[tx-nogit] fold $F (--only-fold $OF) starting $(date -u +%H:%M:%S)Z"
  python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
      --state texas --seed 0 --epochs 50 --only-fold $OF --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --tf32 \
      --per-fold-transition-dir "$TXDIR" --no-checkpoints
  rc=$?
  if [ $rc -ne 0 ]; then echo "[tx-nogit] fold $F FAILED rc=$rc — STOP"; exit $rc; fi
  NEW=$(ls -dt "$RESULTS_ROOT"/check2hgi_dk_ovl/texas/mtlnet_* 2>/dev/null | head -1)
  if [ ! -f "$NEW/metrics/fold1_next_region_val.csv" ]; then echo "[tx-nogit] ERROR: fold1 CSV missing in $NEW"; exit 3; fi
  cp "$NEW/metrics/fold1_next_region_val.csv"   "$MASTER/metrics/fold${F}_next_region_val.csv"
  cp "$NEW/metrics/fold1_next_category_val.csv" "$MASTER/metrics/fold${F}_next_category_val.csv"
  echo "[tx-nogit] fold $F done → copied (fold1→fold${F}) into master $(date -u +%H:%M:%S)Z"
  # score + update doc ON DISK (no git)
  PYTHONPATH=src python scripts/closing_data/h100_score_matched.py "$MASTER" --seed 0 --tag tx_resume >/tmp/tx_nogit_score.txt 2>&1 || true
  if [ -f "$MASTER/h100_matched_score.json" ]; then
    cp "$MASTER/h100_matched_score.json" "$DEST/texas_s0_mtl_partial_score.json"
    python scripts/closing_data/update_tx_cell.py "$MASTER/h100_matched_score.json" docs/studies/closing_data/TX_CELL.md || true
  fi
  cp "$MASTER/metrics/fold${F}_next_region_val.csv" "$MASTER/metrics/fold${F}_next_category_val.csv" "$DEST/" 2>/dev/null || true
  grep -E "cat macro|reg FULL" /tmp/tx_nogit_score.txt 2>/dev/null
done
echo "[tx-nogit] ALL FOLDS in master ($(date -u +%H:%M:%S)Z). Cat ceiling next (solo)."
echo "EXIT=0 (resume complete, MTL done)" >> logs/tx_s0_ep50.log
MTL_RAM_HEADROOM_GB=0 nohup bash scripts/closing_data/tx_cat_ceiling_deferred.sh > logs/tx_cat_ceiling_deferred.log 2>&1 &
echo "[tx-nogit] done $(date -u +%H:%M:%S)Z"
