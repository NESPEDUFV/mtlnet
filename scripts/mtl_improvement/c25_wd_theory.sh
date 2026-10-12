#!/bin/bash
# C25 wd-THEORY — is the residual large-state reg gap (FL best 71.41 vs (c) ceiling 73.31, −1.9pp)
# the weight-decay secondary, NOT architecture? The (c) ceiling (p1) used wd=0.01; the MTL recipe
# (default_mtl) uses wd=0.05. This runs the SAME unweighted real-joint recipe at wd=0.01 on v14,
# AL/GE/FL, seeds {0,1,7,100}; compare to the c25_revalidate v14 arm (wd=0.05, same everything else).
#   wd0.01 closes the FL gap toward 73 → residual was WD, not architecture → skip the arch re-run.
#   wd0.01 ≈ wd0.05 (gap persists) → the residual is genuinely architectural → proceed to Tier 2.
# Run AFTER the revalidation sweep frees the GPU.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_wd_theory.sh <states...> > /tmp/c25wd/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(0 1 7 100); WD=0.01
LOGDIR=/tmp/c25wd; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_wd_theory_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
STATES=("$@"); [ ${#STATES[@]} -eq 0 ] && STATES=(florida alabama georgia)
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25WD $*"; }

# Same unweighted real-joint recipe as c25_revalidate, but --weight-decay 0.01 (matches the (c) ceiling).
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --weight-decay $WD --no-checkpoints"

run(){ # state seed
  local st=$1 sd=$2 key="${st}|s${sd}|wd${WD}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local logt; logt=$(ls "output/$V14/$st"/region_transition_log_seed${sd}_fold*.pt 2>/dev/null | head -1)
  [ -z "$logt" ] || [ "$logt" -ot "output/$V14/$st/input/next_region.parquet" ] && { say "FAIL $key stale log_T"; return 1; }
  local log="$LOGDIR/${st}_s${sd}.log"; say "start $key"
  $PY scripts/train.py $COMMON --state "$st" --seed "$sd" \
      --per-fold-transition-dir "output/$V14/$st" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "wd${WD}" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc)"; fi
}

say "config: CONC=$CONC states='${STATES[*]}' seeds='${SEEDS[*]}' wd=$WD (vs revalidate wd=0.05)"
for st in "${STATES[@]}"; do
  for sd in "${SEEDS[@]}"; do
    run "$st" "$sd" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
