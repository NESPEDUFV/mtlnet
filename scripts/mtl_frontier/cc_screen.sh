#!/bin/bash
# Conditional coupling screen (advisor's recommended direction) — cat posterior →
# reg input feature (iMTL/GETNext). Grid over the key design axis (cat→reg gradient):
#   cc_e2e    : cond_coupling=posterior, cond_detach=False (true iMTL end-to-end)
#   cc_detach : cond_coupling=posterior, cond_detach=True  (reg uses cat pred, no cat→reg grad)
# vs champion G (cond=none, KD-off; baselines reused). AL+FL seed0. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/cc; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/cc_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CC $*"; }

run(){ local tag=$1 st=$2 detach=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st cond_detach=$detach)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --reg-head-param cond_coupling=posterior --reg-head-param cond_dim=7 \
      --reg-head-param "cond_detach=$detach" \
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

say "=== conditional coupling screen, AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "cc_e2e_${st}"    "$st" False & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_detach_${st}" "$st" True  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
