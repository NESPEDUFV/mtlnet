#!/bin/bash
# H100 board lane — per-fold seed-S log_T: build (canonical) -> stage into v14 dir -> verify freshness.
# Adapted from a40_tx_logt_stage.sh. compute_region_transition writes to output/check2hgi/<state>/
# (canonical, substrate-independent region prior); the trainer reads --per-fold-transition-dir
# output/$V14/<state>, so we COPY + touch so the freshness mtime guard passes.
# Usage: bash scripts/closing_data/h100_logt_stage.sh <state> [seed]
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=python
ST="${1:?usage: h100_logt_stage.sh <state> [seed]}"; SD="${2:-0}"
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
CANON_DIR=output/check2hgi/$ST
V14_DIR=output/$V14/$ST
OVL_NR=output/$OVL/$ST/input/next_region.parquet
mkdir -p logs

echo "[$(date '+%F %T')] (1) build canonical seed-$SD per-fold log_T for $ST"
$PY scripts/compute_region_transition.py --state "$ST" --per-fold --seed "$SD" || { echo FAIL_logT_build; exit 1; }

echo "[$(date '+%F %T')] (2) stage into v14 dir $V14_DIR (copy + touch)"
for f in 1 2 3 4 5; do
  cp "$CANON_DIR/region_transition_log_seed${SD}_fold${f}.pt" \
     "$V14_DIR/region_transition_log_seed${SD}_fold${f}.pt" || { echo "FAIL cp fold$f"; exit 1; }
done
sleep 1
touch "$V14_DIR"/region_transition_log_seed${SD}_fold*.pt

echo "[$(date '+%F %T')] (3) verify freshness: staged log_T must be NEWER than overlap next_region"
[ -f "$OVL_NR" ] || { echo "FAIL: overlap next_region missing ($OVL_NR) — build the overlap engine first"; exit 2; }
ovl_ts=$(stat -c '%Y' "$OVL_NR"); ok=1
for f in 1 2 3 4 5; do
  lt_ts=$(stat -c '%Y' "$V14_DIR/region_transition_log_seed${SD}_fold${f}.pt")
  [ "$lt_ts" -le "$ovl_ts" ] && { echo "  STALE fold$f: log_T($lt_ts) <= next_region($ovl_ts)"; ok=0; }
done
echo "  overlap next_region: $(stat -c '%y' "$OVL_NR")"
echo "  staged log_T fold1 : $(stat -c '%y' "$V14_DIR/region_transition_log_seed${SD}_fold1.pt")"
[ "$ok" -eq 1 ] && echo "[$(date '+%F %T')] $ST log_T FRESH ✓ (seed $SD, 5 folds staged)" || { echo "STALE ✗ STOP"; exit 2; }
