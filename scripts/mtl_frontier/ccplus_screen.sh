#!/bin/bash
# R-CC+ screen — extend the conditional-coupling family (the one direction that
# produced real transfer). Cheap→GETNext-faithful→output-side, all vs a FRESH
# matched same-batch champion G (cond off, KD-off). AL+FL seed0. --no-checkpoints.
#
# Configs (all cond_coupling=posterior cond_dim=7 unless noted):
#   base       champion G — cond_coupling=none (matched baseline, this batch)
#   cc_e2e     inject=add  signal=softmax            (anchor — the known +0.235 FL cat)
#   cc_calib   inject=add  signal=calibrated τ=2.0   (softer/cleaner posterior)
#   cc_argmax  inject=add  signal=argmax             (discrete one-hot, GETNext form)
#   cc_topk    inject=add  signal=topk k=2           (sparse posterior mask)
#   cc_film    inject=film signal=softmax            (FiLM γ,β on the fused feature)
#   cc_concat  inject=concat_seq signal=softmax      (input-side, GETNext-faithful)
#   cc_logitp  inject=none signal=softmax + cond_logit_prior  (output-side cat→region prior)
#
# Rundir capture by python $! PID suffix (ref_concurrent_rundir_race). Gate ≥0.3
# either head; any FL seed0 positive → multi-seed FL {0,1,7,100}.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/ccplus; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/ccplus_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CC+ $*"; }

# run <tag> <state> <extra reg-head-params...>
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

# cond_coupling=posterior + cond_dim=7 prefix for every cc config
CP=(--reg-head-param cond_coupling=posterior --reg-head-param cond_dim=7)

say "=== R-CC+ screen, AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "base_${st}"      "$st" &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_e2e_${st}"    "$st" "${CP[@]}" --reg-head-param cond_inject=add &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_calib_${st}"  "$st" "${CP[@]}" --reg-head-param cond_inject=add --reg-head-param cond_signal=calibrated --reg-head-param cond_temp=2.0 &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_argmax_${st}" "$st" "${CP[@]}" --reg-head-param cond_inject=add --reg-head-param cond_signal=argmax &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_topk_${st}"   "$st" "${CP[@]}" --reg-head-param cond_inject=add --reg-head-param cond_signal=topk --reg-head-param cond_topk=2 &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_film_${st}"   "$st" "${CP[@]}" --reg-head-param cond_inject=film &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_concat_${st}" "$st" "${CP[@]}" --reg-head-param cond_inject=concat_seq &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "cc_logitp_${st}" "$st" "${CP[@]}" --reg-head-param cond_inject=none --reg-head-param cond_logit_prior=True &  while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
