#!/bin/bash
# G' MULTI-STATE — the cat-improved both-private dual-tower at AL/AZ/GE x {0,1,7,100} (FL already
# done: cat 74.77±0.04 / reg 73.59±0.07). Confirms the +1.61 cat lift (at zero reg cost) generalizes
# beyond FL → makes G' multi-state like G. model=catpriv; cat-head AND reg-head = next_stan_flow_dualtower
# (aux + prior-OFF). v14, unweighted onecycle KD-OFF. (c) cat ceilings: AL 49.97/AZ 51.01/GE 58.12;
# G cat at those states: AL 52.91/AZ 54.48/GE 61.43 (G' should lift further). PID capture.
#   CONC=2 setsid bash scripts/mtl_improvement/gprime_multistate.sh > /tmp/gpms/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}; SEEDS=(0 1 7 100); STATES="alabama arizona georgia"
LOGDIR=/tmp/gpms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/gprime_multistate_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] GPMS $*"; }
DT="--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
CT="--cat-head-param raw_embed_dim=64 --cat-head-param fusion_mode=aux --cat-head-param freeze_alpha=True --cat-head-param alpha_init=0.0"
run(){ local st=$1 sd=$2; local key="gp_${st}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/gp_${st}_s${sd}.log"; say "start $key"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine $V14 --state "$st" --seed "$sd" \
      --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
      --model mtlnet_crossattn_dualtower_catpriv \
      --cat-head next_stan_flow_dualtower $CT --reg-head next_stan_flow_dualtower $DT \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --per-fold-transition-dir output/$V14/$st --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "gp_${st}" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key — see $log"; fi
}
say "config: CONC=$CONC seeds='${SEEDS[*]}' states='$STATES' (G' cat-improved both-private)"
for st in $STATES; do for sd in "${SEEDS[@]}"; do
  run "$st" "$sd" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done; done
wait
say "ALL DONE"
