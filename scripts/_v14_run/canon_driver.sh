#!/bin/bash
# Matched CANONICAL baseline (engine=check2hgi, frozen GCN substrate) in the SAME harness
# as the v14 sweep: KD OFF, B9 (FL) / H3-alt (AL/AZ), seeds {0,1,7,100}, 5 folds.
# Runs AFTER the v14 driver finishes (chained on its PID). This is the valid apples-to-apples
# comparison; frozen §0.1 is a different harness and not directly comparable.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
ENGINE=check2hgi
SEEDS="0 1 7 100"
RUNDIR=scripts/_v14_run
LOGDIR=$RUNDIR/logs
MANIFEST=$RUNDIR/canon_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CANON $*"; }

# wait for v14 driver to finish
V14PID=${1:-}
if [ -n "$V14PID" ]; then
  say "waiting for v14 driver pid $V14PID"
  while kill -0 "$V14PID" 2>/dev/null; do sleep 60; done
  say "v14 driver finished; starting canonical baseline"
fi

COMMON="--task mtl --task-set check2hgi_next_region --engine $ENGINE \
  --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"
B9="--scheduler cosine --max-lr 3e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5"
H3ALT="--scheduler constant"

run_one(){
  local state=$1 seed=$2 recipe=$3
  local log="$LOGDIR/canon_${state}_seed${seed}.log"
  grep -q "^$state	$seed	" "$MANIFEST" && { say "skip $state seed=$seed"; return 0; }
  say "start $state seed=$seed"
  $PY scripts/train.py $COMMON --state "$state" --seed "$seed" $recipe \
      --per-fold-transition-dir "output/check2hgi/$state" > "$log" 2>&1 \
    || { say "FAIL $state seed=$seed — see $log"; return 1; }
  local rd=$(ls -dt results/$ENGINE/$state/mtlnet_*ep50* 2>/dev/null | head -1)
  printf '%s\t%s\t%s\n' "$state" "$seed" "$rd" >> "$MANIFEST"
  say "done $state seed=$seed -> $rd"
}
for S in $SEEDS; do run_one florida "$S" "$B9";   done
for S in $SEEDS; do run_one alabama "$S" "$H3ALT"; done
for S in $SEEDS; do run_one arizona "$S" "$H3ALT"; done
say "ALL DONE"
