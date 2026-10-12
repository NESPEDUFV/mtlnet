#!/bin/bash
# C25 G-followups (seed 0 screens) — three groups, all unweighted onecycle KD-OFF base recipe:
#  (I) SPECULATIVE hybrids @ FL (user-requested completeness): mtlnet_crossattn_mult,
#      mtlnet_crossattn_xstitch — plain base_a recipe (next_getnext_hard, prior-ON). vs base_a 71.55.
#  (II) G MULTI-STATE @ AL/AZ/GE: the champion (dualtower + aux + prior-OFF) at the other states.
#  (III) G SWEEP @ FL (advisor Group 1 + fp32): category-weight, priv_dropout, log_T-KD(soft), fp32.
# Each arm = ONE full train.py invocation string (after COMMON_BASE) + optional ENV prefix.
# PID-suffix rundir capture (concurrent-race safe). Anchors: G reg 73.57 / cat 73.16; ceiling 73.31.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_gv2.sh > /tmp/c25gv2/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEED=${SEED:-0}
LOGDIR=/tmp/c25gv2; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_gv2_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25GV2 $*"; }

# recipe common to ALL arms (state/model/heads/params supplied per-arm)
COMMON_BASE="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 --seed $SEED \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --no-checkpoints"
# G reg-head param block (dual-tower + aux + prior-OFF)
GHEAD="--reg-head next_stan_flow_dualtower --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"

# tag | state | env | per-arm-args  (per-arm-args appended AFTER COMMON_BASE; later flags override)
ARMS="
mult|florida||--model mtlnet_crossattn_mult --reg-head next_getnext_hard
xstitch|florida||--model mtlnet_crossattn_xstitch --reg-head next_getnext_hard
g_AL|alabama||--model mtlnet_crossattn_dualtower $GHEAD
g_AZ|arizona||--model mtlnet_crossattn_dualtower $GHEAD
g_GE|georgia||--model mtlnet_crossattn_dualtower $GHEAD
g_catw0.50|florida||--model mtlnet_crossattn_dualtower $GHEAD --category-weight 0.50
g_catw0.65|florida||--model mtlnet_crossattn_dualtower $GHEAD --category-weight 0.65
g_catw0.85|florida||--model mtlnet_crossattn_dualtower $GHEAD --category-weight 0.85
g_pdrop0.1|florida||--model mtlnet_crossattn_dualtower $GHEAD --reg-head-param priv_dropout=0.1
g_pdrop0.2|florida||--model mtlnet_crossattn_dualtower $GHEAD --reg-head-param priv_dropout=0.2
g_kd0.1|florida||--model mtlnet_crossattn_dualtower $GHEAD --log-t-kd-weight 0.1
g_kd0.2|florida||--model mtlnet_crossattn_dualtower $GHEAD --log-t-kd-weight 0.2
g_fp32|florida|MTL_DISABLE_AMP=1|--model mtlnet_crossattn_dualtower $GHEAD
"

run(){ # tag state env args
  local tag=$1 state=$2 env=$3 args=$4 key="${tag}|s${SEED}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}_s${SEED}.log"; say "start $key (state=$state env=${env:-none})"
  # every arm gets its state's seeded per-fold log_T: base_a/KD use the α·log_T prior;
  # G (prior-OFF, α=0) loads-but-ignores it, matching G's exact 4-seed invocation.
  env $env $PY scripts/train.py $COMMON_BASE --state "$state" \
      --per-fold-transition-dir output/$V14/$state $args > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC seed=$SEED arms=$(echo "$ARMS"|grep -c '|')"
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  IFS='|' read -r tag state env args <<< "$spec"
  run "$tag" "$state" "$env" "$args" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done <<< "$ARMS"
wait
say "ALL DONE"
