#!/usr/bin/env bash
# v18: wave 1 (seed 0, resume) -> wave 2 (seed 1) -> final aggregation, unattended.
#
# Both waves are resumable and idempotent: a cell whose sidecar exists is skipped loudly, so wave 1
# picks up exactly at texas/california (istanbul, alabama, arizona, florida are already complete).
#
# After each wave the aggregate is regenerated so the study is readable at n=5 then n=10, with the
# current n stated in every table. The run does NOT stop if a single cell fails -- run_wave.sh keeps
# going and writes no sidecar for the failure, so a later re-run refills exactly the gaps.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
BASE=docs/studies/closing_data/v18
DRV=$BASE/logs/chain_DRIVER.log
log(){ echo "[$(date '+%F %T')] CHAIN: $*" | tee -a "$DRV"; }

aggregate(){
  local phase=$1
  python "$BASE/score_all.py" --write   >> "$DRV" 2>&1 || log "score_all FAILED"
  python "$BASE/make_results.py"        >> "$DRV" 2>&1 || log "make_results FAILED"
  python "$BASE/verify_engines.py" --write >/dev/null 2>&1 || true
  python "$BASE/status_update.py" --phase "$phase" >> "$DRV" 2>&1 || true
  log "aggregate done ($phase)"
}

log "===== CHAIN START (commit $(git rev-parse --short HEAD)) ====="

log "--- wave 1 (seed 0) — resuming; completed cells skip ---"
bash "$BASE/run_wave.sh" 0 >> "$BASE/logs/chain_wave0.log" 2>&1
log "wave 1 (seed 0) finished"
aggregate wave1
log "SEED-0 COMPLETE"

log "--- wave 2 (seed 1) ---"
bash "$BASE/run_wave.sh" 1 >> "$BASE/logs/chain_wave1.log" 2>&1
log "wave 2 (seed 1) finished"
aggregate wave2
log "SEED-1 COMPLETE"

log "--- final aggregation ---"
aggregate done
log "===== CHAIN COMPLETE ====="
