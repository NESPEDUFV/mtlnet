#!/usr/bin/env bash
# T6.1 — POI↔POI co-visit InfoNCE 4th boundary λ sweep.
# {AL, AZ, FL} × λ_p2p ∈ {0.05, 0.1, 0.2, 0.3} = 12 cells.
# Each cell: regen embedding (ep=500, force_preprocess=True for covisit_pairs)
# → stash POI emb → run G3 probe with the dual-selector framing gate.
# Stacks on canonical+v3c+T3.2 (the shipping base). Single-seed=42.

set -euo pipefail
cd "$(dirname "$0")/../.."

STATES=(alabama arizona florida)
LAMBDAS=(0.05 0.1 0.2 0.3)
RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t61_sweep
mkdir -p "$LOGDIR" "$RESULTS_DIR"

# Stage 0 — back up shipping outputs (once per state)
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t61_sweep_bak
    if [ ! -d "$bak" ]; then
        mkdir -p "$bak"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$bak/"
        if [ -f output/check2hgi/${state}/input/next_region.parquet ]; then
            cp output/check2hgi/${state}/input/next_region.parquet "$bak/"
        fi
        # T6.1 force_preprocess will rebuild the cache; back it up too so we
        # can restore exact pre-sweep state at the end.
        cp output/check2hgi/${state}/temp/checkin_graph.pt "$bak/"
        echo "[t61-sweep] backed up $state to $bak"
    else
        echo "[t61-sweep] reusing existing backup at $bak"
    fi
done

# Stage 1 — sweep
cell=0
total=$(( ${#STATES[@]} * ${#LAMBDAS[@]} ))
for lam in "${LAMBDAS[@]}"; do
    lam_tag=$(echo "$lam" | tr '.' '_')      # 0.05 → 0_05
    variant_tag="T6_1_lambda${lam_tag}"
    out_dir=${RESULTS_DIR}/${variant_tag}
    mkdir -p "$out_dir"
    for state in "${STATES[@]}"; do
        cell=$((cell+1))
        echo
        echo "================================================================"
        echo "[t61-sweep $cell/$total] state=$state λ=$lam (tag=$variant_tag)"
        echo "================================================================"
        log=${LOGDIR}/${variant_tag}_${state}.log
        echo "[t61-sweep] [$(date +%H:%M:%S)] regen embedding (ep=500, p2p_lambda=$lam)"
        SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
            --state "$state" \
            --encoder resln --encoder-dropout 0.0 \
            --scheduler warmup_constant --warmup-pct 0.05 \
            --weight-decay 5e-2 --epoch 500 \
            --p2p-lambda "$lam" --p2p-temperature 0.1 \
            --p2p-batch-size 1024 --p2p-covisit-k 3 \
            > "$log" 2>&1
        echo "[t61-sweep] [$(date +%H:%M:%S)] regen complete; stashing emb"
        mkdir -p "$out_dir/$state"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$out_dir/$state/"

        case "$state" in
            florida) g3_extra="--max-pois 20000" ;;
            *) g3_extra="" ;;
        esac
        echo "[t61-sweep] [$(date +%H:%M:%S)] G3 probe"
        python scripts/probe/poi_holdout_probe.py \
            --state "$state" \
            --tag "$variant_tag" \
            $g3_extra \
            >> "$log" 2>&1
    done
done

# Stage 2 — restore shipping outputs + clean up backups
echo
echo "[t61-sweep] restoring shipping outputs"
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t61_sweep_bak
    cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/checkin_graph.pt output/check2hgi/${state}/temp/
    if [ -f "$bak"/next_region.parquet ]; then
        cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
    fi
    rm -rf "$bak"
    echo "[t61-sweep] restored $state"
done

echo
echo "[t61-sweep] DONE — 12 cells. Artefacts:"
echo "  emb stashes:   ${RESULTS_DIR}/T6_1_lambda{0_05,0_1,0_2,0_3}/{alabama,arizona,florida}/"
echo "  G3 JSONs:      ${RESULTS_DIR}/G3_{alabama,arizona,florida}_T6_1_lambda{0_05,0_1,0_2,0_3}.json"
echo "  per-cell logs: ${LOGDIR}/T6_1_lambda*.log"
