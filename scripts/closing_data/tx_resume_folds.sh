#!/usr/bin/env bash
# TX MTL resume via --only-fold for folds 3,4,5 (folds 1,2 already in master + pushed).
# Champion-G bf16, dk_ovl, seed 0. log_T is prior-OFF (x0) so its values are inert, but the FILE
# must exist → point --per-fold-transition-dir at output/check2hgi_dk_ovl/texas (where TX's log_T is,
# NOT the design_k dir the generic resume driver uses). Per fold: run --only-fold (F-1) into an
# isolated RESULTS_ROOT, copy its re-indexed fold1 CSVs into the master as fold{F}, score the master,
# update TX_CELL.md, commit+push (race-robust). Fully autonomous; survives session death.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
MASTER=results/check2hgi_dk_ovl/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260624_044542_126420
DEST=docs/results/closing_data/h100/texas_s0_mtl
TXDIR=output/check2hgi_dk_ovl/texas
# NOTE: --compile dropped for the resume — dynamic-shape inductor compile went pathological (>12min
# hang at batch 0, GPU 0%) after the restart's cold cache. Eager is numerically equivalent (compile
# only fuses kernels) and these runs are data-bound, so the speed cost is small. --tf32 kept.
export MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1
export PYTHONPATH=src TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_tx_resume"
export RESULTS_ROOT="$PWD/results_resume_texas_bf16"
mkdir -p "$RESULTS_ROOT" "$DEST" "$HOME/.inductor_cache_tx_resume"

for F in 3 4 5; do
  if [ -f "$MASTER/metrics/fold${F}_next_region_val.csv" ] && [ -f "$MASTER/metrics/fold${F}_next_category_val.csv" ]; then
    echo "[tx-resume] fold $F already in master — skip"; continue
  fi
  OF=$((F-1))   # 0-indexed: canonical fold F <-> --only-fold (F-1), loads fold{F}.pt
  echo "[tx-resume] fold $F (--only-fold $OF) starting $(date -u +%H:%M:%S)Z"
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
  if [ $rc -ne 0 ]; then echo "[tx-resume] fold $F FAILED rc=$rc — STOP (investigate --only-fold)"; exit $rc; fi
  NEW=$(ls -dt "$RESULTS_ROOT"/check2hgi_dk_ovl/texas/mtlnet_* 2>/dev/null | head -1)
  if [ ! -f "$NEW/metrics/fold1_next_region_val.csv" ]; then echo "[tx-resume] ERROR: fold1 CSV missing in $NEW"; exit 3; fi
  cp "$NEW/metrics/fold1_next_region_val.csv"   "$MASTER/metrics/fold${F}_next_region_val.csv"
  cp "$NEW/metrics/fold1_next_category_val.csv" "$MASTER/metrics/fold${F}_next_category_val.csv"
  echo "[tx-resume] fold $F done → copied (fold1→fold${F}) into master"
  # score master + update doc + commit + push
  PYTHONPATH=src python scripts/closing_data/h100_score_matched.py "$MASTER" --seed 0 --tag tx_resume >/tmp/tx_resume_score.txt 2>&1 || true
  if [ -f "$MASTER/h100_matched_score.json" ]; then
    cp "$MASTER/h100_matched_score.json" "$DEST/texas_s0_mtl_partial_score.json"
    python scripts/closing_data/update_tx_cell.py "$MASTER/h100_matched_score.json" docs/studies/closing_data/TX_CELL.md || true
  fi
  cp "$MASTER/metrics/fold${F}_next_region_val.csv" "$MASTER/metrics/fold${F}_next_category_val.csv" "$DEST/" 2>/dev/null || true
  git add docs/studies/closing_data/TX_CELL.md "$DEST" 2>/dev/null || true
  git commit -m "board-h100: TX MTL fold${F} complete (--only-fold resume) — incremental autonomous

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>" >/dev/null 2>&1 || true
  for try in 1 2 3 4; do
    git pull --rebase origin "$BRANCH" >/tmp/tx_resume_pull.txt 2>&1 || true
    if git push origin "$BRANCH" >/tmp/tx_resume_push.txt 2>&1; then break; fi
    echo "[tx-resume] push retry $try"; sleep 10
  done
  echo "[tx-resume] fold $F committed+pushed $(date -u +%H:%M:%S)Z"
done

echo "[tx-resume] ALL FOLDS in master. Launching deferred cat ceiling (solo)."
# signal the deferred cat-ceiling script (it waits for EXIT= in the MTL log) that MTL is complete
echo "EXIT=0 (resume complete, MTL done)" >> logs/tx_s0_ep50.log
nohup bash scripts/closing_data/tx_cat_ceiling_deferred.sh > logs/tx_cat_ceiling_deferred.log 2>&1 &
echo "[tx-resume] done $(date -u +%H:%M:%S)Z"
