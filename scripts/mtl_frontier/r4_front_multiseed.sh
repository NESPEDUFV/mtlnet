#!/bin/bash
# R4 weight-front robustness — multi-seed the two off-champion core weights {0.55,0.85}
# at seeds {1,7,100} (seed0 already in r4_scalar_front_manifest). cw=0.75 (champion G)
# reuses the deterministic ccplus base rows {0,1,7,100}. Gives the near-corner verdict
# 4-seed error bars without re-running the champion. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=florida; SEEDS=(1 7 100); WEIGHTS=(0.55 0.85)
LOGDIR=/tmp/r4ms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r4_front_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R4MS $*"; }

run(){ local cw=$1 seed=$2
  local tag="cw${cw}"; local log="$LOGDIR/${tag}_s${seed}.log"; say "start $tag s$seed"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$seed" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight "$cw" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$ST" "$seed" "$rd" >>"$MAN"; say "done $tag s$seed -> $rd"
  else say "FAIL $tag s$seed (see $log)"; fi
}

say "=== R4 weight-front multi-seed, weights ${WEIGHTS[*]} × seeds ${SEEDS[*]}, CONC=$CONC ==="
for cw in "${WEIGHTS[@]}"; do
  for seed in "${SEEDS[@]}"; do
    run "$cw" "$seed" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  done
done
wait; say "ALL DONE -> $MAN"
