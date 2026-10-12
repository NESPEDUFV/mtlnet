#!/usr/bin/env bash
# v18 queue 3 — runs after queue2 (MTL AZ+IST, row 4). Order per author 2026-08-08.
# Row 8 is POSTPONED and is deliberately NOT in this queue.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
BASE=docs/studies/closing_data/v18
Q=$BASE/logs/queue3_DRIVER.log
log(){ echo "[$(date '+%F %T')] QUEUE3: $*" | tee -a "$Q"; }
log "waiting for queue2 (MTL at AZ+IST, then row 4)"
while pgrep -f run_queue2.sh >/dev/null 2>&1; do sleep 120; done
log "queue2 finished"
log "row 10 — MTL batch size at alabama"
bash "$BASE/run_mtl_bs_alabama.sh" >> "$BASE/logs/queue3_stdout.log" 2>&1
log "QUEUE3 COMPLETE (rows 5/6 at TX and 3b at FL are launched separately once the AL/AZ/IST winner is fixed)"
