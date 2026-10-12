#!/usr/bin/env bash
# Fetch check2hgi data for one state from the shared Google Drive folders.
# Storage-conscious: only downloads what you ask for.
#
# Usage:
#   bash scripts/runpod_fetch_data.sh florida
#   bash scripts/runpod_fetch_data.sh california
#   bash scripts/runpod_fetch_data.sh texas
#   bash scripts/runpod_fetch_data.sh georgia    # small state for hyperparam / smoke tests
#
# Layout (after fetch):
#   output/check2hgi/<state>/embeddings.parquet
#   output/check2hgi/<state>/poi_embeddings.parquet
#   output/check2hgi/<state>/region_embeddings.parquet
#   output/check2hgi/<state>/region_transition_log.pt
#   output/check2hgi/<state>/input/{next,next_poi,next_region}.parquet
#   output/check2hgi/<state>/temp/{sequences_next.parquet,checkin_graph.pt,...}

set -euo pipefail

STATE="${1:-}"
if [[ -z "$STATE" ]]; then
    echo "Usage: $0 <florida|california|texas|georgia>"
    exit 1
fi
STATE="${STATE,,}"   # lowercase

case "$STATE" in
    florida)    FOLDER_ID="1_4RxYvteg1rvN2WRB2AywKctQ1_t-ZhI" ;;
    california) FOLDER_ID="1ZLL8FHPeO7I-3DEfVBogW1C1eFE76ttv" ;;
    texas)      FOLDER_ID="1bLfFDEOM1BJ2ELoQUnd_qMXFpxGsZ7UF" ;;
    georgia)    FOLDER_ID="1v5xiJRzIQfMT8yk-J11sax5uf7Mct5vo" ;;  # small state — for fast smoke / hyperparam tests
    alabama)    FOLDER_ID="1xz9fJ3qbr0Msjt53Vdbnlg-hk16g2uj8" ;;  # F50 T4 cross-state validation (1109 regions)
    arizona)    FOLDER_ID="1L0kYmiH-K9l8wIy8Gyye0A-i5-8nu-DX" ;;  # F50 T4 cross-state validation
    *)
        echo "Unknown state '$STATE'. Valid: florida | california | texas | georgia | alabama | arizona"
        exit 1
        ;;
esac

WORKTREE="${WORKTREE:-$(pwd)}"
DEST="${WORKTREE}/output/check2hgi/${STATE}"
mkdir -p "${DEST}"

echo "[fetch] state    = ${STATE}"
echo "[fetch] dest     = ${DEST}"
echo "[fetch] gdrive   = ${FOLDER_ID}"
echo "[fetch] disk before:"
df -h "${WORKTREE}" | tail -1

if ! command -v gdown >/dev/null 2>&1; then
    echo "[fetch] ERROR: gdown not found. Activate the venv (source .venv/bin/activate) or run runpod_setup.sh first."
    exit 1
fi

gdown --folder "${FOLDER_ID}" -O "${DEST}"

echo ""
echo "[fetch] disk after:"
du -sh "${DEST}"
df -h "${WORKTREE}" | tail -1
echo "[fetch] done."
