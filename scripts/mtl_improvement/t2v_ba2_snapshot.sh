#!/bin/bash
# B-A2 (CRITIQUE §8) — checkpointed G at FL with --save-task-best-snapshots, so route_task_best.py
# can independently re-score the reg_best snapshot against the held-out fold (a DIFFERENT code path
# from mtl_cv's training loop → forecloses "train.py-harness inflation"). Waits for GPU, runs seed0.
#   CONC=1 setsid bash scripts/mtl_improvement/t2v_ba2_snapshot.sh > /tmp/t2v_ba2/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50
LOGDIR=/tmp/t2v_ba2; mkdir -p "$LOGDIR"; MAN=scripts/mtl_improvement/t2v_ba2_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=16
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2VBA2 $*"; }
say "waiting for GPU to free..."; while true; do p=$(pgrep -fc 'scripts/[t]rain.py'); [ "${p:-0}" -gt 0 ] || break; sleep 60; done
say "GPU free — starting checkpointed G (snapshots)"
grep -qF "g_snap|s0	" "$MAN" && { say "already done"; exit 0; }
log="$LOGDIR/g_snap.log"
$PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --per-fold-transition-dir output/$V14/$ST \
  --save-task-best-snapshots > "$log" 2>&1
rc=$?
if [ $rc -eq 0 ]; then
  rd=$(ls -dt results/$V14/$ST/mtlnet_*ep${EPOCHS}_* 2>/dev/null | head -1)
  printf 'g_snap|s0\tg_snap\t%s\n' "$rd" >>"$MAN"; say "done -> $rd (snapshots in \$rd/task_best_snapshots)"
else say "FAIL (rc=$rc) — see $log"; fi
say "ALL DONE"
