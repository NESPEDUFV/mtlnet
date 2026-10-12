#!/bin/bash
# FU2 RE-RUN (2026-06-17 audit fix) — aux_gated had shared_stan=None (head.py:208 omitted
# "aux_gated"); now fixed so the shared pathway is actually consumed. Re-run the FU2
# aux_gated arm (AL+FL seed0) with the fixed code, identical recipe to followup_screens.sh.
# Comparand (champion G fusion=aux, KD-off) is reused from r2_aftb_manifest (deterministic).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/fu2; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/fu2_rerun_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] FU2fix $*"; }

run(){ local tag=$1 st=$2
  local log="$LOGDIR/${tag}.log"; say "start $tag (st=$st, aux_gated FIXED)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --reg-head-param fusion_mode=aux_gated \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t0\t%s\n' "$tag" "$st" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}
say "=== FU2 aux_gated re-run (fixed), AL+FL seed0, CONC=$CONC ==="
run i2_auxgated_alabama_s0 alabama & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run i2_auxgated_florida_s0 florida & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
