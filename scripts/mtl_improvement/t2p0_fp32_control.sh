#!/bin/bash
# T2P.0-CONTROL — fp32 re-run of the EXACT T2P.0 cell (advisor 2026-06-04).
# Isolates the fp16-autocast-no-GradScaler harness confound: the CUDA MTL trainer
# (mtl_cv.py) runs fp16 autocast with NO GradScaler; the p1-STL (c) ceiling runs
# fp32. So part of the T2P.0 reg gap vs (c) may be precision, not joint-loop poison.
# MTL_DISABLE_AMP=1 forces the full fp32 path. Same cell otherwise.
#
# Read against T2P.0 (fp16) + (c) STL ceiling:
#   FL: T2P.0=59.53 (c)=73.31  |  AL: T2P.0=52.90 (c)=62.88
#   fp32 jumps toward (c)  → the gap was PRECISION/harness, NOT joint-loop poison
#                            → T2P.1's premise undermined; fix the trainer precision path.
#   fp32 stays ~T2P.0      → harness exonerated → T2P.1 (staged) gates cleanly.
#
# FL (decisive, σ=0.40) + AL (small-state). 5f×50ep seed42, seeded per-fold log_T.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/t2p0_fp32_control.sh > /tmp/t2p0_fp32/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42
EPOCHS=50
CONC=${CONC:-2}
LOGDIR=/tmp/t2p0_fp32
mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t2p0_fp32_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))
export MTL_DISABLE_AMP=1   # <<< the control knob: force fp32 (no autocast)

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] T2P0-FP32 $*"; }

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
  local key="t2p0_fp32_priv_off_cat0_wd01|${state}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local logt; logt=$(ls "output/$V14/$state"/region_transition_log_seed${SEED}_fold*.pt 2>/dev/null | head -1)
  local parq="output/$V14/$state/input/next_region.parquet"
  if [ -z "$logt" ] || [ "$logt" -ot "$parq" ]; then
    say "FAIL $key — stale/missing seeded log_T (logt='$logt')"; return 1
  fi
  local log="$LOGDIR/${state}.log"
  say "start $key (MTL_DISABLE_AMP=$MTL_DISABLE_AMP)"
  $PY scripts/train.py $COMMON --state "$state" $RECIPE \
      --per-fold-transition-dir "output/$V14/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$V14/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "t2p0_fp32_priv_off_cat0_wd01" "$rd" >> "$MANIFEST"
    say "done $key -> $rd"
  else
    say "FAIL $key (rc=$rc) — see $log"
  fi
}

say "config: CONC=$CONC OMP=$OMP_NUM_THREADS MTL_DISABLE_AMP=$MTL_DISABLE_AMP epochs=$EPOCHS seed=$SEED"
nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
for state in florida alabama; do
  run_state "$state" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done
wait
say "ALL DONE"
