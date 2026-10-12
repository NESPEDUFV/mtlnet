#!/usr/bin/env bash
# Istanbul champion-G @ stride-1 (H100, user-directed; docs nominally assign to M4 — device caveat
# footnoted). Phase 1 (CPU): build stride-1 base + fresh seed-0 log_T. Phase 2: WAIT for the FL jobs
# (PIDs $@) to free the GPU, then run the documented champion recipe (onecycle, NOT textbook H3-alt
# constant — see PHASE_V_ISTANBUL_S0.md line 27; the '...' flags weren't persisted, filled with
# standard LR/fold/epoch flags). set-a seed-0 target was cat 60.15 / reg 69.79 (different windowing).
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_RAM_HEADROOM_GB=4
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board

echo "=== [istanbul] Phase 1: build stride-1 base $(date -u) ==="
IST_ROWS=$(python -c "import pyarrow.parquet as pq; print(pq.ParquetFile('output/check2hgi/istanbul/input/next.parquet').metadata.num_rows)" 2>/dev/null || echo 0)
if [ "${IST_ROWS:-0}" -gt 200000 ]; then
  echo "[istanbul] stride-1 base already built (rows=$IST_ROWS) — skipping rebuild"
else
  python scripts/build_istanbul_stride1.py || { echo "[istanbul] base build FAILED"; exit 1; }
  echo "--- rebuild seed-0 per-fold log_T (fresh vs new base) ---"
  python scripts/compute_region_transition.py --state istanbul --engine check2hgi --per-fold --seed 0 --n-splits 5
fi
echo "--- freshness check (log_T must be newer than next_region.parquet) ---"
stat -c '%y %n' output/check2hgi/istanbul/region_transition_log_seed0_fold1.pt output/check2hgi/istanbul/input/next_region.parquet

echo "=== [istanbul] Phase 2: wait for GPU-free (PIDs $*) $(date -u) ==="
for pid in "$@"; do [ -n "$pid" ] && while kill -0 "$pid" 2>/dev/null; do sleep 60; done; done

echo "=== [istanbul] champion-G @ stride-1 $(date -u) ==="
# EXACT verified CLI from docs/studies/second_dataset/DRY_RUN_RESULTS.md (NYC-verified champion).
# --mtl-loss static_weight --category-weight 0.75 is REQUIRED (with --canon none the loss would
# otherwise default to nash_mtl / cvxpy-ECOS-erroring). seed 0 per PHASE_V_ISTANBUL_S0.
python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
    --state istanbul --engine check2hgi --seed 0 --epochs 50 --folds 5 --batch-size 2048 \
    --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --cat-head next_gru --reg-head next_getnext_hard \
    --task-a-input-type checkin --task-b-input-type region \
    --no-reg-class-weights --no-cat-class-weights \
    --per-fold-transition-dir output/check2hgi/istanbul --log-t-kd-weight 0.0 \
  && echo "[istanbul] champion DONE $(date -u)" || echo "[istanbul] champion FAILED $(date -u)"
