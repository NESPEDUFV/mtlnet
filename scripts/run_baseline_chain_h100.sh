#!/usr/bin/env bash
# Overnight supervisor: after Task A (comparand, PID passed as $1) finishes, run the
# remaining no-gate FL baselines serially (each needs the whole H100). E and B are
# independent of A and of each other, so both run regardless of prior exit status.
#   E = CSLSL cascade (b4_cascade, over v14 design_k substrate)
#   B = CTLE-E2E (ctle_e2e)
# Task C (feature-concat) and D (CTLE-SC, gated) are handled separately.
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
# fp32 (protocol §0) — avoid the no-GradScaler fp16 NaN collapse at FL scale.
export DISABLE_AMP=1 MTL_DISABLE_AMP=1
PY="$(which python)"

A_PID="${1:-}"
echo "=== [chain] START $(date -u) — waiting for Task A (PID ${A_PID}) ==="
if [ -n "$A_PID" ]; then
  while kill -0 "$A_PID" 2>/dev/null; do sleep 60; done
fi
echo "=== [chain] Task A finished; A output: ==="
ls -la docs/results/closing_data/baseline_compare/florida_check2hgi_sc.json 2>/dev/null || echo "WARN: Task A json missing — continuing to E/B anyway"

echo "=== [chain] Task E: CSLSL cascade @ FL $(date -u) ==="
python scripts/baselines/b4_cascade.py --state florida --seed 0 --folds 5 --epochs 50 \
    --python "$PY" > logs/taskE_cslsl_cascade_fl.log 2>&1 \
  && echo "[chain] Task E OK $(date -u)" || echo "[chain] Task E FAILED $(date -u)"

echo "=== [chain] Task B: CTLE-E2E @ FL $(date -u) ==="
python scripts/baselines/ctle_e2e.py --state florida --seed 0 --folds 5 \
    > logs/taskB_ctle_e2e_fl.log 2>&1 \
  && echo "[chain] Task B OK $(date -u)" || echo "[chain] Task B FAILED $(date -u)"

echo "=== [chain] Task C: A2 feature-concat control @ FL $(date -u) ==="
# FL cell of the (AL/AZ-closed) A2 control: HGI⊕raw-visit-features vs HGI vs v14/v11.
# seed 0 x 5 folds x 30ep (matches H100 protocol + closed AL/AZ analysis). 4 arms x 2 tasks.
python scripts/pre_freeze_gates/run_a2.py --states florida --seeds 0 \
    --tasks category region > logs/taskC_a2_concat_fl.log 2>&1 \
  && echo "[chain] Task C OK $(date -u)" || echo "[chain] Task C FAILED $(date -u)"

echo "=== [chain] COMPLETE $(date -u) ==="
echo "--- outputs ---"
ls -la results/ctle_e2e_b1/florida/ 2>/dev/null
ls -la docs/results/closing_data/baseline_compare/florida_check2hgi_sc.json 2>/dev/null
ls -la docs/results/P1/region_head_florida_*A2_*_s0.json 2>/dev/null
