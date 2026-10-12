#!/bin/bash
# R4a — scalarization Pareto front on the FROZEN champion G. Sweep --category-weight
# (static_weight: loss=(1-cw)·L_reg + cw·L_cat) → each weight is a deployable model;
# the (cat-F1, reg-Acc@10) set traces the achievable cat↔reg trade-off. Resolves the
# C21/geom_simple selector saga (publish the front, not a point). FL seed0 first;
# falsifier = front collapses to a point (tasks decoupled = regime datum). --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=${ST:-florida}; SEED=${SEED:-0}
WEIGHTS=(0.40 0.55 0.70 0.75 0.85 0.92)
LOGDIR=/tmp/r4front; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r4_scalar_front_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R4 $*"; }

run(){ local cw=$1
  local tag="cw${cw}"; local log="$LOGDIR/${tag}_s${SEED}.log"; say "start $tag (st=$ST seed=$SEED)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$ST" --seed "$SEED" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
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
    printf '%s\t%s\t%s\t%s\n' "$tag" "$ST" "$cw" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R4 scalarization front, $ST seed$SEED, weights ${WEIGHTS[*]}, CONC=$CONC ==="
for cw in "${WEIGHTS[@]}"; do
  run "$cw" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
