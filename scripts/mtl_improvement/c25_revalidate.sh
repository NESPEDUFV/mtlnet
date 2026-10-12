#!/bin/bash
# C25 RE-VALIDATION sweep (multi-seed) — merges re-run #1 (regime re-test) + #2 (§0.1 re-baseline).
# v14 (check2hgi_design_k_resln_mae_l0_1) vs CANON (check2hgi, v11 GCN = the §0.1 substrate),
# MTL real-joint recipe, BOTH heads UNWEIGHTED (the C25 default), KD-OFF, onecycle, AL/GE/FL,
# seeds {0,1,7,100}. Per-fold seeded log_T already on disk for both engines × all states × all seeds.
# Settles: (1) does the v14 STL substrate gain TRANSFER to MTL under unweighted reg? [Δ=v14−canon]
#          (2) §0.1 MTL reg+cat re-baseline [the CANON arm, multi-seed]
#          (3) MTL reg vs the (c)/(d) STL ceilings; (4) CH25 composite re-derivation [from canon reg].
# Compare to: prior class-WEIGHTED regime finding (v14≈canon tie) + frozen (c) ceilings.
#   Launch: CONC=4 setsid bash scripts/mtl_improvement/c25_revalidate.sh <states...> > /tmp/c25rv/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1; CANON=check2hgi
EPOCHS=50; CONC=${CONC:-4}; SEEDS=(0 1 7 100)
LOGDIR=/tmp/c25rv; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_revalidate_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
STATES=("$@"); [ ${#STATES[@]} -eq 0 ] && STATES=(alabama georgia florida)
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25RV $*"; }

# real-joint, unweighted (new default = no class-weight flags), onecycle, KD-OFF.
COMMON="--task mtl --task-set check2hgi_next_region \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --no-checkpoints"

run(){ # engine state seed
  local eng=$1 st=$2 sd=$3 key="${eng}|${st}|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  # stale-log_T preflight
  local logt; logt=$(ls "output/$eng/$st"/region_transition_log_seed${sd}_fold*.pt 2>/dev/null | head -1)
  local parq="output/$eng/$st/input/next_region.parquet"
  if [ -z "$logt" ] || [ "$logt" -ot "$parq" ]; then
    say "FAIL $key — stale/missing seeded log_T (logt='$logt')"; printf '%s\t-\tFAIL\n' "$key" >>"$MAN"; return 1
  fi
  local log="$LOGDIR/${eng}_${st}_s${sd}.log"
  say "start $key"
  $PY scripts/train.py $COMMON --engine "$eng" --state "$st" --seed "$sd" \
      --per-fold-transition-dir "output/$eng/$st" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$eng/$st/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "$eng" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc)"; printf '%s\t-\tFAIL\n' "$key" >>"$MAN"; fi
}

say "config: CONC=$CONC states='${STATES[*]}' seeds='${SEEDS[*]}' engines=v14,canon recipe=onecycle unweighted KD-off"
for st in "${STATES[@]}"; do
  for eng in "$V14" "$CANON"; do
    for sd in "${SEEDS[@]}"; do
      run "$eng" "$st" "$sd" &
      while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
    done
  done
done
wait
say "ALL DONE"
