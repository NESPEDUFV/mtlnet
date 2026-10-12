#!/usr/bin/env bash
# usage: run_pair.sh <tag> <extra train.py args...>   (runs check-in arm then place arm)
cd /Users/vitor/Desktop/mestrado/ingred
SC="/Volumes/Vitor's SSD/istanbul_pair"; TAG=$1; shift
export OUTPUT_DIR="$SC/output" DATA_ROOT="$SC/data" RESULTS_ROOT="$SC/results" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
       MTL_RAM_HEADROOM_GB=4 MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1
L="$SC/logs/$TAG"; mkdir -p "$L"
SW0=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}')
echo "start $(date '+%F %T') swap_used_MB=$SW0" > "$L/RUN.txt"
( while true; do
    sw=$(sysctl -n vm.swapusage | awk '{gsub("M","",$6); print int($6)}'); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}')
    echo "$(date +%T) swap_used_MB=$sw mem_free_pct=$fr" >> "$L/mem.log"
    if [ "$sw" -gt $((SW0+1500)) ] || [ "$fr" -lt 15 ]; then echo "ABORT $(date +%T) swap=$sw free=$fr" >> "$L/RUN.txt"; pkill -f "scripts/train.py --task next --state istanbul"; touch "$L/ABORTED"; fi
    sleep 5; done ) & WD=$!
for eng in check2hgi_v18 hgi_dk_ovl; do
  [ -e "$L/ABORTED" ] && break
  T0=$(date +%s)
  /usr/bin/time -l .venv/bin/python scripts/train.py --task next --state istanbul --engine $eng \
    --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed 0 \
    --batch-size 8192 --max-lr 0.0005 --logit-adjust-tau 0.5 --no-checkpoints "$@" > "$L/$eng.log" 2>&1
  echo "$eng rc=$? wall=$(( $(date +%s)-T0 ))s peakRSS_bytes=$(grep 'maximum resident' "$L/$eng.log" | awk '{print $1}')" >> "$L/RUN.txt"
done
kill $WD; echo "end $(date '+%F %T')" >> "$L/RUN.txt"; echo DONE >> "$L/RUN.txt"
