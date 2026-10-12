#!/bin/bash
# R5 fix — re-run the two coventr (coverage_entropy) configs that hit the _math
# UnboundLocalError on the first screen pass. APPENDS to r5_screen_manifest.tsv
# (base/covmax rows are valid — covmax doesn't use _math). AL+FL seed0. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r5; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r5_screen_manifest.tsv   # APPEND
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R5fix $*"; }

run(){ local tag=$1 st=$2 gate=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st gate=$gate)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-gate "$gate" \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\t%s\n' "$tag" "$st" "$gate" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== R5 coventr fix, AL+FL seed0, CONC=$CONC ==="
run "coventr_alabama" alabama coverage_entropy &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run "coventr_florida" florida coverage_entropy &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
