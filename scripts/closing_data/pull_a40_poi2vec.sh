#!/bin/bash
# poi2vec delta pull (A40 -> SSD), resilient. CA=seeds{0,1}x5f(10), TX=seed0x5f(5).
set -uo pipefail
A40=vitor.oliveira@nespedgpu.caf.ufv.br
R=/home/vitor.oliveira/PoiMtlNet/output/board_baselines/poi2vec
SSD="/Volumes/Vitor's SSD/ingred/output/board_baselines/poi2vec"
LOGD=/tmp/baseline_manifest
log(){ echo "[$(date '+%H:%M:%S')] $*"; }
wait_mount(){ local w=0; until mount|grep -qi "Vitor's SSD"; do [ $((w%60)) = 0 ] && log "  SSD unmounted, waiting ${w}s"; sleep 10; w=$((w+10)); done; }
chan(){ local st="$1" t=0; mkdir -p "$SSD"
  while :; do wait_mount
    if rsync -a -e ssh "$A40:$R/$st" "$SSD/" >> "$LOGD/pull_poi2vec_$st.log" 2>&1; then log "DONE poi2vec/$st"; return 0; fi
    t=$((t+1)); log "poi2vec/$st fail (try $t) wait+resume"; [ $t -ge 200 ] && return 1; sleep 15
  done; }
log "=== poi2vec delta pull (2 channels) ==="
chan california & chan texas & wait
log "=== poi2vec pull DONE ==="
for st in california texas; do n=$(ls -d "$SSD/$st"/s*_f* 2>/dev/null|wc -l|tr -d ' '); echo "  poi2vec/$st: $n cells"; done
