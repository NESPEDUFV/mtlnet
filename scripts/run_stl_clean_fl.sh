#!/usr/bin/env bash
# STL F37-style run with leak-free per-fold log_T at FL.
# Tests whether the STL ceiling (82.44 reported) is also inflated by the
# C4 leak. Same recipe as F37, only difference: --per-fold-transition-dir.
set -u
WORKTREE="${WORKTREE:-$(pwd)}"
export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-/workspace/PoiMtlNet/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-/workspace/PoiMtlNet/output}"
PY="${PY:-/opt/poimtlnet-venv/bin/python}"
cd "${WORKTREE}"
mkdir -p logs

"$PY" -u scripts/p1_region_head_ablation.py \
    --state florida \
    --heads next_getnext_hard \
    --folds 5 --epochs 50 \
    --batch-size 2048 --seed 42 \
    --input-type region \
    --override-hparams \
        d_model=256 num_heads=8 \
        "transition_path=${OUTPUT_DIR}/check2hgi/florida/region_transition_log.pt" \
    --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/florida" \
    --tag c4_clean \
    --no-resume \
    --max-lr 1e-3 \
    --region-emb-source check2hgi \
    --mtl-preencoder --preenc-hidden 256 --preenc-layers 2 --preenc-dropout 0.1 \
    2>&1 | tee logs/f50_stl_clean_fl.log
