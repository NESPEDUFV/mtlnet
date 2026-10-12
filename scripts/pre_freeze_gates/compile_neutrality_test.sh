#!/bin/bash
# Compile/tf32 DELTA-NEUTRALITY test for the MTL-vs-STL comparison.
# Runs 6 cells on the gated-overlap engine (seed 42, 5f, 50ep) and reports whether the
# DELTA (MTL − ceiling) is preserved when compile/tf32 is applied UNIFORMLY:
#   MTL{off,on} × {STL cat ceiling, STL reg ceiling}{off,on}
# Deltas (reg is the tie-break-sensitive one to watch):
#   Δ_off   = MTL_off − ceiling_off   (trustworthy reference)
#   Δ_on    = MTL_on  − ceiling_on    (uniform compiled — if ≈ Δ_off, uniform compile is safe)
#   Δ_mixed = MTL_on  − ceiling_off   (the board's pre-fix reg asymmetry — quantifies the bias)
#   usage: compile_neutrality_test.sh <state>
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=24
export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
ST=${1:-alabama}; SD=42; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval/neutral_$ST; mkdir -p "$L" logs
say(){ echo "[$(date '+%F %T')] NEUT[$ST] $*" | tee -a "$L/run.log"; }
declare -A RD

# champion-G MTL; $1=tag $2="" or "--compile --tf32"
mtl(){ local tag=$1; shift; local knobs="$*"
  say "MTL $tag ($knobs)"
  $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower $knobs \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$L/mtl_$tag.log" 2>&1 &
  local p=$!; wait $p
  RD[mtl_$tag]=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${p} 2>/dev/null | head -1)
}
# STL cat ceiling (next_gru)
stlcat(){ local tag=$1; shift; local knobs="$*"
  say "STLcat $tag ($knobs)"
  $PY scripts/train.py --task next --state "$ST" --engine "$OVL" --model next_gru \
    --folds "$F" --epochs "$EP" --seed "$SD" --batch-size 2048 --max-lr 3e-3 \
    --gradient-accumulation-steps 1 $knobs --no-checkpoints > "$L/stlcat_$tag.log" 2>&1 &
  local p=$!; wait $p
  RD[stlcat_$tag]=$(ls -d results/$OVL/$ST/*ep${EP}_*_${p} 2>/dev/null | grep -v mtlnet | head -1)
  [ -z "${RD[stlcat_$tag]}" ] && RD[stlcat_$tag]=$(ls -dt results/$OVL/$ST/*ep${EP}_* 2>/dev/null | grep -v mtlnet | head -1)
}
# STL reg ceiling (next_stan_flow a0)
stlreg(){ local tag=$1; shift; local knobs="$*"
  say "STLreg $tag ($knobs)"
  $PY scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region $knobs \
    --tag "neut_${ST}_stlreg_$tag" > "$L/stlreg_$tag.log" 2>&1 &
  wait $!
}

say "=== 6-cell compile-neutrality test ==="
stlcat off ""             ; stlcat on "--compile --tf32"
stlreg off ""             ; stlreg on "--compile --tf32"
mtl    off ""             ; mtl    on "--compile --tf32"
say "=== AGGREGATE ==="
$PY - "${RD[mtl_off]:-}" "${RD[mtl_on]:-}" "${RD[stlcat_off]:-}" "${RD[stlcat_on]:-}" \
     "$L/stlreg_off.log" "$L/stlreg_on.log" <<'PY' 2>&1 | tee -a "$L/run.log"
import sys, json, glob, re, numpy as np
mlo,mln,sco,scn,sro_log,srn_log = sys.argv[1:7]
def mtl_cr(rd):
    c=[];r=[]
    for fi in sorted(glob.glob((rd or "")+"/folds/fold*_info.json")):
        d=json.load(open(fi))["diagnostic_best_epochs"]
        c.append(d["next_category"]["metrics"]["f1"]*100)
        r.append(d["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]*100)
    return (np.mean(c) if c else float('nan')), (np.mean(r) if r else float('nan'))
def cat_report(rd):
    v=[]
    for f in sorted(glob.glob((rd or "")+"/folds/fold*report.json")):
        try:
            d=json.load(open(f))
            for k in ("macro avg","macro_avg"):
                if k in d and "f1-score" in d[k]: v.append(d[k]["f1-score"]*100); break
        except Exception: pass
    return np.mean(v) if v else float('nan')
def p1_acc10(log):
    try:
        m=re.search(r"AGGREGATE:.*Acc@10=([0-9.]+)", open(log).read()); return float(m.group(1))*100 if m else float('nan')
    except Exception: return float('nan')
mo_c,mo_r=mtl_cr(mlo); mn_c,mn_r=mtl_cr(mln)
sco_=cat_report(sco); scn_=cat_report(scn)
sro=p1_acc10(sro_log); srn=p1_acc10(srn_log)
print("\n=============== COMPILE-NEUTRALITY ===============")
print(f"  MTL cat   off={mo_c:.3f} on={mn_c:.3f}   | STLcat off={sco_:.3f} on={scn_:.3f}")
print(f"  MTL reg   off={mo_r:.3f} on={mn_r:.3f}   | STLreg off={sro:.3f} on={srn:.3f}")
print("  --- CAT deltas (MTL - ceiling) ---")
print(f"    Δ_off   = {mo_c-sco_:+.3f}   Δ_on(uniform) = {mn_c-scn_:+.3f}   Δ_mixed = {mn_c-sco_:+.3f}")
print(f"    |Δ_on-Δ_off| = {abs((mn_c-scn_)-(mo_c-sco_)):.3f}")
print("  --- REG deltas (the one to watch) ---")
print(f"    Δ_off   = {mo_r-sro:+.3f}   Δ_on(uniform) = {mn_r-srn:+.3f}   Δ_mixed = {mn_r-sro:+.3f}")
print(f"    |Δ_on-Δ_off| = {abs((mn_r-srn)-(mo_r-sro)):.3f}   (PASS if << fold σ ~0.8)")
PY
say "DONE"
