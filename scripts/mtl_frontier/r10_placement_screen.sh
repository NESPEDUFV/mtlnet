#!/bin/bash
# R10 placement measured-confirmation (user-requested A): the head/tower placements the
# re-eval flagged as regime-bounded, now MEASURED vs champion G (AL+FL seed0).
#   p4_privgrm : GRM gated read INSIDE the private reg STAN tower (--reg-head-param priv_grm=True)  ["in a tower"]
#   p5_grugrm  : GRM gated read on the cat GRU head's last hidden  (--cat-head-param grm_state=True) ["as a head"]
# Expected regime-bounded null/harmful (P4: reg at STL ceiling; P5: length-9 kills growing-memory + cat lifted).
# Champion G bit-identical when both flags off. --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r10place; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r10_placement_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R10P $*"; }

# run <tag> <state> <extra flags...>
run(){ local tag=$1 st=$2; shift 2
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st) extra=[$*]"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      "$@" \
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

say "=== R10 placement screen (P4 in-a-tower, P5 as-a-head), AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "base_${st}"     "$st" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "p4_privgrm_${st}" "$st" --reg-head-param priv_grm=True &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "p5_grugrm_${st}"  "$st" --cat-head-param grm_state=True &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
