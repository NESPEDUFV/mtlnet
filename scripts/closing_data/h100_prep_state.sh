#!/bin/bash
# H100 board prep for ONE state on the FROZEN v14 substrate:
#   1. clear any stale overlap windowed data (e.g. built from a prior/rebuilt substrate)
#   2. build the gated stride-1 overlap engine (symlinks frozen v14 embeddings/poi/region)
#   3. build + stage the seed-0 per-fold log_T into the v14 dir + freshness-check
# Large states (FL/CA/TX) need the 108GB GPU box (build_next_region_for does a full in-memory
# .copy() of the multi-GB overlap frame → OOMs a 14GB VM). AL/AZ are safe anywhere.
# Usage: bash scripts/closing_data/h100_prep_state.sh <state> [seed]
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
ST="${1:?usage: h100_prep_state.sh <state> [seed]}"; SD="${2:-0}"
OVL=output/check2hgi_dk_ovl/$ST/input

echo "[$(date '+%F %T')] (1) clear stale overlap windowed data for $ST"
rm -f "$OVL"/next.parquet "$OVL"/next_region.parquet "$OVL"/sequences_next.parquet "$OVL"/next_build_provenance.json 2>/dev/null || true

echo "[$(date '+%F %T')] (2) build gated overlap engine (frozen v14 symlinks)"
python scripts/mtl_improvement/build_overlap_probe_engine.py "$ST" 1 || { echo "FAIL overlap build $ST"; exit 1; }

echo "[$(date '+%F %T')] (3) build + stage seed-$SD log_T"
# MTL_RAM_HEADROOM_GB low so the compute_region_transition RAM guard passes on small boxes;
# the log_T build itself is tiny. On the 108GB box the default 16 is fine too.
MTL_RAM_HEADROOM_GB="${MTL_RAM_HEADROOM_GB:-2}" bash scripts/closing_data/h100_logt_stage.sh "$ST" "$SD" || { echo "FAIL log_T $ST"; exit 1; }
echo "[$(date '+%F %T')] $ST PREP DONE (frozen substrate, gated overlap, log_T fresh)"
