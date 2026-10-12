#!/bin/bash
# T1.4 full per-task HP tune — the tuned-incumbent ceiling that SETS + FREEZES (c)/(d).
# Curated coordinate grid over the lit-scan-ranked axes; STL-alone on v14, frozen folds,
# seeded per-fold log_T, 5f x 50ep, seed=42. Phase 1 = AL+FL search; winner validated at
# AZ+GE afterwards by re-invoking with those states.
#
#   reg = next_stan_flow on v14 region-emb (Acc@10), driven by p1_region_head_ablation.py.
#         Baselines R0 (default, with-prior) + R1 (alpha=0, prior-off) already exist from
#         T1.3 (t13_cfg1_raw_v14 / t13po_cfg1_v14). This adds tail-loss / dropout / d_model /
#         LR on the alpha=0 branch + one tail-with-prior sanity arm. Out -> docs/results/P1/.
#   cat = next_gru on v14 check-in emb (macro-F1), driven by train.py --task next (the tool
#         that produced the T1.1 cat ceiling; p1's trainer lands ~16pp low). Loss calibration
#         (balanced / logit-adjust / focal / label-smoothing) + a couple HP points.
#         Out -> results/<v14>/<state>/next_*ep50*/ (gitignored); rundir captured to manifest.
#
# Usage:  setsid bash scripts/mtl_improvement/t14_sweep.sh <reg|cat> <state> \
#             > /tmp/t14/<arm>_<state>.log 2>&1 < /dev/null &
set -uo pipefail
ARM=${1:?arm=reg|cat}; ST=${2:?state}
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
export PYTHONPATH=src
V14=check2hgi_design_k_resln_mae_l0_1
LOGDIR=/tmp/t14; mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest_${ARM}_${ST}.tsv"
ts(){ date '+%H:%M:%S'; }; say(){ echo "[$(ts)] T14 $ARM/$ST $*"; }

reg_run(){ # tag  extra-args...
  local tag=$1; shift
  local out="docs/results/P1/region_head_${ST}_region_5f_50ep_${tag}.json"
  [ -f "$out" ] && { say "skip $tag (exists)"; printf 'reg\t%s\t%s\tdone\n' "$tag" "$out" >>"$MAN"; return 0; }
  say "start $tag"
  $PY scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
      --target region --input-type region --region-emb-source "$V14" \
      --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
      --per-fold-transition-dir "output/check2hgi/$ST" \
      "$@" --tag "$tag" --no-resume > "$LOGDIR/${ARM}_${ST}_${tag}.log" 2>&1 \
    && { say "done $tag"; printf 'reg\t%s\t%s\tok\n' "$tag" "$out" >>"$MAN"; } \
    || { say "FAIL $tag (see $LOGDIR/${ARM}_${ST}_${tag}.log)"; printf 'reg\t%s\t%s\tFAIL\n' "$tag" "$out" >>"$MAN"; }
}

cat_run(){ # tag  extra-args...
  local tag=$1; shift
  say "start $tag"
  if $PY scripts/train.py --task next --state "$ST" --engine "$V14" --model next_gru \
      --seed 42 --epochs 50 --folds 5 --batch-size 2048 \
      "$@" --no-checkpoints > "$LOGDIR/${ARM}_${ST}_${tag}.log" 2>&1; then
    local rd; rd=$(ls -dt results/$V14/$ST/next_*ep50* 2>/dev/null | head -1)
    say "done $tag -> $rd"; printf 'cat\t%s\t%s\tok\n' "$tag" "$rd" >>"$MAN"
  else
    say "FAIL $tag (see $LOGDIR/${ARM}_${ST}_${tag}.log)"; printf 'cat\t%s\t-\tFAIL\n' "$tag" >>"$MAN"
  fi
}

A0="freeze_alpha=True alpha_init=0.0"   # prior-off branch (T1.3: alpha=0 best at AL/AZ/FL)

if [ "$ARM" = reg ]; then
  : > "$MAN"
  reg_run r_a0_ldam5     --override-hparams $A0 --tail-loss ldam --ldam-max-margin 0.5
  reg_run r_a0_ldam3     --override-hparams $A0 --tail-loss ldam --ldam-max-margin 0.3
  reg_run r_a0_cb        --override-hparams $A0 --tail-loss cb   --cb-beta 0.999
  reg_run r_a0_do1       --override-hparams $A0 dropout=0.1
  reg_run r_a0_do5       --override-hparams $A0 dropout=0.5
  reg_run r_a0_dm256     --override-hparams $A0 d_model=256
  reg_run r_a0_lr1e3     --override-hparams $A0 --max-lr 1e-3
  reg_run r_a0_dm256_do1 --override-hparams $A0 d_model=256 dropout=0.1
  reg_run r_prior_ldam5  --tail-loss ldam --ldam-max-margin 0.5
  say "ALL REG DONE"
elif [ "$ARM" = cat ]; then
  : > "$MAN"
  cat_run c_balanced     --tail-loss balanced
  cat_run c_la10         --logit-adjust-tau 1.0
  cat_run c_la05         --logit-adjust-tau 0.5
  cat_run c_la10_bal     --logit-adjust-tau 1.0 --tail-loss balanced
  cat_run c_focal2_bal   --focal-gamma 2.0 --tail-loss balanced
  cat_run c_la10_ls05    --logit-adjust-tau 1.0 --cat-label-smoothing 0.05
  cat_run c_combo        --logit-adjust-tau 1.0 --focal-gamma 1.0 --cat-label-smoothing 0.05 --tail-loss balanced
  cat_run c_bal_ls05     --tail-loss balanced --cat-label-smoothing 0.05
  cat_run c_bal_lr3e3    --tail-loss balanced --max-lr 3e-3
  cat_run c_bal_lr5e3    --tail-loss balanced --max-lr 5e-3
  cat_run c_bal_do3      --tail-loss balanced --cat-head-param dropout=0.3
  say "ALL CAT DONE"
else
  echo "arm must be reg|cat"; exit 2
fi
