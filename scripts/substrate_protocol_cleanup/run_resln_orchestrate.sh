#!/usr/bin/env bash
# tier_resln orchestrator — chains: wait(build.DONE) -> MTL -> STL -> analysis.
# The build megascript (run_resln_build.sh) is launched separately and writes
# /tmp/tier_resln_logs/build.DONE on completion. This waiter then runs the MTL
# and STL stages sequentially and dumps the analysis JSON.
# Detached; survives turn boundaries.
set -u
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
LOG=/tmp/tier_resln_logs
mkdir -p "$LOG"
echo "ORCH_PID $$ $(date -u +%FT%TZ)" > "$LOG/orch.pid"

echo "[$(date -u +%H:%M:%S)] orchestrator START; waiting for build.DONE" >> "$LOG/orch.log"
while [ ! -f "$LOG/build.DONE" ]; do sleep 60; done
echo "[$(date -u +%H:%M:%S)] build.DONE seen -> launching MTL" >> "$LOG/orch.log"

bash scripts/substrate_protocol_cleanup/run_resln_mtl.sh
echo "[$(date -u +%H:%M:%S)] MTL stage returned (mtl.DONE=$( [ -f "$LOG/mtl.DONE" ] && echo yes || echo no ))" >> "$LOG/orch.log"

bash scripts/substrate_protocol_cleanup/run_resln_stl.sh
echo "[$(date -u +%H:%M:%S)] STL stage returned (stl.DONE=$( [ -f "$LOG/stl.DONE" ] && echo yes || echo no ))" >> "$LOG/orch.log"

.venv/bin/python scripts/substrate_protocol_cleanup/analyze_resln.py \
    > "docs/results/substrate_protocol_cleanup/tier_resln/analysis.json" 2>> "$LOG/orch.log"
echo "[$(date -u +%H:%M:%S)] analysis.json written" >> "$LOG/orch.log"

echo "ORCH_ALL_DONE $(date -u +%FT%TZ)" > "$LOG/orch.DONE"
echo "[$(date -u +%H:%M:%S)] orchestrator ALL DONE" >> "$LOG/orch.log"
