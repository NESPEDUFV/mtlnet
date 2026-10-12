#!/bin/bash
# R5 FL multi-seed — any FL seed0 positive vs MATCHED same-batch GLOBAL log_T-KD W=0.2
# (gate=none) baseline, FL seeds {0,1,7,100}. Fill CONFIGS with the FL positives
# (name|gate). base (gate=none) is implicit. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=florida; SEEDS=(0 1 7 100)
LOGDIR=/tmp/r5flms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r5_fl_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R5MS $*"; }

# >>> FILL AFTER SEED0 SCREEN <<< (name|gate)
CONFIGS=(
  "covmax|coverage_max"
  "coventr|coverage_entropy"
)

run(){ local tag=$1 seed=$2 gate=$3
  local log="$LOGDIR/${tag}_s${seed}.log"; say "start $tag s$seed gate=$gate"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$seed" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-gate "$gate" \
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

say "=== R5 FL multi-seed, seeds ${SEEDS[*]}, CONC=$CONC ==="
for seed in "${SEEDS[@]}"; do
  run "base" "$seed" none &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  for entry in "${CONFIGS[@]}"; do
    name="${entry%%|*}"; gate="${entry#*|}"
    run "$name" "$seed" "$gate" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  done
done
wait; say "ALL DONE -> $MAN"
