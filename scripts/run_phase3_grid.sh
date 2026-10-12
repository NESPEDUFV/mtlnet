#!/usr/bin/env bash
# Phase 3 Scope D — full leakage-free re-run grid (sequential, single GPU).
#
# Order: per-fold transitions → reg STL × all states × engines → MTL × all states × engines.
# Wall-clock estimate on 1× A100 (40 GB): ~9-10 h for the full 5-state grid.
#
# Override scope via STATES env var, e.g.:
#   STATES="california texas" bash scripts/run_phase3_grid.sh
set -u
cd "$(dirname "$0")/.."

mkdir -p logs/phase3

STATES="${STATES:-alabama arizona florida california texas}"
ENGINES="check2hgi hgi"

echo "######## Phase 3 Scope D sequential grid start $(date) ########"
echo "STATES: $STATES"
echo ""

# ── Step 1 — per-fold transition matrices (CPU) ────────────────────────
echo "=== Step 1/3: per-fold transition matrices ==="
STATES="$STATES" bash scripts/build_phase3_per_fold_transitions.sh || {
    echo "[abort] per-fold transition build failed"
    exit 1
}

# ── Step 2 — reg STL ×N (all states × both engines, GPU 0) ─────────────
echo ""
echo "=== Step 2/3: reg STL with per-fold transitions ==="
for STATE in $STATES; do
    for ENGINE in $ENGINES; do
        if ! bash scripts/run_phase3_reg_stl_cell.sh "$STATE" "$ENGINE" 0; then
            echo "[abort] reg STL $STATE × $ENGINE failed"
            exit 1
        fi
    done
done

# ── Step 3 — MTL B3 ×N (all states × both engines, GPU 0) ──────────────
echo ""
echo "=== Step 3/3: MTL B3 with per-fold transitions ==="
for STATE in $STATES; do
    for ENGINE in $ENGINES; do
        if ! bash scripts/run_phase3_mtl_cell.sh "$STATE" "$ENGINE" 0; then
            echo "[abort] MTL $STATE × $ENGINE failed"
            exit 1
        fi
    done
done

echo ""
echo "######## Phase 3 Scope D sequential grid complete $(date) ########"
echo ""
echo "Next: python3 scripts/finalize_phase3.py"
