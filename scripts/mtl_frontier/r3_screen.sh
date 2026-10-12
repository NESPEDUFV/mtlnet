#!/bin/bash
# R3 (mtl_frontier) — CrossDistil: the genuinely-new parts beyond R1's cat→reg co-loc KD.
# Baseline = G + log_T-KD 0.2 (REUSED from the R1 screen: base_alabama/base_florida).
# Configs (vs baseline):
#   r3_fwd_ec : fwd cat→reg log_C-KD 0.2 + warmup15 + ec0.3  (does CrossDistil rescue R1?)
#   r3_rev    : reverse reg→cat cat-KD 0.2 + warmup15 + ec0.3 (genuinely new direction)
#   r3_both   : both arms
# AL+FL seed0. PID-suffix capture; --no-checkpoints.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/r3_screen; mkdir -p "$LOGDIR"
MAN=scripts/mtl_frontier/r3_screen_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] R3 $*"; }

# args: tag state log_c_w cat_kd_w
run(){ local tag=$1 st=$2 lcw=$3 ckw=$4
  local log="$LOGDIR/${tag}.log"; say "start $tag (state=$st log_c=$lcw cat_kd=$ckw)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
      --engine "$V14" --state "$st" --seed 0 --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region \
      --log-t-kd-weight 0.2 --log-t-kd-tau 1.0 \
      --log-c-kd-weight "$lcw" --cat-kd-weight "$ckw" \
      --log-c-kd-warmup-epochs 15 --log-c-kd-ec-lambda 0.3 \
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

say "=== R3 screen (CrossDistil) vs G+log_T-KD, AL+FL seed0, CONC=$CONC ==="
for st in alabama florida; do
  run "r3_fwd_ec_${st}" "$st" 0.2 0.0 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "r3_rev_${st}"    "$st" 0.0 0.2 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
  run "r3_both_${st}"   "$st" 0.2 0.2 & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
