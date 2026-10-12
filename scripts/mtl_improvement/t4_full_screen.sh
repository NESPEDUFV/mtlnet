#!/bin/bash
# T4.0a + T4.1 COMPLETE single-seed screen under champion G (user: full set, single-seed first,
# parallel, analyze all candidates BEFORE any multi-seed). Each arm = G's exact arch/recipe
# (--canon none + explicit G flags) with only the loss/scale changed. seed0.
#   ARMS: static_weight(=G control), scale_norm(T4.0a), + the full src/losses balancer registry
#   (focal=cat-loss + naive=legacy-iface EXCLUDED; random_weight already in T4.0b but re-run for a
#    uniform in-harness screen).
# Usage: STATE=alabama CONC=5 setsid bash scripts/mtl_improvement/t4_full_screen.sh > /tmp/t4f/alabama.log 2>&1 &
#        STATE=florida CONC=2 setsid bash scripts/mtl_improvement/t4_full_screen.sh > /tmp/t4f/florida.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
ST=${STATE:-alabama}; SD=0; EPOCHS=50; CONC=${CONC:-4}
LOGDIR=/tmp/t4f/$ST; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t4_full_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T4F[$ST] $*"; }

# G arch/recipe COMMON (everything except the loss). --canon none so the bundle's
# static_weight+category-weight don't conflict with non-static balancers.
COMMON=(--task mtl --canon none --task-set check2hgi_next_region --engine "$V14"
  --state "$ST" --seed "$SD" --epochs "$EPOCHS" --folds 5 --batch-size 2048
  --no-reg-class-weights --no-cat-class-weights
  --cat-head next_gru --reg-head next_stan_flow_dualtower
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
  --model mtlnet_crossattn_dualtower
  --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints)

# arm -> extra flags (loss selection). static_weight needs --category-weight.
declare -A ARM
ARM[static_weight]="--mtl-loss static_weight --category-weight 0.75"               # = G control
ARM[scale_norm]="--mtl-loss static_weight --category-weight 0.75 --loss-scale-norm" # T4.0a
ARM[equal_weight]="--mtl-loss equal_weight"
ARM[scheduled_static]="--mtl-loss scheduled_static"
ARM[uncertainty_weighting]="--mtl-loss uncertainty_weighting"
ARM[uw_so]="--mtl-loss uw_so"
ARM[famo]="--mtl-loss famo"
ARM[db_mtl]="--mtl-loss db_mtl"
ARM[dwa]="--mtl-loss dwa"
ARM[gradnorm]="--mtl-loss gradnorm"
ARM[cagrad]="--mtl-loss cagrad"
ARM[nash_mtl]="--mtl-loss nash_mtl"
ARM[aligned_mtl]="--mtl-loss aligned_mtl"
ARM[pcgrad]="--mtl-loss pcgrad"
ARM[fairgrad]="--mtl-loss fairgrad"
ARM[bayesagg_mtl]="--mtl-loss bayesagg_mtl"
ARM[excess_mtl]="--mtl-loss excess_mtl"
ARM[stch]="--mtl-loss stch"
ARM[go4align]="--mtl-loss go4align"

run_arm(){ local arm=$1; local key="${arm}|${ST}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${arm}.log"; say "start $arm"
  $PY scripts/train.py "${COMMON[@]}" ${ARM[$arm]} > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$arm" "$rd" >>"$MAN"; say "done $arm -> $rd"
  else say "FAIL $arm — see $log"; fi
}

ARMS=(static_weight scale_norm equal_weight scheduled_static uncertainty_weighting uw_so famo
      db_mtl dwa gradnorm cagrad nash_mtl aligned_mtl pcgrad fairgrad bayesagg_mtl excess_mtl
      stch go4align)
say "=== T4 full screen: ${#ARMS[@]} arms, seed0, CONC=$CONC ==="
for arm in "${ARMS[@]}"; do
  run_arm "$arm" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait
say "ALL DONE ($ST)"
