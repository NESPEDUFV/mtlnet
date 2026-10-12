#!/bin/bash
# T2V.2/T2V.3 support runs (FL, seed 0): (1) g_ckpt = champion G WITH checkpoints (for the
# T2V.3 independent re-eval); (2) aux_prioron = same arch with the α·log_T prior ON (the clean
# prior-ON comparand for the T2V.2 tail/macro check — does prior-OFF win the head at the tail's
# expense?). Both v14, FL, unweighted onecycle. PID-suffix capture.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/t2v23_priorcheck.sh > /tmp/t2v23/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/t2v23; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/t2v23_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T2V23 $*"; }

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --state $ST --seed $SD \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --per-fold-transition-dir output/$V14/$ST"

run(){ local tag=$1 extra=$2 ckpt=$3; local key="${tag}|s${SD}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}.log"; say "start $key (ckpt=$ckpt)"
  $PY scripts/train.py $COMMON $extra $ckpt > "$log" 2>&1 &
  local pid=$!; wait "$pid"
  if [ $? -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key"; fi
}

# g_ckpt: prior-OFF (the champion) WITH checkpoints (omit --no-checkpoints)
run g_ckpt "--reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0" "" &
while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
# aux_prioron: prior-ON (defaults: alpha_init=0.1 freeze_alpha=False), no checkpoints needed
run aux_prioron "" "--no-checkpoints" &
wait
say "ALL DONE"
