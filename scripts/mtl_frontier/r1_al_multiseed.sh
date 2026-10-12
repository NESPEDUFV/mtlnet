#!/bin/bash
# R1 AL multi-seed confirm — base (G+log_T-KD) vs R1 (+log_C-KD 0.2) at seeds {1,7,100}.
# seed0 already in r1_screen_manifest.tsv. PID-suffix capture; --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}; ST=alabama
LOGDIR=/tmp/r1_alms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r1_al_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R1ALMS $*"; }

run(){ local tag=$1 sd=$2 wc=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (seed=$sd log_c=$wc)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-tau 1.0 \
      --log-c-kd-weight "$wc" --log-c-kd-tau 1.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$ST" "$sd" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R1 AL multi-seed {1,7,100}, base vs R1, CONC=$CONC ==="
for sd in 1 7 100; do
  run base_s${sd} $sd 0.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run r1_s${sd}   $sd 0.2 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
