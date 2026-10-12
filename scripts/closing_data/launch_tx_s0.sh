#!/usr/bin/env bash
# TX ep50 champion-G MTL, seed 0, 5 folds, gated overlap (check2hgi_dk_ovl), bf16.
# Large-state precision = bf16 (CA precedent; fp16 overflowed, bf16≈fp32 per FL gate).
# Reads the dk_ovl-built per-fold log_T (C29-correct; prior-OFF so inert anyway).
# TX needs ~66 GB host RAM for dataset construction → MUST run SOLO (cannot co-exist
# with a large-state run). Auto-fit dataset placement; NEVER override MTL_RAM_HEADROOM_GB.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
mkdir -p "$HOME/.inductor_cache_tx_s0"
echo "WALLCLOCK_START=$(date +%s)"
MTL_AUTOCAST_BF16=1 MTL_DISABLE_AMP_EVAL=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
  PYTHONPATH=src TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_tx_s0" \
  python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
    --state texas --seed 0 --epochs 50 --folds 5 --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower --compile --tf32 \
    --per-fold-transition-dir output/check2hgi_dk_ovl/texas --no-checkpoints
echo "EXIT=$? WALLCLOCK_END=$(date +%s)"
