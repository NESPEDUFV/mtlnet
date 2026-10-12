#!/bin/bash
# R1 (mtl_frontier) screen — log_C co-location KD INCREMENTAL over G + log_T-KD.
#   baseline = champion G WITH log_T-KD 0.2          (log_c OFF)
#   R1       = baseline + log_C-KD 0.2               (the lever)
# AL+FL seed0 (cheap discriminator + scale-conditional check). PID-suffix rundir
# capture (ref_concurrent_rundir_race). --no-checkpoints (memory: always for sweeps).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r1_screen; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r1_screen_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R1SCREEN $*"; }

# args: tag state log_c_weight
run(){ local tag=$1 st=$2 wc=$3
  local log="$LOGDIR/${tag}.log"; say "start $tag (state=$st log_c=$wc)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-tau 1.0 \
      --log-c-kd-weight "$wc" --log-c-kd-tau 1.0 \
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

say "=== R1 screen: G+log_T-KD (base) vs +log_C-KD 0.2 (R1), AL+FL seed0, CONC=$CONC ==="
run base_alabama  alabama 0.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run r1_alabama    alabama 0.2 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run base_florida  florida 0.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
run r1_florida    florida 0.2 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
