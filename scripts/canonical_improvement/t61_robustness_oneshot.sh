#!/usr/bin/env bash
# T6.1 implementation-robustness one-shot at FL.
# Per advisor 2026-05-19: test whether the original T6.1 null was an
# implementation artefact. Three knobs flipped vs original T6.1 sweep:
#   B = 4096       (vs 1024)        — wider in-batch negative pool
#   tau = 0.3      (vs 0.1)         — softer InfoNCE temperature
#   --p2p-no-dedup (vs dedup)       — multiplicity-weighted pair sampling
#   --p2p-symmetric (vs asymmetric) — SimCLR-style symmetric loss
# All four changes together to test whether implementation matters; if positive
# we follow up with single-knob ablations.
# lambda_p2p = 0.2 (the strongest cell from the original sweep at FL).
# FL only, single-seed=42, ep=500 emb + ep=50 MTL.

set -euo pipefail
cd "$(dirname "$0")/../.."

RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t61_robustness_oneshot
mkdir -p "$LOGDIR"

bak=output/check2hgi/florida.t61_robustness_bak
if [ ! -d "$bak" ]; then
    mkdir -p "$bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet \
       "$bak/"
    cp output/check2hgi/florida/temp/checkin_graph.pt "$bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$bak/"
    fi
    echo "[t61-robust] backed up shipping FL"
fi

variant_tag=T6_1_robustness_lambda0_2
out_dir=${RESULTS_DIR}/${variant_tag}
mkdir -p "$out_dir/florida"

log_emb=${LOGDIR}/${variant_tag}_florida_emb.log
log_mtl=${LOGDIR}/${variant_tag}_florida_mtl.log

echo
echo "================================================================"
echo "[t61-robust] FL one-shot: lambda=0.2 B=4096 tau=0.3 no_dedup symmetric"
echo "================================================================"
echo "[t61-robust] [$(date +%H:%M:%S)] regen embedding (ep=500)"
SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
    --state florida \
    --encoder resln --encoder-dropout 0.0 \
    --scheduler warmup_constant --warmup-pct 0.05 \
    --weight-decay 5e-2 --epoch 500 \
    --p2p-lambda 0.2 --p2p-temperature 0.3 --p2p-batch-size 4096 --p2p-covisit-k 3 \
    --p2p-no-dedup --p2p-symmetric \
    > "$log_emb" 2>&1
echo "[t61-robust] [$(date +%H:%M:%S)] regen done; stashing emb"
cp output/check2hgi/florida/poi_embeddings.parquet \
   output/check2hgi/florida/embeddings.parquet \
   output/check2hgi/florida/region_embeddings.parquet \
   "$out_dir/florida/"

echo "[t61-robust] [$(date +%H:%M:%S)] G3 probe (FL, 20K subsample)"
python scripts/probe/poi_holdout_probe.py \
    --state florida \
    --tag "${variant_tag}" \
    --max-pois 20000 \
    >> "$log_emb" 2>&1

sentinel="${out_dir}/_sentinel_$(date +%s)"
touch "$sentinel"
echo "[t61-robust] [$(date +%H:%M:%S)] MTL ep=50 single-seed=42 (canonical B9)"
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
echo "[t61-robust] [$(date +%H:%M:%S)] MTL done"

latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
if [ -n "$latest" ]; then
    mkdir -p "$out_dir/florida_mtl"
    cp -r "$latest" "$out_dir/florida_mtl/"
    echo "[t61-robust] snapshotted $latest"
fi
rm -f "$sentinel"

echo "[t61-robust] restoring shipping FL"
cp "$bak"/poi_embeddings.parquet output/check2hgi/florida/
cp "$bak"/embeddings.parquet output/check2hgi/florida/
cp "$bak"/region_embeddings.parquet output/check2hgi/florida/
cp "$bak"/checkin_graph.pt output/check2hgi/florida/temp/
if [ -f "$bak"/next_region.parquet ]; then
    cp "$bak"/next_region.parquet output/check2hgi/florida/input/
fi
rm -rf "$bak"
echo "[t61-robust] DONE"
