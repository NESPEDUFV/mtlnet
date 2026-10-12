#!/bin/bash
# T2.1 diagnostic ladder (advisor-reordered) — AL+AZ only, R3 onecycle, seed42,
# 5f x 50ep, static_weight cat0.75, KD-OFF, seeded per-fold log_T. Frozen-fold paired.
# Answers the headline ("can a private tower close a meaningful fraction inside one model,
# and where does the disjoint<<ceiling residual come from?") on the cheap states before any
# FL/multi-seed spend. PID-safe rundir capture (ref-concurrent-rundir-race).
#
# 4 core arms (Δ measured vs arm #1, the matched (a)@onecycle zero-point):
#   base_a       mtlnet_crossattn          next_getnext_hard        -            prior=on   (zero-point)
#   dt_gated_on  mtlnet_crossattn_dualtower next_stan_flow_dualtower gated        prior=on   (primary)
#   dt_priv_on   mtlnet_crossattn_dualtower next_stan_flow_dualtower private_only prior=on   (gate isolation)
#   dt_priv_off  mtlnet_crossattn_dualtower next_stan_flow_dualtower private_only prior=off  (KILLER CELL)
#
#   Launch: CONC=4 setsid bash scripts/mtl_improvement/t21_ladder.sh > /tmp/t21_ladder/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42
EPOCHS=50
CONC=${CONC:-4}
LOGDIR=/tmp/t21_ladder
mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_ladder_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] LADDER $*"; }

# R3 onecycle (the LR-sweep winner) — identical recipe for ALL arms (clean arch Δ).
RECIPE="--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --seed $SEED \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

# arm spec: tag|model|reg_head|fusion(or -)|prior(on/off)
ARMS="base_a|mtlnet_crossattn|next_getnext_hard|-|on
dt_gated_on|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|gated|on
dt_priv_on|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|private_only|on
dt_priv_off|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|private_only|off"

run_arm(){
  local state=$1 spec=$2
  local tag model reg_head fusion prior
  IFS='|' read -r tag model reg_head fusion prior <<< "$spec"
  local key="${tag}|${state}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local hp="--reg-head $reg_head"
  if [ "$reg_head" = "next_stan_flow_dualtower" ]; then
    hp="$hp --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=${fusion}"
    [ "$prior" = "off" ] && hp="$hp --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
  fi
  local log="$LOGDIR/${tag}_${state}.log"
  say "start $key (model=$model fusion=$fusion prior=$prior)"
  $PY scripts/train.py $COMMON --model "$model" --state "$state" $RECIPE $hp \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >> "$MANIFEST"
    say "done $key -> $rd"
  else
    say "FAIL $key (rc=$rc) — see $log"
  fi
}

say "config: CONC=$CONC OMP=$OMP_NUM_THREADS epochs=$EPOCHS seed=$SEED recipe='$RECIPE'"
nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
for state in alabama arizona; do
  while IFS= read -r spec; do
    [ -z "$spec" ] && continue
    run_arm "$state" "$spec" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done <<< "$ARMS"
done
wait
say "ALL DONE"
