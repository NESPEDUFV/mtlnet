#!/bin/bash
# C25 re-baseline — does the REAL JOINT MTL recipe recover reg to the STL ceiling
# under the unweighted-reg fix? (NOT the cat-0 isolation — the actual §0.1 recipe.)
# Real joint: mtlnet_crossattn + next_getnext_hard (reg, prior-ON) + next_gru (cat) +
# category-weight 0.75, onecycle, v14, region input, KD-OFF, seeded per-fold log_T.
# Arms per state:
#   old   = pre-C25 (class-weighted reg)  → --reg-class-weights        (the buggy baseline)
#   fix   = C25 default (unweighted reg)  → (no flag; new default)     (the fix)
# Compare reg disjoint Acc@10 vs the frozen (c) STL ceilings (AL 62.88 / GE 58.45 / FL 73.31)
# + cat macro-F1 (cat stays class-weighted by default → expect ~unchanged across arms).
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/c25_rebaseline.sh <state...> > /tmp/c25/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
SEED=42; EPOCHS=50; CONC=${CONC:-2}
LOGDIR=/tmp/c25; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_rebaseline_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
STATES=("$@"); [ ${#STATES[@]} -eq 0 ] && STATES=(alabama georgia florida)
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25 $*"; }

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --seed $SEED \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --no-checkpoints"

run(){ # state arm
  local st=$1 arm=$2 key="${arm}|${st}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  # best = both heads UNWEIGHTED (the C25 validated default, no flags);
  # old  = both heads WEIGHTED (pre-C25 buggy behaviour) for the delta.
  local extra=""; [ "$arm" = old ] && extra="--reg-class-weights --cat-class-weights"
  local log="$LOGDIR/${arm}_${st}.log"
  say "start $key (extra='$extra')"
  $PY scripts/train.py $COMMON --state "$st" $extra \
      --per-fold-transition-dir "output/$V14/$st" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$arm" "$rd" >> "$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC states='${STATES[*]}' arms=old,fix recipe=real-joint-onecycle"
for st in "${STATES[@]}"; do
  for arm in best old; do
    run "$st" "$arm" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
