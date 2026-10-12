#!/usr/bin/env bash
# T6.3 — low-rank per-POI bias at Checkin2POI attention-logit.
# Per advisor (2026-05-19): AL/AZ kill-check FIRST. Run AL+AZ first; only if
# both pass §6.5 (no -0.5 pp reg kill on the substrate) AND G3 (low-visit Δ
# ≤ +1 pp at both states) do we promote to FL. Single-seed=42 throughout.
# 2 ranks × 2 small states = 4 emb cells in stage 1; +2 FL cells in stage 2
# if stage 1 passes. ~12 min stage 1, ~10 min stage 2 wall, sequential.

set -euo pipefail
cd "$(dirname "$0")/../.."

RANKS=(4 8)
SMALL_STATES=(alabama arizona)
RESULTS_DIR=docs/results/canonical_improvement
LOGDIR=logs/t63_sweep
mkdir -p "$LOGDIR" "$RESULTS_DIR"

# Stage 0 — backup small-state shipping outputs
for state in "${SMALL_STATES[@]}"; do
    bak=output/check2hgi/${state}.t63_sweep_bak
    if [ ! -d "$bak" ]; then
        mkdir -p "$bak"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet "$bak/"
        cp output/check2hgi/${state}/temp/checkin_graph.pt "$bak/"
        if [ -f output/check2hgi/${state}/input/next_region.parquet ]; then
            cp output/check2hgi/${state}/input/next_region.parquet "$bak/"
        fi
        echo "[t63-sweep] backed up $state"
    fi
done

# Stage 1 — AL + AZ at both ranks, emb regen + G3 only (no MTL here)
cell=0
total_stage1=$(( ${#RANKS[@]} * ${#SMALL_STATES[@]} ))
for rank in "${RANKS[@]}"; do
    variant_tag="T6_3_r${rank}"
    out_dir=${RESULTS_DIR}/${variant_tag}
    mkdir -p "$out_dir"
    for state in "${SMALL_STATES[@]}"; do
        cell=$((cell+1))
        echo
        echo "================================================================"
        echo "[t63-sweep stage1 $cell/$total_stage1] state=$state r=$rank"
        echo "================================================================"
        log=${LOGDIR}/${variant_tag}_${state}.log
        echo "[t63-sweep] [$(date +%H:%M:%S)] emb regen (ep=500, t63 r=$rank)"
        SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
            --state "$state" \
            --encoder resln --encoder-dropout 0.0 \
            --scheduler warmup_constant --warmup-pct 0.05 \
            --weight-decay 5e-2 --epoch 500 \
            --t63-enabled --t63-rank "$rank" \
            > "$log" 2>&1
        echo "[t63-sweep] [$(date +%H:%M:%S)] regen done; stashing emb"
        mkdir -p "$out_dir/$state"
        cp output/check2hgi/${state}/poi_embeddings.parquet \
           output/check2hgi/${state}/embeddings.parquet \
           output/check2hgi/${state}/region_embeddings.parquet \
           "$out_dir/$state/"
        echo "[t63-sweep] [$(date +%H:%M:%S)] G3 probe"
        python scripts/probe/poi_holdout_probe.py \
            --state "$state" \
            --tag "${variant_tag}" \
            >> "$log" 2>&1
    done
done

# Stage 1 gate evaluation
echo
echo "================================================================"
echo "[t63-sweep] stage 1 done. Checking AL/AZ G3 gates before FL stage 2."
echo "================================================================"
python -c "
import json, sys
RES = 'docs/results/canonical_improvement'
ship = {}
for s in ['alabama','arizona']:
    with open(f'{RES}/G3_{s}_shipping.json') as f: ship[s] = json.load(f)['summary']
print(f'{\"state\":<10} {\"r\":<3} {\"lowq25 Δ\":>10} {\"hi/lo\":>7} {\"hi/lo shipping\":>14} {\"gate\":>5}')
print('-'*55)
ok = True
for r in [4, 8]:
    for s in ['alabama','arizona']:
        with open(f'{RES}/G3_{s}_T6_3_r{r}.json') as f:
            v = json.load(f)['summary']
        b_lo = ship[s]['low_visit_q25']['top1']['mean']*100
        b_ratio = ship[s]['high_visit_q75']['top1']['mean']/ship[s]['low_visit_q25']['top1']['mean']
        dlow = v['low_visit_q25']['top1']['mean']*100 - b_lo
        ratio = v['high_visit_q75']['top1']['mean']/v['low_visit_q25']['top1']['mean']
        gate = '✓' if (dlow <= 1.0 and ratio >= b_ratio) else '✗'
        if gate == '✗': ok = False
        print(f'{s:<10} {r:<3} {dlow:>+8.2f} {ratio:>5.2f}x  {b_ratio:>10.2f}x {gate:>5}')
print()
if not ok:
    print('[t63-sweep] STAGE 1 GATE FAILED: at least one cell trips the G3 gate.')
    print('[t63-sweep] Per advisor pre-registration, T6.3 STOPS HERE. No FL stage.')
    sys.exit(1)
print('[t63-sweep] All AL/AZ cells pass G3 gates.')
sys.exit(0)
" 2>&1 | tee -a "${LOGDIR}/_gate_check.log"

GATE_RC=$?
if [ "$GATE_RC" -ne 0 ]; then
    echo "[t63-sweep] Gate failed — restoring shipping and exiting."
    for state in "${SMALL_STATES[@]}"; do
        bak=output/check2hgi/${state}.t63_sweep_bak
        cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
        cp "$bak"/embeddings.parquet output/check2hgi/${state}/
        cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
        cp "$bak"/checkin_graph.pt output/check2hgi/${state}/temp/
        if [ -f "$bak"/next_region.parquet ]; then
            cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
        fi
        rm -rf "$bak"
    done
    exit 1
fi

# Stage 2 — FL r=4, r=8
fl_bak=output/check2hgi/florida.t63_sweep_bak
if [ ! -d "$fl_bak" ]; then
    mkdir -p "$fl_bak"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet "$fl_bak/"
    cp output/check2hgi/florida/temp/checkin_graph.pt "$fl_bak/"
    if [ -f output/check2hgi/florida/input/next_region.parquet ]; then
        cp output/check2hgi/florida/input/next_region.parquet "$fl_bak/"
    fi
fi
for rank in "${RANKS[@]}"; do
    variant_tag="T6_3_r${rank}"
    out_dir=${RESULTS_DIR}/${variant_tag}
    mkdir -p "$out_dir"
    echo
    echo "================================================================"
    echo "[t63-sweep stage2] state=florida r=$rank"
    echo "================================================================"
    log=${LOGDIR}/${variant_tag}_florida.log
    echo "[t63-sweep] [$(date +%H:%M:%S)] FL emb regen (ep=500, t63 r=$rank)"
    SEED=42 python scripts/canonical_improvement/regen_emb_t3.py \
        --state florida \
        --encoder resln --encoder-dropout 0.0 \
        --scheduler warmup_constant --warmup-pct 0.05 \
        --weight-decay 5e-2 --epoch 500 \
        --t63-enabled --t63-rank "$rank" \
        > "$log" 2>&1
    mkdir -p "$out_dir/florida"
    cp output/check2hgi/florida/poi_embeddings.parquet \
       output/check2hgi/florida/embeddings.parquet \
       output/check2hgi/florida/region_embeddings.parquet \
       "$out_dir/florida/"
    echo "[t63-sweep] [$(date +%H:%M:%S)] FL G3 probe"
    python scripts/probe/poi_holdout_probe.py \
        --state florida --tag "${variant_tag}" --max-pois 20000 \
        >> "$log" 2>&1

    # FL MTL ep=50 single-seed=42
    out_mtl=${out_dir}/florida_mtl
    mkdir -p "$out_mtl"
    log_mtl=${LOGDIR}/${variant_tag}_florida_mtl.log
    sentinel="${out_mtl}/_sentinel_$(date +%s)"
    touch "$sentinel"
    echo "[t63-sweep] [$(date +%H:%M:%S)] FL MTL ep=50"
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
    echo "[t63-sweep] [$(date +%H:%M:%S)] MTL done"
    latest=$(find results/check2hgi/florida -maxdepth 1 -type d -newer "$sentinel" -name 'mtlnet_*' | head -1)
    if [ -n "$latest" ]; then cp -r "$latest" "$out_mtl/"; fi
    rm -f "$sentinel"
done

# Restore all
echo "[t63-sweep] restoring shipping"
for state in "${SMALL_STATES[@]}" florida; do
    bak=output/check2hgi/${state}.t63_sweep_bak
    [ -d "$bak" ] || continue
    cp "$bak"/poi_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/region_embeddings.parquet output/check2hgi/${state}/
    cp "$bak"/checkin_graph.pt output/check2hgi/${state}/temp/
    if [ -f "$bak"/next_region.parquet ]; then
        cp "$bak"/next_region.parquet output/check2hgi/${state}/input/
    fi
    rm -rf "$bak"
done
echo "[t63-sweep] DONE"
