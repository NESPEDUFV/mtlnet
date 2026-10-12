#!/bin/bash
# Sequential GPU orchestrator (single A40): CA fit, TX fit (peak-VRAM checks with
# S2 chunked val-metric + dummy inert log_T), then FL full numbers (50ep/5fold).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
L=/tmp/gate_eval; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] ORCH $*" | tee -a "$L/orchestrate.log"; }

# guard: wait out any straggler GPU job
while pgrep -f "scripts/train.py --task mtl" >/dev/null; do sleep 5; done

say "=== CA GPU-fit (overlap, S2 on) ==="
bash scripts/pre_freeze_gates/overlap_gpu_fit.sh california 3 2>&1 | tee -a "$L/orchestrate.log"

say "=== TX GPU-fit (overlap, S2 on) ==="
bash scripts/pre_freeze_gates/overlap_gpu_fit.sh texas 3 2>&1 | tee -a "$L/orchestrate.log"

say "=== FL gated-overlap champion-G FULL (50ep, 5 folds, S2 on) ==="
bash scripts/pre_freeze_gates/gated_overlap_g.sh florida 42 50 5 2>&1 | tee -a "$L/orchestrate.log"

say "ALL DONE"
