#!/bin/bash
# Advisor HIGH-EV action: a FAIR per-arch tune of next_stan (STAN spatio-temporal attention
# backbone) AS THE CAT HEAD — the one arch family the S.2 cat screen excluded. Our frozen cat
# ceiling is a plain attention-free GRU (49.97 AL); STAN-attention is what wins the reg task.
# The original screen ran challengers at registry defaults with one LR (violating hard-rule 7's
# per-arch LR mini-sweep). This runs the dominant axes (LR x d_model) the screen skipped.
# All with logit-adjust τ=0.5 (the frozen cat-loss recipe) so the comparison isolates the encoder.
#   Floor to beat: next_gru τ=0.5 = AL 49.97 (≥0.5pp = a real cat-encoder win).
#
#   Launch: setsid bash scripts/mtl_improvement/stan_for_cat.sh <state> \
#               > /tmp/sfc/<state>.log 2>&1 < /dev/null &
set -uo pipefail
ST=${1:?state}
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
L=/tmp/sfc; mkdir -p "$L"; MAN="$L/manifest_${ST}.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] SFC $ST $*"; }

run(){ # tag  extra-args...
  local tag=$1; shift
  say "start $tag"
  if $PY scripts/train.py --task next --state "$ST" --engine "$V14" --model next_stan \
      --seed 42 --epochs 50 --folds 5 --batch-size 2048 --logit-adjust-tau 0.5 \
      "$@" --no-checkpoints > "$L/${ST}_${tag}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$ST/next_*ep50* 2>/dev/null | head -1)
    say "done $tag -> $rd"; printf 'stan_cat\t%s\t%s\tok\n' "$tag" "$rd" >>"$MAN"
  else say "FAIL $tag (see $L/${ST}_${tag}.log)"; printf 'stan_cat\t%s\t-\tFAIL\n' "$tag" >>"$MAN"; fi
}

# d_model=128 across the LR axis (default_next max_lr=1e-2)
run d128_lr1e2 --model-param d_model=128                          # default LR
run d128_lr3e3 --model-param d_model=128 --max-lr 3e-3
run d128_lr1e3 --model-param d_model=128 --max-lr 1e-3
# d_model=256 across the LR axis (more capacity for attention)
run d256_lr1e2 --model-param d_model=256
run d256_lr3e3 --model-param d_model=256 --max-lr 3e-3
run d256_lr1e3 --model-param d_model=256 --max-lr 1e-3
say "ALL SFC $ST DONE"
