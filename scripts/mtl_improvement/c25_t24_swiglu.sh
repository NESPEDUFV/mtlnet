#!/bin/bash
# C25 TIER-2.4 hybrid — pre-norm + SwiGLU cross-attn backbone (mtlnet_crossattn_swiglu)
# under the C25 unweighted real-joint fix. FL, multi-seed {0,1,7,100}. Same recipe as
# c25_tier2_refix.sh (onecycle, KD-OFF, unweighted, next_getnext_hard reg head). The
# ONLY change vs the base_a crossattn arm is the shared-backbone block (post-norm+GELU →
# pre-norm+SwiGLU, capacity-matched per the unit gate). Compare reg disjoint vs:
#   base_a  (mtlnet_crossattn, c25_revalidate FL) = 71.55
#   dual-tower (c25_tier2_refix)                  = 73.06  (current FL best)
#   (c) STL ceiling                               = 73.31
# Self-sequences behind the running T2.3 MoE driver: polls until no train.py proc remains,
# then runs. Launch:  setsid bash scripts/mtl_improvement/c25_t24_swiglu.sh > /tmp/c25t24/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
EPOCHS=50; CONC=${CONC:-2}; SEEDS=(0 1 7 100); ST=${ST:-florida}
LOGDIR=/tmp/c25t24; mkdir -p "$LOGDIR"
MAN=scripts/mtl_improvement/c25_t24_swiglu_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] C25T24 $*"; }

# --- wait for the GPU to free (the T2.3 MoE driver finishes first) ---
say "waiting for GPU to free (T2.3 MoE driver to finish)..."
# bracket pattern avoids self-match; pgrep -c always prints a count (0 when none)
# — do NOT append `|| echo 0` (it double-emits "0\n0" and breaks the integer test).
while true; do p=$(pgrep -fc 'scripts/[t]rain.py'); [ "${p:-0}" -gt 0 ] || break; sleep 60; done
say "GPU free — starting SwiGLU sweep"
export OMP_NUM_THREADS=$((32 / CONC))

COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"

run(){ # seed
  local sd=$1 key="swiglu|s${sd}"
  grep -qF "$key	" "$MAN" && { say "skip $key"; return 0; }
  local log="$LOGDIR/swiglu_s${sd}.log"; say "start $key"
  $PY scripts/train.py $COMMON --state "$ST" --seed "$sd" \
      --model mtlnet_crossattn_swiglu > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$ST/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$key" "swiglu" "$rd" >>"$MAN"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "config: CONC=$CONC state=$ST seeds='${SEEDS[*]}' model=mtlnet_crossattn_swiglu unweighted"
for sd in "${SEEDS[@]}"; do
  run "$sd" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
