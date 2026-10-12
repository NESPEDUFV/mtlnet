#!/bin/bash
# A40 board lane — TX seed-0 per-fold log_T: build (canonical) -> stage into v14 dir -> verify freshness.
# Mirrors p3_board.sh:build_logT + HANDOFF_BOARD_A40.md §3b. CPU; run while a GPU cell is busy.
#   compute_region_transition writes to output/check2hgi/<state>/ (canonical); the trainer reads
#   --per-fold-transition-dir output/$V14/$state, so we COPY + touch so the freshness mtime guard passes.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python
ST=texas; SD=0
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
CANON_DIR=output/check2hgi/$ST
V14_DIR=output/$V14/$ST
OVL_NR=output/$OVL/$ST/input/next_region.parquet
L=/tmp/a40_board; mkdir -p "$L"

echo "[$(date '+%F %T')] (1) build canonical seed-$SD per-fold log_T for $ST"
$PY scripts/compute_region_transition.py --state "$ST" --per-fold --seed "$SD"
rc=$?; [ $rc -ne 0 ] && { echo "FAIL log_T build rc=$rc"; exit $rc; }

echo "[$(date '+%F %T')] (2) stage into v14 dir $V14_DIR (copy + touch)"
for f in 1 2 3 4 5; do
  cp "$CANON_DIR/region_transition_log_seed${SD}_fold${f}.pt" \
     "$V14_DIR/region_transition_log_seed${SD}_fold${f}.pt" || { echo "FAIL cp fold$f"; exit 1; }
done
sleep 1
touch "$V14_DIR"/region_transition_log_seed${SD}_fold*.pt

echo "[$(date '+%F %T')] (3) verify freshness: staged log_T must be NEWER than overlap next_region"
ovl_ts=$(stat -c '%Y' "$OVL_NR")
ok=1
for f in 1 2 3 4 5; do
  lt_ts=$(stat -c '%Y' "$V14_DIR/region_transition_log_seed${SD}_fold${f}.pt")
  if [ "$lt_ts" -le "$ovl_ts" ]; then echo "  STALE fold$f: log_T($lt_ts) <= next_region($ovl_ts)"; ok=0; fi
done
echo "  overlap next_region: $(stat -c '%y' "$OVL_NR")"
echo "  staged log_T fold1 : $(stat -c '%y' "$V14_DIR/region_transition_log_seed${SD}_fold1.pt")"
if [ "$ok" -eq 1 ]; then echo "[$(date '+%F %T')] TX log_T FRESH ✓ (seed $SD, 5 folds staged)"; else echo "[$(date '+%F %T')] TX log_T STALE ✗ — STOP"; exit 2; fi
