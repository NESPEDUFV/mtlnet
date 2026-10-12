#!/bin/bash
# X3 (HANDOFF_AUDIT) — β trajectory logged to decay 0.108→≈0 by ~ep25 (AdamW wd=0.05).
# Run G at FL seed0 with β peeled into the zero-WD group (MTL_BETA_NO_WD=1) to test whether
# WD (not the model's own gradient) was driving β→0 and suppressing the shared→reg pathway.
# Compare reg/cat vs A_fl_kdoff (the X-series KD-off baseline). Gate: ≥0.3pp either head.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida
LOGDIR=/tmp/x3beta; mkdir -p "$LOGDIR"; MAN=scripts/mtl_improvement/x3_beta_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=16
ts(){ date '+%Y-%m-%d %H:%M:%S'; }
echo "[$(ts)] X3 start FL seed0 G + MTL_BETA_NO_WD=1"
MTL_BETA_NO_WD=1 $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
    --engine "$V14" --state "$ST" --seed 0 --epochs 50 --folds 5 --batch-size 2048 \
    --model mtlnet_crossattn_dualtower \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$LOGDIR/run.log" 2>&1 &
pid=$!; wait "$pid"
if [ $? -eq 0 ]; then
  rd=$(ls -d results/$V14/$ST/mtlnet_*ep50_*_${pid} 2>/dev/null | head -1)
  [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
  printf 'X3_fl_beta_nowd\t%s\t%s\n' "$ST" "$rd" >>"$MAN"
  echo "[$(ts)] X3 done -> $rd"
else echo "[$(ts)] X3 FAIL (see $LOGDIR/run.log)"; fi
