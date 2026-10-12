#!/bin/bash
# Adds the HGI arm to the STL verification sweep (FL, next-cat + next-reg, seeds {0,1,7,100}),
# so we can directly check the embedding_eval headline: STL next-reg Acc@10 v14 0.7024 vs
# canon 0.6943 vs HGI 0.7060 (HGI keeps a −0.36pp edge), and STL next-cat v14 67.36 ≫ HGI ~34.
# Chains on the v11/v14 STL driver PID (arg 1) to avoid GPU contention. Reuses stl_manifest.tsv.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
STATE=florida; ENG=hgi; SEEDS="0 1 7 100"
LOGDIR=scripts/_v14_run/logs/stl; mkdir -p "$LOGDIR"
MAN=scripts/_v14_run/stl_manifest.tsv; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] STL-HGI $*"; }

PID=${1:-}
if [ -n "$PID" ]; then say "waiting for v11/v14 STL driver pid $PID"; while kill -0 "$PID" 2>/dev/null; do sleep 60; done; say "predecessor done"; fi

for seed in $SEEDS; do
  log="$LOGDIR/cat_${ENG}_seed${seed}.log"
  if grep -q "^cat	$ENG	$seed	" "$MAN"; then say "skip cat hgi s$seed"; else
    say "cat start hgi s$seed"
    $PY scripts/train.py --task next --state $STATE --engine $ENG --seed "$seed" \
        --epochs 50 --folds 5 --batch-size 2048 --cat-head next_gru --no-checkpoints > "$log" 2>&1 \
      && { rd=$(ls -dt results/$ENG/$STATE/next_*ep50* 2>/dev/null|head -1); printf 'cat\t%s\t%s\t%s\n' "$ENG" "$seed" "$rd" >> "$MAN"; say "cat done hgi s$seed -> $rd"; } \
      || say "cat FAIL hgi s$seed"
  fi
done
for seed in $SEEDS; do
  log="$LOGDIR/reg_${ENG}_seed${seed}.log"; tag="${ENG}_s${seed}"
  if grep -q "^reg	$ENG	$seed	" "$MAN"; then say "skip reg hgi s$seed"; else
    say "reg start hgi s$seed"
    $PY scripts/p1_region_head_ablation.py --state $STATE --heads next_stan_flow \
        --folds 5 --epochs 50 --batch-size 2048 --seed "$seed" \
        --input-type region --region-emb-source $ENG --tag "$tag" \
        --per-fold-transition-dir output/check2hgi/$STATE > "$log" 2>&1 \
      && { js="docs/results/embedding_eval/region_head_${STATE}_region_5f_50ep_${tag}.json"; printf 'reg\t%s\t%s\t%s\n' "$ENG" "$seed" "$js" >> "$MAN"; say "reg done hgi s$seed -> $js"; } \
      || say "reg FAIL hgi s$seed"
  fi
done
say "ALL DONE"
