#!/usr/bin/env bash
# Sequential queue (user-approved, avoids over-saturating the GPU): after the v14 cascade
# (PID $1) finishes, run the E-parallel comparand, then Task D (CTLE-SC cells + compare).
# A and B (dk_ovl) keep running independently; this queue never adds more than one heavy
# v14/CTLE job at a time.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_RAM_HEADROOM_GB=4
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export BASELINE_PY="$(which python)"

ECASC="${1:-}"
echo "=== [queue] waiting for E-cascade (PID $ECASC) $(date -u) ==="
[ -n "$ECASC" ] && while kill -0 "$ECASC" 2>/dev/null; do sleep 60; done
echo "=== [queue] E-cascade done; starting E-parallel $(date -u) ==="

bash scripts/run_eparallel_v14_fl.sh > logs/eparallel_v14_fl.log 2>&1 \
  && echo "[queue] E-parallel OK $(date -u)" || echo "[queue] E-parallel FAILED $(date -u)"

echo "=== [queue] starting Task D (CTLE-SC cells + compare) $(date -u) ==="
# Task D builds its own cells then compares; no further wait needed (run inline, no PID args).
bash scripts/run_taskD_ctle_sc_fl.sh > logs/taskD_ctle_sc_fl.log 2>&1 \
  && echo "[queue] Task D OK $(date -u)" || echo "[queue] Task D FAILED $(date -u)"

echo "=== [queue] COMPLETE $(date -u) ==="
ls -la docs/results/closing_data/baseline_compare/florida_ctle.json 2>/dev/null
