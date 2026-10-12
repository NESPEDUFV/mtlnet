#!/usr/bin/env bash
# v18 REGENERATION — the autonomous top-level driver. Runs wave seed 0 then wave seed 1 to n=10,
# under the author-approved recipe in FINAL_SETTINGS.md.
#
#   bash docs/studies/closing_data/v18/run_regen.sh            # seeds 0 1 (default)
#   SEEDS="0 1 7 100" bash .../run_regen.sh                    # full n=20
#
# DESIGN GOALS (author: "as autonomous as possible, we just monitor status")
#   - Resumable: any cell with a sidecar is SKIPPED loudly. Safe to kill and relaunch at any time.
#   - Self-healing: a failed cell does not stop the wave; it is recorded and RETRIED once at the end
#     of the wave, then left as failed for a human.
#   - Health-guarded: waits for host RAM before large-state MTL (shared box: neighbours spike to
#     80-100 GB and the kernel OOM-killer has taken innocent jobs before), and ABORTS the wave if
#     free disk falls under a floor rather than filling /home.
#   - Observable without reading logs: status.json + PROGRESS.md + log.md rewritten per cell.
#
# WHAT IS ALREADY DONE AND WILL BE SKIPPED
#   The 10 dedicated-REGION cells are UNCHANGED by the new recipe (region keeps tau=0, because logit
#   adjustment significantly HURTS Acc@10: AL -1.841 p=0.0002, IST -2.749 p<0.0001). Their sidecars
#   were kept and will be skipped. Verified bit-reproducible: today's fresh AL/IST tau=0 arms
#   reproduced the stored 69.9956 / 75.1563 exactly.
#   The 19 cat+joint sidecars used the SUPERSEDED recipe and were moved to
#   docs/results/closing_data/v18_superseded_oldrecipe/ -- they will be regenerated.
#
# PARALLELISM (measured on this box, not guessed)
#   Small states (istanbul, alabama, arizona) run 2-wide: ~1.18x throughput, and the card holds two
#   small jobs comfortably. Large states (florida, texas, california) run STRICTLY 1-wide -- their
#   MTL dataset build peaks ~66 GB host RAM and 2-wide is recorded as infeasible there. Concurrency
#   never changes a cell's numbers (each run is independently seeded and deterministic); it only
#   changes wall time. That policy lives in run_wave.sh and is unchanged here.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate

BASE=docs/studies/closing_data/v18
SEEDS=${SEEDS:-"0 1"}
DISK_FLOOR_GB=${DISK_FLOOR_GB:-25}
DRV=$BASE/logs/regen_DRIVER.log
mkdir -p "$BASE/logs"
log(){ echo "[$(date '+%F %T')] REGEN: $*" | tee -a "$DRV"; }
disk_free_gb(){ df -BG --output=avail /home | tail -1 | tr -dc '0-9'; }

log "================ v18 REGENERATION START ================"
log "commit $(git rev-parse --short HEAD)  seeds: $SEEDS  disk floor ${DISK_FLOOR_GB} GB"
log "recipe: FINAL_SETTINGS.md (approved 2026-08-09) -- logit-adjust tau=0.5 on cat heads,"
log "        region UNCHANGED at tau=0, MTL cw0.50, bs8192, cat-lr 1e-3 small / 2e-3 large"

for SEED in $SEEDS; do
  d=$(disk_free_gb)
  if [ "$d" -lt "$DISK_FLOOR_GB" ]; then
    log "ABORT before seed $SEED: only ${d} GB free on /home (floor ${DISK_FLOOR_GB})."
    python "$BASE/status_update.py" --phase blocked \
      --blocked-on "disk: ${d} GB free on /home, below the ${DISK_FLOOR_GB} GB floor" >/dev/null 2>&1 || true
    exit 1
  fi
  log "---- WAVE seed=$SEED starting (disk ${d} GB free) ----"
  bash "$BASE/run_wave.sh" "$SEED" 2>&1 | tee -a "$DRV"
  log "---- WAVE seed=$SEED first pass done; retrying any failed cells once ----"
  # Second pass: run_wave is idempotent, so re-invoking retries exactly the cells that have no
  # sidecar. One retry only -- a cell that fails twice is a real problem, not a transient.
  bash "$BASE/run_wave.sh" "$SEED" 2>&1 | tee -a "$DRV"
  # FIX 2026-08-10: this resolved to docs/studies/results/... which does not exist, so every wave
  # logged a flat "0/18 cells present" while the aggregation beside it was reading the right dir.
  n=$(ls docs/results/closing_data/v18/*_s${SEED}_*.json 2>/dev/null | wc -l)
  log "---- WAVE seed=$SEED COMPLETE: $n/18 cells present ----"
  python "$BASE/make_results.py" >> "$DRV" 2>&1 || log "  (make_results.py failed, non-fatal)"
done

log "================ v18 REGENERATION COMPLETE ================"
python "$BASE/status_update.py" --phase done >/dev/null 2>&1 || true
