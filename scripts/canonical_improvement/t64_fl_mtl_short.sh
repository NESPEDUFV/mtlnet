#!/usr/bin/env bash
# T6.4 FL MTL re-run with --epochs 15 (was 50). The reg head peaks at ep ~5-15
# under the T6.4 substrate then destabilises. joint_score (uses macro F1) is
# blind to reg_top10 collapse. Capping training at ep=15 stops before collapse.
#
# Reuses stashed embeddings from docs/results/canonical_improvement/T6_4_*/florida/
# (deterministic SEED=42 — no need to re-train the encoder).
# Still re-runs generate_next_input_from_checkins to produce next_region.parquet
# from the variant's check-in embeddings.

set -euo pipefail
cd "$(dirname "$0")/../.."

RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t64_fl_mtl_short
mkdir -p "$LOGDIR" "$RESULTS_DIR"

VARIANTS=(two_pass infonce_tau0_5)

# Backup shipping FL once
bak=output/check2hgi/florida.t64_fl_mtl_short_bak
if [ ! -d "$bak" ]; then
    mkdir -p "$bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet \
       "$bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$bak/"
    fi
    echo "[fl-mtl-short] backed up shipping FL to $bak"
fi

for variant in "${VARIANTS[@]}"; do
    stash=${RESULTS_DIR}/T6_4_${variant}/florida
    out_dir=${RESULTS_DIR}/T6_4_${variant}/florida_mtl_ep15
    mkdir -p "$out_dir"

    echo
    echo "================================================================"
    echo "[fl-mtl-short] variant=$variant — restoring stashed emb + regen inputs + MTL@ep15"
    echo "================================================================"
    log_in=${LOGDIR}/T6_4_${variant}_inputs.log
    log_mtl=${LOGDIR}/T6_4_${variant}_mtl.log

    cp "$stash"/poi_embeddings.parquet output/check2hgi/florida/
    cp "$stash"/embeddings.parquet output/check2hgi/florida/
    cp "$stash"/region_embeddings.parquet output/check2hgi/florida/

    echo "[fl-mtl-short] [$(date +%H:%M:%S)] regen next_region.parquet"
    python -c "
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'research')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('Florida', EmbeddingEngine.CHECK2HGI)
" > "$log_in" 2>&1
    echo "[fl-mtl-short] [$(date +%H:%M:%S)] inputs regenerated"

    sentinel="${out_dir}/_sentinel_$(date +%s)"
    touch "$sentinel"
    echo "[fl-mtl-short] [$(date +%H:%M:%S)] launching B9 MTL with --epochs 15"
    python scripts/train.py --task mtl --task-set check2hgi_next_region \
        --state florida --engine check2hgi --seed 42 \
        --epochs 15 --folds 5 --batch-size 2048 \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --scheduler cosine --max-lr 3e-3 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --task-a-input-type checkin --task-b-input-type region \
        --per-fold-transition-dir output/check2hgi/florida \
        > "$log_mtl" 2>&1
    echo "[fl-mtl-short] [$(date +%H:%M:%S)] MTL run complete"

    latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
    if [ -n "$latest" ]; then
        cp -r "$latest" "$out_dir/"
        echo "[fl-mtl-short] snapshotted $latest"
    fi
    rm -f "$sentinel"
done

echo
echo "[fl-mtl-short] restoring shipping FL"
cp "$bak"/poi_embeddings.parquet output/check2hgi/florida/
cp "$bak"/embeddings.parquet output/check2hgi/florida/
cp "$bak"/region_embeddings.parquet output/check2hgi/florida/
if [ -f "$bak"/next_region.parquet ]; then
    cp "$bak"/next_region.parquet output/check2hgi/florida/input/
fi
rm -rf "$bak"
echo "[fl-mtl-short] DONE"
