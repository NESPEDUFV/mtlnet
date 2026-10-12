#!/bin/bash
# C25 combos SCREEN — 1-seed (seed 0) screens of dual-tower-with-swapped-shared-component +
# speculative hybrids, under the C25 unweighted real-joint fix (FL, onecycle, KD-OFF). Promising
# arms (reg approaching/above dual_gated 73.06 / ceiling 73.31) get promoted to 4 seeds separately.
# Same recipe as c25_tier2_refix.sh. Capture by PID suffix (concurrent-rundir-race safe).
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_combos_screen.sh > /tmp/c25combo/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEED=${SEED:-0}; ST=${ST:-florida}
LOGDIR=/tmp/c25combo; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_combos_screen_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25CMB $*"; }

# Optional GPU-free poll-wait (WAIT=1) so a second instance queues behind a running one.
# bracket-pattern avoids self-match; pgrep -c always prints a count (do NOT `|| echo 0`).
if [ "${WAIT:-0}" = "1" ]; then
  say "WAIT=1 — polling until GPU frees (a prior screen instance finishes)..."
  while true; do p=$(pgrep -fc 'scripts/[t]rain.py'); [ "${p:-0}" -gt 0 ] || break; sleep 60; done
  say "GPU free — proceeding"
fi

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"

# tag | model | reg_head | extra-head/model-params
# Advisor-ranked screen. All carry raw_embed_dim=64 (builds the private tower) + prior-OFF.
# dual_swiglu_off = combo (F), the one new model; the rest are FLAG-only on the dual-tower.
OFF="--reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
ARMS="dual_prioroff|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=gated $OFF
dual_aux_off|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux $OFF
dual_privonly_off|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=private_only $OFF
dual_swiglu_off|mtlnet_crossattn_dualtower_swiglu|next_stan_flow_dualtower|--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=gated $OFF"

run(){ local tag=$1 model=$2 rh=$3 extra=$4 key="${tag}|s${SEED}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}_s${SEED}.log"; say "start $key (model=$model)"
  $PY scripts/train.py $COMMON --state "$ST" --seed "$SEED" \
      --model "$model" --reg-head "$rh" $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC state=$ST seed=$SEED (1-seed screen) unweighted onecycle"
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  IFS='|' read -r tag model rh extra <<< "$spec"
  run "$tag" "$model" "$rh" "$extra" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done <<< "$ARMS"
wait
say "ALL DONE"
