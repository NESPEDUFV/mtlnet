#!/bin/bash
# Lightweight RAM watchdog: logs free-memory % every 15s; if it drops below FLOOR_PCT,
# kills the target process pattern (the eval) to protect the machine from another OOM reboot.
set -uo pipefail
PATTERN="${1:?usage: ram_watchdog.sh <pgrep-pattern> [floor_pct]}"
FLOOR="${2:-18}"
log(){ echo "[$(date '+%H:%M:%S')] $*"; }
log "watchdog start — pattern='$PATTERN' floor=${FLOOR}% free"
while pgrep -f "$PATTERN" >/dev/null 2>&1; do
  free=$(memory_pressure 2>/dev/null | awk -F': ' '/free percentage/{gsub(/%/,"",$2); print $2}')
  free=${free:-100}
  la=$(uptime | awk -F'load averages: ' '{print $2}')
  log "free=${free}%  load=${la}"
  if [ "${free%.*}" -lt "$FLOOR" ] 2>/dev/null; then
    log "!! free ${free}% < ${FLOOR}% — KILLING '$PATTERN' to prevent OOM reboot"
    pkill -9 -f "$PATTERN"
    break
  fi
  sleep 15
done
log "watchdog exit (target gone or killed)"
