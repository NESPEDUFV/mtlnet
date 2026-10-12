#!/bin/bash
# FL gated-overlap comparison: STL cat ceiling + STL reg ceiling + champion-G MTL,
# all on check2hgi_dk_ovl (gated stride-1), seed 42, 5 folds, 50 epochs — same recipe
# family as the AL R1 comparison (NO --compile/--tf32, so it's comparable to AL + the
# r1 doc). S2 chunked val-metric on (overlap scale). Sequential (single A40).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=florida; SD=42; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval; mkdir -p "$L" logs
say(){ echo "[$(date '+%F %T')] FLCMP $*" | tee -a "$L/fl_compare.log"; }

# ---------- Cell 1: STL cat ceiling (next_gru, next_category) ----------
say "=== STL cat ceiling (next_gru) on $OVL ==="
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 --no-checkpoints \
    > "$L/fl_stl_cat.log" 2>&1 &
pid=$!; wait "$pid"
STLCAT_RD=$(ls -d results/$OVL/$ST/*ep${EP}_*_${pid} 2>/dev/null | head -1)
[ -z "$STLCAT_RD" ] && STLCAT_RD=$(ls -dt results/$OVL/$ST/*ep${EP}_* 2>/dev/null | head -1)
say "STL cat -> $STLCAT_RD"

# ---------- Cell 2: STL reg ceiling (next_stan_flow, region, alpha0) ----------
say "=== STL reg ceiling (next_stan_flow a0) on $OVL windowing ==="
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --tag "fl_ovl_stl_reg_s${SD}" \
    > "$L/fl_stl_reg.log" 2>&1 &
pid=$!; wait "$pid"
say "STL reg done (see $L/fl_stl_reg.log AGGREGATE line)"

# ---------- Cell 3: champion-G MTL ----------
say "=== champion-G MTL on $OVL ==="
bash scripts/pre_freeze_gates/gated_overlap_g.sh "$ST" "$SD" "$EP" "$F" 2>&1 | tee -a "$L/fl_compare.log"

# ---------- aggregate ----------
say "=== AGGREGATE ==="
MTL_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null | head -1)
$PY - "$STLCAT_RD" "$MTL_RD" "$L/fl_stl_reg.log" <<'PY' 2>&1 | tee -a "$L/fl_compare.log"
import sys, json, glob, re, numpy as np
stlcat_rd, mtl_rd, stlreg_log = sys.argv[1], sys.argv[2], sys.argv[3]
def agg_cat_report(rd):
    vals=[]
    for f in sorted(glob.glob(rd+"/folds/fold*_*report.json"))+sorted(glob.glob(rd+"/folds/fold*_info.json")):
        try:
            d=json.load(open(f))
            # try a few shapes
            for k in ("macro avg","macro_avg"):
                if isinstance(d,dict) and k in d and "f1-score" in d[k]: vals.append(d[k]["f1-score"]*100); break
        except Exception: pass
    return vals
def agg_mtl(rd):
    cat=[]; reg=[]
    for fi in sorted(glob.glob(rd+"/folds/fold*_info.json")):
        d=json.load(open(fi))["diagnostic_best_epochs"]
        cat.append(d["next_category"]["metrics"]["f1"]*100)
        reg.append(d["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]*100)
    return cat,reg
def ms(x): return f"{np.mean(x):.2f} ± {np.std(x):.2f} (n={len(x)})" if x else "n/a"
# STL cat
sc=agg_cat_report(stlcat_rd) if stlcat_rd else []
# STL reg from p1 log AGGREGATE line
sr=None
try:
    txt=open(stlreg_log).read()
    m=re.search(r"AGGREGATE:.*Acc@10=([0-9.]+)", txt)
    if m: sr=float(m.group(1))*100
except Exception: pass
mc,mr=agg_mtl(mtl_rd) if mtl_rd else ([],[])
print("\n================= FL GATED-OVERLAP COMPARISON (seed 42, 5f) =================")
print(f"  STL cat ceiling (next_gru)      macro-F1 = {ms(sc)}")
print(f"  STL reg ceiling (next_stan a0)  Acc@10   = {sr:.2f}" if sr is not None else "  STL reg ceiling: parse failed (see fl_stl_reg.log)")
print(f"  champion-G MTL                  cat F1   = {ms(mc)}")
print(f"  champion-G MTL                  reg Acc@10 = {ms(mr)}")
if sc and mc: print(f"  -> MTL cat − STL cat ceiling = {np.mean(mc)-np.mean(sc):+.2f}")
if sr and mr: print(f"  -> MTL reg − STL reg ceiling = {np.mean(mr)-sr:+.2f}")
PY
say "ALL DONE"
