#!/bin/bash
# T2.1 full protocol — staged, after the LR mini-sweep winner is pinned.
# Frozen-fold paired (deterministic StratifiedGroupKFold(seed)); Δ vs frozen (c)/(d).
# PID-safe rundir capture (see t21_lr_sweep.sh / ref-concurrent-rundir-race).
#
# STAGES (env STAGE, run one at a time, decide between them):
#   fusion_pick : {gated,private_only,aux} x prior-ON x static_weight x {AL,AZ,FL} 5f50ep s42  (9 runs)
#   refine      : BEST_MODE x {priorOFF, pcgrad} x {AL,AZ,FL}                                   (6 runs)
#   substrate   : BEST_CFG  x gcn_ctrl(canonical-fresh) x {AL,AZ,FL}  (regime x substrate 2x2)  (3 runs)
#   promote     : BEST_CFG  x seeds {0,1,7} x {AL,AZ,FL}                                         (9 runs)
#   hgi         : BEST_CFG  x HGI substrate x seeds {0,1} x {AL,AZ} 5f30ep                       (4 runs)
#
# Recipe is STATE-CONDITIONAL: FL=B9 (production large-state), AL/AZ=$SMALL_RECIPE
# (the LR-sweep winner). Pass SMALL_RECIPE + BEST_MODE/BEST_CFG via env.
#   Launch: STAGE=fusion_pick SMALL_RECIPE="--scheduler constant --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3" \
#           CONC=3 setsid bash scripts/mtl_improvement/t21_full_protocol.sh > /tmp/t21_full/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
CANON=check2hgi          # canonical-fresh (gcn_ctrl) substrate
EPOCHS=${EPOCHS:-50}
CONC=${CONC:-3}
STAGE=${STAGE:?set STAGE}
SMALL_RECIPE=${SMALL_RECIPE:?set SMALL_RECIPE (AL/AZ recipe = LR-sweep winner)}
BEST_MODE=${BEST_MODE:-gated}
LOGDIR=/tmp/t21_full
mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_full_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] T21FULL $*"; }

# FL production large-state recipe (B9). AL/AZ use the LR-sweep winner.
B9="--scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5"
state_recipe(){ case "$1" in florida) echo "$B9" ;; *) echo "$SMALL_RECIPE" ;; esac; }

# COMMON minus the model/head/substrate/recipe knobs (added per-arm).
base_common(){
  echo "--task mtl --task-set check2hgi_next_region --seed $2 \
    --epochs $EPOCHS --folds 5 --batch-size 2048 \
    --model mtlnet_crossattn_dualtower \
    --mtl-loss $3 --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --task-a-input-type checkin --task-b-input-type region \
    --log-t-kd-weight 0.0 --no-checkpoints --engine $1"
}

# run_arm <state> <engine> <seed> <mtl_loss> <fusion_mode> <prior:on|off> <tag>
run_arm(){
  local state=$1 engine=$2 seed=$3 loss=$4 mode=$5 prior=$6 tag=$7
  local key="${tag}|${state}|s${seed}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local hp="--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=${mode}"
  [ "$prior" = "off" ] && hp="$hp --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
  # prior-off ⇒ drop --alpha-no-weight-decay (no learnable α); strip it from FL B9 too.
  local rec; rec=$(state_recipe "$state")
  [ "$prior" = "off" ] && rec=$(echo "$rec" | sed 's/--alpha-no-weight-decay//')
  local log="$LOGDIR/${tag}_${state}_s${seed}.log"
  say "start $key (engine=$engine loss=$loss mode=$mode prior=$prior)"
  $PY scripts/train.py $(base_common "$engine" "$seed" "$loss") --state "$state" $rec $hp \
      --per-fold-transition-dir "output/$engine/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$engine/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >> "$MANIFEST"
    say "done $key -> $rd"
  else
    say "FAIL $key (rc=$rc) — see $log"
  fi
}

# Job pool over an arm list "state engine seed loss mode prior tag" (one per line on stdin).
run_pool(){
  while read -r st eng sd ls md pr tg; do
    [ -z "$st" ] && continue
    run_arm "$st" "$eng" "$sd" "$ls" "$md" "$pr" "$tg" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
  wait
}

say "STAGE=$STAGE CONC=$CONC OMP=$OMP_NUM_THREADS epochs=$EPOCHS BEST_MODE=$BEST_MODE"
say "SMALL_RECIPE=$SMALL_RECIPE"
case "$STAGE" in
  fusion_pick)
    { for st in alabama arizona florida; do for md in gated private_only aux; do
        echo "$st $V14 42 static_weight $md on fp_${md}"
      done; done; } | run_pool ;;
  refine)
    { for st in alabama arizona florida; do
        echo "$st $V14 42 static_weight $BEST_MODE off rf_priorOFF"
        echo "$st $V14 42 pcgrad        $BEST_MODE on  rf_pcgrad"
      done; } | run_pool ;;
  substrate)
    { for st in alabama arizona florida; do
        echo "$st $CANON 42 static_weight $BEST_MODE on sub_gcnctrl"
      done; } | run_pool ;;
  promote)
    { for st in alabama arizona florida; do for sd in 0 1 7; do
        echo "$st $V14 $sd static_weight $BEST_MODE on promote"
      done; done; } | run_pool ;;
  hgi)
    { for st in alabama arizona; do for sd in 0 1; do
        echo "$st hgi $sd static_weight $BEST_MODE on hgi_probe"
      done; done; } | run_pool ;;
  *) say "unknown STAGE=$STAGE"; exit 2 ;;
esac
say "STAGE $STAGE DONE"
