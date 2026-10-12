#!/bin/bash
# Parallel (5-channel) A40 -> SSD pull, drop-resilient for the flaky external enclosure.
# Each channel retries through a bus-drop: waits for the SSD to remount, resumes (rsync skips
# size-matched files, re-pulls the rest). NO --inplace -> an interrupted file is temp+renamed,
# so a cell is ever either byte-correct or absent (never a corrupt-but-complete file). A final
# pass hashes every large-state cell vs BASELINES_HASH_MANIFEST.json and re-pulls mismatches.
set -uo pipefail
A40=vitor.oliveira@nespedgpu.caf.ufv.br
R=/home/vitor.oliveira/PoiMtlNet/output/board_baselines
SSDROOT="/Volumes/Vitor's SSD"
SSD="$SSDROOT/ingred/output/board_baselines"
MAN=/Users/vitor/Desktop/mestrado/ingred/docs/studies/closing_data/BASELINES_HASH_MANIFEST.json
LOGD=/tmp/baseline_manifest; mkdir -p "$LOGD"
MAX_RETRY=200
log(){ echo "[$(date '+%H:%M:%S')] $*"; }

wait_mount(){ # block until the SSD is mounted again (flaky enclosure auto-remounts)
  local w=0
  until mount | grep -qi "Vitor's SSD"; do
    [ $((w%60)) = 0 ] && log "  SSD unmounted — waiting for remount (${w}s)..."
    sleep 10; w=$((w+10))
  done
}

channel(){ # baseline state
  local b="$1" st="$2" tag="$1_$2" t=0
  while :; do
    wait_mount; mkdir -p "$SSD/$b" 2>/dev/null
    if rsync -a -e ssh "$A40:$R/$b/$st" "$SSD/$b/" >> "$LOGD/pull_$tag.log" 2>&1; then
      log "DONE $b/$st"; return 0
    fi
    t=$((t+1)); log "channel $b/$st rsync failed (try $t) — likely SSD drop; waiting + resuming"
    [ "$t" -ge "$MAX_RETRY" ] && { log "GIVE UP $b/$st after $t tries"; return 1; }
    sleep 15
  done
}

log "=== v2 parallel A40 -> SSD (5 channels, drop-resilient) ==="
channel b2b  california & channel b2b  texas &
channel ctle florida    & channel ctle california & channel ctle texas &
wait
log "=== all channels returned — VERIFY vs manifest ==="

# hash-verify each large-state cell vs the manifest; collect mismatches
python3 - "$MAN" "$SSD" > "$LOGD/verify_mismatches.txt" 2>>"$LOGD/pull_verify.log" <<'PY'
import json,sys,hashlib,os
man=json.load(open(sys.argv[1]))["cells"]; ssd=sys.argv[2]
states={"b2b":["california","texas"],"ctle":["florida","california","texas"]}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(8<<20),b''): h.update(c)
    return h.hexdigest()
bad=0; ok=0; miss=0
for b,sts in states.items():
    for st in sts:
        d=os.path.join(ssd,b,st)
        if not os.path.isdir(d): continue
        for cell in sorted(os.listdir(d)):
            cid=f"{b}/{st}/{cell}"
            if cid not in man: continue
            emb=os.path.join(d,cell,"embeddings.parquet")
            if not os.path.exists(emb): print(cid); miss+=1; continue
            if sha(emb)==man[cid]["sha256"]: ok+=1
            else: print(cid); bad+=1
sys.stderr.write(f"verify: ok={ok} corrupt={bad} missing={miss}\n")
PY
cat "$LOGD/pull_verify.log" 2>/dev/null | tail -2
nmis=$(grep -c . "$LOGD/verify_mismatches.txt" 2>/dev/null || echo 0)
log "mismatched/missing cells: $nmis"

# re-pull mismatched cells (whole cell dir), once, resilient
if [ "$nmis" -gt 0 ]; then
  log "re-pulling $nmis mismatched cells..."
  while read -r cid; do
    [ -z "$cid" ] && continue
    b=$(echo "$cid"|cut -d/ -f1); st=$(echo "$cid"|cut -d/ -f2); cell=$(echo "$cid"|cut -d/ -f3)
    wait_mount; rm -rf "$SSD/$b/$st/$cell" 2>/dev/null
    rsync -a -e ssh "$A40:$R/$b/$st/$cell" "$SSD/$b/$st/" >> "$LOGD/pull_repull.log" 2>&1 && log "  re-pulled $cid" || log "  FAIL re-pull $cid"
  done < "$LOGD/verify_mismatches.txt"
fi
log "=== v2 pull COMPLETE ==="
df -h "$SSDROOT" | tail -1
for p in b2b/california b2b/texas ctle/florida ctle/california ctle/texas; do
  full=$(find "$SSD/$p" -name embeddings.parquet 2>/dev/null|wc -l|tr -d ' '); printf "  %-16s %s/20 emb\n" "$p" "${full:-0}"
done
