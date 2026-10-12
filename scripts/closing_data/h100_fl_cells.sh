#!/bin/bash
# H100 board lane — FL full cell set on the rebuilt-substrate gated-overlap engine (own-states).
# Board recipe: seed 0, 5 folds, 50 ep, compiled+tf32, MTL_STRICT=1. Three GPU cells, STRICTLY SEQUENTIAL:
#   Cell 1: STL cat ceiling (next_gru, next_category)
#   Cell 2: STL reg ceiling (next_stan_flow a0, region) on overlap windowing  [B-A2 trap: --engine-override OVL]
#   Cell 3: champion-G v16 MTL on overlap (--canon none + explicit pins; canon wrong-substrate guard else hard-fails)
# Then matched score (FULL top10 fp32 both sides) -> device-internal Δcat / Δreg vs δ_reg=2pp.
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=python
export MTL_CHUNK_VAL_METRIC=1
export P1_CHUNK_VAL_METRIC=1              # p1 STL-reg ceiling: CPU val-metric (avoids large GPU logit cat at overlap scale)
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_h100
# auto-fit dataset (default). NEVER MTL_DATASET_GPU=1.

ST=florida; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/h100_board; mkdir -p "$L"

# ---------- Cell 1: STL cat ceiling (next_gru) ----------
clog="$L/fl_stl_cat_s${SD}.log"
echo "[$(date '+%F %T')] FL Cell1 — STL cat ceiling (next_gru) on $OVL, compiled+tf32"
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 \
    --compile --tf32 --no-checkpoints > "$clog" 2>&1 &
pid=$!; wait "$pid"; rc=$?; [ $rc -ne 0 ] && { echo "Cell1 FAIL rc=$rc"; tail -25 "$clog"; exit $rc; }
STLCAT_RD=$(ls -d results/$OVL/$ST/*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "$STLCAT_RD" > "$L/fl_stl_cat_s${SD}.rundir"
echo "[$(date '+%F %T')] FL Cell1 DONE -> ${STLCAT_RD:-<rundir-by-PID not found; see $clog>}"

# ---------- Cell 2: STL reg ceiling (next_stan_flow a0) on OVERLAP ----------
rlog="$L/fl_stl_reg_s${SD}.log"
echo "[$(date '+%F %T')] FL Cell2 — STL reg ceiling (next_stan_flow a0) on $OVL, compiled+tf32"
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --compile --tf32 --tag "fl_ovl_stl_reg_s${SD}" > "$rlog" 2>&1
rc=$?; [ $rc -ne 0 ] && { echo "Cell2 FAIL rc=$rc"; tail -25 "$rlog"; exit $rc; }
STL_CEIL=$(grep -aoE "AGGREGATE:.*Acc@10=[0-9.]+" "$rlog" | grep -aoE "Acc@10=[0-9.]+" | head -1 | cut -d= -f2)
echo "[$(date '+%F %T')] FL Cell2 DONE — STL reg ceiling Acc@10(full,frac) = ${STL_CEIL:-PARSE_FAIL}"

# ---------- Cell 3: champion-G v16 MTL on OVERLAP ----------
mlog="$L/fl_mtl_s${SD}.log"
echo "[$(date '+%F %T')] FL Cell3 — champion-G MTL on $OVL, compiled+tf32"
$PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower \
    --checkpoint-selector geom_simple --no-reg-class-weights --no-cat-class-weights \
    --canon none --compile --tf32 \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$mlog" 2>&1 &
pid=$!; wait "$pid"; rc=$?; [ $rc -ne 0 ] && { echo "Cell3 FAIL rc=$rc"; tail -30 "$mlog"; exit $rc; }
MTL_RD=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "$MTL_RD" > "$L/fl_mtl_s${SD}.rundir"
echo "[$(date '+%F %T')] FL Cell3 DONE — MTL rundir: ${MTL_RD:-<not found; see $mlog>}"

# ---------- matched score + Δ ----------
echo "[$(date '+%F %T')] FL — matched score (FULL top10 fp32) + Δ"
$PY scripts/closing_data/h100_score_matched.py "$MTL_RD" --seed "$SD" --tag "fl_ovl_mtl_s${SD}"
echo "STL_REG_CEIL_FRAC=${STL_CEIL:-nan}" | tee "$L/fl_stl_reg_ceil_s${SD}.txt"
echo "[$(date '+%F %T')] FL ALL DONE — run h100_fl_delta.py to print Δcat/Δreg (needs STL cat rundir + STL reg ceil + MTL score)"
