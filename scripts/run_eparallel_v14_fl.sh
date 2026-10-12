#!/usr/bin/env bash
# E-parallel comparand: champion-G matched-head on the SAME v14 set-a base as the cascade,
# but cross-attn ON (the b4_cascade command MINUS the 5 cascade pins). This is the "parallel"
# column of the M4 cascade-vs-parallel table; FL completes what M4's MPS run OOM'd on.
set -euo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
export PYTHONPATH=src DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_RAM_HEADROOM_GB=4
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
echo "=== [E-parallel] champion-G v14 set-a (cross-attn ON) $(date -u) ==="
python scripts/train.py --task mtl --task-set check2hgi_next_region \
    --engine check2hgi_design_k_resln_mae_l0_1 --state florida --seed 0 --folds 5 --epochs 50 \
    --batch-size 2048 --model mtlnet_crossattn_dualtower \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --task-a-input-type checkin --task-b-input-type region \
    --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/florida \
    --checkpoint-selector geom_simple
echo "=== [E-parallel] DONE $(date -u) ==="
