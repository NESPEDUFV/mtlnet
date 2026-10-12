#!/usr/bin/env bash
# v18 smoke: validate the FULL training path on the alabama v18 engine before spending GPU hours.
# 1 fold, 2 epochs. Proves: engine registration, next.parquet loader, next_region loader + region
# tower, --canon none + MTL_STRICT guard, per-head LR env, fp32. Numbers are meaningless here.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
L=docs/studies/closing_data/v18/logs
mkdir -p "$L"

echo "=== [1/2] dedicated next-category smoke (alabama, 1 fold, 2 ep) ==="
MTL_NO_TRAIN_DIAGNOSTICS=1 python scripts/train.py --task next --state alabama --engine "$ENG" \
  --model next_gru --embedding-dim 64 --folds 5 --only-folds 0 --epochs 2 --seed 0 \
  --batch-size 2048 --max-lr 0.005 --no-checkpoints > "$L/smoke_cat.log" 2>&1
echo "cat smoke rc=$?"; tail -6 "$L/smoke_cat.log"

echo
echo "=== [2/2] joint MTL smoke (alabama, 1 fold, 2 ep) — the MTL_STRICT guard test ==="
export MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_ONECYCLE_PER_HEAD_LR=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
  --state alabama --seed 0 --epochs 2 --folds 5 --only-folds 0 --batch-size 8192 \
  --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --tf32 \
  --per-fold-transition-dir "output/$V14/alabama" --no-checkpoints > "$L/smoke_mtl.log" 2>&1
echo "mtl smoke rc=$?"; tail -8 "$L/smoke_mtl.log"
