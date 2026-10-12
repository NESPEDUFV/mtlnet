#!/bin/bash
# SAFE overlap GPU-fit + host-RAM diagnostic. Runs champion-G MTL fold-1 on the
# gated check2hgi_dk_ovl engine with the dataset kept CPU-resident (MTL_DATASET_CPU=1)
# and S2 chunked val, under an RSS WATCHDOG that hard-kills the process if its host
# RSS exceeds RAM_CAP_GB (default 60) — so it can NEVER OOM-kill the box. Records
# peak GPU VRAM and peak host RSS, and stops once fold-1 clears validation.
#   usage: overlap_fit_safe.sh <state> [ram_cap_gb] [epochs]
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=${1:-california}; RAM_CAP_GB=${2:-60}; EPOCHS=${3:-2}; DS_MODE=${4:-cpu}
# dataset-device mode: cpu (CPU-resident, GPU peak N-independent) | gpu (force
# pre-move to GPU) | auto (the _dataset_device auto-fit). Only ONE may be set.
case "$DS_MODE" in
  cpu) export MTL_DATASET_CPU=1 ;;
  gpu) export MTL_DATASET_GPU=1 ;;
  auto) : ;;  # neither -> auto-fit
  *) echo "bad DS_MODE=$DS_MODE (cpu|gpu|auto)"; exit 2 ;;
esac
echo "DS_MODE=$DS_MODE"
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval; mkdir -p "$L"
log="$L/safefit_${ST}_${DS_MODE}.log"; verdict="$L/safefit_${ST}_${DS_MODE}.verdict"; : > "$verdict"
CAP_KB=$(( RAM_CAP_GB * 1024 * 1024 ))
echo "[$(date '+%F %T')] SAFE-FIT $ST ds=$DS_MODE (RAM cap ${RAM_CAP_GB} GB)"
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
pid=$!; PEAKG=0; PEAKR=0
for i in $(seq 1 600); do
  kill -0 $pid 2>/dev/null || { echo "PROC_EXIT peakGPU=${PEAKG}MiB peakRSS=$((PEAKR/1024/1024))GB" > "$verdict"; break; }
  # sum RSS (KB) of the train PID + any children
  rss=$(ps -o rss= --ppid $pid -p $pid 2>/dev/null | awk '{s+=$1} END{print s+0}')
  [ "$rss" -gt "$PEAKR" ] && PEAKR=$rss
  g=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
  [ -n "$g" ] && [ "$g" -gt "$PEAKG" ] && PEAKG=$g
  if [ "$rss" -gt "$CAP_KB" ]; then
    kill -9 $pid 2>/dev/null
    echo "RAM-CAP-HIT (>${RAM_CAP_GB}GB) peakGPU=${PEAKG}MiB peakRSS=$((rss/1024/1024))GB" > "$verdict"; break
  fi
  if grep -aqiE 'out of memory|OutOfMemory|CUDA out' "$log"; then
    echo "GPU-OOM peakGPU=${PEAKG}MiB peakRSS=$((PEAKR/1024/1024))GB" > "$verdict"; kill $pid 2>/dev/null; break
  fi
  if grep -aqE 'FOLD 2/5|Epoch 2/' "$log"; then
    echo "FIT peakGPU=${PEAKG}MiB peakRSS=$((PEAKR/1024/1024))GB" > "$verdict"; kill $pid 2>/dev/null; break
  fi
  sleep 2
done
sleep 2; kill -9 $pid 2>/dev/null
echo "[$(date '+%F %T')] SAFE-FIT $ST -> $(cat "$verdict")"
grep -aiE "host-RAM estimate|MemoryError|out of memory" "$log" | tail -3 || true
