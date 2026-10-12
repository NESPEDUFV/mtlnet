#!/bin/bash
# Tier S Prong-A screen (STL-alone, against the T1.4-FROZEN floor — does NOT re-open (c)/(d)).
#   S.1 reg: coded reg heads vs next_stan_flow alpha=0 floor (AL 62.88). Driver = p1 (the reg-floor
#            tool). One p1 call runs all heads at their REGISTRY DEFAULT (prior-aware heads keep their
#            prior — a coarse screen; the prior is a known drag, so a prior-on head that still beats the
#            prior-OFF floor is clearly promising). Top-2-3 get a proper alpha=0 tune at promotion.
#   S.2 cat: coded encoders vs next_gru logit-adjust tau=0.5 floor (AL 41.86). Driver = train.py/next_cv.py
#            (the cat-floor tool). ALL candidates inherit logit-adjust tau=0.5 so the comparison isolates
#            the ENCODER (S.2 design rule).
# Screen at AL 5f/50ep seed42; promote top-2-3 to FL+AL+AZ + GE confirm (separate step).
#
#   Launch: setsid bash scripts/mtl_improvement/tierS_screen.sh <reg|cat> <state> \
#               > /tmp/tierS/<arm>_<state>.log 2>&1 < /dev/null &
set -uo pipefail
ARM=${1:?arm=reg|cat}; ST=${2:?state}
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
L=/tmp/tierS; mkdir -p "$L"; MAN="$L/manifest_${ARM}_${ST}.tsv"
say(){ echo "[$(date +%H:%M:%S)] TIERS $ARM/$ST $*"; }

if [ "$ARM" = reg ]; then
  : > "$MAN"
  # one p1 call, all candidate reg heads (p1 handles per-head aux / prior internally)
  HEADS="next_stan_flow next_getnext next_stan next_tgstan next_stahyper next_getnext_hard next_lstm next_transformer_relpos"
  say "start reg screen heads: $HEADS"
  $PY scripts/p1_region_head_ablation.py --state "$ST" --heads $HEADS \
      --target region --input-type region --region-emb-source "$V14" \
      --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
      --per-fold-transition-dir "output/check2hgi/$ST" \
      --tag tierS_reg_screen --no-resume > "$L/reg_${ST}_screen.log" 2>&1 \
    && { say "done reg screen"; printf 'reg\tscreen\tdocs/results/P1/region_head_%s_region_5f_50ep_tierS_reg_screen.json\tok\n' "$ST" >>"$MAN"; } \
    || say "FAIL reg screen (see $L/reg_${ST}_screen.log)"
  say "ALL REG SCREEN DONE"
elif [ "$ARM" = cat ]; then
  : > "$MAN"
  for enc in next_lstm next_temporal_cnn next_tcn_residual next_conv_attn \
             next_transformer_relpos next_transformer_optimized next_single next_hybrid; do
    say "start cat $enc (logit-adjust tau=0.5)"
    if $PY scripts/train.py --task next --state "$ST" --engine "$V14" --model "$enc" \
        --seed 42 --epochs 50 --folds 5 --batch-size 2048 --logit-adjust-tau 0.5 \
        --no-checkpoints > "$L/cat_${ST}_${enc}.log" 2>&1; then
      rd=$(ls -dt results/$V14/$ST/next_*ep50* 2>/dev/null | head -1)
      say "done cat $enc -> $rd"; printf 'cat\t%s\t%s\tok\n' "$enc" "$rd" >>"$MAN"
    else
      say "FAIL cat $enc (see $L/cat_${ST}_${enc}.log)"; printf 'cat\t%s\t-\tFAIL\n' "$enc" >>"$MAN"
    fi
  done
  say "ALL CAT SCREEN DONE"
else echo "arm must be reg|cat"; exit 2; fi
