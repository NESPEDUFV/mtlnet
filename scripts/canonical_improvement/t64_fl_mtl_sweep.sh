#!/usr/bin/env bash
# T6.4 FL MTL evaluation — canonical B9 invocation on the two G3-clean FL
# candidates from the τ-refinement sweep: --two-pass-corruption (no τ knob)
# and --p2r-use-infonce τ=0.5 (winning τ across states).
#
# For each variant:
#   1. backup shipping FL outputs (once at start)
#   2. regen FL embedding with variant flags (overwrites output/check2hgi/florida/)
#   3. run scripts/train.py canonical B9 invocation
#   4. snapshot the resulting results/check2hgi/florida/mtlnet_*/ run-dir into
#      docs/results/canonical_improvement/T6_4_{variant}/florida_mtl/
# end: restore shipping FL.

set -euo pipefail
cd "$(dirname "$0")/../.."

RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t64_fl_mtl
mkdir -p "$LOGDIR" "$RESULTS_DIR"

declare -A FLAGS=(
    [two_pass]="--two-pass-corruption"
    [infonce_tau0_5]="--p2r-use-infonce --p2r-infonce-temperature 0.5"
)
VARIANTS=(two_pass infonce_tau0_5)

# Backup once
bak=output/check2hgi/florida.t64_fl_mtl_bak
if [ ! -d "$bak" ]; then
    mkdir -p "$bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet \
       "$bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$bak/"
    fi
    echo "[fl-mtl] backed up shipping FL outputs to $bak"
fi

cell=0
for variant in "${VARIANTS[@]}"; do
    cell=$((cell+1))
    flags=${FLAGS[$variant]}
    out_dir=${RESULTS_DIR}/T6_4_${variant}/florida_mtl
    mkdir -p "$out_dir"

    echo
    echo "================================================================"
    echo "[fl-mtl $cell/${#VARIANTS[@]}] variant=$variant flags=$flags"
    echo "================================================================"
    log_emb=${LOGDIR}/T6_4_${variant}_florida_emb.log
    log_mtl=${LOGDIR}/T6_4_${variant}_florida_mtl.log

    echo "[fl-mtl] [$(date +%H:%M:%S)] regen embedding (also regens next_region.parquet)"
    SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
        --state florida \
        --encoder resln --encoder-dropout 0.0 \
        --scheduler warmup_constant --warmup-pct 0.05 \
        --weight-decay 5e-2 --epoch 500 \
        $flags \
        > "$log_emb" 2>&1
    echo "[fl-mtl] [$(date +%H:%M:%S)] regen complete"

    echo "[fl-mtl] [$(date +%H:%M:%S)] launching canonical B9 MTL on FL"
    # Sentinel before the run so we can identify which run dir is fresh.
    sentinel="${out_dir}/_sentinel_$(date +%s)"
    touch "$sentinel"
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
    echo "[fl-mtl] [$(date +%H:%M:%S)] MTL run complete; snapshotting results"

    # Find the run dir created since the sentinel touch.
    latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
    if [ -z "$latest" ]; then
        echo "[fl-mtl] WARNING: no fresh run dir found for $variant"
    else
        echo "[fl-mtl] copying $latest → $out_dir/"
        cp -r "$latest" "$out_dir/"
    fi
    rm -f "$sentinel"
done

echo
echo "[fl-mtl] restoring shipping FL outputs"
cp "$bak"/poi_embeddings.parquet output/check2hgi/florida/
cp "$bak"/embeddings.parquet output/check2hgi/florida/
cp "$bak"/region_embeddings.parquet output/check2hgi/florida/
if [ -f "$bak"/next_region.parquet ]; then
    cp "$bak"/next_region.parquet output/check2hgi/florida/input/
fi
rm -rf "$bak"
echo "[fl-mtl] DONE"
