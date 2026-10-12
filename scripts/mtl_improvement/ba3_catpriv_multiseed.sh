#!/bin/bash
# B-A3 PROMOTE — multi-seed {1,7,100} confirmation of the both-private dual-tower (cat-private
# champion). seed0 reused (cat 74.74 / reg 73.52 vs G 73.16/73.57). model=catpriv; cat-head AND
# reg-head = next_stan_flow_dualtower (aux + prior-OFF). FL, unweighted onecycle KD-OFF. PID capture.
#   CONC=2 setsid bash scripts/mtl_improvement/ba3_catpriv_multiseed.sh > /tmp/ba3ms/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; EPOCHS=50; CONC=${CONC:-2}; SEEDS=(1 7 100)
LOGDIR=/tmp/ba3ms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/ba3_catpriv_ms_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] BA3MS $*"; }
DT="--reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
CT="--cat-head-param raw_embed_dim=64 --cat-head-param fusion_mode=aux --cat-head-param freeze_alpha=True --cat-head-param alpha_init=0.0"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
  --model mtlnet_crossattn_dualtower_catpriv \
  --cat-head next_stan_flow_dualtower $CT --reg-head next_stan_flow_dualtower $DT \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"
run(){ local sd=$1; local key="catpriv|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/catpriv_s${sd}.log"; say "start $key"
  $PY scripts/train.py $COMMON --seed "$sd" > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "catpriv" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key"; fi
}
say "config: CONC=$CONC FL seeds='${SEEDS[*]}' (both-private dual-tower; seed0 reused)"
for sd in "${SEEDS[@]}"; do
  run "$sd" & while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
