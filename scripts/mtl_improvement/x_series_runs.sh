#!/bin/bash
# X-series GPU runs (HANDOFF_AUDIT 2026-06-12), all G recipe, seed0, post-aux-gate-fix.
#   A: FL G KD-off, WITH checkpoints (X2 G-unchanged baseline + X1 roll-probe ckpt + X4 fp16)
#   B: FL G KD-off, MTL_DISABLE_AMP_EVAL=1 (X4 fp32 eval; same weights as A by determinism)
#   C: FL G + log_T-KD 0.2  (X2 real KD-on-G test, FL)
#   D: AL G + log_T-KD 0.2  (X2 real KD-on-G test, AL)
# KD-off AL baseline reuses the R0 seed0 AL G rundir. PID-suffix rundir capture.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/xseries; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/x_series_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] XRUN $*"; }

# args: tag state kd_weight extra_env extra_flags
run(){ local tag=$1 st=$2 kd=$3 env=$4 extra=$5
  local log="$LOGDIR/${tag}.log"; say "start $tag (state=$st kd=$kd env='$env' extra='$extra')"
  env $env $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --model mtlnet_crossattn_dualtower \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --log-t-kd-weight "$kd" \
      --per-fold-transition-dir "output/$V14/$st" $extra > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -z "$rd" ] && rd="UNKNOWN_pid${pid}"
    printf '%s\t%s\t%s\n' "$tag" "$st" "$rd" >>"$MAN"; say "done $tag -> $rd"
  else say "FAIL $tag (see $log)"; fi
}

say "=== X-series runs (G seed0, post-fix), CONC=$CONC ==="
# A: FL KD-off baseline (X2 G-unchanged ref + X4 fp16 ref + X1 roll-probe aligned ref)
run A_fl_kdoff_ckpt   florida 0.0 ""                         "--no-checkpoints" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# C: FL KD-on 0.2
run C_fl_kd02         florida 0.2 ""                         "--no-checkpoints" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# B: FL KD-off fp32 eval
run B_fl_kdoff_fp32   florida 0.0 "MTL_DISABLE_AMP_EVAL=1"   "--no-checkpoints" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# D: AL KD-on 0.2
run D_al_kd02         alabama 0.2 ""                         "--no-checkpoints" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
# E: FL KD-off, X1 roll probe (task-b stream rolled by 1 at eval); compare cat-F1 vs A
run E_fl_rollprobe    florida 0.0 "MTL_ROLL_TASKB_EVAL=1"    "--no-checkpoints" \
  & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
wait; say "ALL DONE -> $MAN"
