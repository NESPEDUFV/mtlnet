#!/usr/bin/env bash
# mtl-protocol-fix Rank 2 (§4.6) — class-balanced batch sampler on reg head.
# Two runs: baseline (no flag) vs --reg-balanced-sampler.
#
# Usage:
#   bash scripts/mtl_protocol_fix/run_balanced_sampler_compare.sh alabama
#   bash scripts/mtl_protocol_fix/run_balanced_sampler_compare.sh arizona
#   bash scripts/mtl_protocol_fix/run_balanced_sampler_compare.sh florida
#
# Per CLAUDE.md: AL/AZ → H3-alt recipe; FL → B9 recipe.
# Single-seed=42, 5 folds, 50 epochs.

set -euo pipefail
STATE="${1:?usage: $0 STATE}"
OUT_DIR="docs/results/mtl_protocol_fix/phase3_rank2_balanced_sampler/${STATE}"
mkdir -p "${OUT_DIR}"

case "${STATE}" in
  alabama|arizona)
    RECIPE_FLAGS=(
      --scheduler constant
      --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3
    )
    BS=2048
    ;;
  florida|california|texas)
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

ARMS=("baseline" "balanced")
for ARM in "${ARMS[@]}"; do
  EXTRA=()
  if [[ "${ARM}" == "balanced" ]]; then
    EXTRA+=(--reg-balanced-sampler)
  fi
  RUN_LOG="${OUT_DIR}/run_${ARM}.log"
  echo "=== ${STATE} arm=${ARM} → ${RUN_LOG} ==="
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
    "${EXTRA[@]}" \
    2>&1 | tee "${RUN_LOG}"
done

echo "=== ${STATE} balanced-sampler compare complete ==="
