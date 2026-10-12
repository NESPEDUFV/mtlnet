#!/bin/bash
# FL gated-overlap comparison at SEED-0, full 50ep/5f, COMPILED board path:
# --compile --tf32 on all 3 cells (uniform) + MTL_COMPILE_DYNAMIC=1 for the MTL + SHARED
# persistent inductor caches (reuse the seed-42 compiled graphs -> ~0 warmup). Tests (a) the
# reg -1.12 flag at a 2nd seed, (b) the compiled board path end-to-end at full scale.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=florida; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] FLS0 $*" | tee -a "$L/fl_s0.log"; }
KNOBS="--compile --tf32"

say "=== STL cat ceiling (next_gru) COMPILED seed-0 ==="
t0=$(date +%s)
TORCHINDUCTOR_CACHE_DIR="$L/ind_flc_stlcat" $PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" --batch-size 2048 --max-lr 3e-3 \
    --gradient-accumulation-steps 1 $KNOBS --no-checkpoints > "$L/fls0_stl_cat.log" 2>&1 &
pid=$!; wait $pid
STLCAT_RD=$(ls -d results/$OVL/$ST/next_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo $(( $(date +%s)-t0 )) > "$L/fls0_wall_stlcat"; say "STL cat -> $STLCAT_RD ($(cat $L/fls0_wall_stlcat)s)"

say "=== STL reg ceiling (next_stan_flow a0) COMPILED seed-0 ==="
t0=$(date +%s)
TORCHINDUCTOR_CACHE_DIR="$L/ind_flc_stlreg" $PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region $KNOBS \
    --tag "fl_ovl_stl_reg_compiled_s${SD}" > "$L/fls0_stl_reg.log" 2>&1 &
pid=$!; wait $pid
echo $(( $(date +%s)-t0 )) > "$L/fls0_wall_stlreg"; say "STL reg done ($(cat $L/fls0_wall_stlreg)s)"

say "=== champion-G MTL COMPILED+DYNAMIC seed-0 (shared cache reuse) ==="
t0=$(date +%s)
MTL_COMPILE_DYNAMIC=1 TORCHINDUCTOR_CACHE_DIR="$L/flmtl_cache" $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower $KNOBS \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$L/fls0_mtl.log" 2>&1 &
pid=$!; wait $pid
MTL_RD=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
[ -z "$MTL_RD" ] && MTL_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null | head -1)
echo $(( $(date +%s)-t0 )) > "$L/fls0_wall_mtl"; say "MTL -> $MTL_RD ($(cat $L/fls0_wall_mtl)s)"

say "=== AGGREGATE (seed-0 vs seed-42) ==="
$PY - "$STLCAT_RD" "$MTL_RD" "$L/fls0_stl_reg.log" "$L" <<'PY' 2>&1 | tee -a "$L/fl_s0.log"
import sys, json, glob, re, numpy as np
sco, mtl_rd, srlog, L = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
def cat_rep(rd):
    v=[]
    for f in sorted(glob.glob((rd or "")+"/folds/fold*report.json")):
        try:
            d=json.load(open(f)); k="macro avg" if "macro avg" in d else "macro_avg"
            if k in d and "f1-score" in d[k]: v.append(d[k]["f1-score"]*100)
        except Exception: pass
    return (np.mean(v),np.std(v)) if v else (float('nan'),0)
def mtl_metrics(rd):
    c=[];rf=[]
    for fi in sorted(glob.glob((rd or "")+"/folds/fold*_info.json")):
        m=json.load(open(fi))["diagnostic_best_epochs"]
        c.append(m["next_category"]["metrics"]["f1"]*100)
        rm=m["next_region"]["per_metric_best"]["top10_acc_indist"]["metrics"]
        rf.append(rm["top10_acc_indist"]*100*(1-rm["ood_fraction"]))
    return (np.mean(c),np.std(c)),(np.mean(rf),np.std(rf))
def p1acc(log):
    m=re.search(r"AGGREGATE:.*Acc@10=([0-9.]+)", open(log).read()); return float(m.group(1))*100 if m else float('nan')
def wall(n):
    try: return int(open(f"{L}/fls0_wall_{n}").read())
    except: return None
def fmt(s): return f"{s//3600}h{(s%3600)//60:02d}m{s%60:02d}s" if s and s>=3600 else (f"{s//60}m{s%60:02d}s" if s else "n/a")
scm,scs=cat_rep(sco); (mcm,mcs),(mrm,mrs)=mtl_metrics(mtl_rd); sr=p1acc(srlog)
dcat=mcm-scm; dreg=mrm-sr
print("\n=========== FL SEED-0 (compiled) vs SEED-42 ===========")
print(f"  {'':16}{'SEED-0':>16}{'SEED-42':>16}")
print(f"  STL cat F1   {scm:>10.2f}±{scs:.2f}{75.20:>13.2f}")
print(f"  STL reg @10  {sr:>16.2f}{76.64:>16.2f}")
print(f"  MTL cat F1   {mcm:>10.2f}±{mcs:.2f}{78.32:>13.2f}")
print(f"  MTL reg full {mrm:>10.2f}±{mrs:.2f}{75.52:>13.2f}")
print(f"  --- DELTAS (MTL - ceiling) ---")
print(f"  cat: seed0 {dcat:+.2f}  | seed42 +3.12")
print(f"  reg: seed0 {dreg:+.2f}  | seed42 -1.12   <- is the reg gap seed-42-specific?")
print(f"  --- WALL (compiled, shared-cache reuse) ---")
for n,lbl in (('stlcat','STL cat'),('stlreg','STL reg'),('mtl','MTL')):
    print(f"  {lbl:8}: {fmt(wall(n))}")
print(f"  (uncompiled seed-42 baselines: STL cat 23m50, STL reg 39m41, MTL 3h11m)")
PY
say "ALL DONE"
