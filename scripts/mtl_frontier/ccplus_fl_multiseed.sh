#!/bin/bash
# R-CC+ FL multi-seed gate — any FL seed0 positive from ccplus_screen.sh, run at
# FL seeds {0,1,7,100} with a MATCHED same-batch champion G baseline per seed
# (protocol lesson #1: matched baselines, not stitched-reused). --no-checkpoints.
#
# Fill CONFIGS below with the FL positives (name + its extra reg-head-params).
# Each entry: "name|<extra --reg-head-param ...>". base (champion G) is implicit.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=florida; SEEDS=(0 1 7 100)
LOGDIR=/tmp/ccplus_flms; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/ccplus_fl_multiseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CC+MS $*"; }

# >>> FILL AFTER SCREEN <<< (name|extra reg-head-params). Example placeholders:
CP="--reg-head-param cond_coupling=posterior --reg-head-param cond_dim=7 --reg-head-param cond_inject=add"
CONFIGS=(
  "cc_e2e|$CP"
  "cc_calib|$CP --reg-head-param cond_signal=calibrated --reg-head-param cond_temp=2.0"
  "cc_argmax|$CP --reg-head-param cond_signal=argmax"
)

run(){ local tag=$1 seed=$2; shift 2
  local log="$LOGDIR/${tag}_s${seed}.log"; say "start $tag s$seed extra=[$*]"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$seed" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      "$@" \
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

say "=== R-CC+ FL multi-seed, seeds ${SEEDS[*]}, CONC=$CONC ==="
for seed in "${SEEDS[@]}"; do
  run "base" "$seed" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  for entry in "${CONFIGS[@]}"; do
    name="${entry%%|*}"; extra="${entry#*|}"
    run "$name" "$seed" $extra &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  done
done
wait; say "ALL DONE -> $MAN"
