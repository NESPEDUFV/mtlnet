#!/usr/bin/env bash
# usage: g1_run.sh <tag> <cmd...>   (run from anywhere; cwd becomes the SSD clone)
C="/Volumes/Vitor's SSD/ingred_g1"; R=/Users/vitor/Desktop/mestrado/ingred; cd "$C" || exit 9
export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" OUTPUT_DIR="$C/output" DATA_ROOT="$C/data" RESULTS_ROOT="$C/results"
export MTL_RAM_HEADROOM_GB=4 MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 PYTHONDONTWRITEBYTECODE=1
TAG=$1; shift; L="$C/g1_logs/$TAG"; mkdir -p "$L"; touch "$L/MARKER"
SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD) swap_used_MB=$SW0" > "$L/RUN.txt"; echo "cmd: $*" >> "$L/RUN.txt"
( while true; do
    sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}')
    echo "$(date +%T) swap_used_MB=$sw mem_free_pct=$fr" >> "$L/mem.log"
    if [ "$sw" -gt $((SW0+1500)) ] || [ "$fr" -lt 15 ]; then echo "ABORT $(date +%T) swap=$sw free=$fr" >> "$L/RUN.txt"; pkill -f "$C/scripts/"; pkill -f "ingred_g1"; touch "$L/ABORTED"; fi
    sleep 5; done ) & WD=$!
T0=$(date +%s)
/usr/bin/time -l "$@" > "$L/out.log" 2>&1; RC=$?
echo "rc=$RC wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/out.log" | awk '{print $1}')" >> "$L/RUN.txt"
kill $WD
LEAK=$(find $R/output/ $R/data/ $R/results/ $R/docs/results/ -newer "$L/MARKER" 2>/dev/null | head -5)
[ -z "$LEAK" ] && echo "repo-write-guard OK" >> "$L/RUN.txt" || { echo "repo-write-guard FAIL:" >> "$L/RUN.txt"; echo "$LEAK" >> "$L/RUN.txt"; }
echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
