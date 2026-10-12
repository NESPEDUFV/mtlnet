#!/bin/bash
# T2.1 hardening + onecycle-lever validation (user-approved 2026-06-04).
# All arms: onecycle per-head (cat1e-3/reg3e-3/shared1e-3), static_weight cat0.75,
# KD-OFF, prior-ON, v14, 5f x 50ep, seeded per-fold log_T. PID-safe rundir capture.
#
# STAGE=harden  (seed42):
#   t20_hardshare  mtlnet                     next_getnext_hard        -      AL,AZ,FL  (hard-share anchor)
#   base_a         mtlnet_crossattn           next_getnext_hard        -      FL        (matched baseline @FL)
#   dt_gated_on    mtlnet_crossattn_dualtower next_stan_flow_dualtower gated  FL        (centerpiece @FL)
#   t22_crossstitch mtlnet_crossstitch        next_getnext_hard        -      AL,AZ,FL  (§6.3 partial-winner)
#   → completes the sharing dose-response curve + hardens the negative across AL/AZ/FL.
#
# STAGE=validate  (seeds {0,1,7,100}):
#   onecyc_val     mtlnet_crossattn           next_getnext_hard        -      AL,AZ,FL  (vs landed H3-alt/B9 (a))
#   → validates the onecycle reg-recipe lever multi-seed.
#
#   Launch: STAGE=harden CONC=3 setsid bash scripts/mtl_improvement/t21_harden.sh > /tmp/t21_harden/harden.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
STAGE=${STAGE:?set STAGE=harden|validate}
CONC=${CONC:-3}; EPOCHS=50
LOGDIR=/tmp/t21_harden; mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_harden_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] HARDEN $*"; }

RECIPE="--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

# arm: tag|model|reg_head|fusion|prior|state|seed
arms_harden(){
  for st in alabama arizona florida; do
    echo "t20_hardshare|mtlnet|next_getnext_hard|-|on|$st|42"
    echo "t22_crossstitch|mtlnet_crossstitch|next_getnext_hard|-|on|$st|42"
  done
  echo "base_a|mtlnet_crossattn|next_getnext_hard|-|on|florida|42"
  echo "dt_gated_on|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|gated|on|florida|42"
}
arms_validate(){
  for st in alabama arizona florida; do for sd in 0 1 7 100; do
    echo "onecyc_val|mtlnet_crossattn|next_getnext_hard|-|on|$st|$sd"
  done; done
}
# harden2 (capstone optional hardening): multi-seed CrossStitch (the one non-losing arch) +
# multi-seed FL dual-tower (harden the FL negative). Baseline = onecyc_val multi-seed (= base_a).
arms_harden2(){
  for sd in 0 1 7; do
    for st in alabama arizona florida; do
      echo "cs|mtlnet_crossstitch|next_getnext_hard|-|on|$st|$sd"
    done
    echo "dtfl|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|gated|on|florida|$sd"
  done
}

run_arm(){
  local spec=$1 tag model reg_head fusion prior state seed
  IFS='|' read -r tag model reg_head fusion prior state seed <<< "$spec"
  local key="${tag}|${state}|s${seed}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local hp="--reg-head $reg_head"
  if [ "$reg_head" = "next_stan_flow_dualtower" ]; then
    hp="$hp --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=${fusion}"
    [ "$prior" = "off" ] && hp="$hp --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
  fi
  local log="$LOGDIR/${tag}_${state}_s${seed}.log"
  say "start $key (model=$model)"
  $PY scripts/train.py $COMMON --model "$model" --state "$state" --seed "$seed" $RECIPE $hp \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >> "$MANIFEST"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "STAGE=$STAGE CONC=$CONC OMP=$OMP_NUM_THREADS"
nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
# Process substitution (NOT a pipe) so the loop runs in THIS shell — otherwise
# `wait` can't see the backgrounded run_arm jobs and prints DONE prematurely.
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  run_arm "$spec" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done < <( case "$STAGE" in harden) arms_harden;; validate) arms_validate;; harden2) arms_harden2;; esac )
wait
say "STAGE $STAGE DONE"
