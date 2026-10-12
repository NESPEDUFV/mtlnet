#!/usr/bin/env bash
# F21c — STL GETNext-hard 5f × 50ep on AL + AZ.
# Strict matched-head baseline for B3. Isolates MTL-coupling contribution
# from the head-choice contribution.
#
# See docs/studies/check2hgi/FOLLOWUPS_TRACKER.md §F21c
# and docs/studies/check2hgi/PAPER_STRUCTURE.md §3.3.

set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:?set DATA_ROOT}"
export OUTPUT_DIR="${OUTPUT_DIR:?set OUTPUT_DIR}"
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export PYTORCH_ENABLE_MPS_FALLBACK=1
PY="${PY:-python3}"

cd "${WORKTREE}"
DEST="${WORKTREE}/docs/results/B3_baselines"
mkdir -p "${DEST}"

archive_latest() {
    local state="$1" dest_name="$2"
    # p1_region_head_ablation.py saves under docs/results/P1/
    local src="${WORKTREE}/docs/results/P1/region_head_${state}_region_5f_50ep_stl_gethard.json"
    if [ -f "${src}" ]; then
        cp "${src}" "${DEST}/${dest_name}.json"
        echo "[F21c] saved → ${DEST}/${dest_name}.json"
    else
        echo "[F21c] WARNING: expected output at ${src} not found"
    fi
}

run() {
    local tag="$1" state="$2" dest_name="$3"
    echo ""
    echo "================================================================"
    echo "=== [${tag}] start $(date) (state=${state})"
    echo "================================================================"
    "$PY" -u scripts/p1_region_head_ablation.py \
        --state "${state}" --heads next_getnext_hard \
        --folds 5 --epochs 50 --seed 42 --input-type region \
        --override-hparams \
            d_model=256 num_heads=8 \
            "transition_path=${OUTPUT_DIR}/check2hgi/${state}/region_transition_log.pt" \
        --tag stl_gethard
    rc=$?
    echo "[${tag}] exit ${rc} at $(date)"
    [ $rc -eq 0 ] && archive_latest "${state}" "${dest_name}"
}

# AL first (cheap, ~30 min)
run "f21c_al" alabama "stl_getnext_hard_al_5f50ep"

# AZ next (~1.5 h)
run "f21c_az" arizona "stl_getnext_hard_az_5f50ep"

echo ""
echo "================================================================"
echo "=== F21c AL + AZ complete at $(date)"
echo "=== FL (F21c continuation) can be launched separately: "
echo "===   WORKTREE=$WORKTREE PY=$PY DATA_ROOT=$DATA_ROOT OUTPUT_DIR=$OUTPUT_DIR \\"
echo "===     bash scripts/run_f21c_fl.sh"
echo "================================================================"
ls -la "${DEST}/" 2>/dev/null
