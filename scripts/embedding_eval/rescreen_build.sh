#!/usr/bin/env bash
# Safe re-screen embedding rebuild — NEVER touches the frozen output/check2hgi/.
#
#   bash scripts/embedding_eval/rescreen_build.sh <variant_engine_value> <state> [epoch] -- <regen flags...>
#
# Mechanism: build with OUTPUT_DIR pointed at a scratch dir (paths.py reads
# OUTPUT_DIR at import, so the real output/ is physically untouchable), pre-seed
# the scratch with the frozen check2hgi graph so same-graph variants (v3c,
# side-features, dropedge, p2p) reuse the canonical preprocessing (force_preprocess
# stays off => identical graph => region partition aligned + faster). Then harvest
# embeddings.parquet + region_embeddings.parquet into the REAL output/<variant>/.
set -euo pipefail
cd "$(dirname "$0")/../.."
VARIANT="$1"; STATE="$2"; EPOCH="${3:-500}"; shift 3 || shift $#
[ "${1:-}" = "--" ] && shift || true

SCRATCH="$(pwd)/output_scratch/${VARIANT}_${STATE}"
DEST="output/${VARIANT}/${STATE}"
FROZEN="output/check2hgi/${STATE}"

echo "[build] variant=$VARIANT state=$STATE epoch=$EPOCH scratch=$SCRATCH"
rm -rf "$SCRATCH"; mkdir -p "$SCRATCH/check2hgi/${STATE}"
# pre-seed the frozen preprocessing (graph + sequences) so a same-graph variant
# reuses it; a flag that forces preprocess (gat/rgcn/dropedge/p2p) just rebuilds.
[ -d "$FROZEN/temp" ] && cp -r "$FROZEN/temp" "$SCRATCH/check2hgi/${STATE}/" || true

# export PYTHONPATH so subprocesses regen spawns (e.g. compute_poi_side_features.py)
# can import `configs` (the main script self-inserts src, but children don't).
export PYTHONPATH="$(pwd)/src:$(pwd)/research${PYTHONPATH:+:$PYTHONPATH}"
OUTPUT_DIR="$SCRATCH" .venv/bin/python scripts/canonical_improvement/regen_emb_t3.py \
  --state "$STATE" --epoch "$EPOCH" "$@"

# sanity: the frozen substrate must be byte-untouched (different OUTPUT_DIR ⇒ it is)
mkdir -p "$DEST"
cp "$SCRATCH/check2hgi/${STATE}/embeddings.parquet" "$DEST/"
cp "$SCRATCH/check2hgi/${STATE}/region_embeddings.parquet" "$DEST/"
echo "[harvest] -> $DEST/{embeddings,region_embeddings}.parquet"
rm -rf "$SCRATCH"
echo "[done] $VARIANT/$STATE"
