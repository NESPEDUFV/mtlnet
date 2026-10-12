#!/usr/bin/env bash
# T6.4 ep=500 sweep — {two_pass, infonce, both} × {AL, AZ, FL}, seed=42.
# Stacks on canonical+v3c+T3.2 shipping base.
#
# Workflow per cell:
#   1. backup current output/check2hgi/{state}/ (POI/checkin/region parquet)
#      → done ONCE at sweep start in alabama.t64_sweep_bak/ etc.
#   2. regen_emb_t3.py with variant flags (overwrites output/check2hgi/{state}/)
#   3. stash POI embedding to docs/results/canonical_improvement/T6_4_{variant}/{state}/
#   4. G3 probe with --tag T6_4_{variant} (writes G3_{state}_T6_4_{variant}.json)
# End-of-sweep:
#   - restore the once-only backup to output/check2hgi/{state}/
#   - delete .t64_sweep_bak/

set -euo pipefail
cd "$(dirname "$0")/../.."  # repo root

STATES=(alabama arizona florida)
VARIANTS=(two_pass infonce both)
RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t64_sweep
mkdir -p "$LOGDIR" "$RESULTS_DIR"

flags_for_variant() {
    case "$1" in
        two_pass) echo "--two-pass-corruption" ;;
        infonce)  echo "--p2r-use-infonce --p2r-infonce-temperature 0.1" ;;
        both)     echo "--p2r-use-infonce --p2r-infonce-temperature 0.1 --two-pass-corruption" ;;
        *) echo "unknown variant: $1" >&2; exit 1 ;;
    esac
}

# ------------------------------------------------------------------
# Stage 0 — back up shipping outputs (once per state)
# ------------------------------------------------------------------
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t64_sweep_bak
    if [ ! -d "$bak" ]; then
        mkdir -p "$bak"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$bak/"
        # next_region.parquet also gets regenerated → back it up too
        if [ -f output/check2hgi/${state}/input/next_region.parquet ]; then
            cp output/check2hgi/${state}/input/next_region.parquet "$bak/"
        fi
        echo "[sweep] backed up $state shipping outputs to $bak"
    else
        echo "[sweep] reusing existing backup at $bak"
    fi
done

# ------------------------------------------------------------------
# Stage 1 — run all 9 cells
# ------------------------------------------------------------------
total=$(( ${#STATES[@]} * ${#VARIANTS[@]} ))
cell=0
for variant in "${VARIANTS[@]}"; do
    variant_flags=$(flags_for_variant "$variant")
    out_dir=${RESULTS_DIR}/T6_4_${variant}
    mkdir -p "$out_dir"
    for state in "${STATES[@]}"; do
        cell=$((cell+1))
        echo
        echo "================================================================"
        echo "[sweep $cell/$total] variant=$variant state=$state flags=$variant_flags"
        echo "================================================================"
        log=${LOGDIR}/T6_4_${variant}_${state}.log
        ts=$(date +%H:%M:%S)
        echo "[sweep] [$ts] regen embedding"
        SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
            --state "$state" \
            --encoder resln --encoder-dropout 0.0 \
            --scheduler warmup_constant --warmup-pct 0.05 \
            --weight-decay 5e-2 --epoch 500 \
            $variant_flags \
            > "$log" 2>&1
        echo "[sweep] [$(date +%H:%M:%S)] regen complete; stashing emb"
        mkdir -p "$out_dir/$state"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$out_dir/$state/"

        echo "[sweep] [$(date +%H:%M:%S)] G3 probe"
        case "$state" in
            florida) g3_extra="--max-pois 20000" ;;
            *) g3_extra="" ;;
        esac
        python scripts/probe/poi_holdout_probe.py \
            --state "$state" \
            --tag T6_4_${variant} \
            $g3_extra \
            >> "$log" 2>&1
    done
done

# ------------------------------------------------------------------
# Stage 2 — restore shipping baselines + clean up
# ------------------------------------------------------------------
echo
echo "[sweep] restoring shipping outputs"
for state in "${STATES[@]}"; do
    bak=output/check2hgi/${state}.t64_sweep_bak
    cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
    if [ -f "$bak"/next_region.parquet ]; then
        cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
    fi
    rm -rf "$bak"
    echo "[sweep] restored $state"
done

echo
echo "[sweep] DONE — 9 cells complete. Artefacts:"
echo "  emb backups:   ${RESULTS_DIR}/T6_4_{two_pass,infonce,both}/{alabama,arizona,florida}/"
echo "  G3 JSONs:      ${RESULTS_DIR}/G3_{alabama,arizona,florida}_T6_4_{two_pass,infonce,both}.json"
echo "  per-cell logs: ${LOGDIR}/T6_4_*.log"
