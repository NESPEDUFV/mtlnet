#!/bin/bash
# T1.1/T1.2 ceiling completion — pin (c) STL-on-v14 + (d) composite arms at every state.
# GPU-runnable cells (HGI trains on CPU in parallel). seed42, 5f×50ep, seeded log_T.
#   STL-reg (p1_region_head_ablation, next_stan_flow, region input):
#     - GE STL-reg: v14 + canonical
#     - HGI-STL-reg (composite reg arm): AL + AZ  (GE after HGI train -> t1_ceilings_ge_hgi)
#   STL-cat (train.py --task next, next_gru): AL/AZ/GE x {v14, canonical}   (FL landed)
#   Launch: setsid bash scripts/mtl_improvement/t1_ceilings.sh > /tmp/t1ceil/run.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
LOGDIR=/tmp/t1ceil; mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest.tsv"; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T1CEIL $*"; }

reg_run(){ # state engine tag
  local st=$1 eng=$2 tag=$3; local log="$LOGDIR/reg_${tag}.log"
  grep -q "^reg	$tag	" "$MAN" && { say "skip reg $tag"; return 0; }
  say "start reg $tag ($st/$eng)"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source "$eng" \
      --folds 5 --epochs 50 --batch-size 2048 --seed 42 --target region --tag "$tag" \
      --per-fold-transition-dir "output/check2hgi/$st" > "$log" 2>&1 \
    || { say "FAIL reg $tag — see $log"; return 1; }
  printf 'reg\t%s\tdocs/results/P1/region_head_%s_region_5f_50ep_%s.json\n' "$tag" "$st" "$tag" >> "$MAN"
  say "done reg $tag"
}

cat_run(){ # state engine
  local st=$1 eng=$2; local tag="cat_${eng}_${st}"; local log="$LOGDIR/${tag}.log"
  grep -q "^cat	$tag	" "$MAN" && { say "skip $tag"; return 0; }
  say "start $tag ($st/$eng)"
  $PY scripts/train.py --task next --state "$st" --engine "$eng" --seed 42 \
      --epochs 50 --folds 5 --batch-size 2048 --cat-head next_gru --no-checkpoints > "$log" 2>&1 \
    || { say "FAIL $tag — see $log"; return 1; }
  local rd=$(ls -dt results/$eng/$st/next_*ep50* 2>/dev/null | head -1)
  printf 'cat\t%s\t%s\n' "$tag" "$rd" >> "$MAN"
  say "done $tag -> $rd"
}

# (c) GE STL-reg
reg_run georgia "$V14"       ge_stlreg_v14_s42
reg_run georgia check2hgi    ge_stlreg_canon_s42
# (d) HGI-STL-reg (composite reg arm) AL/AZ
reg_run alabama hgi          al_stlreg_hgi_s42
reg_run arizona hgi          az_stlreg_hgi_s42
# (c) STL-cat v14 + canonical at AL/AZ/GE
for st in alabama arizona georgia; do
  cat_run "$st" "$V14"
  cat_run "$st" check2hgi
done
say "ALL DONE"
