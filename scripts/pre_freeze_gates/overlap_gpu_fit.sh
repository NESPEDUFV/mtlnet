#!/bin/bash
# Overlap GPU-fit test: run champion-G MTL on the GATED check2hgi_dk_ovl engine
# and record PEAK VRAM, stopping as soon as fold-1 clears its first validation
# (where peak VRAM / any OOM occurs). Answers "does stride-1 overlap MTL fit the A40?"
#   usage: overlap_gpu_fit.sh <state> [epochs]
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
# S2 chunked val-metric (essential at overlap scale: full val-logit O(N_val·C)
# OOMs the large-C states otherwise). Byte-identical; just streams the val metric.
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=${1:-california}; EPOCHS=${2:-3}
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
LOGDIR=/tmp/gate_eval; mkdir -p "$LOGDIR"
log="$LOGDIR/fit_${ST}.log"; verdict="$LOGDIR/fit_${ST}.verdict"; : > "$verdict"
echo "[$(date '+%F %T')] FIT $ST overlap champion-G (stop after fold-1 val)"
$PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed 42 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
pid=$!; PEAK=0
for i in $(seq 1 400); do
  kill -0 $pid 2>/dev/null || { echo "PROC_EXIT peak=${PEAK}" > "$verdict"; break; }
  m=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
  [ -n "$m" ] && [ "$m" -gt "$PEAK" ] && PEAK=$m
  if grep -aqiE 'out of memory|OutOfMemory|CUDA out' "$log"; then echo "OOM peak=${PEAK}" > "$verdict"; kill $pid 2>/dev/null; break; fi
  # fold-1 cleared validation once we see fold-1 epoch-2 OR fold 2 start
  if grep -aqE 'FOLD 2/5|Fold 1/5 completed|Epoch 2/' "$log"; then echo "FIT peak=${PEAK}" > "$verdict"; kill $pid 2>/dev/null; break; fi
  sleep 6
done
sleep 3; kill $pid 2>/dev/null
echo "[$(date '+%F %T')] FIT $ST -> $(cat "$verdict") (A40 has 46068 MiB)"
grep -aiE "out of memory|OutOfMemory" "$log" | head -1 || true
