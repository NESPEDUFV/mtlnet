#!/usr/bin/env bash
# usage: g1_run.sh <tag> <cmd...>  -- cwd = this clone. Watchdog kills ONLY its own child tree (by PID), never by name.
C="/Volumes/Vitor's SSD/ingred_g1"; R=/Users/vitor/Desktop/mestrado/ingred; cd "$C" || exit 9
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" OUTPUT_DIR="${OUTPUT_DIR:-$C/output}" DATA_ROOT="$C/data" RESULTS_ROOT="${RESULTS_ROOT:-$C/results}"
export MTL_RAM_HEADROOM_GB=4 MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 PYTHONDONTWRITEBYTECODE=1
TAG=$1; shift; L="$C/g1_logs/$TAG"; mkdir -p "$L"; touch "$L/MARKER"
SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD) swap_used_MB=$SW0" > "$L/RUN.txt"; echo "cmd: $*" >> "$L/RUN.txt"
LOCK="/Volumes/Vitor's SSD/g1_heavy.lock"
HEAVY=0; case "$*" in *train.py*|*p1_region_head_ablation.py*|*b3_hmt_grn.py*) [ "${G1_HEAVY:-0}" = 1 ] && HEAVY=1;; esac
if [ "$HEAVY" = 1 ]; then  # at most ONE MPS training process at a time across all drivers (~10 GB wired Metal memory each)
  echo "waiting for heavy lock $(date +%T)" >> "$L/RUN.txt"
  until mkdir "$LOCK" 2>/dev/null; do op=$(cat "$LOCK/pid" 2>/dev/null); if [ -n "$op" ] && ! kill -0 "$op" 2>/dev/null; then rm -rf "${LOCK:?}"; fi; sleep 10; done
  echo $$ > "$LOCK/pid"; echo "$TAG" > "$LOCK/tag"; echo "heavy lock acquired $(date +%T)" >> "$L/RUN.txt"
  SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
fi
T0=$(date +%s)
/usr/bin/time -l "$@" > "$L/out.log" 2>&1 & CP=$!
( while kill -0 $CP 2>/dev/null; do
    sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}')
    di=$(df -g / | awk 'NR==2{print $4}'); ds=$(df -g "/Volumes/Vitor's SSD" | awk 'NR==2{print $4}')
    echo "$(date +%T) swap_used_MB=$sw mem_free_pct=$fr disk_int_GB=$di disk_ssd_GB=$ds" >> "$L/mem.log"
    if [ "$sw" -gt $((SW0+1000)) ] || [ "$fr" -lt 20 ] || [ "$ds" -lt 5 ]; then echo "ABORT $(date +%T) swap=$sw free=$fr disk_int=$di disk_ssd=$ds" >> "$L/RUN.txt"; touch "$L/ABORTED"; pkill -TERM -P $CP; kill -TERM $CP 2>/dev/null; break; fi
    sleep 5; done ) & WD=$!
wait $CP; RC=$?; kill $WD 2>/dev/null; wait $WD 2>/dev/null
[ "$HEAVY" = 1 ] && [ "$(cat "$LOCK/pid" 2>/dev/null)" = "$$" ] && rm -rf "${LOCK:?}"
echo "rc=$RC wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/out.log" | awk '{print $1}')" >> "$L/RUN.txt"
LEAK=$( { find $R/output/ $R/data/ $R/results/ $R/docs/results/ -newer "$L/MARKER" ! -name .DS_Store 2>/dev/null;  } | head -5)
[ -z "$LEAK" ] && echo "repo-write-guard OK" >> "$L/RUN.txt" || { echo "repo-write-guard FAIL:" >> "$L/RUN.txt"; echo "$LEAK" >> "$L/RUN.txt"; }
echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
