#!/usr/bin/env bash
# T6.2 FL MTL evaluation — canonical B9 ep=50 single-seed=42 for each cell.
# Reuses stashed embeddings from docs/results/canonical_improvement/T6_2_a*/florida/.
# Regenerates only next_region.parquet from the variant's check-in embeddings.

set -euo pipefail
cd "$(dirname "$0")/../.."

RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t62_fl_mtl
mkdir -p "$LOGDIR"

CELLS=(1_5_0_3 1_5_0_5 2_0_0_3 2_0_0_5)

bak=output/check2hgi/florida.t62_fl_mtl_bak
if [ ! -d "$bak" ]; then
    mkdir -p "$bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet "$bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$bak/"
    fi
    echo "[t62-fl-mtl] backed up shipping FL"
fi

cell=0
for cell_tag in "${CELLS[@]}"; do
    cell=$((cell+1))
    stash=${RESULTS_DIR}/T6_2_a${cell_tag}/florida
    out_dir=${RESULTS_DIR}/T6_2_a${cell_tag}/florida_mtl
    mkdir -p "$out_dir"

    echo
    echo "================================================================"
    echo "[t62-fl-mtl $cell/${#CELLS[@]}] cell=$cell_tag"
    echo "================================================================"
    log_in=${LOGDIR}/T6_2_a${cell_tag}_inputs.log
    log_mtl=${LOGDIR}/T6_2_a${cell_tag}_mtl.log

    cp "$stash"/poi_embeddings.parquet output/check2hgi/florida/
    cp "$stash"/embeddings.parquet output/check2hgi/florida/
    cp "$stash"/region_embeddings.parquet output/check2hgi/florida/

    echo "[t62-fl-mtl] [$(date +%H:%M:%S)] regen next_region.parquet"
    python -c "
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'research')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('Florida', EmbeddingEngine.CHECK2HGI)
" > "$log_in" 2>&1

    sentinel="${out_dir}/_sentinel_$(date +%s)"
    touch "$sentinel"
    echo "[t62-fl-mtl] [$(date +%H:%M:%S)] MTL ep=50 ss=42"
    python scripts/train.py --task mtl --task-set check2hgi_next_region \
        --state florida --engine check2hgi --seed 42 \
        --epochs 50 --folds 5 --batch-size 2048 \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --scheduler cosine --max-lr 3e-3 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --task-a-input-type checkin --task-b-input-type region \
        --per-fold-transition-dir output/check2hgi/florida \
        > "$log_mtl" 2>&1
    echo "[t62-fl-mtl] [$(date +%H:%M:%S)] MTL done"

    latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
    if [ -n "$latest" ]; then
        cp -r "$latest" "$out_dir/"
        echo "[t62-fl-mtl] snapshotted $latest"
    fi
    rm -f "$sentinel"
done

echo
echo "[t62-fl-mtl] restoring shipping FL"
cp "$bak"/poi_embeddings.parquet output/check2hgi/florida/
cp "$bak"/embeddings.parquet output/check2hgi/florida/
cp "$bak"/region_embeddings.parquet output/check2hgi/florida/
if [ -f "$bak"/next_region.parquet ]; then
    cp "$bak"/next_region.parquet output/check2hgi/florida/input/
fi
rm -rf "$bak"
echo "[t62-fl-mtl] DONE"
