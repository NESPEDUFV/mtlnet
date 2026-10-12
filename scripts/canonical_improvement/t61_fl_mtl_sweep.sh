#!/usr/bin/env bash
# T6.1 FL MTL evaluation — canonical B9 ep=50 single-seed=42 for each λ.
# Reuses stashed embeddings from docs/results/canonical_improvement/T6_1_lambda*/
# (deterministic at SEED=42; no need to re-train check2hgi).
# Regenerates only next_region.parquet from the variant's check-in embeddings.
#
# Compared against the matched-protocol shipping FL ep=50 ss=42 baseline at
# docs/results/canonical_improvement/shipping_florida_mtl_ep50_seed42/.

set -euo pipefail
cd "$(dirname "$0")/../.."

RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t61_fl_mtl
mkdir -p "$LOGDIR"

LAMBDAS=(0_05 0_1 0_2 0_3)

# Backup shipping FL once at start
bak=output/check2hgi/florida.t61_fl_mtl_bak
if [ ! -d "$bak" ]; then
    mkdir -p "$bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet \
       "$bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$bak/"
    fi
    echo "[t61-fl-mtl] backed up shipping FL outputs to $bak"
fi

cell=0
for lam_tag in "${LAMBDAS[@]}"; do
    cell=$((cell+1))
    stash=${RESULTS_DIR}/T6_1_lambda${lam_tag}/florida
    out_dir=${RESULTS_DIR}/T6_1_lambda${lam_tag}/florida_mtl
    mkdir -p "$out_dir"

    echo
    echo "================================================================"
    echo "[t61-fl-mtl $cell/${#LAMBDAS[@]}] λ_tag=${lam_tag}"
    echo "================================================================"
    log_in=${LOGDIR}/T6_1_lambda${lam_tag}_inputs.log
    log_mtl=${LOGDIR}/T6_1_lambda${lam_tag}_mtl.log

    # Restore the variant's stashed embeddings
    cp "$stash"/poi_embeddings.parquet output/check2hgi/florida/
    cp "$stash"/embeddings.parquet output/check2hgi/florida/
    cp "$stash"/region_embeddings.parquet output/check2hgi/florida/

    echo "[t61-fl-mtl] [$(date +%H:%M:%S)] regen next_region.parquet for variant"
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
    echo "[t61-fl-mtl] [$(date +%H:%M:%S)] launching canonical B9 MTL ep=50 single-seed=42"
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
    echo "[t61-fl-mtl] [$(date +%H:%M:%S)] MTL run complete"

    latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
    if [ -n "$latest" ]; then
        cp -r "$latest" "$out_dir/"
        echo "[t61-fl-mtl] snapshotted $latest"
    fi
    rm -f "$sentinel"
done

# Restore shipping FL
echo
echo "[t61-fl-mtl] restoring shipping FL outputs"
cp "$bak"/poi_embeddings.parquet output/check2hgi/florida/
cp "$bak"/embeddings.parquet output/check2hgi/florida/
cp "$bak"/region_embeddings.parquet output/check2hgi/florida/
if [ -f "$bak"/next_region.parquet ]; then
    cp "$bak"/next_region.parquet output/check2hgi/florida/input/
fi
rm -rf "$bak"
echo "[t61-fl-mtl] DONE — 4 MTL runs complete"
