#!/usr/bin/env bash
# PARALLEL-SAFE copy (stricter: swap +800 MB, free<25%, SSD<5 GB) -- yields before the primary G1 job. usage: g5_run_par.sh <tag> <state> <folds> <epoch_select>
cd /Users/vitor/Desktop/mestrado/ingred
SC="/Volumes/Vitor's SSD/gpu_queue_scratch"; TAG=$1; ST=$2; NF=$3; ES=$4
export OUTPUT_DIR="$SC/output" DATA_ROOT="$SC/data" RESULTS_ROOT="$SC/results" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 MTL_RAM_HEADROOM_GB=4
L="$SC/logs/$TAG"; mkdir -p "$L"
SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD) swap_used_MB=$SW0 state=$ST folds=$NF epoch_select=$ES" > "$L/RUN.txt"
( while true; do
    sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}')
    echo "$(date +%T) swap_used_MB=$sw mem_free_pct=$fr" >> "$L/mem.log"
    ds=$(df -g "/Volumes/Vitor's SSD" | awk 'NR==2{print $4}'); if [ "$sw" -gt $((SW0+800)) ] || [ "$fr" -lt 25 ] || [ "$ds" -lt 5 ]; then echo "ABORT $(date +%T) swap=$sw free=$fr" >> "$L/RUN.txt"; pkill -f "scripts/baselines/b3_hmt_grn.py"; touch "$L/ABORTED"; fi
    sleep 5; done ) & WD=$!
T0=$(date +%s)
/usr/bin/time -l .venv/bin/python scripts/baselines/b3_hmt_grn.py --state $ST --seed 0 --folds $NF --epochs 50 \
   --engine check2hgi_dk_ovl --epoch-select $ES > "$L/b3.log" 2>&1
echo "b3 rc=$? wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/b3.log" | awk '{print $1}')" >> "$L/RUN.txt"
kill $WD; echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
