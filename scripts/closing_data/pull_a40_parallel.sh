#!/bin/bash
# Parallel A40 -> SSD pull: one rsync channel per (baseline,state) so the transfer isn't
# capped by a single SSH stream. Each stream writes its own dir (no conflicts). Resumable
# (rsync skips size-matched files), so safe to relaunch over the partial serial run.
set -uo pipefail
A40=vitor.oliveira@nespedgpu.caf.ufv.br
R=/home/vitor.oliveira/PoiMtlNet/output/board_baselines
SSD="/Volumes/Vitor's SSD/ingred/output/board_baselines"
LOGD=/tmp/baseline_manifest; mkdir -p "$LOGD"
log(){ echo "[$(date '+%H:%M:%S')] $*"; }

one(){ # baseline state
  local b="$1" st="$2" tag="$1_$2"
  mkdir -p "$SSD/$b"
  log "start $b/$st"
  rsync -a --inplace -e ssh "$A40:$R/$b/$st" "$SSD/$b/" \
      > "$LOGD/pull_$tag.log" 2>&1 && log "DONE $b/$st" || log "FAIL $b/$st (see pull_$tag.log)"
}

log "=== parallel A40 -> SSD (5 channels) ==="
one b2b  california &
one b2b  texas      &
one ctle florida    &
one ctle california &
one ctle texas      &
wait
log "=== ALL CHANNELS DONE ==="
log "SSD free: $(df -h "$SSD"|awk 'NR==2{print $4}')"
for p in b2b/california b2b/texas ctle/florida ctle/california ctle/texas; do
  n=$(ls -d "$SSD/$p"/s*_f* 2>/dev/null|wc -l|tr -d ' '); printf "  %-16s %s cells\n" "$p" "${n:-0}"
done