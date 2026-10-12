#!/usr/bin/env bash
# Wait for TX c2hgi MTL B9 to finish, then run TX hgi MTL B9 alone (full GPU).
# TX hgi previously OOMed when packed 2-way with TX c2hgi at ~70 GB combined.
set -u
cd "$(dirname "$0")/.."

TX_C2_OUT_PARENT="results/check2hgi/texas"
TX_HGI_OUT_PARENT="results/hgi/texas"
LOG=logs/phase3/tx_hgi_recovery.log

mkdir -p logs/phase3
date > "$LOG"

echo "[recovery] waiting for TX c2hgi MTL B9 python to finish..." | tee -a "$LOG"
while pgrep -f "scripts/train.py.*--task mtl.*--state texas.*--engine check2hgi" > /dev/null; do
    sleep 30
done
echo "[recovery] TX c2hgi finished at $(date)" | tee -a "$LOG"

# Verify TX c2hgi produced fold5_info.json
if ! ls $TX_C2_OUT_PARENT/mtlnet_*/folds/fold5_info.json >/dev/null 2>&1; then
    echo "[recovery] WARNING — TX c2hgi run dir missing fold5_info.json — c2hgi may have failed too" | tee -a "$LOG"
fi

# Wipe any stale TX hgi run dir from the OOM crash
rm -rf $TX_HGI_OUT_PARENT/mtlnet_* 2>/dev/null || true

echo "[recovery] launching TX hgi MTL B9 alone (full GPU)" | tee -a "$LOG"
bash scripts/run_phase3_mtl_cell.sh texas hgi 0 >> "$LOG" 2>&1
RC=$?
echo "[recovery] TX hgi exit=$RC at $(date)" | tee -a "$LOG"
exit $RC
