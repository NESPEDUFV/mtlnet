#!/bin/bash
# v14 MTL sweep driver. log_T-KD OFF (clean substrate comparison vs frozen §0.1 v11 canon).
# Order: FL (already built) first, then build+run AL, then AZ.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
ENGINE=check2hgi_design_k_resln_mae_l0_1
SEEDS="0 1 7 100"
RUNDIR=scripts/_v14_run
LOGDIR=$RUNDIR/logs
mkdir -p "$LOGDIR"
MANIFEST=$RUNDIR/manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] $*"; }

COMMON="--task mtl --task-set check2hgi_next_region --engine $ENGINE \
  --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"
B9="--scheduler cosine --max-lr 3e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5"
H3ALT="--scheduler constant"

build_substrate(){
  local state=$1
  if [ -f "output/$ENGINE/$state/embeddings.parquet" ]; then
    say "BUILD skip $state"; else
    say "BUILD start $state"
    $PY scripts/probe/build_design_k_delaunay.py --state "$state" \
        --out-suffix resln_mae_l0_1 --epochs 500 --device cuda > "$LOGDIR/build_$state.log" 2>&1 \
      || { say "BUILD FAIL $state"; return 1; }
    say "BUILD done $state"
  fi
  if [ -f "output/$ENGINE/$state/input/next_region.parquet" ]; then
    say "POSTBUILD skip $state"; else
    say "POSTBUILD start $state"
    bash scripts/substrate_protocol_cleanup/postbuild_design_substrate.sh "$ENGINE" "$state" \
        > "$LOGDIR/postbuild_$state.log" 2>&1 \
      || { say "POSTBUILD FAIL $state"; return 1; }
    say "POSTBUILD done $state"
  fi
}

stage_logT(){
  local state=$1
  local src=output/check2hgi/$state dst=output/$ENGINE/$state
  for S in $SEEDS; do for f in 1 2 3 4 5; do
    cp "$src/region_transition_log_seed${S}_fold${f}.pt" "$dst/region_transition_log_seed${S}_fold${f}.pt"
  done; done
  sleep 1; touch "$dst"/region_transition_log_seed*_fold*.pt
  say "log_T staged $state ($(ls $dst/region_transition_log_seed*_fold*.pt|wc -l) files)"
}

run_one(){
  local state=$1 seed=$2 recipe=$3
  local log="$LOGDIR/mtl_${state}_seed${seed}.log"
  grep -q "^$state	$seed	" "$MANIFEST" && { say "MTL skip $state seed=$seed (done)"; return 0; }
  say "MTL start $state seed=$seed"
  $PY scripts/train.py $COMMON --state "$state" --seed "$seed" $recipe \
      --per-fold-transition-dir "output/$ENGINE/$state" > "$log" 2>&1 \
    || { say "MTL FAIL $state seed=$seed — see $log"; return 1; }
  local rd=$(ls -dt results/$ENGINE/$state/mtlnet_*ep50* 2>/dev/null | head -1)
  printf '%s\t%s\t%s\n' "$state" "$seed" "$rd" >> "$MANIFEST"
  say "MTL done $state seed=$seed -> $rd"
}

run_state(){
  local state=$1 recipe=$2
  build_substrate "$state" || return 1
  stage_logT "$state"
  for S in $SEEDS; do run_one "$state" "$S" "$recipe"; done
}

run_state florida "$B9"
run_state alabama "$H3ALT"
run_state arizona "$H3ALT"
say "ALL DONE"
