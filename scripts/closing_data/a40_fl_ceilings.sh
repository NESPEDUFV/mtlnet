#!/bin/bash
# A40 board lane — FL STL ceilings to complete FL's B-A2 (user-requested 2026-06-22; QUEUE AFTER Task 2).
# Two sequential GPU cells on the gated-overlap engine, seed 0, 5f, compiled+tf32:
#   Cell 1: STL cat ceiling  (train.py --task next --model next_gru, next_category)
#   Cell 2: STL reg ceiling  (p1 next_stan_flow a0, region; --engine-override OVL = B-A2 windowing match)
# Then Δcat / Δreg vs the committed Task-1 FL MTL result (champion-G). Launch AFTER TX (single A40, serial).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

# shared CUDA board env (§3). MTL_CHUNK_VAL_METRIC=1 also routes the p1 reg-ceiling val metric to CPU (S2-analog).
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board

ST=florida; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"
MTL_JSON=docs/results/closing_data/a40/fl_ab_s0_matched_score.json   # Task-1 champion-G MTL result

# ---------------- Cell 1: STL cat ceiling (next_gru, next_category) on OVERLAP -----------------
cat_log="$L/fl_stl_cat_s${SD}.log"
echo "[$(date '+%F %T')] FL ceilings Cell 1 — STL cat ceiling (next_gru) on $OVL, compiled+tf32"
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 --no-checkpoints \
    --compile --tf32 > "$cat_log" 2>&1 &
pid=$!; wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] Cell 1 FAIL rc=$rc — tail:"; tail -25 "$cat_log"; exit $rc; fi
CAT_RD=$(ls -d results/$OVL/$ST/next_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "[$(date '+%F %T')] Cell 1 DONE — STL cat rundir: ${CAT_RD:-<not found; inspect $cat_log>}"

# ---------------- Cell 2: STL reg ceiling (next_stan_flow a0) on OVERLAP -----------------------
reg_log="$L/fl_stl_reg_s${SD}.log"
echo "[$(date '+%F %T')] FL ceilings Cell 2 — STL reg ceiling (next_stan_flow a0) on $OVL, compiled+tf32"
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --compile --tf32 \
    --tag "fl_ovl_stl_reg_s${SD}" > "$reg_log" 2>&1
rc=$?; if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] Cell 2 FAIL rc=$rc — tail:"; tail -25 "$reg_log"; exit $rc; fi
STL_REG=$(grep -aoE "AGGREGATE:.*Acc@10=[0-9.]+" "$reg_log" | grep -aoE "Acc@10=[0-9.]+" | head -1 | cut -d= -f2)
echo "[$(date '+%F %T')] Cell 2 DONE — STL reg ceiling Acc@10(full) = ${STL_REG:-PARSE_FAIL} (frac)"

# ---------------- Score + Δ ---------------------------------------------------------------------
echo "[$(date '+%F %T')] FL ceilings — score + Δcat/Δreg vs Task-1 MTL"
$PY - "$CAT_RD" "${STL_REG:-nan}" "$MTL_JSON" <<'PY'
import sys, json, glob, csv, statistics as st
cat_rd, stl_reg, mtl_json = sys.argv[1], sys.argv[2], sys.argv[3]
# STL cat ceiling: per-fold max macro-F1 (`f1`), fold-mean (diagnostic-best, matches MTL cat scoring)
catf=[]
for f in sorted(glob.glob(cat_rd + "/metrics/fold*_next_val.csv")):
    rows=list(csv.DictReader(open(f)))
    if rows: catf.append(max(float(r["f1"]) for r in rows) * 100)
stl_cat = st.mean(catf) if catf else float("nan")
stl_cat_std = (st.pstdev(catf) if len(catf) > 1 else 0.0)
stl_reg_pct = float(stl_reg) * 100 if stl_reg not in ("nan", "") else float("nan")
mtl = json.load(open(mtl_json))
mtl_cat, mtl_reg = mtl["cat_macro_f1_mean"], mtl["reg_full_top10_mean"]
print("\n================= FL GATED-OVERLAP B-A2 (seed 0, 5f) =================")
print(f"  STL cat ceiling (next_gru)         macro-F1 = {stl_cat:.4f} ± {stl_cat_std:.4f}  (per-fold={[round(x,4) for x in catf]})")
print(f"  STL reg ceiling (next_stan_flow a0) Acc@10  = {stl_reg_pct:.4f}")
print(f"  champion-G MTL (Task 1)             cat F1  = {mtl_cat:.4f}")
print(f"  champion-G MTL (Task 1)             reg@10  = {mtl_reg:.4f}")
print(f"  -> Δcat (MTL − STL cat ceiling)             = {mtl_cat - stl_cat:+.4f} pp")
print(f"  -> Δreg (MTL − STL reg ceiling)             = {mtl_reg - stl_reg_pct:+.4f} pp   (δ_reg = 2 pp)")
out={"state":"florida","seed":0,"folds":5,"engine":"check2hgi_dk_ovl",
     "stl_cat_ceiling_macro_f1":round(stl_cat,4),"stl_cat_per_fold":[round(x,4) for x in catf],
     "stl_reg_ceiling_top10":round(stl_reg_pct,4),
     "mtl_cat_macro_f1":mtl_cat,"mtl_reg_full_top10":mtl_reg,
     "delta_cat":round(mtl_cat-stl_cat,4),"delta_reg":round(mtl_reg-stl_reg_pct,4),
     "cat_rundir":cat_rd}
open("docs/results/closing_data/a40/fl_ba2_s0.json","w").write(json.dumps(out,indent=2))
print("  wrote docs/results/closing_data/a40/fl_ba2_s0.json")
PY
echo "[$(date '+%F %T')] FL ceilings ALL DONE"
