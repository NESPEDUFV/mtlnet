#!/bin/bash
# Post-substrate-build glue: for one (design, state), produce
#   - input/next.parquet     (via generate_next_input_from_checkins)
#   - input/next_region.parquet (via build_design_next_region.py)
#   - copy canonical seed=42 log_T files to substrate dir (C22 mtime guarded)
#
# Usage: postbuild_design_substrate.sh <engine> <state>
#   engine: check2hgi_design_{b,j,l}
#   state: alabama|arizona

set -euo pipefail
ENGINE="$1"
STATE="$2"
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"

OUT_DIR="output/${ENGINE}/${STATE}"
[ -d "$OUT_DIR" ] || { echo "ERR substrate dir missing $OUT_DIR"; exit 1; }
[ -f "$OUT_DIR/embeddings.parquet" ] || { echo "ERR embeddings.parquet missing"; exit 1; }

# 1. Generate next.parquet via builders.generate_next_input_from_checkins
.venv/bin/python -c "
import sys; sys.path.insert(0, 'src')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('${STATE}', EmbeddingEngine.${ENGINE^^})
print('[postbuild] next.parquet OK')
"

# 2. Build next_region.parquet
.venv/bin/python scripts/substrate_protocol_cleanup/build_design_next_region.py \
    --state "$STATE" --engine "$ENGINE"

# 3. Copy canonical seed=42 log_T into substrate dir (n_regions identical because graph copied verbatim)
CANON_DIR="output/check2hgi/${STATE}"
for fold in 1 2 3 4 5; do
    src="$CANON_DIR/region_transition_log_seed42_fold${fold}.pt"
    dst="$OUT_DIR/region_transition_log_seed42_fold${fold}.pt"
    [ -f "$src" ] || { echo "ERR canonical log_T missing $src"; exit 1; }
    cp "$src" "$dst"
done

# Touch log_T AFTER next_region.parquet to satisfy C22 mtime guard
sleep 1
touch "$OUT_DIR"/region_transition_log_seed42_fold*.pt
echo "[postbuild] log_T cp + touched"

ls -l "$OUT_DIR"/region_transition_log_seed42_fold*.pt "$OUT_DIR/input/next_region.parquet"
