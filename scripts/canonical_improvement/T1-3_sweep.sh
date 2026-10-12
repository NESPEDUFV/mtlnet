#!/usr/bin/env bash
# T1.3 — α boundary-weight sweep for canonical Check2HGI.
# 6 valid grid points × 2 small states (AL + AZ).
# Per grid point:
#   1. Regen AL embeddings (cuda) — then start AZ regen in background
#   2. Build per-fold log_T + next_region.parquet for AL
#   3. Launch AL MTL B9full (~3 min)
#   4. Wait for AZ regen; build per-fold log_T + next_region.parquet for AZ; launch AZ MTL
#   5. Wait both MTLs; capture (cat F1, reg Acc@10) per fold and per state.
#
# Total wall: ~6 grid × ~5 min = ~30 min.
#
# Run from /home/vitor.oliveira/worktree-check2hgi-canonical-improve with venv active.

set -uo pipefail

# 6 valid grid points: (c2p, p2r, r2c) with sum=1.0 and all > 0.
# Already captured: c02p02r06, c02p04r04, c02p06r02 (T1-3_*.json).
# Remaining: grids 4-6.
declare -a GRID=(
    "0.4 0.2 0.4"
    "0.4 0.4 0.2"
    "0.6 0.2 0.2"
)

LOG_ROOT=/home/vitor.oliveira/PoiMtlNet/logs
RESULTS_ROOT=/home/vitor.oliveira/PoiMtlNet/docs/results/canonical_improvement
mkdir -p "$RESULTS_ROOT"

SUMMARY_JSON="${RESULTS_ROOT}/T1-3_sweep_summary.json"
echo '{"experiment":"T1.3","grid":[]}' > "$SUMMARY_JSON.tmp"

train_one_state() {
    local state=$1 ts=$2 tag=$3
    local log="${LOG_ROOT}/T1-3_MTL_${tag}_${state}_${ts}.log"
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
        > "$log" 2>&1
}

for triple in "${GRID[@]}"; do
    read -r C P R <<< "$triple"
    TAG="c${C//./}p${P//./}r${R//./}"   # e.g. c02p04r04
    TS=$(date +%Y%m%d_%H%M%S)
    echo "==========================================="
    echo "T1.3 GRID POINT: c2p=$C p2r=$P r2c=$R  [tag=$TAG  ts=$TS]"
    echo "==========================================="

    # 1. Regen AL on cuda (sequential — uses cuda)
    echo "[$TAG/$TS] regenerating AL embeddings..."
    python docs/infra/a40/regen_emb_alpha.py --state alabama \
        --alpha-c2p "$C" --alpha-p2r "$P" --alpha-r2c "$R" \
        > "${LOG_ROOT}/T1-3_REGEN_${TAG}_AL_${TS}.log" 2>&1
    if [ $? -ne 0 ]; then
        echo "[$TAG] AL regen FAILED — see ${LOG_ROOT}/T1-3_REGEN_${TAG}_AL_${TS}.log"
        continue
    fi

    # 2. Regen AZ on cuda
    echo "[$TAG/$TS] regenerating AZ embeddings..."
    python docs/infra/a40/regen_emb_alpha.py --state arizona \
        --alpha-c2p "$C" --alpha-p2r "$P" --alpha-r2c "$R" \
        > "${LOG_ROOT}/T1-3_REGEN_${TAG}_AZ_${TS}.log" 2>&1

    # 3. Rebuild next_region.parquet + per-fold log_T for both
    echo "[$TAG/$TS] rebuilding next_region.parquet + per-fold log_T..."
    python scripts/regenerate_next_region.py --state alabama > /dev/null 2>&1
    python scripts/regenerate_next_region.py --state arizona > /dev/null 2>&1
    python scripts/compute_region_transition.py --state alabama --per-fold --n-splits 5 --seed 42 > /dev/null 2>&1
    python scripts/compute_region_transition.py --state arizona --per-fold --n-splits 5 --seed 42 > /dev/null 2>&1

    # 4. Launch AL MTL in background and AZ MTL also in background; wait for both
    echo "[$TAG/$TS] launching MTL AL (bg) + AZ (bg)..."
    train_one_state alabama "$TS" "$TAG" &
    AL_PID=$!
    train_one_state arizona "$TS" "$TAG" &
    AZ_PID=$!
    wait $AL_PID
    AL_RC=$?
    wait $AZ_PID
    AZ_RC=$?
    echo "[$TAG/$TS] MTL done. AL rc=$AL_RC, AZ rc=$AZ_RC"

    # 5. Capture run dirs + write a per-grid-point result JSON
    AL_RUN=$(ls -td /home/vitor.oliveira/PoiMtlNet/results/check2hgi/alabama/mtlnet_*/ | head -1)
    AZ_RUN=$(ls -td /home/vitor.oliveira/PoiMtlNet/results/check2hgi/arizona/mtlnet_*/ | head -1)
    python /home/vitor.oliveira/PoiMtlNet/docs/infra/a40/T1-3_record.py \
        --tag "$TAG" --c2p "$C" --p2r "$P" --r2c "$R" \
        --al-run "$AL_RUN" --az-run "$AZ_RUN" \
        --out "${RESULTS_ROOT}/T1-3_${TAG}.json"
done

echo "T1.3 sweep complete. Per-grid JSONs under ${RESULTS_ROOT}/T1-3_*.json"
