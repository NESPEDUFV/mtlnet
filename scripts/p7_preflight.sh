#!/usr/bin/env bash
# P7 preflight — verify machine is ready to run scripts/p7_launcher.sh for a given state.
#
# Usage: STATE=california DATA_ROOT=/path PY=/path/to/python bash scripts/p7_preflight.sh

set -u
STATE="${STATE:?set STATE=florida|california|texas}"
DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
OUTPUT_DIR="${OUTPUT_DIR:-/tmp/check2hgi_data}"
PY="${PY:-python}"

# Capitalize first letter for shapefile lookup
STATE_CAP="$(echo ${STATE:0:1} | tr '[:lower:]' '[:upper:]')${STATE:1}"

fail=0
ok() { echo "[OK]   $1"; }
bad() { echo "[FAIL] $1"; fail=$((fail+1)); }

echo "=== P7 preflight for STATE=${STATE} ==="

# 1. Python + packages
if [ ! -x "$PY" ]; then
    bad "Python not executable at ${PY}"
else
    pyver=$("$PY" --version 2>&1)
    ok "Python found: ${pyver}"
    for pkg in torch pandas numpy cvxpy; do
        if ! "$PY" -c "import ${pkg}" 2>/dev/null; then
            bad "Python package missing: ${pkg}"
        else
            ok "Python package: ${pkg}"
        fi
    done
    # Device check
    dev=$("$PY" -c "import torch; print('mps' if torch.backends.mps.is_available() else ('cuda' if torch.cuda.is_available() else 'cpu'))" 2>/dev/null)
    ok "Torch device: ${dev}"
fi

# 2. Raw data
if [ -f "${DATA_ROOT}/checkins/${STATE_CAP}.parquet" ]; then
    sz=$(du -sh "${DATA_ROOT}/checkins/${STATE_CAP}.parquet" | cut -f1)
    ok "Checkin data: ${DATA_ROOT}/checkins/${STATE_CAP}.parquet (${sz})"
else
    bad "Missing checkin data: ${DATA_ROOT}/checkins/${STATE_CAP}.parquet"
fi

# 3. Shapefiles (for embedding-gen)
case "${STATE}" in
    florida)   shp="tl_2022_12_tract_FL" ;;
    california) shp="tl_2022_06_tract_CA" ;;
    texas)     shp="tl_2022_48_tract_TX" ;;
    alabama)   shp="tl_2022_01_tract_AL" ;;
    arizona)   shp="tl_2022_04_tract_AZ" ;;
    *) shp="?" ;;
esac
if [ "${shp}" != "?" ] && [ -d "${DATA_ROOT}/miscellaneous/${shp}" ]; then
    ok "Shapefile: ${DATA_ROOT}/miscellaneous/${shp}"
else
    bad "Missing shapefile: ${DATA_ROOT}/miscellaneous/${shp}"
fi

# 4. Check2HGI embeddings + inputs (or need to generate)
EMBED_DIR="${OUTPUT_DIR}/check2hgi/${STATE}"
if [ -f "${EMBED_DIR}/input/next_region.parquet" ]; then
    ok "Check2HGI next_region parquet ready: ${EMBED_DIR}/input/next_region.parquet"
else
    bad "MISSING Check2HGI inputs at ${EMBED_DIR}/input/next_region.parquet"
    echo "       → Generate by running: python pipelines/embedding/check2hgi.pipe.py"
    echo "       → (first uncomment target state in STATES dict)"
    echo "       → Then: python pipelines/create_inputs_check2hgi.pipe.py --state ${STATE}"
fi

# 5. Disk space
if command -v df >/dev/null; then
    avail_gb=$(df -BG "${OUTPUT_DIR%/*}" 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}' || \
               df -h "${OUTPUT_DIR%/*}" 2>/dev/null | awk 'NR==2 {gsub(/G/,"",$4); print $4}')
    if [ -n "${avail_gb}" ] && [ "${avail_gb%.*}" -lt 10 ] 2>/dev/null; then
        bad "Low disk space on ${OUTPUT_DIR%/*}: ${avail_gb}G (need ≥20G per state)"
    else
        ok "Disk space: ${avail_gb}G available on ${OUTPUT_DIR%/*}"
    fi
fi

# 6. Git state
if [ -d .git ]; then
    branch=$(git branch --show-current 2>/dev/null)
    commit=$(git rev-parse --short HEAD 2>/dev/null)
    ok "Git: branch=${branch} commit=${commit}"
    # Warn if not on expected branch
    if [ "${branch}" != "worktree-check2hgi-mtl" ] && [ "${branch}" != "main" ]; then
        echo "[WARN] Expected branch 'worktree-check2hgi-mtl' or 'main', got '${branch}'"
    fi
fi

echo ""
if [ $fail -eq 0 ]; then
    echo "=== PREFLIGHT PASSED — ready to run scripts/p7_launcher.sh ==="
    exit 0
else
    echo "=== PREFLIGHT FAILED (${fail} issue(s)) — fix above before launching ==="
    exit 1
fi
