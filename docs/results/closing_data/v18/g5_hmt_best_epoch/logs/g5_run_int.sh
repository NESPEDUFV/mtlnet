#!/usr/bin/env bash
# G5 on the INTERNAL disk. usage: g5_run_int.sh <tag> <state> <folds> <epoch_select>
# Watchdog kills ONLY its own child tree by PID at: free<15%, swap growth >1500 MB, kernel pressure CRITICAL, internal disk <5 GB.
cd /Users/vitor/Desktop/mestrado/ingred || exit 9
G=/Users/vitor/g5_scratch; TAG=$1; ST=$2; NF=$3; ES=$4
export OUTPUT_DIR="$G/output" DATA_ROOT="$G/data" RESULTS_ROOT="$G/results" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MTL_RAM_HEADROOM_GB=4
L="$G/logs/$TAG"; mkdir -p "$L"
SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD) swap_used_MB=$SW0 state=$ST folds=$NF epoch_select=$ES" > "$L/RUN.txt"
T0=$(date +%s)
/usr/bin/time -l .venv/bin/python scripts/baselines/b3_hmt_grn.py --state $ST --seed 0 --folds $NF --epochs 50 --engine check2hgi_dk_ovl --epoch-select $ES > "$L/b3.log" 2>&1 & CP=$!
( while kill -0 $CP 2>/dev/null; do
    pl=$(sysctl -n kern.memorystatus_vm_pressure_level); sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}'); di=$(df -g / | awk 'NR==2{print $4}')
    co=$(vm_stat | awk '/occupied by compressor/{gsub("\\.","",$NF); printf "%.1f",$NF*16384/1e9}')
    echo "$(date +%T) pressure=$pl swap_used_MB=$sw mem_free_pct=$fr compressor_GB=$co disk_int_GB=$di" >> "$L/mem.log"
    if [ "$pl" -ge 4 ] || [ "$sw" -gt $((SW0+1500)) ] || [ "$fr" -lt 15 ] || [ "$di" -lt 5 ]; then echo "ABORT $(date +%T) pressure=$pl swap=$sw free=$fr disk_int=$di" >> "$L/RUN.txt"; touch "$L/ABORTED"; pkill -TERM -P $CP; kill -TERM $CP 2>/dev/null; break; fi
    sleep 5; done ) & WD=$!
wait $CP; RC=$?; kill $WD 2>/dev/null; wait $WD 2>/dev/null
echo "b3 rc=$RC wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/b3.log" | awk '{print $1}')" >> "$L/RUN.txt"
echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
