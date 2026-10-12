#!/usr/bin/env bash
# L2 (STL capacity ladder, next-cat) + L3 (MTL check2hgi_next_region) driver
# for the embedding-eval ladder. Seed 42, states FL/AL/AZ.
#
#   MODE=smoke  bash scripts/embedding_eval/run_l2l3.sh   # 1 epoch / 1 fold validate
#   MODE=full   bash scripts/embedding_eval/run_l2l3.sh   # 50 epochs / 5 folds
#
# Results land in results/<engine>/<state>/ (train.py default). Per-run logs go
# to docs/results/embedding_eval/l2l3/logs/. --no-checkpoints throughout (sweep).
set -u
cd "$(dirname "$0")/../.."
PY=.venv/bin/python
SEED=42
MODE="${MODE:-smoke}"
if [ "$MODE" = "smoke" ]; then EPOCHS=1; FOLDS=1; else EPOCHS=50; FOLDS=5; fi
LOGDIR="docs/results/embedding_eval/l2l3/logs"
mkdir -p "$LOGDIR"

STL_FAMILY="check2hgi check2hgi_design_b check2hgi_resln check2hgi_resln_design_b"
MTL_FAMILY="$STL_FAMILY"

echo "### MODE=$MODE EPOCHS=$EPOCHS FOLDS=$FOLDS SEED=$SEED"

# ---- preflight: stale log_T check (CLAUDE.md lesson) ----
echo "### preflight: log_T freshness (tlog must be newer than next_region.parquet)"
stale=0
for eng in $MTL_FAMILY; do for st in florida alabama arizona; do
  tl="output/$eng/$st/region_transition_log_seed${SEED}_fold1.pt"
  nr="output/$eng/$st/input/next_region.parquet"
  if [ -f "$tl" ] && [ -f "$nr" ]; then
    if [ "$tl" -ot "$nr" ]; then echo "  STALE: $tl older than $nr"; stale=1; fi
  else echo "  MISSING: $tl or $nr"; stale=1; fi
done; done
[ "$stale" = "0" ] && echo "  all fresh" || { echo "### ABORT: stale/missing log_T — rebuild via compute_region_transition.py"; exit 2; }

run() { # name, cmd...
  local name="$1"; shift
  echo ">>> [$name] $*"
  "$@" > "$LOGDIR/${name}.log" 2>&1 \
    && echo "    OK   $name" || echo "    FAIL $name (see $LOGDIR/${name}.log)"
}

# ---- L2: STL next-cat capacity ladder ----
# next_gru (cheap rung) for every engine; next_single (transformer rung) for the
# canonical check2hgi per state to draw one capacity curve without 2x the cost.
for st in florida alabama arizona; do
  if [ "$st" = "florida" ]; then engines="hgi $STL_FAMILY"; else engines="$STL_FAMILY"; fi
  for eng in $engines; do
    run "l2_${eng}_${st}_gru" \
      $PY scripts/train.py --task next --state "$st" --engine "$eng" --seed $SEED \
      --epochs $EPOCHS --folds $FOLDS --batch-size 2048 --model next_gru \
      --max-lr 0.01 --no-checkpoints
  done
  run "l2_check2hgi_${st}_single" \
    $PY scripts/train.py --task next --state "$st" --engine check2hgi --seed $SEED \
    --epochs $EPOCHS --folds $FOLDS --batch-size 2048 --model next_single \
    --max-lr 0.01 --no-checkpoints
done

# ---- L3: MTL check2hgi_next_region (next-cat + next-reg jointly) ----
# FL = B9 (cosine/max-lr 3e-3 + alternating + alpha-no-wd + min-best-epoch).
# AL/AZ = H3-alt (constant scheduler, drop the three B9-only flags).
for st in florida alabama arizona; do
  for eng in $MTL_FAMILY; do
    common="--task mtl --task-set check2hgi_next_region --state $st --engine $eng \
      --seed $SEED --epochs $EPOCHS --folds $FOLDS --batch-size 2048 \
      --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 \
      --cat-head next_gru --reg-head next_getnext_hard \
      --task-a-input-type checkin --task-b-input-type region \
      --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --per-fold-transition-dir output/$eng/$st --no-checkpoints"
    if [ "$st" = "florida" ]; then
      run "l3_${eng}_${st}_b9" $PY scripts/train.py $common \
        --scheduler cosine --max-lr 3e-3 \
        --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5
    else
      run "l3_${eng}_${st}_h3alt" $PY scripts/train.py $common --scheduler constant
    fi
  done
done

echo "### ALL DONE ($MODE)"
