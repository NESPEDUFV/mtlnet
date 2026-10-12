#!/usr/bin/env bash
# Phase 3 takeover dispatcher.
#
# Replaces the original sequential orchestrator (run_phase3_grid.sh) once it has
# already produced AL+AZ+FL+CA reg STL data and is mid TX c2hgi reg STL. We:
#   1. SIGKILL the original orchestrator (PID from logs/phase3/orchestrator.pid)
#      → orphans the running TX c2hgi STL python to init; it keeps writing to
#        the JSON output and per-cell log because file descriptors are
#        inherited and unaffected by the parent's death.
#   2. Launch TX hgi STL in parallel (alongside the orphaned TX c2hgi STL).
#   3. Wait for both reg STL to land, then dispatch MTL B9 cells two at a time.
#
# Pairing strategy for MTL: same-state pairs so wall-clock is naturally
# balanced (c2hgi and hgi for a given state are within 5% of each other).
#
# Pre-conditions:
#   - per-fold transition matrices for all 5 states already built
#   - logs/phase3/orchestrator.pid points at the original bash orchestrator
#   - run_phase3_mtl_cell.sh already updated to B9 recipe (TAG=MTL_B9_*)
set -u
cd "$(dirname "$0")/.."

mkdir -p logs/phase3

# ── Step 1 — kill the original sequential orchestrator ──────────────────
ORCH_PID=$(cat logs/phase3/orchestrator.pid 2>/dev/null || echo "")
if [ -n "$ORCH_PID" ] && kill -0 "$ORCH_PID" 2>/dev/null; then
    echo "[takeover] SIGKILL original orchestrator PID=$ORCH_PID"
    kill -KILL "$ORCH_PID" 2>/dev/null || true
    sleep 1
    # Confirm orphaned-but-running TX c2hgi python (or any p1_region_head process)
    if pgrep -f "p1_region_head_ablation.py" > /dev/null; then
        echo "[takeover] orphaned p1_region_head python still running — good"
    fi
else
    echo "[takeover] original orchestrator already exited (PID=$ORCH_PID)"
fi
rm -f logs/phase3/orchestrator.pid

# ── Step 2 — launch TX hgi STL in parallel with the orphaned TX c2hgi ───
# Skip if TX hgi STL already complete (idempotent).
TX_HGI_OUT=docs/results/P1/region_head_texas_region_5f_50ep_STL_TEXAS_hgi_reg_gethard_pf_5f50ep.json
if [ -f "$TX_HGI_OUT" ]; then
    echo "[takeover] TX hgi STL already complete — skipping"
else
    echo "[takeover] launching TX hgi STL in parallel with orphaned TX c2hgi STL"
    nohup bash scripts/run_phase3_reg_stl_cell.sh texas hgi 0 \
        > logs/phase3/tx_hgi_stl_takeover.log 2>&1 &
    TX_HGI_PID=$!
    echo $TX_HGI_PID > logs/phase3/tx_hgi_stl.pid
    echo "[takeover] TX hgi STL pid=$TX_HGI_PID"
fi

# ── Step 3 — wait for both TX reg STL cells to land ─────────────────────
echo "[takeover] waiting for both TX reg STL cells to complete..."
TX_C2HGI_OUT=docs/results/P1/region_head_texas_region_5f_50ep_STL_TEXAS_check2hgi_reg_gethard_pf_5f50ep.json
while true; do
    have_c=$([ -f "$TX_C2HGI_OUT" ] && echo Y || echo N)
    have_h=$([ -f "$TX_HGI_OUT"   ] && echo Y || echo N)
    running_p1=$(pgrep -f "p1_region_head_ablation.py.*texas" | wc -l)
    if [ "$have_c" = "Y" ] && [ "$have_h" = "Y" ] && [ "$running_p1" = "0" ]; then
        break
    fi
    sleep 30
done
echo "[takeover] TX reg STL phase complete at $(date)"

# ── Step 4 — MTL B9 phase: 2-way parallel by same-state pair ────────────
echo ""
echo "######## Phase 3 MTL B9 — 2-way parallel dispatch start $(date) ########"

dispatch_pair() {
    local STATE="$1"
    echo "================================================================"
    echo "[mtl-pair] $STATE c2hgi+hgi — $(date)"
    bash scripts/run_phase3_mtl_cell.sh "$STATE" check2hgi 0 &
    P1=$!
    bash scripts/run_phase3_mtl_cell.sh "$STATE" hgi       0 &
    P2=$!
    local FAIL=0
    wait $P1 || FAIL=1
    wait $P2 || FAIL=1
    if [ $FAIL -ne 0 ]; then
        echo "[abort] MTL pair $STATE failed (FAIL=$FAIL)"
        return 1
    fi
    echo "[mtl-pair] $STATE done $(date)"
}

# Order: small states first so we get fast feedback on the B9 CLI before
# committing to the big-state runs.
for STATE in alabama arizona florida california texas; do
    dispatch_pair "$STATE" || exit 1
done

echo ""
echo "######## Phase 3 MTL B9 phase complete $(date) ########"
echo ""
echo "Next: python3 scripts/finalize_phase3.py"
