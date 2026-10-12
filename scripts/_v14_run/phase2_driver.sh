#!/bin/bash
# Phase 2: (a) the AL v14 MTL the main driver skipped after the postbuild bug,
#          (b) matched CANONICAL baseline FL/AL/AZ. Same harness, KD OFF, seeds {0,1,7,100}.
# Chains on the main v14 driver PID (arg 1).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
SEEDS="0 1 7 100"
RUNDIR=scripts/_v14_run; LOGDIR=$RUNDIR/logs
V14ENG=check2hgi_design_k_resln_mae_l0_1
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] P2 $*"; }

V14PID=${1:-}
if [ -n "$V14PID" ]; then
  say "waiting for v14 driver pid $V14PID"
  while kill -0 "$V14PID" 2>/dev/null; do sleep 60; done
  say "v14 driver finished"
fi

COMMON="--task mtl --task-set check2hgi_next_region \
  --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"
B9="--scheduler cosine --max-lr 3e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5"
H3ALT="--scheduler constant"

run_one(){  # engine state seed recipe transdir manifest logprefix
  local eng=$1 state=$2 seed=$3 recipe=$4 trans=$5 man=$6 pfx=$7
  [ -f "$man" ] || : > "$man"
  grep -q "^$state	$seed	" "$man" && { say "skip $pfx $state seed=$seed"; return 0; }
  local log="$LOGDIR/${pfx}_${state}_seed${seed}.log"
  say "start $pfx $state seed=$seed"
  $PY scripts/train.py $COMMON --engine "$eng" --state "$state" --seed "$seed" $recipe \
      --per-fold-transition-dir "$trans" > "$log" 2>&1 \
    || { say "FAIL $pfx $state seed=$seed — see $log"; return 1; }
  local rd=$(ls -dt results/$eng/$state/mtlnet_*ep50* 2>/dev/null | head -1)
  printf '%s\t%s\t%s\n' "$state" "$seed" "$rd" >> "$man"
  say "done $pfx $state seed=$seed -> $rd"
}

# (a) missing AL v14 MTL — stage log_T then run
ALDST=output/$V14ENG/alabama
for S in $SEEDS; do for f in 1 2 3 4 5; do
  cp output/check2hgi/alabama/region_transition_log_seed${S}_fold${f}.pt "$ALDST/region_transition_log_seed${S}_fold${f}.pt"
done; done
sleep 1; touch "$ALDST"/region_transition_log_seed*_fold*.pt
say "AL v14 log_T staged ($(ls $ALDST/region_transition_log_seed*_fold*.pt|wc -l))"
for S in $SEEDS; do run_one "$V14ENG" alabama "$S" "$H3ALT" "$ALDST" "$RUNDIR/manifest.tsv" mtl; done

# (b) matched canonical baseline
CM="$RUNDIR/canon_manifest.tsv"
for S in $SEEDS; do run_one check2hgi florida "$S" "$B9"   output/check2hgi/florida "$CM" canon; done
for S in $SEEDS; do run_one check2hgi alabama "$S" "$H3ALT" output/check2hgi/alabama "$CM" canon; done
for S in $SEEDS; do run_one check2hgi arizona "$S" "$H3ALT" output/check2hgi/arizona "$CM" canon; done
say "ALL DONE"
