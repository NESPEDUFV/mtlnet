#!/bin/bash
# STL verification sweep: replicate embedding_eval STL numbers for v11 (check2hgi) and
# v14 (check2hgi_design_k_resln_mae_l0_1) at Florida, both tasks, leak-free multi-seed {0,1,7,100}.
#   next-cat : train.py --task next  --cat-head next_gru        -> next/f1 (macro-F1)
#   next-reg : p1_region_head_ablation.py --heads next_stan_flow --input-type region
#              --region-emb-source <eng> --per-fold-transition-dir output/check2hgi/florida (seeded log_T)
# Expected (FINAL_SYNTHESIS, leak-free multi-seed FL):
#   next-cat F1: v11 ~64.6 (fresh) / 67.32 (frozen on-disk) ; v14 67.36
#   next-reg Acc@10: v11 0.6943 ; v14 0.7024 ; (HGI 0.7060)
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
STATE=florida
V11=check2hgi
V14=check2hgi_design_k_resln_mae_l0_1
SEEDS="0 1 7 100"
LOGDIR=scripts/_v14_run/logs/stl; mkdir -p "$LOGDIR"
MAN=scripts/_v14_run/stl_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] STL $*"; }

cat_run(){ # engine seed
  local eng=$1 seed=$2; local log="$LOGDIR/cat_${eng}_seed${seed}.log"
  grep -q "^cat	$eng	$seed	" "$MAN" && { say "skip cat $eng s$seed"; return 0; }
  say "cat start $eng s$seed"
  $PY scripts/train.py --task next --state $STATE --engine "$eng" --seed "$seed" \
      --epochs 50 --folds 5 --batch-size 2048 --cat-head next_gru --no-checkpoints \
      > "$log" 2>&1 || { say "cat FAIL $eng s$seed"; return 1; }
  local rd=$(ls -dt results/$eng/$STATE/next_*ep50* 2>/dev/null | head -1)
  printf 'cat\t%s\t%s\t%s\n' "$eng" "$seed" "$rd" >> "$MAN"; say "cat done $eng s$seed -> $rd"
}

reg_run(){ # engine seed
  local eng=$1 seed=$2; local log="$LOGDIR/reg_${eng}_seed${seed}.log"
  grep -q "^reg	$eng	$seed	" "$MAN" && { say "skip reg $eng s$seed"; return 0; }
  say "reg start $eng s$seed"
  local tag="${eng}_s${seed}"
  $PY scripts/p1_region_head_ablation.py --state $STATE --heads next_stan_flow \
      --folds 5 --epochs 50 --batch-size 2048 --seed "$seed" \
      --input-type region --region-emb-source "$eng" --tag "$tag" \
      --per-fold-transition-dir output/check2hgi/$STATE \
      > "$log" 2>&1 || { say "reg FAIL $eng s$seed"; return 1; }
  local js="docs/results/embedding_eval/region_head_${STATE}_region_5f_50ep_${tag}.json"
  printf 'reg\t%s\t%s\t%s\n' "$eng" "$seed" "$js" >> "$MAN"; say "reg done $eng s$seed -> $js"
}

# next-cat first (no log_T dependency), both engines, all seeds
for s in $SEEDS; do cat_run $V11 $s; done
for s in $SEEDS; do cat_run $V14 $s; done
# next-reg (seeded per-fold log_T already present in output/check2hgi/florida)
for s in $SEEDS; do reg_run $V11 $s; done
for s in $SEEDS; do reg_run $V14 $s; done
say "ALL DONE"
