#!/usr/bin/env bash
# Board-H100 STL ceiling launcher (gated-overlap dk_ovl, seed0 5f, compiled+tf32).
# Mirrors a40_fl_ceilings.sh cell recipes. Usage: board_h100_ceiling.sh <state> <kind:reg|cat> <cache_suffix>
#   reg = STL reg ceiling (p1 next_stan_flow a0, fp32, region) — the MTL-reg-vs-ceiling reference
#   cat = STL cat ceiling (train.py --task next --model next_gru) — precision-insensitive
set -euo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
STATE="$1"; KIND="$2"; SUF="$3"
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
export MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export PYTHONPATH=src
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_${SUF}
if [ "$KIND" = "reg" ]; then
  python scripts/p1_region_head_ablation.py --state "$STATE" --heads next_stan_flow \
      --input-type region --region-emb-source "$V14" \
      --override-hparams freeze_alpha=True alpha_init=0.0 \
      --engine-override "$OVL" \
      --per-fold-transition-dir "output/$V14/$STATE" \
      --folds 5 --epochs 50 --seed 0 --target region \
      --compile --tf32 --tag "${STATE}_ovl_stl_reg_s0"
elif [ "$KIND" = "cat" ]; then
  python scripts/train.py --task next --state "$STATE" --engine "$OVL" \
      --model next_gru --folds 5 --epochs 50 --seed 0 \
      --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 --no-checkpoints \
      --compile --tf32
else echo "bad kind: $KIND"; exit 2; fi
