#!/bin/bash
# C25 #19 — FL-B9 weighted A/B (reproduce pre-C25) run under the unweighted fix.
# Re-runs the EXACT §0.1 paper-canon B9 recipe at FL on the frozen canon (v11 GCN)
# substrate, seeds {0,1,7,100}, but WEIGHTED (reproduce pre-C25: both heads
# class-weighted via --reg-class-weights --cat-class-weights). The clean A/B control: how much does the
# unweighting fix move the headline §0.1 FL MTL numbers on the SAME recipe + SAME
# substrate the paper reports (not the v14/onecycle real-joint of c25_revalidate)?
# B9 recipe = cosine + alternating-optimizer-step + alpha-no-weight-decay + min-best-5.
# Compare reg/cat disjoint vs the WEIGHTED §0.1 FL MTL baseline.
# Self-sequences behind the T2.4 SwiGLU sweep: waits until c25_t24_swiglu_manifest.tsv
# has all 4 seeds, then runs. Launch:
#   setsid bash scripts/mtl_improvement/c25_fl_b9_continuity.sh > /tmp/c25b9w/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; ENG=check2hgi   # canon (frozen v11 GCN substrate)
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(0 1 7 100); ST=${ST:-florida}
LOGDIR=/tmp/c25b9w; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_fl_b9_weighted_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
SWIGLU_MAN=scripts/mtl_improvement/c25_t24_swiglu_manifest.tsv
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25B9W $*"; }

# --- wait for the SwiGLU sweep (and any train.py) to finish ---
say "weighted B9 A/B — GPU assumed free (post-continuity)"
export OMP_NUM_THREADS=$((32 / CONC))

# §0.1 paper-canon B9 recipe (FL/large-state), WEIGHTED (pre-C25 repro), KD-OFF for v11 §0.1.
COMMON="--task mtl --task-set check2hgi_next_region --engine $ENG \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --per-fold-transition-dir output/$ENG/$ST --no-checkpoints --reg-class-weights --cat-class-weights"

run(){ # seed
  local sd=$1 key="b9w|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/b9_s${sd}.log"; say "start $key"
  $PY scripts/train.py $COMMON --state "$ST" --seed "$sd" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$ENG/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "b9w" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC state=$ST seeds='${SEEDS[*]}' engine=$ENG (canon GCN) B9 WEIGHTED (pre-C25 A/B)"
for sd in "${SEEDS[@]}"; do
  run "$sd" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
