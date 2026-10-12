#!/bin/bash
# Corrected fast closers. --folds 5 (matches the n_splits=5 inert dummy log_T) but KILLED
# after fold-1 completes (captures peak VRAM + fold-1 wall). Q3: TX compile off-vs-on in
# AUTO dataset mode (forcing OOMs TX). Q1: CA with MTL_DATASET_GPU=1 (force) to see if the
# smaller-than-TX CA dataset fits forced. champion-G gated overlap.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval/fast2; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] FAST2 $*" | tee -a "$L/run.log"; }

cell(){ # label state dsmode(auto|gpu) compile(off|on)
  local lbl=$1 ST=$2 ds=$3 cm=$4
  local knobs=""; [ "$cm" = on ] && knobs="--compile --tf32"
  ( unset MTL_DATASET_GPU MTL_DATASET_CPU; [ "$ds" = gpu ] && export MTL_DATASET_GPU=1
    export TORCHINDUCTOR_CACHE_DIR="$L/ind_$lbl"
    say "$lbl: $ST ds=$ds compile=$cm"
    $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
      --state "$ST" --seed 42 --epochs 8 --folds 5 --batch-size 2048 \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower $knobs \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$L/$lbl.log" 2>&1 ) &
  local pid=$!; local PEAK=0
  for i in $(seq 1 300); do
    kill -0 $pid 2>/dev/null || { echo "EXIT" >"$L/$lbl.verdict"; break; }
    m=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null|head -1); [ -n "$m" ]&&[ "$m" -gt "$PEAK" ]&&PEAK=$m
    if grep -aqiE "out of memory|OutOfMemory|CUDA out" "$L/$lbl.log"; then echo "OOM peak=${PEAK}" >"$L/$lbl.verdict"; kill -9 $pid 2>/dev/null; break; fi
    fc=$(grep -aoE "Fold 1/5 completed in [0-9.]+s" "$L/$lbl.log" 2>/dev/null | head -1)
    if [ -n "$fc" ]; then echo "FIT peak=${PEAK} ${fc}" >"$L/$lbl.verdict"; kill -9 $pid 2>/dev/null; break; fi
    sleep 4
  done
  kill -9 $pid 2>/dev/null
  say "$lbl -> $(cat "$L/$lbl.verdict" 2>/dev/null)"
}

cell tx_auto_off  texas      auto off
cell tx_auto_on   texas      auto on
cell ca_force_off california gpu  off

say "=== SUMMARY ==="
echo "  Q3 (compile speed, TX, AUTO): off=$(grep -aoE 'completed in [0-9.]+s' "$L/tx_auto_off.verdict" 2>/dev/null) on=$(grep -aoE 'completed in [0-9.]+s' "$L/tx_auto_on.verdict" 2>/dev/null)" | tee -a "$L/run.log"
echo "  Q1 (MTL_DATASET_GPU=1 force): TX=OOM(known)  CA=$(cat "$L/ca_force_off.verdict" 2>/dev/null)" | tee -a "$L/run.log"
say "DONE"
