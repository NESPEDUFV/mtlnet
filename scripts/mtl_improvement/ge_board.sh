#!/bin/bash
# GE board cells (T0.2/T0.3) — MTL v14 vs matched canonical at Georgia, mirroring the landed
# FL/AL/AZ board (v14_mtl_vs_canonical.md): KD-OFF, seeds {0,1,7,100}, 5f×50ep, seeded log_T.
# Recipe = H3-alt (GE n_regions=2283 ≈ small/middle band; held constant with AL/AZ to isolate
# the SCALE effect on v14-survival from the recipe). MPS-safe small-state runs.
# Run AFTER build_ge.sh completes (needs v14 next_region.parquet + staged log_T).
#   Launch: setsid bash scripts/mtl_improvement/ge_board.sh > /tmp/ge_board/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
ST=georgia; SEEDS="0 1 7 100"
LOGDIR=/tmp/ge_board; mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest.tsv"; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] GE-BOARD $*"; }

# precheck: GE essentials present
[ -f "output/$V14/$ST/input/next_region.parquet" ] || { say "FATAL v14 next_region missing — run build_ge.sh first"; exit 1; }
[ -f "output/$V14/$ST/region_transition_log_seed100_fold5.pt" ] || { say "FATAL v14 log_T missing"; exit 1; }
[ -f "output/check2hgi/$ST/region_transition_log_seed100_fold5.pt" ] || { say "FATAL canonical log_T missing"; exit 1; }

COMMON="--task mtl --task-set check2hgi_next_region \
  --epochs 50 --folds 5 --batch-size 2048 --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints --scheduler constant"   # H3-alt = constant scheduler

run_one(){ # engine logtdir tag seed
  local eng=$1 logtdir=$2 tag=$3 seed=$4
  local log="$LOGDIR/${tag}_seed${seed}.log"
  grep -q "^$tag	$seed	" "$MAN" && { say "skip $tag seed=$seed"; return 0; }
  say "start $tag seed=$seed"
  $PY scripts/train.py $COMMON --engine "$eng" --state "$ST" --seed "$seed" \
      --per-fold-transition-dir "$logtdir" > "$log" 2>&1 \
    || { say "FAIL $tag seed=$seed — see $log"; return 1; }
  local rd=$(ls -dt results/$eng/$ST/mtlnet_*ep50* 2>/dev/null | head -1)
  printf '%s\t%s\t%s\n' "$tag" "$seed" "$rd" >> "$MAN"
  say "done $tag seed=$seed -> $rd"
}

for S in $SEEDS; do run_one "$V14"       "output/$V14/$ST"       v14   "$S"; done
for S in $SEEDS; do run_one "check2hgi"  "output/check2hgi/$ST"  canon "$S"; done
say "ALL DONE"
