#!/bin/bash
# Tier-S Prong-A multi-state CONFIRM (decide if the screen warrants a head change).
# cat: next_lstm (the only encoder that tied next_gru at AL) at AZ+GE+FL, --model + logit-adjust τ=0.5,
#      vs the next_gru floor (AZ 51.01 / GE 58.12 / FL 69.97). next_single already has all-state data
#      (the old mis-pinned ceiling) and wins only at GE -> fails the multi-band gate, not re-run.
# reg: next_tgstan (the one AL tie, 62.84) at FL, vs the α=0 floor (FL 73.31) — scale check.
# Promotion gate: >=0.5pp over the floor at >=2 of {small,middle,large} bands -> T5 candidate (head change).
#
#   Launch: setsid bash scripts/mtl_improvement/tierS_confirm.sh > /tmp/tierS/confirm.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
L=/tmp/tierS; mkdir -p "$L"; MAN="$L/manifest_confirm.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] CONFIRM $*"; }

cat_lstm(){ local st=$1
  say "cat next_lstm $st"
  if $PY scripts/train.py --task next --state "$st" --engine "$V14" --model next_lstm \
      --seed 42 --epochs 50 --folds 5 --batch-size 2048 --logit-adjust-tau 0.5 --no-checkpoints \
      > "$L/confirm_cat_lstm_${st}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$st/next_*ep50* 2>/dev/null | head -1)
    printf 'cat\tnext_lstm\t%s\t%s\tok\n' "$st" "$rd" >>"$MAN"; say "done cat_lstm $st -> $rd"
  else printf 'cat\tnext_lstm\t%s\t-\tFAIL\n' "$st" >>"$MAN"; say "FAIL cat_lstm $st"; fi
}
reg_head(){ local st=$1 h=$2
  say "reg $h $st"
  local out="docs/results/P1/region_head_${st}_region_5f_50ep_confirm_${h}.json"
  if $PY scripts/p1_region_head_ablation.py --state "$st" --heads "$h" \
      --target region --input-type region --region-emb-source "$V14" \
      --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
      --per-fold-transition-dir "output/check2hgi/$st" --tag "confirm_${h}" --no-resume \
      > "$L/confirm_reg_${h}_${st}.log" 2>&1; then
    printf 'reg\t%s\t%s\t%s\tok\n' "$h" "$st" "$out" >>"$MAN"; say "done reg $h $st"
  else printf 'reg\t%s\t%s\t-\tFAIL\n' "$h" "$st" >>"$MAN"; say "FAIL reg $h $st"; fi
}

# cat next_lstm at the 3 untested states (AL already = 49.76)
for st in arizona georgia florida; do cat_lstm "$st"; done
# reg next_tgstan scale-check at FL
reg_head florida next_tgstan
say "ALL CONFIRM DONE"
