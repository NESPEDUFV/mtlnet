#!/bin/bash
# T4.0b — RLW litmus (Lin TMLR'22). Champion G but --mtl-loss random_weight (Dirichlet per-step
# random task weights) instead of static_weight cw=0.75. If RLW ≈ G, the INTER-TASK WEIGHT is NOT
# the bottleneck → the lever is scale/intra-task imbalance, and most of T4.1 can be skipped.
# Comparand: G (static_weight) seed-0 (R0): AL reg-full 62.57? (use per-seed) ; FL 73.14(s0)/cat 73.04.
# Zero new code. AL + FL, seed 0.
#   CONC=1 setsid bash scripts/mtl_improvement/t40_rlw_litmus.sh > /tmp/t40/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; SD=0; EPOCHS=50
LOGDIR=/tmp/t40; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t40_rlw_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=24
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T40 $*"; }

rlw_run(){ local st=$1; local key="rlw|${st}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${key//|/_}.log"; say "start $key"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$V14" \
      --state "$st" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --mtl-loss random_weight --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$st/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\trlw\t%s\n' "$key" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}

say "=== T4.0b RLW litmus on G, AL+FL seed0 ==="
rlw_run alabama
rlw_run florida
say "ALL DONE"
