#!/usr/bin/env bash
# T1.5 — optimizer hygiene sweep on canonical Check2HGI.
# Three single-factor + one stacked variants at AL+AZ.
#
# Variants:
#   v1: + 5% warmup (warmup_constant scheduler)
#   v2: cosine 1e-3 → 1e-5 (no warmup)
#   v3a: AdamW wd=1e-3
#   v3b: AdamW wd=1e-2
#   v3c: AdamW wd=5e-2
#   v4: stacked = best-of-each (decided after v1/v2/v3 land)
#
# Per variant:
#   1. Regen AL embeddings with custom hygiene flags (cuda)
#   2. Regen AZ embeddings
#   3. Rebuild next_region.parquet + per-fold log_T for both
#   4. Launch MTL B9full AL+AZ in parallel
#   5. Record metrics + leak probe via T1-5_record.py
#
# Run from worktree (or main repo) with venv active.

set -uo pipefail

LOG_ROOT=/home/vitor.oliveira/PoiMtlNet/logs
RESULTS_ROOT=/home/vitor.oliveira/PoiMtlNet/docs/results/canonical_improvement
mkdir -p "$RESULTS_ROOT"

# Variant rows: tag | scheduler | warmup_pct | weight_decay
declare -a VARIANTS=(
    "v1_warmup5  warmup_constant  0.05  0"
    "v2_cosine   cosine           0     0"
    "v3a_wd1e3   step             0     1e-3"
    "v3b_wd1e2   step             0     1e-2"
    "v3c_wd5e2   step             0     5e-2"
)

regen_one() {
    local state=$1 sched=$2 warmup=$3 wd=$4 tag=$5
    python docs/infra/a40/regen_emb_t15.py --state "$state" \
        --scheduler "$sched" --warmup-pct "$warmup" --weight-decay "$wd" \
        > "${LOG_ROOT}/T1-5_REGEN_${tag}_${state}_${TS}.log" 2>&1
}

train_one_state() {
    local state=$1 tag=$2
    python scripts/train.py \
        --task mtl --task-set check2hgi_next_region \
        --state "$state" --engine check2hgi --seed 42 \
        --epochs 50 --folds 5 --batch-size 2048 \
        --model mtlnet_crossattn \
        --mtl-loss static_weight --category-weight 0.75 \
        --scheduler cosine --max-lr 3e-3 \
        --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
        --cat-head next_gru --reg-head next_getnext_hard \
        --task-a-input-type checkin --task-b-input-type region \
        --per-fold-transition-dir "output/check2hgi/${state}" \
        > "${LOG_ROOT}/T1-5_MTL_${tag}_${state}_${TS}.log" 2>&1
}

for row in "${VARIANTS[@]}"; do
    read -r TAG SCHED WARMUP WD <<< "$row"
    TS=$(date +%Y%m%d_%H%M%S)
    echo "==========================================="
    echo "T1.5 VARIANT: tag=$TAG sched=$SCHED warmup=$WARMUP wd=$WD  [ts=$TS]"
    echo "==========================================="

    echo "[$TAG] regenerating AL ..."
    regen_one alabama "$SCHED" "$WARMUP" "$WD" "$TAG" || { echo "[$TAG] AL regen FAILED"; continue; }
    echo "[$TAG] regenerating AZ ..."
    regen_one arizona "$SCHED" "$WARMUP" "$WD" "$TAG" || { echo "[$TAG] AZ regen FAILED"; continue; }

    echo "[$TAG] rebuilding next_region.parquet + per-fold log_T ..."
    python scripts/regenerate_next_region.py --state alabama > /dev/null 2>&1
    python scripts/regenerate_next_region.py --state arizona > /dev/null 2>&1
    python scripts/compute_region_transition.py --state alabama --per-fold --n-splits 5 --seed 42 > /dev/null 2>&1
    python scripts/compute_region_transition.py --state arizona --per-fold --n-splits 5 --seed 42 > /dev/null 2>&1

    echo "[$TAG] launching MTL AL + AZ in parallel ..."
    train_one_state alabama "$TAG" &
    AL_PID=$!
    train_one_state arizona "$TAG" &
    AZ_PID=$!
    wait $AL_PID
    AL_RC=$?
    wait $AZ_PID
    AZ_RC=$?
    echo "[$TAG] MTL done. AL rc=$AL_RC AZ rc=$AZ_RC"

    AL_RUN=$(ls -td /home/vitor.oliveira/PoiMtlNet/results/check2hgi/alabama/mtlnet_*/ | head -1)
    AZ_RUN=$(ls -td /home/vitor.oliveira/PoiMtlNet/results/check2hgi/arizona/mtlnet_*/ | head -1)
    python /home/vitor.oliveira/PoiMtlNet/docs/infra/a40/T1-3_record.py \
        --tag "$TAG" --c2p 0.4 --p2r 0.3 --r2c 0.3 \
        --al-run "$AL_RUN" --az-run "$AZ_RUN" \
        --out "${RESULTS_ROOT}/T1-5_${TAG}.json"
done

echo "T1.5 sweep complete. Per-variant JSONs under ${RESULTS_ROOT}/T1-5_*.json"
