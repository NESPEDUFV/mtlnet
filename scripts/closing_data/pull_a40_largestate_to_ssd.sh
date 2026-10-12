#!/bin/bash
# Pull the A40-built large-state board baseline cells -> the SSD (the "remo"/remote = A40 backup).
# Snapshot-now scope: b2b {CA,TX}, ctle {FL,CA,TX}. poi2vec CA/TX still building on the A40 -> delta later.
set -uo pipefail
A40=vitor.oliveira@nespedgpu.caf.ufv.br
R=/home/vitor.oliveira/PoiMtlNet/output/board_baselines
SSD="/Volumes/Vitor's SSD/ingred/output/board_baselines"
log(){ echo "[$(date '+%H:%M:%S')] $*"; }

pull(){ # baseline state
  local b="$1" st="$2"
  mkdir -p "$SSD/$b"
  log "pull $b/$st ..."
  rsync -a -e ssh "$A40:$R/$b/$st" "$SSD/$b/" && log "  done $b/$st" || log "  FAIL $b/$st"
}

log "=== A40 large-state -> SSD ==="
pull b2b  california
pull b2b  texas
pull ctle florida
pull ctle california
pull ctle texas
log "=== pull DONE ==="
log "SSD free: $(df -h "$SSD" | awk 'NR==2{print $4}')"
