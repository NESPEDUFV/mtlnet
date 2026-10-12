#!/bin/bash
# Q3: SAME FL gated-overlap comparison (STL cat + STL reg + champion-G MTL) but with
# --compile --tf32 on ALL THREE cells (uniform, so the comparison stays fair). Captures
# per-cell WALL TIME (clean — serial) and the matched deltas, to compare vs the uncompiled
# baseline (STL cat 75.20 / STL reg 76.64 / MTL +3.12 cat, -1.12 reg; walls 23m50/39m41/3h11).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=florida; SD=42; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval; mkdir -p "$L" logs
say(){ echo "[$(date '+%F %T')] FLCMPC $*" | tee -a "$L/fl_compiled.log"; }
KNOBS="--compile --tf32"

# Cell 1: STL cat (compiled)
say "=== STL cat ceiling (next_gru) COMPILED ==="
t0=$(date +%s)
TORCHINDUCTOR_CACHE_DIR="$L/ind_flc_stlcat" $PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" --batch-size 2048 --max-lr 3e-3 \
    --gradient-accumulation-steps 1 $KNOBS --no-checkpoints > "$L/flc_stl_cat.log" 2>&1 &
pid=$!; wait $pid
STLCAT_RD=$(ls -d results/$OVL/$ST/next_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo $(( $(date +%s)-t0 )) > "$L/flc_wall_stlcat"; say "STL cat COMPILED -> $STLCAT_RD ($(cat $L/flc_wall_stlcat)s)"

# Cell 2: STL reg (compiled)
say "=== STL reg ceiling (next_stan_flow a0) COMPILED ==="
t0=$(date +%s)
TORCHINDUCTOR_CACHE_DIR="$L/ind_flc_stlreg" $PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region $KNOBS \
    --tag "fl_ovl_stl_reg_compiled_s${SD}" > "$L/flc_stl_reg.log" 2>&1 &
pid=$!; wait $pid
echo $(( $(date +%s)-t0 )) > "$L/flc_wall_stlreg"; say "STL reg COMPILED done ($(cat $L/flc_wall_stlreg)s)"

# Cell 3: champion-G MTL (compiled)
say "=== champion-G MTL COMPILED ==="
t0=$(date +%s)
TORCHINDUCTOR_CACHE_DIR="$L/ind_flc_mtl" $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower $KNOBS \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$L/flc_mtl.log" 2>&1 &
pid=$!; wait $pid
MTL_RD=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
[ -z "$MTL_RD" ] && MTL_RD=$(ls -dt results/$OVL/$ST/mtlnet_*ep${EP}_* 2>/dev/null | head -1)
echo $(( $(date +%s)-t0 )) > "$L/flc_wall_mtl"; say "MTL COMPILED -> $MTL_RD ($(cat $L/flc_wall_mtl)s)"

say "=== AGGREGATE (compiled vs uncompiled) ==="
$PY - "$STLCAT_RD" "$MTL_RD" "$L/flc_stl_reg.log" "$L" <<'PY' 2>&1 | tee -a "$L/fl_compiled.log"
import sys, json, glob, re, numpy as np
sco, mtl_rd, srlog, L = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
def cat_rep(rd):
    v=[]
    for f in sorted(glob.glob((rd or "")+"/folds/fold*report.json")):
        try:
            d=json.load(open(f)); k="macro avg" if "macro avg" in d else "macro_avg"
            if k in d and "f1-score" in d[k]: v.append(d[k]["f1-score"]*100)
        except Exception: pass
    return (np.mean(v), np.std(v)) if v else (float('nan'),0)
def mtl_metrics(rd):
    c=[]; rf=[]
    for fi in sorted(glob.glob((rd or "")+"/folds/fold*_info.json")):
        m=json.load(open(fi))["diagnostic_best_epochs"]
        c.append(m["next_category"]["metrics"]["f1"]*100)
        rm=m["next_region"]["per_metric_best"]["top10_acc_indist"]["metrics"]
        rf.append(rm["top10_acc_indist"]*100*(1-rm["ood_fraction"]))  # B-A2 full
    return (np.mean(c),np.std(c)), (np.mean(rf),np.std(rf))
def p1acc(log):
    m=re.search(r"AGGREGATE:.*Acc@10=([0-9.]+)", open(log).read()); return float(m.group(1))*100 if m else float('nan')
def wall(n):
    try: return int(open(f"{L}/flc_wall_{n}").read())
    except: return None
def fmt(s): return f"{s//3600}h{(s%3600)//60:02d}m{s%60:02d}s" if s and s>=3600 else (f"{s//60}m{s%60:02d}s" if s else "n/a")
scm,scs=cat_rep(sco); (mcm,mcs),(mrm,mrs)=mtl_metrics(mtl_rd); sr=p1acc(srlog)
print("\n=========== Q3: FL COMPILED (--compile --tf32) vs UNCOMPILED ===========")
print(f"  {'cell':16}{'COMPILED':>22}{'UNCOMPILED':>22}")
print(f"  {'STL cat F1':16}{f'{scm:.2f} ± {scs:.2f}':>22}{'75.20 ± 0.76':>22}")
print(f"  {'STL reg Acc@10':16}{f'{sr:.2f}':>22}{'76.64':>22}")
print(f"  {'MTL cat F1':16}{f'{mcm:.2f} ± {mcs:.2f}':>22}{'78.32 ± 0.93':>22}")
print(f"  {'MTL reg full':16}{f'{mrm:.2f} ± {mrs:.2f}':>22}{'75.52 ± 1.07':>22}")
dcat=mcm-scm; dreg=mrm-sr
print(f"  --- DELTAS (MTL - ceiling), matched ---")
print(f"  cat: compiled {dcat:+.2f}  | uncompiled +3.12  | shift {dcat-3.12:+.2f}")
print(f"  reg: compiled {dreg:+.2f}  | uncompiled -1.12  | shift {dreg-(-1.12):+.2f}  (neutral if |shift| << ~0.8)")
print(f"  --- WALL TIME (clean, serial) compiled vs uncompiled ---")
uw={'stlcat':23*60+50,'stlreg':39*60+41,'mtl':3*3600+11*60}
for n,lbl in (('stlcat','STL cat'),('stlreg','STL reg'),('mtl','MTL')):
    cw=wall(n); uwn=uw[n]; sp=f"{(uwn/cw-1)*100:+.0f}%" if cw else ""
    print(f"  {lbl:8}: compiled {fmt(cw):>10}  uncompiled {fmt(uwn):>10}  speedup {sp}")
PY
say "ALL DONE"
