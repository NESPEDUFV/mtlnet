#!/bin/bash
# T2P.0-INPUT-ARTIFACT control (2026-06-04) — the decisive reframing test.
# DISCOVERY: the (c) STL reg ceiling was built with p1 `--input-type region`
# (pooled region_embeddings.parquet lookup), but the MTL reg head + the dual-tower
# private tower eat `next_region.parquet` (check-in-level contextual emb) — a
# DIFFERENT embedding space (cosine ~0.11-0.20 with the pooled lookup, 0/2000 exact
# matches at AL/AZ/FL). So the design doc's premise "a private STAN on next_input IS
# exactly the STL path" is FALSE, and the whole "MTL reg 10-14pp below the STL
# ceiling" gap (incl. the T2P.0 linchpin) is CONFOUNDED by input representation.
#
# This isolates it: run the SAME next_stan_flow alpha=0 head, SAME p1 harness, SAME
# recipe, on BOTH input-types at AL+FL. Within-session paired delta = pure input
# effect.
#   region  arm  -> should reproduce (c): AL ~62.88 / FL ~73.31  (harness validation)
#   checkin arm  -> the MATCHED comparand for the MTL reg head (same next_region.parquet)
#
# If checkin << region (toward MTL reg disjoint AL 52.9 / FL 59.5):
#   -> the MTL-reg gap is the INPUT REPRESENTATION, not joint-loop poison / architecture.
#      The Tier-2 "irreducibly architectural" + Tier-2P "joint loop caps reg" headlines
#      are substantially an input-artifact confound; the real lever = give MTL reg the
#      pooled-region pathway. If checkin ~= region -> input is fine, the MTL gap is real.
#
# next_stan_flow alpha=0 default-HP (d_model=128, matches the dual-tower private tower),
# 5f x 50ep seed42, --input-type {checkin,region}, AL+FL.
#   Launch: CONC=2 setsid bash scripts/mtl_improvement/t2p0_input_artifact.sh > /tmp/t2p0_inp/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python
V14=check2hgi_design_k_resln_mae_l0_1
CONC=${CONC:-2}
LOGDIR=/tmp/t2p0_inp
mkdir -p "$LOGDIR"
MAN="$LOGDIR/manifest.tsv"; [ -f "$MAN" ] || : > "$MAN"
export OMP_NUM_THREADS=$((32 / CONC))
A0="freeze_alpha=True alpha_init=0.0"

ts(){ date '+%Y-%m-%d %H:%M:%S'; }
say(){ echo "[$(ts)] T2P0-INP $*"; }

run(){ # state input_type
  local st=$1 it=$2
  local tag="inpart_${it}"
  local out="docs/results/P1/region_head_${st}_${it}_5f_50ep_${tag}.json"
  grep -qF "${st}	${it}	" "$MAN" && { say "skip $st/$it"; return 0; }
  say "start $st/$it -> $out"
  $PY scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --target region --input-type "$it" --region-emb-source "$V14" \
    --folds 5 --epochs 50 --batch-size 2048 --seed 42 \
    --per-fold-transition-dir "output/check2hgi/$st" \
    --override-hparams $A0 --tag "$tag" --no-resume \
    > "$LOGDIR/${st}_${it}.log" 2>&1 &
  local pid=$!; wait "$pid"; local rc=$?
  if [ $rc -eq 0 ] && [ -f "$out" ]; then
    printf '%s\t%s\t%s\tok\n' "$st" "$it" "$out" >>"$MAN"; say "done $st/$it"
  else
    say "FAIL $st/$it (rc=$rc) — see $LOGDIR/${st}_${it}.log"; printf '%s\t%s\t-\tFAIL\n' "$st" "$it" >>"$MAN"
  fi
}

say "config: CONC=$CONC OMP=$OMP_NUM_THREADS — next_stan_flow a0, AL+FL, input {checkin,region}"
for st in alabama florida; do
  for it in checkin region; do
    run "$st" "$it" &
    while [ "$(jobs -rp | wc -l)" -ge "$CONC" ]; do sleep 5; done
  done
done
wait
say "ALL DONE"
