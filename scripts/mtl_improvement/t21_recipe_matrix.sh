#!/bin/bash
# T2.1 recipe×state matrix completion + CA/TX validation (user-approved 2026-06-04).
# Baseline head (mtlnet_crossattn + next_getnext_hard), prior-ON, static_weight cat0.75,
# KD-OFF, per-head LR, seed42, 5f x 50ep. PID-safe rundir capture.
#
# Decomposes the onecycle small-state win (is it the aggressive schedule or the no-alt-opt?):
#   v14 cells:   B9@AL, B9@AZ (the "reverse"), H3-alt@FL (weak recipe at FL).
#                (onecycle@AL/AZ/FL already = base_a 56.45/44.26/61.87; H3-alt@AL/AZ + B9@FL = landed.)
#   CA/TX cells: B9 + onecycle @ CA,TX on the CANONICAL substrate (v14 not built at CA/TX; the recipe
#                effect is substrate-agnostic — documented). Confirms the small↔large recipe boundary.
#
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/t21_recipe_matrix.sh > /tmp/t21_rmatrix/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
CONC=${CONC:-2}; EPOCHS=50
LOGDIR=/tmp/t21_rmatrix; mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_rmatrix_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] RMATRIX $*"; }

recipe(){ case "$1" in
  H3ALT)    echo "--scheduler constant --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3" ;;
  B9)       echo "--scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5" ;;
  ONECYCLE) echo "--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3" ;;
esac; }

COMMON="--task mtl --task-set check2hgi_next_region --seed 42 \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn --reg-head next_getnext_hard \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

# tag|recipe|state|engine
ARMS="b9|B9|alabama|$V14
b9|B9|arizona|$V14
h3alt|H3ALT|florida|$V14
b9|B9|california|check2hgi
b9|B9|texas|check2hgi
onecyc|ONECYCLE|california|check2hgi
onecyc|ONECYCLE|texas|check2hgi"

run_arm(){
  local spec=$1 tag rec state engine
  IFS='|' read -r tag rec state engine <<< "$spec"
  local key="${tag}|${state}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  local r; r=$(recipe "$rec")
  local log="$LOGDIR/${tag}_${state}.log"
  say "start $key (recipe=$rec engine=$engine)"
  $PY scripts/train.py $COMMON --engine "$engine" --state "$state" $r \
      --per-fold-transition-dir "output/$engine/$state" > "$log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/$engine/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete rd='$rd'"
    printf '%s\t%s\t%s\n' "$key" "$tag" "$rd" >> "$MANIFEST"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc) — see $log"; fi
}

say "CONC=$CONC OMP=$OMP_NUM_THREADS"; nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
while IFS= read -r spec; do
  [ -z "$spec" ] && continue
  run_arm "$spec" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
done < <(printf '%s\n' "$ARMS")
wait
say "ALL DONE"
