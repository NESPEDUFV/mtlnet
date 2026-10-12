#!/bin/bash
# CRITIQUE close-out — the DROPPED flag-controllable arms (finish T2V.6/T2V.7).
# Anchor: G reg 73.57 / cat 73.16 (FL seed0). Arms:
#   T2V.7 (cat loss family, completes logit-adjust): focal γ=2.0 ; class-balanced (cb)
#   T2V.6 (optimizers/balancers the study never ran): uncertainty-weighting ; CAGrad ; Nash (k=2)
# All on G's arch (dual-tower aux prior-OFF), FL seed0, v14. CONC=2. PID capture.
#   CONC=2 setsid bash scripts/mtl_improvement/t2v_dropped_flagarms.sh > /tmp/t2vflag/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t2vflag; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v_dropped_flagarms_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2VFLAG $*"; }
GHEAD="--reg-head next_stan_flow_dualtower --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
base(){ echo "--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --cat-head next_gru $GHEAD \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --per-fold-transition-dir output/$V14/$ST --no-checkpoints"; }
run(){ local tag=$1; shift; local extra="$*"; local key="${tag}|s${SD}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}.log"; say "start $key"
  $PY scripts/train.py $(base) $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}
ARMS=(
  "t2v7_focal2|--mtl-loss static_weight --category-weight 0.75 --focal-gamma 2.0"
  "t2v7_cb|--mtl-loss static_weight --category-weight 0.75 --tail-loss cb"
  "t2v6_uncert|--mtl-loss uncertainty_weighting"
  "t2v6_cagrad|--mtl-loss cagrad"
  "t2v6_nash|--mtl-loss nash_mtl"
)
say "config: CONC=$CONC FL seed0 — dropped T2V.6/7 flag-arms (${#ARMS[@]})"
for spec in "${ARMS[@]}"; do
  tag=${spec%%|*}; extra=${spec#*|}
  run "$tag" $extra &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
