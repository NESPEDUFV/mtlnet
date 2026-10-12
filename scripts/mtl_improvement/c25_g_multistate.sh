#!/bin/bash
# C25 G MULTI-STATE confirmation — 4-seed {1,7,100} of champion G at AL/AZ/GE (seed 0 reused
# from c25_gv2_manifest.tsv). G = dualtower + aux fusion + prior-OFF, v14, unweighted onecycle
# KD-OFF. Confirms the Pareto-positive "single MTL beats both STL ceilings" claim multi-state.
# (c) ceilings: AL reg 62.88/cat 49.97 ; AZ 55.11/51.01 ; GE 58.45/58.12. PID-suffix capture.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_g_multistate.sh > /tmp/c25gms/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(1 7 100)
LOGDIR=/tmp/c25gms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_g_multistate_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25GMS $*"; }

GHEAD="--reg-head next_stan_flow_dualtower --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower $GHEAD --no-checkpoints"

STATES="alabama arizona georgia"
run(){ local st=$1 sd=$2 key="g_${st}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/g_${st}_s${sd}.log"; say "start $key"
  $PY scripts/train.py $COMMON --state "$st" --seed "$sd" \
      --per-fold-transition-dir output/$V14/$st > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "g_${st}" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}
say "config: CONC=$CONC seeds='${SEEDS[*]}' states='$STATES' (4-seed G confirm; seed0 from gv2)"
for st in $STATES; do for sd in "${SEEDS[@]}"; do
  run "$st" "$sd" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done; done
wait
say "ALL DONE"
