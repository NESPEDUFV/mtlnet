#!/bin/bash
# closing_data C1 (confirm-on-G) — train champion G with per-task-best snapshots,
# then re-score each fold's 3 snapshots with route_task_best.py (independent code
# path) to get per-task-best routing vs the single geom_simple checkpoint.
#
# Champion G = --canon v16 (the bundle IS the full G recipe incl. the v14 engine,
# dualtower, onecycle, unweighted, KD off; it omits --checkpoint-selector so the
# code default geom_simple — the shipped deploy default we compare against — is used).
# The reg snapshot's best-monitor is Acc@10 (top10_acc_indist) by the v15 default
# (check2hgi_next_region task_b primary_metric=TOP10) → the degenerate-snapshot
# guard the original AL Acc@1 failure motivated is already satisfied.
#
# Usage: bash scripts/closing_data/c1_run_g.sh <state> <seed>
#   bash scripts/closing_data/c1_run_g.sh alabama 0
set -euo pipefail

STATE="$1"; SEED="$2"
ENGINE=check2hgi_design_k_resln_mae_l0_1

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO"
PY=.venv/bin/python

OUT_DIR="output/${ENGINE}/${STATE}"
TDIR="$OUT_DIR"
NEXT_REGION="$OUT_DIR/input/next_region.parquet"
LOGROOT=/tmp/c1_run; mkdir -p "$LOGROOT"
say(){ echo "[c1_run $STATE s$SEED] $*"; }

# --- stale-log_T preflight (CLAUDE.md hard rule) ---
# Portable mtime: GNU coreutils (Linux/A40) uses `stat -c %Y`; BSD (macOS/M2) uses `stat -f %m`.
mtime(){ stat -c %Y "$1" 2>/dev/null || stat -f %m "$1"; }
[ -f "$NEXT_REGION" ] || { echo "ERR next_region missing: $NEXT_REGION (run c1_prep_substrate.sh)"; exit 1; }
nr_m=$(mtime "$NEXT_REGION")
for f in 1 2 3 4 5; do
    lt="$TDIR/region_transition_log_seed${SEED}_fold${f}.pt"
    [ -f "$lt" ] || { echo "ERR missing log_T $lt (run c1_prep_substrate.sh $STATE $SEED)"; exit 1; }
    [ "$(mtime "$lt")" -ge "$nr_m" ] || { echo "ERR STALE log_T $lt < next_region"; exit 1; }
done
say "log_T freshness OK (5 folds seed=$SEED)"

# Under --no-checkpoints the runner writes snapshots + config.json to the
# TOP-LEVEL results dir (shared across seeds → must isolate per seed).
RESULTS_PATH="results/${ENGINE}/${STATE}"
TOP_SNAP="$RESULTS_PATH/task_best_snapshots"
SNAPDIR="$RESULTS_PATH/c1_snap_s${SEED}"      # seed-isolated copy
CONFIG="$SNAPDIR/config.json"
ROUTEDIR="$RESULTS_PATH/c1_route_s${SEED}"

# --- train champion G with per-task-best snapshots, no bulky checkpoints ---
RUNLOG="$LOGROOT/${STATE}_s${SEED}.train.log"
rm -rf "$TOP_SNAP"   # clear any prior seed's snapshots so we don't mix folds
say "training champion G (--canon v16) -> $RUNLOG"
$PY scripts/train.py --task mtl --canon v16 \
    --state "$STATE" --seed "$SEED" \
    --per-fold-transition-dir "$TDIR" \
    --save-task-best-snapshots --no-checkpoints \
    > "$RUNLOG" 2>&1
say "train done"

# --- isolate this seed's snapshots + the seed-stamped config ---
[ -d "$TOP_SNAP" ] || { echo "ERR task_best_snapshots not produced at $TOP_SNAP"; exit 1; }
[ "$(ls "$TOP_SNAP"/*_best.pt 2>/dev/null | wc -l)" -eq 15 ] || { echo "ERR expected 15 snapshots in $TOP_SNAP"; exit 1; }
rm -rf "$SNAPDIR"; mkdir -p "$SNAPDIR"
cp "$TOP_SNAP"/*_best.pt "$SNAPDIR/"
cp "$RESULTS_PATH/config.json" "$CONFIG"   # carries this run's seed + champion-G heads
say "snapshots isolated -> $SNAPDIR"

# --- route_task_best per fold (independent re-score path) ---
# NOTE: do NOT pass --task-set — that forces the DEFAULT preset heads and the
# dual-tower state_dict fails to load. Omitting it makes route_task_best
# reconstruct the champion-G heads (next_gru cat / next_stan_flow_dualtower reg)
# from config.json's persisted task_set dict.
mkdir -p "$ROUTEDIR"
for f in 1 2 3 4 5; do
    say "route_task_best fold $f"
    $PY scripts/route_task_best.py \
        --snapshots-dir "$SNAPDIR" --fold "$f" --config "$CONFIG" \
        --task-a-input-type checkin --task-b-input-type region \
        --output-json "$ROUTEDIR/route_fold${f}.json" \
        >> "$LOGROOT/${STATE}_s${SEED}.route.log" 2>&1
    grep -E "reg:|cat:" "$LOGROOT/${STATE}_s${SEED}.route.log" | tail -2
done
say "DONE — routing JSONs in $ROUTEDIR"
echo "ROUTEDIR=$ROUTEDIR"
