#!/usr/bin/env bash
# T6.2 — composite C3 edge-weight sweep.
# {AL, AZ, FL} × (alpha_delaunay, w_r) ∈ {1.5, 2.0} × {0.3, 0.5} = 12 cells.
# Each cell: regen embedding (ep=500, force_preprocess=True for C3 weights)
# → G3 probe with dual-selector gate. Stacks on canonical+v3c+T3.2.

set -euo pipefail
cd "$(dirname "$0")/../.."

STATES=(alabama arizona florida)
declare -a CELLS=("1.5_0.3" "1.5_0.5" "2.0_0.3" "2.0_0.5")
RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t62_sweep
mkdir -p "$LOGDIR" "$RESULTS_DIR"

# Stage 0 — backup shipping per state
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t62_sweep_bak
    if [ ! -d "$bak" ]; then
        mkdir -p "$bak"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$bak/"
        if [ -f output/check2hgi/${state}/input/next_region.parquet ]; then
            cp output/check2hgi/${state}/input/next_region.parquet "$bak/"
        fi
        cp output/check2hgi/${state}/temp/checkin_graph.pt "$bak/"
        echo "[t62-sweep] backed up $state to $bak"
    fi
done

cell=0
total=$(( ${#STATES[@]} * ${#CELLS[@]} ))
for cell_id in "${CELLS[@]}"; do
    alpha=$(echo "$cell_id" | cut -d_ -f1)
    wr=$(echo "$cell_id" | cut -d_ -f2)
    cell_tag=$(echo "$cell_id" | tr '.' '_')   # 1.5_0.3 → 1_5_0_3
    variant_tag="T6_2_a${cell_tag}"
    out_dir=${RESULTS_DIR}/${variant_tag}
    mkdir -p "$out_dir"
    for state in "${STATES[@]}"; do
        cell=$((cell+1))
        echo
        echo "================================================================"
        echo "[t62-sweep $cell/$total] state=$state alpha_delaunay=$alpha w_r=$wr (tag=$variant_tag)"
        echo "================================================================"
        log=${LOGDIR}/${variant_tag}_${state}.log
        echo "[t62-sweep] [$(date +%H:%M:%S)] regen embedding"
        SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
            --state "$state" \
            --encoder resln --encoder-dropout 0.0 \
            --scheduler warmup_constant --warmup-pct 0.05 \
            --weight-decay 5e-2 --epoch 500 \
            --c3-alpha-delaunay "$alpha" --c3-w-r "$wr" \
            > "$log" 2>&1
        echo "[t62-sweep] [$(date +%H:%M:%S)] regen complete; stashing emb"
        mkdir -p "$out_dir/$state"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$out_dir/$state/"

        case "$state" in
            florida) g3_extra="--max-pois 20000" ;;
            *) g3_extra="" ;;
        esac
        echo "[t62-sweep] [$(date +%H:%M:%S)] G3 probe"
        python scripts/probe/poi_holdout_probe.py \
            --state "$state" \
            --tag "$variant_tag" \
            $g3_extra \
            >> "$log" 2>&1
    done
done

# Stage 2 — restore
echo
echo "[t62-sweep] restoring shipping outputs"
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t62_sweep_bak
    cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/checkin_graph.pt output/check2hgi/${state}/temp/
    if [ -f "$bak"/next_region.parquet ]; then
        cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
    fi
    rm -rf "$bak"
    echo "[t62-sweep] restored $state"
done

echo "[t62-sweep] DONE — 12 cells. Artefacts under ${RESULTS_DIR}/T6_2_*."
