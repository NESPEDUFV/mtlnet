#!/bin/bash
# onecycle @ v11 (canonical GCN, the BRACIS paper substrate) @ AL/AZ @ {0,1,7,100} —
# the paper-substrate confirmation needed to legitimately re-state §0.1 small-state (a) MTL.
# Compares vs §0.1's B9@v11 (AL reg 50.17 / AZ 40.78) + STL ceilings (61.21/53.06).
# Baseline head (mtlnet_crossattn + next_getnext_hard), prior-ON, static_weight cat0.75,
# KD-OFF, per-head LR, 5f x 50ep, seeded per-fold log_T. Small states ~3min/run.
#   Launch: CONC=4 setsid bash scripts/mtl_improvement/t21_onecyc_v11.sh > /tmp/t21_v11/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
CONC=${CONC:-4}; EPOCHS=50
LOGDIR=/tmp/t21_v11; mkdir -p "$LOGDIR"
MANIFEST=scripts/mtl_improvement/t21_v11_manifest.tsv
[ -f "$MANIFEST" ] || : > "$MANIFEST"
export OMP_NUM_THREADS=$((32 / CONC))
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] V11ONE $*"; }

RECIPE="--scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3"
COMMON="--task mtl --task-set check2hgi_next_region --engine check2hgi \
  --epochs $EPOCHS --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn --reg-head next_getnext_hard \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --task-a-input-type checkin --task-b-input-type region \
  --log-t-kd-weight 0.0 --no-checkpoints"

run_arm(){
  local state="$1"
  local seed="$2"
  local key="onecyc_v11|${state}|s${seed}"
  grep -qF "$key	" "$MANIFEST" && { say "skip $key"; return 0; }
  say "start $key"
  $PY scripts/train.py $COMMON --state "$state" --seed "$seed" $RECIPE \
      --per-fold-transition-dir "output/check2hgi/$state" > "$LOGDIR/${state}_s${seed}.log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ]; then
    local rd; rd=$(ls -d results/check2hgi/$state/mtlnet_*ep${EPOCHS}_*_${pid} 2>/dev/null | head -1)
    [ -f "$rd/summary/full_summary.json" ] || say "WARN $key incomplete"
    printf '%s\t%s\t%s\n' "$key" "onecyc_v11" "$rd" >> "$MANIFEST"; say "done $key -> $rd"
  else say "FAIL $key (rc=$rc)"; fi
}

say "CONC=$CONC"; nvidia-smi --query-gpu=memory.used --format=csv,noheader | sed 's/^/[gpu] /'
while read -r st sd; do
  [ -z "$st" ] && continue
  run_arm "$st" "$sd" &
  while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 3; done
done < <(for s in alabama arizona; do for d in 0 1 7 100; do echo "$s $d"; done; done)
wait
say "ALL DONE"
