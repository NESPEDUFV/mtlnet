#!/bin/bash
# T1.3 — Encoder-isolation probe (gates Tier 2). Decompose which of the §6.4 four
# suspects owns the ~75% MTL→STL reg residual, using the EXISTING F41 Exp-D machinery
# in p1_region_head_ablation.py (no new code). Three STL reg configs on the v14 substrate,
# frozen-fold paired (same seed42 split + seeded log_T), AL+AZ+FL, 5f × 50ep:
#   cfg1  raw STAN  (STL ceiling)                         : plain
#   cfg2  STAN + MTL next_encoder prepended (Linear+ReLU+LN+Drop, 64->256, 2 layers)
#         : --mtl-preencoder   (isolates suspect (i) the upstream encoder)
#   cfg3  STAN + input LayerNorm only (identity-ish control): --input-layernorm
# Gate: cfg2 << cfg1 (toward MTL floor) => encoder owns the residual, re-scope T2.1 to
# encoder-bypass; cfg2 ~= cfg1 => residual is the shared-backbone handoff => dual-tower justified.
# Run AFTER the GE build frees the GPU (builds saturate the A40 — do not collocate).
#   Launch: setsid bash scripts/mtl_improvement/t13_encoder_probe.sh > /tmp/t13/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
SEED=42; FOLDS=5; EPOCHS=50
STATES="alabama arizona florida"
LOGDIR=/tmp/t13; mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest.tsv"; [ -f "$MAN" ] || : > "$MAN"
ts(){ date '+%Y-%m-%d %H:%M:%S'; }; say(){ echo "[$(ts)] T13 $*"; }

run_cfg(){ # state cfgname extra_flags
  local st=$1 cfg=$2; shift 2; local extra="$*"
  local tag="t13_${cfg}_v14_s${SEED}"
  local log="$LOGDIR/${st}_${cfg}.log"
  grep -q "^${st}	${cfg}	" "$MAN" && { say "skip $st $cfg (done)"; return 0; }
  say "start $st $cfg [$extra]"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source "$V14" \
      --folds $FOLDS --epochs $EPOCHS --batch-size 2048 --seed $SEED \
      --target region --tag "$tag" \
      --per-fold-transition-dir "output/check2hgi/$st" $extra > "$log" 2>&1 \
    || { say "FAIL $st $cfg — see $log"; return 1; }
  local js="docs/results/embedding_eval/region_head_${st}_region_${FOLDS}f_${EPOCHS}ep_${tag}.json"
  printf '%s\t%s\t%s\n' "$st" "$cfg" "$js" >> "$MAN"
  say "done $st $cfg -> $js"
}

for st in $STATES; do
  run_cfg "$st" cfg1_raw       ""
  run_cfg "$st" cfg2_mtlenc    "--mtl-preencoder"
  run_cfg "$st" cfg3_inputln   "--input-layernorm"
done
say "ALL DONE"
