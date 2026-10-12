#!/usr/bin/env bash
# tier_resln (Design J branch) orchestrator — build -> MTL -> STL.
# Launches the build megascript itself (foreground within this detached proc),
# then runs MTL and STL stages sequentially. Survives turn boundaries via setsid.
set -u
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
LOG=/tmp/tier_reslndj_logs
mkdir -p "$LOG"
echo "ORCH_PID $$ $(date -u +%FT%TZ)" > "$LOG/orch.pid"

echo "[$(date -u +%H:%M:%S)] orchestrator START -> build" >> "$LOG/orch.log"
bash scripts/substrate_protocol_cleanup/run_reslndj_build.sh
echo "[$(date -u +%H:%M:%S)] build returned (build.DONE=$( [ -f "$LOG/build.DONE" ] && echo yes || echo no ))" >> "$LOG/orch.log"

bash scripts/substrate_protocol_cleanup/run_reslndj_mtl.sh
echo "[$(date -u +%H:%M:%S)] MTL returned (mtl.DONE=$( [ -f "$LOG/mtl.DONE" ] && echo yes || echo no ))" >> "$LOG/orch.log"

bash scripts/substrate_protocol_cleanup/run_reslndj_stl.sh
echo "[$(date -u +%H:%M:%S)] STL returned (stl.DONE=$( [ -f "$LOG/stl.DONE" ] && echo yes || echo no ))" >> "$LOG/orch.log"

echo "ORCH_ALL_DONE $(date -u +%FT%TZ)" > "$LOG/orch.DONE"
echo "[$(date -u +%H:%M:%S)] orchestrator ALL DONE" >> "$LOG/orch.log"
