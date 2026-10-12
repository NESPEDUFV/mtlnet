#!/bin/bash
# Push Mac-built board baseline embeddings (on the SSD) -> Google Drive, THROTTLED so the
# local CloudStorage cache (~20 GB free) never overfills faster than the Drive daemon uploads.
# Resumable (skips a dst that already matches size). Pushes the deliverable per cell only:
# embeddings.parquet + provenance/leak markers. Symlinks (region/poi) + regennable input/ skipped.
set -uo pipefail
SSD="/Volumes/Vitor's SSD/ingred/output"
DRIVE="/Users/vitor/Library/CloudStorage/GoogleDrive-vho2009@hotmail.com/My Drive/mestrado (1)/PoiMtlNet/output"
FLOOR_GB=5          # wait until at least this many GB free on the cache volume before a copy
MAXWAIT=1800        # seconds to wait for the daemon to drain before giving up on one file
log(){ echo "[$(date '+%H:%M:%S')] $*"; }

free_gb(){ df -g "$DRIVE" 2>/dev/null | awk 'NR==2{print $4}'; }

wait_for_space(){
  local waited=0
  while :; do
    local f; f=$(free_gb); f=${f:-0}
    [ "$f" -ge "$FLOOR_GB" ] && return 0
    [ "$waited" -ge "$MAXWAIT" ] && { log "WARN timeout waiting for cache drain (${f}GB free)"; return 0; }
    log "  cache low (${f}GB free) — waiting for Drive upload..."; sleep 30; waited=$((waited+30))
  done
}

copy_one(){ # src dst
  local src="$1" dst="$2"
  [ -L "$src" ] && return 0                       # skip symlinks
  [ -f "$src" ] || return 0
  local ss; ss=$(stat -f%z "$src")
  if [ -f "$dst" ]; then local ds; ds=$(stat -f%z "$dst" 2>/dev/null||echo -1); [ "$ds" = "$ss" ] && return 0; fi
  wait_for_space
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst" && log "  + ${dst#$DRIVE/} ($((ss/1048576))MB)" || log "  ! FAIL ${dst#$DRIVE/}"
}

push_cell_dir(){ # src_cell_dir rel
  local d="$1" rel="$2"
  for f in "$d"/embeddings.parquet "$d"/*.json "$d"/*.txt; do
    [ -e "$f" ] || continue
    copy_one "$f" "$DRIVE/$rel/$(basename "$f")"
  done
}

log "=== Mac-built board baselines -> Drive (floor=${FLOOR_GB}GB) ==="
# board_baselines cells (only the Mac-built states)
declare -a B2B=(alabama arizona florida georgia)
declare -a CTLE=(alabama arizona georgia)
declare -a POI=(alabama arizona florida georgia)
for st in "${B2B[@]}";  do for c in "$SSD"/board_baselines/b2b/$st/s*_f*;     do [ -d "$c" ] && push_cell_dir "$c" "board_baselines/b2b/$st/$(basename "$c")"; done; done
for st in "${CTLE[@]}"; do for c in "$SSD"/board_baselines/ctle/$st/s*_f*;    do [ -d "$c" ] && push_cell_dir "$c" "board_baselines/ctle/$st/$(basename "$c")"; done; done
for st in "${POI[@]}";  do for c in "$SSD"/board_baselines/poi2vec/$st/s*_f*; do [ -d "$c" ] && push_cell_dir "$c" "board_baselines/poi2vec/$st/$(basename "$c")"; done; done
# b2c one-hot64 (all 6 states present on SSD; embeddings.parquet only)
for st in alabama arizona california florida georgia texas; do
  copy_one "$SSD/baseline_b2c_onehot64/$st/embeddings.parquet" "$DRIVE/baseline_b2c_onehot64/$st/embeddings.parquet"
done
log "=== Mac-built push DONE ==="
