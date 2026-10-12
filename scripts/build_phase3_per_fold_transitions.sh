#!/usr/bin/env bash
# Phase 3 Scope D — build per-fold leakage-free transition matrices for all states.
#
# For each state in STATES (default: alabama arizona florida california texas),
# runs `scripts/compute_region_transition.py --per-fold` which uses the trainer's
# StratifiedGroupKFold(seed=42) to split userids and builds 5 transition matrices
# per state from train-only edges.
#
# Outputs (per state) under output/check2hgi/<state>/:
#   region_transition_log_fold1.pt
#   ...
#   region_transition_log_fold5.pt
#
# Does NOT touch the legacy `region_transition_log.pt` (full-dataset, leaky).
#
# CPU-only, ~5 min per state.
#
# Usage:
#   bash scripts/build_phase3_per_fold_transitions.sh
#   STATES="california texas" bash scripts/build_phase3_per_fold_transitions.sh
set -eu
cd "$(dirname "$0")/.."

export PYTHONPATH=src
export OUTPUT_DIR="${OUTPUT_DIR:-$(pwd)/output}"

STATES="${STATES:-alabama arizona florida california texas}"

mkdir -p logs/phase3

echo "######## Phase 3 — building per-fold transition matrices ########"
echo "STATES: ${STATES}"
echo "OUTPUT_DIR: ${OUTPUT_DIR}"
echo ""

for STATE in $STATES; do
    LOG="logs/phase3/build_per_fold_transitions_${STATE}.log"
    echo "================================================================"
    echo "[per-fold transitions: ${STATE}] start $(date)"
    echo "  log=${LOG}"

    # Skip if already complete (idempotent)
    ALL_PRESENT=true
    for fold in 1 2 3 4 5; do
        f="${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log_fold${fold}.pt"
        [ -f "$f" ] || ALL_PRESENT=false
    done
    if [ "$ALL_PRESENT" = "true" ]; then
        echo "  ✓ already present (5/5 fold matrices) — skipping"
        echo "================================================================"
        continue
    fi

    python3 -u scripts/compute_region_transition.py \
        --state "$STATE" \
        --per-fold \
        --n-splits 5 \
        --seed 42 \
        --smoothing-eps 0.01 \
        > "$LOG" 2>&1
    rc=$?
    if [ $rc -ne 0 ]; then
        echo "[per-fold transitions: ${STATE}] FAILED rc=${rc} — see ${LOG}"
        tail -20 "$LOG"
        exit $rc
    fi

    # Verify outputs
    for fold in 1 2 3 4 5; do
        f="${OUTPUT_DIR}/check2hgi/${STATE}/region_transition_log_fold${fold}.pt"
        if [ ! -f "$f" ]; then
            echo "[per-fold transitions: ${STATE}] MISSING $f"
            exit 1
        fi
    done
    echo "[per-fold transitions: ${STATE}] OK at $(date) (5/5 matrices written)"
    echo "================================================================"
done

echo ""
echo "######## All per-fold transition matrices built $(date) ########"
