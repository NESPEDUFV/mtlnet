#!/bin/bash
# R9 — BayesAgg-MTL optimizer close-out. Re-run the existing `bayesagg_mtl` loss at the
# CHAMPION recipe (not the registry defaults that produced the undiagnosed 19-arm crater,
# AL cat 37.75) vs a matched champion G (static_weight 0.75). Diagnoses whether the crater
# is a defaults artifact or an impl pathology. NOTE: the repo bayesagg_mtl weights by
# gradient MAGNITUDE variance (Kendall-style), NOT the ICML'24 posterior gradient-direction
# uncertainty — so this tests the magnitude-variance approximation; the faithful port is
# unbuilt (expected null by the cos≈0 / 19-arm / Mueller regime). AL+FL seed0. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r9; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r9_screen_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R9 $*"; }

# run <tag> <state> <loss-args...>
run(){ local tag=$1 st=$2; shift 2
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st) loss=[$*]"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      "$@" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\n' "$tag" "$st" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R9 BayesAgg-MTL champion-recipe screen, AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "base_${st}"     "$st" --mtl-loss static_weight --category-weight 0.75 &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "bayesagg_${st}" "$st" --mtl-loss bayesagg_mtl                          &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
