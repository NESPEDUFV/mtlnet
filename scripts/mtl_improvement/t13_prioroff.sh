#!/bin/bash
# T1.3 strengthening (advisor P1) — prior-OFF re-run. Disables the α·log_T prior
# (--override-hparams freeze_alpha=True alpha_init=0.0) so reg Acc@10 reflects the
# EMBEDDING pathway alone (stan_logits), unmasked by the transition prior. Re-tests
# cfg1 (raw) vs cfg2 (+MTL next_encoder) on v14, AL/AZ/FL, 5f×50ep seed42.
# If cfg2≈cfg1 prior-OFF ⇒ the encoder genuinely isn't harmful (verdict rescued).
# If cfg2≪cfg1 prior-OFF ⇒ the prior masked encoder damage ⇒ encoder IS a factor.
#   Launch: setsid bash scripts/mtl_improvement/t13_prioroff.sh > /tmp/t13po/run.log 2>&1 < /dev/null &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42; FOLDS=5; EPOCHS=50; STATES="alabama arizona florida"
LOGDIR=/tmp/t13po; mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest.tsv"; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T13PO $*"; }

run_cfg(){ local st=$1 cfg=$2; shift 2; local extra="$*"
  local tag="t13po_${cfg}_v14_s${SEED}"; local log="$LOGDIR/${st}_${cfg}.log"
  grep -q "^${st}	${cfg}	" "$MAN" && { say "skip $st $cfg"; return 0; }
  say "start $st $cfg [$extra]"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source "$V14" \
      --folds $FOLDS --epochs $EPOCHS --batch-size 2048 --seed $SEED \
      --target region --tag "$tag" \
      --override-hparams freeze_alpha=True alpha_init=0.0 \
      --per-fold-transition-dir "output/check2hgi/$st" $extra > "$log" 2>&1 \
    || { say "FAIL $st $cfg — see $log"; return 1; }
  printf '%s\t%s\tdocs/results/P1/region_head_%s_region_%df_%dep_%s.json\n' "$st" "$cfg" "$st" "$FOLDS" "$EPOCHS" "$tag" >> "$MAN"
  say "done $st $cfg"
}
for st in $STATES; do
  run_cfg "$st" cfg1_raw    ""
  run_cfg "$st" cfg2_mtlenc "--mtl-preencoder"
done
say "ALL DONE"
