#!/bin/bash
# O2 + O3 (audit AUDIT_TIER1_TIERS_2026-06-03 §6) — multi-seed cat macro-F1.
#
# O2 (closes the Tier-S "failed to show a win" crack): next_lstm + next_single cat at the
#     two states they nominally WIN single-seed (GE: lstm +0.51 / single +1.45; AZ: lstm +0.48),
#     multi-seed {0,1,7,100}. Floor = frozen (c)-cat next_gru (AZ 51.01 / GE 58.12).
#     >=0.5pp multi-seed mean over the floor at >=2 bands -> real T5.2 candidate (does NOT
#     re-open the frozen (c)).
# O3 (resolves the FL ceiling-below-MTL inversion): next_gru cat at FL, multi-seed {0,1,7,100}.
#     (c)-cat FL = 69.97 (seed42) sits 0.29pp BELOW the MTL diagnostic-best 70.26 — confirm
#     it's a single-seed/metric confound, not a bug recurrence (arch already = NextHeadGRU).
#
# All via the cat-floor tool (train.py --task next --model X --logit-adjust-tau 0.5), the SAME
# harness that pinned the frozen (c)-cat ceiling. cat macro-F1 = full_summary['next']['f1']['mean'].
#
#   Launch: setsid bash scripts/mtl_improvement/o2o3_multiseed_cat.sh <o2|o3> \
#               > /tmp/o2o3/<arm>.log 2>&1 < /dev/null &
set -uo pipefail
ARM=${1:?arm=o2|o3}
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src PYTHONUNBUFFERED=1
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
SEEDS="0 1 7 100"
L=/tmp/o2o3; mkdir -p "$L"; MAN="$L/manifest_${ARM}.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] $ARM $*"; }

run(){ # head state seed
  local h=$1 st=$2 sd=$3
  say "start $h/$st/seed$sd"
  if $PY scripts/train.py --task next --state "$st" --engine "$V14" --model "$h" \
      --seed "$sd" --epochs 50 --folds 5 --batch-size 2048 --logit-adjust-tau 0.5 \
      --no-checkpoints > "$L/${ARM}_${h}_${st}_s${sd}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$st/next_*ep50* 2>/dev/null | head -1)
    printf '%s\t%s\t%s\t%s\tok\n' "$h" "$st" "$sd" "$rd" >>"$MAN"
    say "done $h/$st/seed$sd -> $rd"
  else
    printf '%s\t%s\t%s\t-\tFAIL\n' "$h" "$st" "$sd" >>"$MAN"
    say "FAIL $h/$st/seed$sd (see $L/${ARM}_${h}_${st}_s${sd}.log)"
  fi
}

if [ "$ARM" = o2 ]; then
  for st in arizona georgia; do
    for h in next_lstm next_single; do
      for sd in $SEEDS; do run "$h" "$st" "$sd"; done
    done
  done
elif [ "$ARM" = o3 ]; then
  for sd in $SEEDS; do run next_gru florida "$sd"; done
else echo "arm must be o2|o3"; exit 2; fi
say "ALL $ARM DONE"
