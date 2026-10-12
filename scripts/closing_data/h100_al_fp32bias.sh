#!/bin/bash
# Small-state precision-bias test (AL): does true-fp32 MTL close the reg gap vs the STL ceiling
# that fp16-autocast leaves? AL (1109 regions) is too small to fp16-overflow, so fp16 MTL does NOT
# crash here — the fp16-vs-fp32 delta is a PURE precision-bias measurement (not a crash).
# Runs SERIALLY (same alabama output dir): STL reg ceiling -> fp16 MTL -> fp32 MTL -> compare.
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=python
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True" OMP_NUM_THREADS=8
export MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 MTL_CHUNK_VAL_METRIC=1
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_h100
ST=alabama; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/h100_board/al; mkdir -p "$L"
MTL_FLAGS="--task mtl --task-set check2hgi_next_region --engine $OVL --state $ST --seed $SD \
  --epochs $EP --folds $F --batch-size 2048 --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple \
  --no-reg-class-weights --no-cat-class-weights --canon none --compile \
  --per-fold-transition-dir output/$V14/$ST --no-checkpoints"
say(){ echo "[$(date '+%F %T')] [AL-bias] $*"; }

# 1) STL reg ceiling (p1 is fp32 already; GPU-val fine at AL scale)
say "Cell A — STL reg ceiling (next_stan_flow a0)"
$PY -u scripts/p1_region_head_ablation.py --state $ST --heads next_stan_flow --input-type region \
  --region-emb-source $V14 --override-hparams freeze_alpha=True alpha_init=0.0 \
  --engine-override $OVL --per-fold-transition-dir output/$V14/$ST \
  --folds $F --epochs $EP --seed $SD --target region --compile --tf32 \
  --tag ${ST}_ovl_stl_reg_s${SD} > "$L/stl_reg.log" 2>&1
CEIL=$(grep -aoE "AGGREGATE:.*Acc@10=[0-9.]+" "$L/stl_reg.log"|grep -aoE "Acc@10=[0-9.]+"|head -1|cut -d= -f2)
say "STL reg ceiling Acc@10(frac)=${CEIL:-PARSE_FAIL}"

# 2) fp16 MTL (default recipe — fp16 autocast)
say "Cell B — fp16 MTL (default autocast)"
rm -rf results/$OVL/$ST/mtlnet_* 2>/dev/null
$PY scripts/train.py $MTL_FLAGS --tf32 > "$L/fp16_mtl.log" 2>&1
FP16_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null|head -1)
$PY scripts/closing_data/h100_score_matched.py "$FP16_RD" --seed $SD --tag ${ST}_fp16 >/dev/null 2>&1
say "fp16 MTL rundir=$FP16_RD"
cp "$FP16_RD/h100_matched_score.json" "$L/fp16_score.json"

# 3) fp32 MTL (MTL_DISABLE_AMP=1)
say "Cell C — fp32 MTL (MTL_DISABLE_AMP=1)"
mv "$FP16_RD" "${FP16_RD}__fp16keep" 2>/dev/null   # preserve fp16 rundir from the mtime glob
MTL_DISABLE_AMP=1 MTL_DISABLE_AMP_EVAL=1 $PY scripts/train.py $MTL_FLAGS > "$L/fp32_mtl.log" 2>&1
FP32_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null|grep -v __fp16keep|head -1)
$PY scripts/closing_data/h100_score_matched.py "$FP32_RD" --seed $SD --tag ${ST}_fp32 >/dev/null 2>&1
say "fp32 MTL rundir=$FP32_RD"
cp "$FP32_RD/h100_matched_score.json" "$L/fp32_score.json"

# 4) compare
$PY - "$L/fp16_score.json" "$L/fp32_score.json" "${CEIL:-nan}" <<'PY'
import sys, json
fp16=json.load(open(sys.argv[1])); fp32=json.load(open(sys.argv[2]))
ceil=float(sys.argv[3])*100 if sys.argv[3] not in ("nan","") else float("nan")
r16=fp16["reg_full_top10_mean"]; r32=fp32["reg_full_top10_mean"]
c16=fp16["cat_macro_f1_mean"]; c32=fp32["cat_macro_f1_mean"]
print("\n========== AL PRECISION-BIAS (seed0, 5f, gated overlap) ==========")
print(f"  STL reg ceiling        = {ceil:.4f}")
print(f"  fp16 MTL reg / Δreg    = {r16:.4f} / {r16-ceil:+.4f}   (cat {c16:.4f})")
print(f"  fp32 MTL reg / Δreg    = {r32:.4f} / {r32-ceil:+.4f}   (cat {c32:.4f})")
print(f"  -> fp32 closes the reg gap by {r32-r16:+.4f} pp" if r32>r16 else f"  -> fp32 does NOT raise reg ({r32-r16:+.4f}) -> gap is real joint-loop")
PY
say "DONE"
