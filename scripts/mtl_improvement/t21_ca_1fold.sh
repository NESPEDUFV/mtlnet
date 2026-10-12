#!/bin/bash
# Fast directional CA read (user-requested): B9 vs onecycle @ CA, --folds 1
# (→ n_splits=2, runs fold 1), seed42, 50ep, canonical substrate, leak-free
# (2-fold seeded log_T). Serial (CONC=1) — CA is ~39GB/run. PID-safe capture.
# NOTE: 1-fold n_splits=2 is NOT directly comparable to the 5-fold matrix cells
# (different train/val sizes); it is a DIRECTIONAL B9-vs-onecycle Δ at the largest state.
#   Launch: setsid bash scripts/mtl_improvement/t21_ca_1fold.sh > /tmp/t21_ca1f/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
LOGDIR=/tmp/t21_ca1f; mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_ca1f_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=32 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] CA1F $*"; }

COMMON="--task mtl --task-set check2hgi_next_region --engine check2hgi --state california --seed 42 \
  --epochs 50 --folds 1 --batch-size 2048 \
  --model mtlnet_crossattn --reg-head next_getnext_hard \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints \
  --per-fold-transition-dir output/check2hgi/california"

run(){
  local tag=$1; shift; local rec="$*"
  grep -qF "$tag	" "$MANIFEST" && { say "skip $tag"; return 0; }
  say "start $tag ($rec)"
  $PY scripts/train.py $COMMON $rec > "$LOGDIR/${tag}.log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/check2hgi/california/mtlnet_*ep50_*_${pid} 2>/dev/null | head -1)
    printf '%s\t%s\t%s\n' "$tag" "$tag" "$rd" >> "$MANIFEST"; say "done $tag -> $rd"
  else say "FAIL $tag (rc=$rc)"; fi
}

say "start (CONC=1 serial)"
run onecyc_ca "--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
run b9_ca "--scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5"
say "ALL DONE"
