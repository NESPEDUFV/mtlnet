#!/bin/bash
# T1.4 phase-2: validate the AL+FL winners at AZ + GE (the middle/small band).
# Winners from the AL+FL search:
#   reg = next_stan_flow alpha=0 PLAIN (no tail-loss, default HP); d_model=256 the
#         only competitive HP tweak -> confirm both at AZ+GE.
#   cat = next_gru logit-adjustment (tau=0.5 won AL, tau=1.0 won FL) -> run both temps
#         at AZ+GE, vs the existing balanced baseline (T1.1: AZ 43.16, GE 54.02).
# Pre-existing: reg alpha=0 at AZ = 55.11 (T1.3 prior-off); reg alpha=0 at GE = MISSING.
#
#   Launch: setsid bash scripts/mtl_improvement/t14_validate_azge.sh \
#               > /tmp/t14/validate_azge.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; V14=check2hgi_design_k_resln_mae_l0_1
A0="freeze_alpha=True alpha_init=0.0"
L=/tmp/t14; mkdir -p "$L"; MAN="$L/manifest_validate.tsv"; : > "$MAN"
say(){ echo "[$(date +%H:%M:%S)] VALIDATE $*"; }

reg(){ # state tag  hp...
  local st=$1 tag=$2; shift 2
  local out="docs/results/P1/region_head_${st}_region_5f_50ep_${tag}.json"
  [ -f "$out" ] && { say "skip $st/$tag"; printf 'reg\t%s\t%s\t%s\tdone\n' "$st" "$tag" "$out" >>"$MAN"; return; }
  say "start reg $st/$tag"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --target region --input-type region --region-emb-source "$V14" \
    --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
    --per-fold-transition-dir "output/check2hgi/$st" \
    --override-hparams $A0 "$@" --tag "$tag" --no-resume > "$L/val_reg_${st}_${tag}.log" 2>&1 \
    && printf 'reg\t%s\t%s\t%s\tok\n' "$st" "$tag" "$out" >>"$MAN" \
    || printf 'reg\t%s\t%s\t-\tFAIL\n' "$st" "$tag" >>"$MAN"
}
catt(){ # state tag  flags...
  local st=$1 tag=$2; shift 2
  say "start cat $st/$tag"
  if $PY scripts/train.py --task next --state "$st" --engine "$V14" --cat-head next_gru \
      --seed 42 --epochs 50 --folds 5 --batch-size 2048 "$@" --no-checkpoints \
      > "$L/val_cat_${st}_${tag}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$st/next_*ep50* 2>/dev/null | head -1)
    printf 'cat\t%s\t%s\t%s\tok\n' "$st" "$tag" "$rd" >>"$MAN"
  else printf 'cat\t%s\t%s\t-\tFAIL\n' "$st" "$tag" >>"$MAN"; fi
}

# --- reg: alpha=0 plain at GE (missing) + d_model=256 at AZ & GE ---
reg georgia ge_r_a0          # alpha=0 plain
reg georgia ge_r_a0_dm256 d_model=256
reg arizona az_r_a0_dm256 d_model=256
# --- cat: logit-adjust both temps at AZ & GE ---
catt arizona az_c_la05 --logit-adjust-tau 0.5
catt arizona az_c_la10 --logit-adjust-tau 1.0
catt georgia ge_c_la05 --logit-adjust-tau 0.5
catt georgia ge_c_la10 --logit-adjust-tau 1.0
say "ALL VALIDATE DONE"
