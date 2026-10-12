#!/usr/bin/env bash
# Phase 3 Scope D — full leakage-free re-run grid, parallel across GPUs in one pod.
#
# Strategy:
#   Step 1 (CPU):  per-fold transition matrices for each state
#   Step 2 (GPU):  reg STL × {STATES} × {ENGINES} = 2*|STATES| cells
#                  packed across GPUs (~10 GB/cell on A100 — pack 2-3 per 40 GB GPU)
#   Step 3 (GPU):  MTL B3 × {STATES} × {ENGINES} = 2*|STATES| cells
#                  1 cell per GPU on 40 GB A100 (~22 GB each)
#
# Auto-detects GPU count and dispatches appropriately. Falls back to sequential
# scripts/run_phase3_grid.sh if only 1 GPU available.
#
# Override scope via STATES env var.
set -u
cd "$(dirname "$0")/.."

mkdir -p logs/phase3

STATES="${STATES:-alabama arizona florida california texas}"
ENGINES="check2hgi hgi"
NGPU=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | wc -l)

echo "######## Phase 3 Scope D parallel grid start $(date) ########"
echo "STATES: $STATES   GPUs: $NGPU"
echo ""

if [ "$NGPU" -lt 2 ]; then
    echo "[info] Only $NGPU GPU detected — falling back to sequential grid"
    exec bash scripts/run_phase3_grid.sh
fi

# ── Step 1 — per-fold transition matrices (CPU) ────────────────────────
echo "=== Step 1/3: per-fold transition matrices ==="
STATES="$STATES" bash scripts/build_phase3_per_fold_transitions.sh || {
    echo "[abort] per-fold transition build failed"
    exit 1
}

# ── Helper: dispatch a list of cells across N GPUs in waves ────────────
# Cells are passed as space-separated entries "STATE:ENGINE".
dispatch_waves() {
    local LAUNCHER="$1"; shift
    local CELLS=("$@")
    local NCELLS=${#CELLS[@]}
    local IDX=0
    local FAIL=0
    while [ $IDX -lt $NCELLS ]; do
        local PIDS=()
        for ((g=0; g<NGPU && IDX<NCELLS; g++)); do
            local entry="${CELLS[$IDX]}"
            local STATE="${entry%%:*}"
            local ENGINE="${entry##*:}"
            bash "$LAUNCHER" "$STATE" "$ENGINE" "$g" &
            PIDS+=($!)
            echo "  → $LAUNCHER $STATE $ENGINE on GPU $g (PID $!)"
            IDX=$((IDX+1))
        done
        for pid in "${PIDS[@]}"; do
            wait "$pid" || FAIL=1
        done
        if [ $FAIL -ne 0 ]; then
            echo "[abort] wave failed in $LAUNCHER"
            return $FAIL
        fi
    done
    return 0
}

# Build cell list: "STATE:ENGINE" entries
CELLS=()
for STATE in $STATES; do
    for ENGINE in $ENGINES; do
        CELLS+=("$STATE:$ENGINE")
    done
done

# ── Step 2 — reg STL waves ──────────────────────────────────────────────
echo ""
echo "=== Step 2/3: reg STL with per-fold transitions (${#CELLS[@]} cells) ==="
dispatch_waves "scripts/run_phase3_reg_stl_cell.sh" "${CELLS[@]}" || exit 1

# ── Step 3 — MTL B3 waves ───────────────────────────────────────────────
echo ""
echo "=== Step 3/3: MTL B3 with per-fold transitions (${#CELLS[@]} cells) ==="
dispatch_waves "scripts/run_phase3_mtl_cell.sh" "${CELLS[@]}" || exit 1

echo ""
echo "######## Phase 3 Scope D parallel grid complete $(date) ########"
echo ""
echo "Next: python3 scripts/finalize_phase3.py"
