#!/usr/bin/env bash
# Board-H100 champion-G MTL launcher (gated-overlap substrate check2hgi_dk_ovl, seed0 5f).
# Usage: board_h100_mtl.sh <state> <arm:bf16|fp32> <cache_suffix>
# Recipe = champion-G on dk_ovl. --canon none + explicit class-weight flags (see AL_PRECISION_GATE.md
# "recipe note"): the bare command would trip the wrong-substrate canon-guard under MTL_STRICT=1.
set -euo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
STATE="$1"; ARM="$2"; SUF="$3"
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export PYTHONPATH=src
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_${SUF}
if [ "$ARM" = "bf16" ]; then
  export MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1
elif [ "$ARM" = "fp32" ]; then
  export MTL_DISABLE_AMP=1
else echo "bad arm: $ARM"; exit 2; fi
python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
    --state "$STATE" --seed 0 --epochs 50 --folds 5 --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --no-reg-class-weights --no-cat-class-weights \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower --compile --tf32 \
    --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/"$STATE" --no-checkpoints
