#!/bin/bash
# P0 FIX (HANDOFF_AUDIT 2026-06-12): the FL cat-transfer rows _s1/_s7/_s100 in
# cat_transfer_manifest.tsv ALL pointed to ONE rundir (20260610_031405) — only one
# extra FL run ever happened. Re-run FL catonly_cw1.0 at seeds {1,7,100} CLEANLY,
# combine with the clean seed0 base (20260608_185334) for the true 4-seed FL mean.
# Recipe = cat_transfer_ablation.sh verbatim, only --seed varies.
# PID-suffix rundir capture (ref_concurrent_rundir_race) — NOT `ls -dt|head -1`.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1; EPOCHS=50; CONC=${CONC:-2}
ST=florida
LOGDIR=/tmp/catabl_reseed; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/cat_transfer_reseed_manifest.tsv; : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] RESEED $*"; }
run(){ local sd=$1; local key="catonly_cw1.0_s${sd}|${ST}"
  local log="$LOGDIR/s${sd}.log"; say "start seed=$sd (cw=1.0, reg OFF)"
  $PY scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$V14" \
      --state "$ST" --seed "$sd" --epochs "$EPOCHS" --folds 5 --batch-size 2048 \
      --no-reg-class-weights --no-cat-class-weights \
      --mtl-loss static_weight --category-weight 1.0 \
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
    [ -z "$rd" ] && { say "WARN no PID-suffixed rundir for $pid"; rd="UNKNOWN_pid${pid}"; }
    printf '%s\tcatonly\t%s\n' "$key" "$rd" >>"$MAN"; say "done seed=$sd -> $rd"
  else say "FAIL seed=$sd (see $log)"; fi
}
say "=== FL cat-transfer RE-SEED {1,7,100}, cw=1.0 reg OFF, CONC=$CONC ==="
for sd in 1 7 100; do
  run "$sd" & while [ "$(jobs -rp|wc -l)" -ge "$CONC" ]; do sleep 8; done
done
wait; say "ALL DONE -> $MAN"
