#!/usr/bin/env bash
# T6.4 τ refinement sweep: --p2r-use-infonce × τ ∈ {0.3, 0.5} × {AL, AZ, FL}.
# τ=0.1 already done in the main T6.4 sweep — this widens the temperature axis
# to see if a softer InfoNCE keeps the FL benefit while easing the AL/AZ leak
# signature (Δlow > +1 pp at AL, ratio compression at AZ).
#
# Stacks on canonical+v3c+T3.2 shipping base.

set -euo pipefail
cd "$(dirname "$0")/../.."

STATES=(alabama arizona florida)
TAUS=(0.3 0.5)
RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t64_tau_sweep
mkdir -p "$LOGDIR" "$RESULTS_DIR"

# Back up shipping per state (or reuse if main sweep's backup still exists)
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t64_tau_sweep_bak
    if [ ! -d "$bak" ]; then
        mkdir -p "$bak"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$bak/"
        if [ -f output/check2hgi/${state}/input/next_region.parquet ]; then
            cp output/check2hgi/${state}/input/next_region.parquet "$bak/"
        fi
        echo "[tau-sweep] backed up $state to $bak"
    fi
done

cell=0
total=$(( ${#STATES[@]} * ${#TAUS[@]} ))
for tau in "${TAUS[@]}"; do
    tau_tag=$(echo "$tau" | tr '.' '_')   # 0.3 → 0_3 (filesystem-safe)
    variant_tag="T6_4_infonce_tau${tau_tag}"
    out_dir=${RESULTS_DIR}/${variant_tag}
    mkdir -p "$out_dir"
    for state in "${STATES[@]}"; do
        cell=$((cell+1))
        echo
        echo "================================================================"
        echo "[tau-sweep $cell/$total] state=$state τ=$tau"
        echo "================================================================"
        log=${LOGDIR}/${variant_tag}_${state}.log
        echo "[tau-sweep] [$(date +%H:%M:%S)] regen embedding"
        SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
            --state "$state" \
            --encoder resln --encoder-dropout 0.0 \
            --scheduler warmup_constant --warmup-pct 0.05 \
            --weight-decay 5e-2 --epoch 500 \
            --p2r-use-infonce --p2r-infonce-temperature "$tau" \
            > "$log" 2>&1
        echo "[tau-sweep] [$(date +%H:%M:%S)] regen complete; stashing emb"
        mkdir -p "$out_dir/$state"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$out_dir/$state/"

        case "$state" in
            florida) g3_extra="--max-pois 20000" ;;
            *) g3_extra="" ;;
        esac
        echo "[tau-sweep] [$(date +%H:%M:%S)] G3 probe"
        python scripts/probe/poi_holdout_probe.py \
            --state "$state" \
            --tag "$variant_tag" \
            $g3_extra \
            >> "$log" 2>&1
    done
done

echo
echo "[tau-sweep] restoring shipping outputs"
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t64_tau_sweep_bak
    cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
    if [ -f "$bak"/next_region.parquet ]; then
        cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
    fi
    rm -rf "$bak"
    echo "[tau-sweep] restored $state"
done

echo "[tau-sweep] DONE — 6 cells. G3 JSONs at ${RESULTS_DIR}/G3_{alabama,arizona,florida}_T6_4_infonce_tau{0_3,0_5}.json"
