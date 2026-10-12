#!/bin/bash
# T1.4 CAT RE-PIN (bug fix 2026-06-03): the original cat sweep used `--cat-head next_gru`,
# which is SILENTLY IGNORED on `--task next` (it only applies on the MTL track) — so the
# whole cat ceiling actually ran the DEFAULT model `next_single`, not next_gru. The real
# next_gru is ~+8pp higher (AL la05: 49.97 vs the mis-pinned 41.86). This re-pins the cat
# ceiling with the ACTUAL next_gru via `--model next_gru`, re-verifying the loss winner.
# Configs: balanced / logit-adjust tau in {0.5,1.0} / +ls / combo. AL+FL search -> AZ+GE.
#
#   Launch: setsid bash scripts/mtl_improvement/t14_cat_repin.sh <state> \
#               > /tmp/t14/catrepin_<state>.log 2>&1 < /dev/null &
set -uo pipefail
ST=${1:?state}
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
L=/tmp/t14; mkdir -p "$L"; MAN="$L/manifest_catrepin_${ST}.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] CATREPIN $ST $*"; }

run(){ # tag flags...
  local tag=$1; shift
  say "start $tag (next_gru)"
  if $PY scripts/train.py --task next --state "$ST" --engine "$V14" --model next_gru \
      --seed 42 --epochs 50 --folds 5 --batch-size 2048 "$@" --no-checkpoints \
      > "$L/catrepin_${ST}_${tag}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$ST/next_*ep50* 2>/dev/null | head -1)
    say "done $tag -> $rd"; printf 'cat\t%s\t%s\tok\n' "$tag" "$rd" >>"$MAN"
  else say "FAIL $tag"; printf 'cat\t%s\t-\tFAIL\n' "$tag" >>"$MAN"; fi
}

run g_balanced   --tail-loss balanced
run g_la05       --logit-adjust-tau 0.5
run g_la10       --logit-adjust-tau 1.0
run g_la10_ls05  --logit-adjust-tau 1.0 --cat-label-smoothing 0.05
run g_combo      --logit-adjust-tau 1.0 --focal-gamma 1.0 --cat-label-smoothing 0.05 --tail-loss balanced
say "ALL CATREPIN $ST DONE"
