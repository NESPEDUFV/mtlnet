#!/usr/bin/env bash
# Autonomous per-fold committer for the TX MTL run. Survives session death (nohup).
# On each newly-completed TX fold: copy raw CSVs into a tracked dir, score the
# accumulated folds, regenerate TX_CELL.md's table, copy the score JSON, commit + push.
# Exits when TX writes EXIT= to its log. Idempotent (tracks committed folds in a state file).
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
DEST=docs/results/closing_data/h100/texas_s0_mtl
STATE_F=/tmp/tx_autocommit_done.txt
LOG=logs/tx_s0_ep50.log
mkdir -p "$DEST"; touch "$STATE_F"

commit_fold() {
  local f="$1" txrl="$2"
  cp "$txrl/metrics/${f}_next_region_val.csv" "$txrl/metrics/${f}_next_category_val.csv" "$DEST/" 2>/dev/null
  PYTHONPATH=src python scripts/closing_data/h100_score_matched.py "$txrl" --seed 0 --tag tx_auto >/tmp/tx_auto_score.txt 2>&1 || true
  if [ -f "$txrl/h100_matched_score.json" ]; then
    cp "$txrl/h100_matched_score.json" "$DEST/texas_s0_mtl_partial_score.json"
    python scripts/closing_data/update_tx_cell.py "$txrl/h100_matched_score.json" docs/studies/closing_data/TX_CELL.md || true
  fi
  git add docs/studies/closing_data/TX_CELL.md "$DEST" 2>/dev/null || true
  git commit -m "board-h100: TX MTL ${f} complete — incremental autonomous per-fold

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>" >/dev/null 2>&1 || true
  # race-robust push: rebase onto any concurrent commits (e.g. CA cell) then push, retry up to 4x
  for try in 1 2 3 4; do
    git pull --rebase origin "$BRANCH" >/tmp/tx_autocommit_pull.txt 2>&1 || true
    if git push origin "$BRANCH" >/tmp/tx_autocommit_push.txt 2>&1; then break; fi
    echo "[tx-autocommit] push retry $try for ${f}"; sleep 10
  done
  echo "[tx-autocommit] committed+pushed ${f} ($(date -u +%H:%M:%S)Z)"
}

echo "[tx-autocommit] watching TX folds → commit+push each ($(date -u +%H:%M:%S)Z)"
while true; do
  txrl=$(ls -dt results/check2hgi_dk_ovl/texas/mtlnet_*ep50* 2>/dev/null | head -1)
  if [ -n "$txrl" ]; then
    for rcsv in $(ls "$txrl"/metrics/fold*_next_region_val.csv 2>/dev/null); do
      f=$(basename "$rcsv" | grep -oE 'fold[0-9]')
      [ -f "$txrl/metrics/${f}_next_category_val.csv" ] || continue   # need BOTH heads = fold fully done
      grep -qx "$f" "$STATE_F" && continue
      commit_fold "$f" "$txrl"
      echo "$f" >> "$STATE_F"
    done
  fi
  if grep -q 'EXIT=' "$LOG" 2>/dev/null; then
    echo "[tx-autocommit] TX terminated — final sweep + exit"
    # one last pass already done above; commit the TX_CELL status note
    git add docs/studies/closing_data/TX_CELL.md "$DEST" 2>/dev/null || true
    git commit -m "board-h100: TX MTL run terminated — final per-fold state

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>" >/dev/null 2>&1 || true
    git push origin "$BRANCH" >/dev/null 2>&1 || true
    break
  fi
  sleep 90
done
echo "[tx-autocommit] done ($(date -u +%H:%M:%S)Z)"
