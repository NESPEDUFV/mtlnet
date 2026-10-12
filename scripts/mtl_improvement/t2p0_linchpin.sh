#!/bin/bash
# T2P.0 — Tier-2P LINCHPIN (joint-loop isolation). Decides T2P.1 (staged) vs
# T2P.2 (asymmetric per-task recipe). INDEX #T2P-0, HANDOFF §0c.
#
# The cell = the ladder's killer cell `dt_priv_off` (private_only, prior-OFF =
# the (c)-STL reg topology trained jointly) + TWO changes that STL-match it:
#   --category-weight 0.0   (cat gradient zeroed; verified in static_weight:
#                            weights=[1-cw, cw]=[1,0] → 0*cat_loss, no grad into
#                            shared/cat params; in private_only reg never touches
#                            the cross-attn either → only the private tower trains)
#   --weight-decay 0.01     (STL (c) used wd=0.01; the joint recipe uses 0.05)
# So the ONLY remaining difference from STL-standalone is the JOINT LOOP itself
# (max_size_cycle mixed-batch iteration + the shared optimizer/scheduler step).
#
# Decision (vs frozen (c): AL 62.88 / AZ 55.11 / FL 73.31, and vs the wd=0.05
# cells: dtpriv_cat0 AL 52.98 / AZ 40.83 [mech], dt_priv_off AL 52.32 [ladder]):
#   recovers to ≈(c)  → collapse was wd/recipe mismatch → T2P.2 primary
#   still ≈52/41      → the joint LOOP caps reg even at identical arch+HP → T2P.1 primary
#
# AL+AZ+FL, 5f×50ep, seed42, onecycle per-head, KD-OFF, seeded per-fold log_T.
# PID-safe rundir capture (ref-concurrent-rundir-race). Idempotent manifest skip.
#   Launch: CONC=3 setsid bash scripts/mtl_improvement/t2p0_linchpin.sh > /tmp/t2p0/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42
EPOCHS=50
CONC=${CONC:-3}
LOGDIR=/tmp/t2p0
mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t2p0_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] T2P0 $*"; }

RECIPE="--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
COMMON="--task mtl --task-set check2hgi_next_region --engine $V14 --seed $SEED \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn_dualtower --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=private_only \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --mtl-loss static_weight --category-weight 0.0 --weight-decay 0.01 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

run_state(){
  local state=$1
  local key="t2p0_priv_off_cat0_wd01|${state}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  # Stale-log_T preflight (CLAUDE.md): log_T must be newer than next_region.parquet.
  local logt; logt=$(ls "output/$V14/$state"/region_transition_log_seed${SEED}_fold*.pt 2>/dev/null | head -1)
  local parq="output/$V14/$state/input/next_region.parquet"
  if [ -z "$logt" ] || [ "$logt" -ot "$parq" ]; then
    say "FAIL $key — stale/missing seeded log_T (logt='$logt'); rebuild via compute_region_transition.py --per-fold --seed $SEED --n-splits 5"
    return 1
  fi
  local log="$LOGDIR/${state}.log"
  say "start $key"
  $PY scripts/train.py $COMMON --state "$state" $RECIPE \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "t2p0_priv_off_cat0_wd01" "$rd" >> "$MANIFEST"
    say "done $key -> $rd"
  else
    say "FAIL $key (rc=$rc) — see $log"
  fi
}

say "config: CONC=$CONC OMP=$OMP_NUM_THREADS epochs=$EPOCHS seed=$SEED recipe='$RECIPE'"
nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
for state in alabama arizona florida; do
  run_state "$state" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
