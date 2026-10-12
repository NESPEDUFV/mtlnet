#!/bin/bash
# T2.1 mechanism probe — "is the MTL→STL reg drag multi-task competition, or the
# joint harness/optimizer itself?" Re-run two heads with cat-weight=0 (reg-only,
# the P4 frozen-cat test applied to the dual-tower) and compare to the (c) STL
# ceiling. R3 onecycle, seed42, AL+AZ, 5f x 50ep, KD-OFF, seeded per-fold log_T.
#
#   base_cat0     : mtlnet_crossattn          next_getnext_hard         prior-ON   cat0
#   dtpriv_cat0   : mtlnet_crossattn_dualtower next_stan_flow_dualtower private_only prior-OFF cat0
#
# Read: if base_cat0 ≈ (c) AND dtpriv_cat0 ≈ (c) → cat-competition is the drag.
#       if both << (c) → the joint harness/optimizer (cross-attn+wd0.05) is the wall.
#       if base_cat0 ≈ (c) but dtpriv_cat0 << (c) → the private tower is genuinely worse.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
CONC=${CONC:-4}; EPOCHS=50
LOGDIR=/tmp/t21_mech; mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_mech_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] MECH $*"; }

RECIPE="--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --seed 42 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.0 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

# tag|model|reg_head|fusion|prior
ARMS="base_cat0|mtlnet_crossattn|next_getnext_hard|-|on
dtpriv_cat0|mtlnet_crossattn_dualtower|next_stan_flow_dualtower|private_only|off"

run_arm(){
  local state=$1 spec=$2 tag model reg_head fusion prior
  IFS='|' read -r tag model reg_head fusion prior <<< "$spec"
  local key="${tag}|${state}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local hp="--reg-head $reg_head"
  if [ "$reg_head" = "next_stan_flow_dualtower" ]; then
    hp="$hp --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=${fusion}"
    [ "$prior" = "off" ] && hp="$hp --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0"
  fi
  local log="$LOGDIR/${tag}_${state}.log"
  say "start $key"
  $PY scripts/train.py $COMMON --model "$model" --state "$state" $RECIPE $hp \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete"
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >> "$MANIFEST"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc)"; fi
}

for state in alabama arizona; do
  while IFS= read -r spec; do [ -z "$spec" ] && continue
    run_arm "$state" "$spec" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done <<< "$ARMS"
done
wait; say "ALL DONE"
