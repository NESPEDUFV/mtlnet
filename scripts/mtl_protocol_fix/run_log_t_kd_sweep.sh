#!/usr/bin/env bash
# mtl-protocol-fix Rank 1 (§4.5) — log_T as supervisory signal.
# Sweep --log-t-kd-weight ∈ {0.0, 0.05, 0.1, 0.2} at a target state.
#
# Usage:
#   bash scripts/mtl_protocol_fix/run_log_t_kd_sweep.sh alabama
#   bash scripts/mtl_protocol_fix/run_log_t_kd_sweep.sh arizona
#   bash scripts/mtl_protocol_fix/run_log_t_kd_sweep.sh florida
#
# Per CLAUDE.md: AL/AZ → H3-alt recipe; FL → B9 recipe.
# Single-seed=42, 5 folds, 50 epochs, batch=2048.

set -euo pipefail
STATE="${1:?usage: $0 STATE}"
WEIGHTS=(0.0 0.05 0.1 0.2)
OUT_DIR="docs/results/mtl_protocol_fix/phase3_rank1_log_t_kd/${STATE}"
mkdir -p "${OUT_DIR}"

case "${STATE}" in
  alabama|arizona)
    # H3-alt small-state recipe.
    RECIPE_FLAGS=(
      --scheduler constant
      --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    )
    BS=2048
    ;;
  florida|california|texas)
    # B9 large-state recipe.
    RECIPE_FLAGS=(
      --alternating-optimizer-step
      --alpha-no-weight-decay
      --min-best-epoch 5
      --scheduler cosine --max-lr 3e-3
      --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    )
    BS=2048
    if [[ "${STATE}" == "california" ]]; then BS=1024; fi
    if [[ "${STATE}" == "texas" ]]; then BS=512; fi
    ;;
  *)
    echo "Unknown state: ${STATE}" >&2; exit 1
    ;;
esac

for W in "${WEIGHTS[@]}"; do
  TAG="w${W//./}"
  RUN_LOG="${OUT_DIR}/run_${TAG}.log"
  echo "=== ${STATE} log_t_kd_weight=${W} → ${RUN_LOG} ==="
  python scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state "${STATE}" --engine check2hgi --seed 42 \
    --epochs 50 --folds 5 --batch-size "${BS}" \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    "${RECIPE_FLAGS[@]}" \
    --cat-head next_gru --reg-head next_getnext_hard \
    --task-a-input-type checkin --task-b-input-type region \
    --per-fold-transition-dir "output/check2hgi/${STATE}" \
    --log-t-kd-weight "${W}" \
    --log-t-kd-tau 1.0 \
    2>&1 | tee "${RUN_LOG}"
done

echo "=== ${STATE} sweep complete ==="
