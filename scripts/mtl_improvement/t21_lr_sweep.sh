#!/bin/bash
# T2.1 per-arch LR mini-sweep (hard rule 7) — the PRIMARY variant (b gated),
# prior-ON, v14 substrate, KD-OFF, seeded per-fold log_T, AL+AZ, 5f x 40ep, seed42.
# 5 LR regimes; the winner sets the recipe for the full T2.1 protocol.
#
# Regimes:
#   R1 constant_1e3   — all groups 1e-3, constant scheduler (simplest baseline)
#   R2 b9             — cosine max-lr 3e-3 + alt-opt + alpha-no-wd + min-best-5 (the FL champion recipe)
#   R3 onecycle       — onecycle max-lr 3e-3 pct0.3 per-head (the STL-reg-ceiling scheduler / arch-default)
#   R4 head_group     — constant, reg_head 3e-3 / reg_encoder 1e-3 (private tower its own effective group)
#   R5 onecycle_warm5 — onecycle max-lr 3e-3 pct0.05 per-head (b9-ish + 5% warmup)
#
# MPS-collocates small-state runs (each underutilizes the A40). Concurrency via
# CONC env (default 3); OMP pinned to 32/CONC. Idempotent via a manifest.
#   Launch: setsid bash scripts/mtl_improvement/t21_lr_sweep.sh > /tmp/t21_lrsweep/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42
EPOCHS=40
CONC=${CONC:-3}
LOGDIR=/tmp/t21_lrsweep
mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_lrsweep_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] LRSWEEP $*"; }

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --seed $SEED \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn_dualtower \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=gated \
  --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

# Regime recipe strings (keyed by name).
recipe(){
  case "$1" in
    R1_constant_1e3) echo "--cat-lr 1e-3 --reg-lr 1e-3 --shared-lr 1e-3 --scheduler constant" ;;
    R2_b9)           echo "--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --scheduler cosine --max-lr 3e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5" ;;
    R3_onecycle)     echo "--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --scheduler onecycle --max-lr 3e-3" ;;
    R4_head_group)   echo "--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --reg-encoder-lr 1e-3 --reg-head-lr 3e-3 --scheduler constant" ;;
    R5_onecycle_warm5) echo "--cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --scheduler onecycle --max-lr 3e-3 --pct-start 0.05" ;;
    *) echo "BAD_REGIME"; return 1 ;;
  esac
}

REGIMES="R1_constant_1e3 R2_b9 R3_onecycle R4_head_group R5_onecycle_warm5"
STATES="alabama arizona"

run_one(){
  local state=$1 regime=$2
  local key="${state}|${regime}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key (done)"; return 0; }
  local rec; rec=$(recipe "$regime") || { say "FAIL bad regime $regime"; return 1; }
  local log="$LOGDIR/${regime}_${state}.log"
  say "start $key"
  # Race-free rundir capture: train.py names its rundir ...{ts}_{os.getpid()}
  # (src/tracking/experiment.py). Background it, capture the PID, and map the
  # rundir deterministically by its PID suffix — NOT `ls -dt` (which races under
  # concurrency and silently mis-attributes runs to the same dir).
  $PY scripts/train.py $COMMON --state "$state" $rec \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!
  wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    if [ -z "$rd" ] || [ ! -f "$rd/summary/full_summary.json" ]; then
      say "WARN $key — rundir for pid=$pid not found/incomplete (rd='$rd')"
    fi
    printf '%s\t%s\t%s\n' "$key" "$regime" "$rd" >> "$MANIFEST"
    say "done $key (pid=$pid) -> $rd"
  else
    say "FAIL $key (pid=$pid rc=$rc) — see $log"
  fi
}

# Job pool: launch up to CONC concurrent runs.
say "config: CONC=$CONC OMP=$OMP_NUM_THREADS epochs=$EPOCHS seed=$SEED"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader | sed 's/^/[gpu] /'
pids=()
for state in $STATES; do
  for regime in $REGIMES; do
    run_one "$state" "$regime" &
    pids+=($!)
    # throttle to CONC
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu-final] /'
