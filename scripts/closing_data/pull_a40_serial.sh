#!/bin/bash
# SERIAL (1-channel) A40 -> SSD pull — the proven-tolerable mode for the flaky enclosure
# (5 concurrent writers flap the bus; one writer works). Drop-resilient: waits for remount
# and resumes. NO --inplace (temp+rename -> a cell is byte-correct or absent). Final pass
# hash-verifies every large-state cell vs BASELINES_HASH_MANIFEST.json and re-pulls mismatches.
set -uo pipefail
A40=vitor.oliveira@nespedgpu.caf.ufv.br
R=/home/vitor.oliveira/PoiMtlNet/output/board_baselines
SSDROOT="/Volumes/Vitor's SSD"
SSD="$SSDROOT/ingred/output/board_baselines"
MAN=/Users/vitor/Desktop/mestrado/ingred/docs/studies/closing_data/BASELINES_HASH_MANIFEST.json
LOGD=/tmp/baseline_manifest; mkdir -p "$LOGD"
MAX_RETRY=300
log(){ echo "[$(date '+%H:%M:%S')] $*"; }
wait_mount(){ local w=0; until mount | grep -qi "Vitor's SSD"; do [ $((w%60)) = 0 ] && log "  SSD unmounted — waiting remount (${w}s)..."; sleep 10; w=$((w+10)); done; }
channel(){ local b="$1" st="$2" tag="$1_$2" t=0
  while :; do wait_mount; mkdir -p "$SSD/$b" 2>/dev/null
    if rsync -a -e ssh "$A40:$R/$b/$st" "$SSD/$b/" >> "$LOGD/pull_$tag.log" 2>&1; then log "DONE $b/$st"; return 0; fi
    t=$((t+1)); log "$b/$st rsync failed (try $t) — wait+resume"; [ "$t" -ge "$MAX_RETRY" ] && { log "GIVE UP $b/$st"; return 1; }; sleep 15
  done; }

log "=== SERIAL A40 -> SSD (1 channel) ==="
channel b2b  california
channel b2b  texas
channel ctle florida
channel ctle california
channel ctle texas
log "=== pulls done — VERIFY vs manifest ==="
python3 - "$MAN" "$SSD" > "$LOGD/verify_mismatches.txt" 2>>"$LOGD/pull_verify.log" <<'PY'
import json,sys,hashlib,os
man=json.load(open(sys.argv[1]))["cells"]; ssd=sys.argv[2]
states={"b2b":["california","texas"],"ctle":["florida","california","texas"]}
def sha(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda:f.read(8<<20),b''): h.update(c)
    return h.hexdigest()
bad=ok=miss=0
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
cat "$LOGD/pull_verify.log" 2>/dev/null | tail -1
nmis=$(grep -c . "$LOGD/verify_mismatches.txt" 2>/dev/null || echo 0); log "mismatched/missing: $nmis"
if [ "$nmis" -gt 0 ]; then log "re-pulling $nmis cells..."; while read -r cid; do [ -z "$cid" ] && continue
    b=$(echo "$cid"|cut -d/ -f1); st=$(echo "$cid"|cut -d/ -f2); cell=$(echo "$cid"|cut -d/ -f3)
    wait_mount; rm -rf "$SSD/$b/$st/$cell" 2>/dev/null
    rsync -a -e ssh "$A40:$R/$b/$st/$cell" "$SSD/$b/$st/" >> "$LOGD/pull_repull.log" 2>&1 && log "  re-pulled $cid" || log "  FAIL $cid"
  done < "$LOGD/verify_mismatches.txt"; fi
log "=== SERIAL pull COMPLETE ==="; df -h "$SSDROOT" | tail -1
for p in b2b/california b2b/texas ctle/florida ctle/california ctle/texas; do full=$(find "$SSD/$p" -name embeddings.parquet 2>/dev/null|wc -l|tr -d ' '); printf "  %-16s %s/20\n" "$p" "${full:-0}"; done
