#!/bin/bash
# H100 board — full cell set for ONE state on the FROZEN v14 gated-overlap engine.
# Board recipe: seed (def 0), 5 folds, 50 ep, compiled+tf32, MTL_STRICT=1, --canon none + explicit pins.
# Three GPU cells, SERIAL within the state (run multiple STATES in parallel — they are path-segregated):
#   Cell 1: STL cat ceiling (next_gru, next_category)
#   Cell 2: STL reg ceiling (next_stan_flow a0, region) on overlap   [B-A2: --engine-override OVL]
#   Cell 3: champion-G v16 MTL on overlap
# Then matched score (FULL top10 fp32 both sides) -> device-internal Δcat / Δreg vs δ_reg=2pp + result JSON.
#
# STL-reg val metric: GPU path for small/medium C (fast), auto-CPU for large C (CA/TX) via
# P1_S2_AUTO_BUDGET_GB=10 (the MTL cell keeps S2 via MTL_CHUNK_VAL_METRIC=1, unset for the p1 cell).
# Rundirs captured by most-recent-of-prefix within the state dir (reliable under cross-state parallelism;
# the /commands/python wrapper makes $! != the python PID, so PID-suffix capture is unreliable here).
set -uo pipefail
REPO=/teamspace/studios/this_studio/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=python
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=8
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board_h100
# auto-fit dataset (default). NEVER MTL_DATASET_GPU=1 for CA/TX.

ST="${1:?usage: h100_state_cells.sh <state> [seed]}"; SD="${2:-0}"; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/h100_board/$ST; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] [$ST] $*"; }

# ---------- Cell 1: STL cat ceiling (next_gru) ----------
say "Cell1 STL cat (next_gru) on $OVL, compiled+tf32"
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 \
    --compile --tf32 --no-checkpoints > "$L/stl_cat.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "Cell1 FAIL rc=$rc"; tail -20 "$L/stl_cat.log"; exit $rc; }
STLCAT_RD=$(ls -dt results/$OVL/$ST/next_*ep${EP}_* 2>/dev/null | head -1)
say "Cell1 done -> $STLCAT_RD"

# ---------- Cell 2: STL reg ceiling (next_stan_flow a0) on OVERLAP ----------
say "Cell2 STL reg (next_stan_flow a0) on $OVL, compiled+tf32 (P1_S2_AUTO_BUDGET_GB=10)"
env -u MTL_CHUNK_VAL_METRIC P1_S2_AUTO_BUDGET_GB=10 \
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --compile --tf32 --tag "${ST}_ovl_stl_reg_s${SD}" > "$L/stl_reg.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "Cell2 FAIL rc=$rc"; tail -20 "$L/stl_reg.log"; exit $rc; }
say "Cell2 done (reg ceiling JSON in docs/results/P1/)"

# ---------- Cell 3: champion-G v16 MTL on OVERLAP ----------
say "Cell3 champion-G MTL on $OVL, compiled+tf32"
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
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$L/mtl.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "Cell3 FAIL rc=$rc"; tail -30 "$L/mtl.log"; exit $rc; }
MTL_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null | head -1)
say "Cell3 done -> $MTL_RD"

# ---------- matched score + Δ + result JSON ----------
say "matched score + Δ"
$PY scripts/closing_data/h100_score_matched.py "$MTL_RD" --seed "$SD" --tag "${ST}_ovl_mtl_s${SD}"
$PY - "$ST" "$SD" "$STLCAT_RD" "$MTL_RD" <<'PY'
import sys, json, glob
from pathlib import Path
st, sd, stlcat_rd, mtl_rd = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
# STL cat ceiling macro-F1 (diagnostic-best, f1 mean)
cat_ceil = json.load(open(Path(stlcat_rd)/"summary/full_summary.json"))["next"]["f1"]["mean"]*100
# STL reg ceiling FULL top10 (p1 aggregate)
rj = sorted(glob.glob(f"docs/results/P1/region_head_{st}_region_5f_50ep_{st}_ovl_stl_reg_s{sd}*.json"))
reg_ceil = None
if rj:
    h = next(iter(json.load(open(rj[-1]))["heads"].values()))
    reg_ceil = h["aggregate"]["top10_acc_mean"]*100
# MTL matched
sc = json.load(open(Path(mtl_rd)/"h100_matched_score.json"))
mtl_cat, mtl_reg = sc["cat_macro_f1_mean"], sc["reg_full_top10_mean"]
dcat = mtl_cat - cat_ceil
dreg = (mtl_reg - reg_ceil) if reg_ceil is not None else float('nan')
out = {"state": st, "seed": sd, "substrate": "frozen v14 (verified)", "windowing": "gated stride-1 overlap min_seq10",
       "stl_cat_ceiling_macro_f1": round(cat_ceil,4), "stl_reg_ceiling_full_top10": round(reg_ceil,4) if reg_ceil else None,
       "mtl_cat_macro_f1": round(mtl_cat,4), "mtl_reg_full_top10": round(mtl_reg,4),
       "delta_cat": round(dcat,4), "delta_reg": round(dreg,4) if reg_ceil else None,
       "mtl_rundir": mtl_rd, "stl_cat_rundir": stlcat_rd}
Path("docs/results/closing_data/h100").mkdir(parents=True, exist_ok=True)
op = f"docs/results/closing_data/h100/{st}_s{sd}_board.json"
json.dump(out, open(op,"w"), indent=2)
print(f"\n================= {st.upper()} BOARD (seed {sd}, 5f, FROZEN v14, gated overlap) =================")
print(f"  STL cat ceiling = {cat_ceil:.4f} | MTL cat = {mtl_cat:.4f} | Δcat = {dcat:+.4f}")
print(f"  STL reg ceiling = {reg_ceil if reg_ceil else 'NA'} | MTL reg = {mtl_reg:.4f} | Δreg = {dreg:+.4f} (δ_reg=2pp)" if reg_ceil else f"  reg ceiling parse FAILED")
print(f"  -> {op}")
PY
say "ALL DONE"
