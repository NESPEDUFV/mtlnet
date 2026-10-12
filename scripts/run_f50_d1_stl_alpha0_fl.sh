#!/usr/bin/env bash
# F50 D1 — STL next_getnext_hard with alpha=0 frozen, FL 5f×50ep.
# Tests how much of STL's 82.44 ceiling comes from the α·log_T graph prior
# vs the encoder. If α=0 → ~50-65 → prior dominates. If α=0 → ~75-80 →
# encoder is doing the work and MTL is failing to train it.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
PY="${PY:-python3}"

cd "${WORKTREE}"
mkdir -p logs

# Use p1_region_head_ablation.py — same recipe as F37 P2 (which got 82.44)
# but with alpha=0 frozen. _parse_overrides coerces int/float — pass
# freeze_alpha=1 (Python bool(1)=True triggers register_buffer path).
echo "=== [D1 STL alpha=0 frozen] start $(date) ==="
"$PY" -u scripts/p1_region_head_ablation.py \
    --state florida --heads next_getnext_hard \
    --folds 5 --epochs 50 --seed 42 --input-type region \
    --batch-size "${BATCH_SIZE:-2048}" \
    --override-hparams \
        d_model=256 num_heads=8 \
        alpha_init=0.0 freeze_alpha=1 \
        "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --tag stl_gethard_alpha0_d1 2>&1 | tee logs/f50_d1_stl_alpha0_fl.log
rc=${PIPESTATUS[0]}
echo "[D1] exit ${rc} at $(date)"
