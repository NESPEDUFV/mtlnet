#!/usr/bin/env bash
# Phase 3 takeover V2 — recover from AL/AZ HGI data contamination.
#
# Pre-conditions (must hold before launch):
#   - output/hgi/{alabama,arizona}/input/{next.parquet,next_region.parquet}
#     have been re-uploaded with correct HGI POI-level embeddings
#     (verified to differ from the c2hgi versions; col0 dtype = float).
#   - 8/10 STL JSONs already in P1/ (only AL hgi + AZ hgi missing).
#   - All 4 mtlnet_* run dirs deleted (clean MTL B9 phase).
#
# This script:
#   1. Re-runs AL hgi STL + AZ hgi STL in parallel on GPU 0 (<4 min total).
#   2. Runs all 5 MTL B9 same-state pairs (c2hgi+hgi together, 2-way parallel
#      on GPU 0 leveraging H100 80 GB headroom). Same-state pairing balances
#      wall-clock since c2hgi and hgi for the same state have similar size.
#
# H100 80 GB allows ~3-way packing of MTL B9 (each ~22-25 GB) but 2-way is the
# safer choice to leave headroom for transient activation peaks.
set -u
cd "$(dirname "$0")/.."

mkdir -p logs/phase3

# ── Step 1 — recover the 2 missing STL cells in parallel ────────────────
echo "######## V2 Step 1/2 — AL+AZ HGI STL recovery (parallel) $(date) ########"
bash scripts/run_phase3_reg_stl_cell.sh alabama hgi 0 \
    > logs/phase3/STL_ALABAMA_hgi_takeover_v2.log 2>&1 &
P1=$!
bash scripts/run_phase3_reg_stl_cell.sh arizona hgi 0 \
    > logs/phase3/STL_ARIZONA_hgi_takeover_v2.log 2>&1 &
P2=$!
echo "  AL hgi STL pid=$P1, AZ hgi STL pid=$P2"
FAIL=0
wait $P1 || FAIL=1
wait $P2 || FAIL=1
if [ $FAIL -ne 0 ]; then
    echo "[abort] STL recovery failed"
    exit 1
fi
echo "######## V2 Step 1 complete $(date) ########"

# ── Step 2 — MTL B9 phase (5 same-state pairs, 2-way parallel) ──────────
echo ""
echo "######## V2 Step 2/2 — MTL B9 phase (2-way pairs) $(date) ########"

dispatch_pair() {
    local STATE="$1"
    echo "================================================================"
    echo "[mtl-pair] $STATE c2hgi+hgi — $(date)"
    bash scripts/run_phase3_mtl_cell.sh "$STATE" check2hgi 0 &
    A=$!
    bash scripts/run_phase3_mtl_cell.sh "$STATE" hgi       0 &
    B=$!
    local F=0
    wait $A || F=1
    wait $B || F=1
    if [ $F -ne 0 ]; then
        echo "[abort] MTL pair $STATE failed"
        return 1
    fi
    echo "[mtl-pair] $STATE done $(date)"
}

# Order: small states first → fast B9 CLI re-validation post-fix, then big.
for STATE in alabama arizona florida california texas; do
    dispatch_pair "$STATE" || exit 1
done

echo ""
echo "######## V2 takeover complete $(date) ########"
echo "Next: python3 scripts/finalize_phase3.py"
