#!/bin/bash
# C25 combos PROMOTE — 4-seed confirmation of the ceiling-breaking screen winners:
#   (G) dual_aux_off       : dual-tower + aux fusion + prior-OFF  (screen s0: reg 73.56 / cat 73.12)
#   (H) dual_privonly_off  : dual-tower + private_only + prior-OFF (screen s0: reg 73.43 / cat 72.19)
# Runs seeds {1,7,100} (seed 0 reused from c25_combos_screen_manifest.tsv). FL, unweighted onecycle
# KD-OFF, same recipe. Anchors: STL ceiling 73.31, dual_gated(prior-ON) 73.06. PID-suffix capture.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_combos_promote.sh > /tmp/c25promote/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(1 7 100); ST=${ST:-florida}
LOGDIR=/tmp/c25promote; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_combos_promote_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25PRM $*"; }

OFF="--reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"

# tag | model | fusion_mode
ARMS="dual_aux_off|mtlnet_crossattn_dualtower|aux
dual_privonly_off|mtlnet_crossattn_dualtower|private_only"

run(){ local tag=$1 model=$2 fm=$3 sd=$4 key="${tag}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/${tag}_s${sd}.log"; say "start $key (model=$model fusion=$fm)"
  $PY scripts/train.py $COMMON --state "$ST" --seed "$sd" --model "$model" \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=$fm $OFF > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC state=$ST seeds='${SEEDS[*]}' (promote G+H to 4 seeds)"
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  IFS='|' read -r tag model fm <<< "$spec"
  for sd in "${SEEDS[@]}"; do
    run "$tag" "$model" "$fm" "$sd" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done <<< "$ARMS"
wait
say "ALL DONE"
