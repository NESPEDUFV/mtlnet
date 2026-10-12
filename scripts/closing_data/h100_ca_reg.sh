#!/bin/bash
# H100 board lane — CA early matched B-A2 reg pair on gated-overlap (HANDOFF_BOARD_A100.md §3d).
# CA = largest state (8501 regions), most at-risk for δ_reg=2pp. Two GPU cells, STRICTLY SEQUENTIAL:
#   Cell A: STL next_stan_flow reg ceiling on overlap (p1, compiled+tf32, --engine-override OVL)  [B-A2 trap]
#   Cell B: champion-G v16 MTL on overlap (state=california; --canon none + explicit pins)
# Δreg = (MTL reg FULL top10) − (STL reg ceiling FULL top10), reported vs δ_reg=2pp.
# auto-fit: NEVER MTL_DATASET_GPU=1 for CA (forces ~31GB redundant copies -> OOM). Leave unset.
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=python
export MTL_CHUNK_VAL_METRIC=1            # for Cell B (MTL) S2 chunked val; explicitly unset for Cell A below
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_h100

ST=california; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/h100_board; mkdir -p "$L"

# ---------- Cell A: STL reg ceiling (next_stan_flow a0) on OVERLAP ----------
stl_log="$L/ca_stl_reg_s${SD}.log"
# CA STL-reg auto-RESUMES from its per-fold checkpoint (p1 resume=True). With FL DONE the GPU is
# free, so GPU-val (P1_S2_AUTO_BUDGET_GB=30 > 19.9) fits the ~63GB val materialization ALONE on the
# 80GB H100 and is ~3x faster per fold than CPU-val. Path-invariant metric (advisory) → the GPU-val
# remaining folds combine cleanly with the CPU-val folds already in the checkpoint.
echo "[$(date '+%F %T')] CA Cell A — STL reg ceiling (next_stan_flow a0) on $OVL, compiled+tf32 (GPU val; FL done, resumes from ckpt)"
env -u MTL_CHUNK_VAL_METRIC -u P1_CHUNK_VAL_METRIC P1_S2_AUTO_BUDGET_GB=30 \
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --compile --tf32 --tag "ca_ovl_stl_reg_s${SD}" > "$stl_log" 2>&1
rc=$?; [ $rc -ne 0 ] && { echo "Cell A FAIL rc=$rc"; tail -25 "$stl_log"; exit $rc; }
STL_CEIL=$(grep -aoE "AGGREGATE:.*Acc@10=[0-9.]+" "$stl_log" | grep -aoE "Acc@10=[0-9.]+" | head -1 | cut -d= -f2)
echo "[$(date '+%F %T')] CA Cell A DONE — STL reg ceiling Acc@10(full,frac) = ${STL_CEIL:-PARSE_FAIL}"
echo "STL_REG_CEIL_FRAC=${STL_CEIL:-nan}" > "$L/ca_stl_reg_ceil_s${SD}.txt"

# ---------- Cell B: champion-G v16 MTL on OVERLAP (CA, ~many hours, auto-fit) ----------
mtl_log="$L/ca_mtl_s${SD}.log"
echo "[$(date '+%F %T')] CA Cell B — champion-G MTL on $OVL, compiled+tf32 (auto-fit, CPU-resident dataset)"
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
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$mtl_log" 2>&1 &
pid=$!; wait "$pid"; rc=$?; [ $rc -ne 0 ] && { echo "Cell B FAIL rc=$rc"; tail -30 "$mtl_log"; exit $rc; }
# rundir by most-recent-of-prefix within the state dir (the /commands/python wrapper makes
# $! != the python PID, so the PID-suffix glob is unreliable on this box). State+prefix segregated.
MTL_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null | head -1)
echo "$MTL_RD" > "$L/ca_mtl_s${SD}.rundir"
echo "[$(date '+%F %T')] CA Cell B DONE — MTL rundir: ${MTL_RD:-<not found; see $mtl_log>}"

# ---------- Δreg ----------
echo "[$(date '+%F %T')] CA — matched score + Δreg"
$PY scripts/closing_data/h100_score_matched.py "$MTL_RD" --seed "$SD" --tag "ca_ovl_mtl_s${SD}"
$PY - "$MTL_RD" "${STL_CEIL:-nan}" <<'PY'
import sys, json
from pathlib import Path
rd, stl = sys.argv[1], sys.argv[2]
sc = json.load(open(Path(rd) / "h100_matched_score.json"))
mtl_reg = sc["reg_full_top10_mean"]
stl_ceil = float(stl) * 100 if stl not in ("nan", "") else float("nan")
dreg = mtl_reg - stl_ceil
print("\n================= CA GATED-OVERLAP B-A2 (seed 0, 5f) =================")
print(f"  STL reg ceiling (next_stan_flow a0) Acc@10 = {stl_ceil:.4f}")
print(f"  champion-G MTL  reg FULL top10_acc         = {mtl_reg:.4f}")
print(f"  champion-G MTL  cat macro-F1               = {sc['cat_macro_f1_mean']:.4f}")
print(f"  -> Δreg (MTL − STL ceiling)                = {dreg:+.4f} pp   (δ_reg = 2 pp)")
v = "INSIDE (|Δreg|<=~1.5pp)" if abs(dreg)<=1.5 else ("borderline (<=2pp)" if abs(dreg)<=2.0 else "FLAG reg-claim re-scope (>2pp) — NOT a stop")
print(f"  -> verdict: {v}")
PY
echo "[$(date '+%F %T')] CA ALL DONE"
