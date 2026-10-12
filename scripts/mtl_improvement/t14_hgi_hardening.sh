#!/bin/bash
# T1.4 (d)-arm hardening probe. The reg winner is alpha=0 (prior-off) on v14 — the
# log_T prior is a net drag once the v14 embeddings are strong (T1.3 side-finding).
# The composite ceiling (d)'s reg arm is STL-HGI-reg; the hardening footnote requires
# applying the same head-level tune to it OR declaring it un-tuned by design. This runs
# STL-HGI-reg with alpha=0 at all 4 states and compares to the prior-on (d) reg values
# (T1.2: AL 63.05 / AZ 53.50 / GE 56.50 / FL 70.62). Apply per-state whichever is higher.
#
#   Launch: setsid bash scripts/mtl_improvement/t14_hgi_hardening.sh \
#               > /tmp/t14/hgi_harden.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; A0="freeze_alpha=True alpha_init=0.0"
L=/tmp/t14; mkdir -p "$L"; MAN="$L/manifest_hgi_harden.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] HGIHARDEN $*"; }

for st in alabama arizona georgia florida; do
  tag="${st:0:2}_stlreg_hgi_a0"
  out="docs/results/P1/region_head_${st}_region_5f_50ep_${tag}.json"
  [ -f "$out" ] && { say "skip $st (exists)"; printf '%s\t%s\tdone\n' "$st" "$out" >>"$MAN"; continue; }
  say "start $st (HGI reg alpha=0)"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --target region --input-type region --region-emb-source hgi \
    --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
    --per-fold-transition-dir "output/check2hgi/$st" \
    --override-hparams $A0 --tag "$tag" --no-resume > "$L/hgi_harden_${st}.log" 2>&1 \
    && { say "done $st"; printf '%s\t%s\tok\n' "$st" "$out" >>"$MAN"; } \
    || { say "FAIL $st"; printf '%s\t-\tFAIL\n' "$st" >>"$MAN"; }
done
say "ALL HGI HARDEN DONE"
