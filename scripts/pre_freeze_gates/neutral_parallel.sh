#!/bin/bash
# Compile/tf32 delta-neutrality test with bounded GPU concurrency.
# 6 cells: {MTL champion-G, STL cat ceiling, STL reg ceiling} × {compile off, on}.
# Concurrency-safe for CORRECTNESS: separate processes are each deterministic (GPU
# sharing changes speed, not numbers). Each compile cell gets an ISOLATED inductor
# cache so concurrent compiles don't race. Rundirs captured by PID (no ls -dt race).
#   usage: neutral_parallel.sh <state> <concurrency>   (AL: 4 parallel; TX: 1 serial)
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python; export OMP_NUM_THREADS=8
ST=${1:-alabama}; CONC=${2:-4}; SD=42; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/gate_eval/neutral_$ST; mkdir -p "$L" logs
say(){ echo "[$(date '+%F %T')] NEUT[$ST] $*" >> "$L/run.log"; }
common_env(){ export MTL_CHUNK_VAL_METRIC=1 PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"; }

run_cell(){
  local kind=$1 mode=$2
  common_env
  export TORCHINDUCTOR_CACHE_DIR="$L/inductor_${kind}_${mode}"
  local knobs=""; [ "$mode" = "on" ] && knobs="--compile --tf32"
  local clog="$L/${kind}_${mode}.log"; local pid
  local _t0=$(date +%s)
  case "$kind" in
    mtl)
      $PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
        --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
        --mtl-loss static_weight --category-weight 0.75 \
        --cat-head next_gru --reg-head next_stan_flow_dualtower \
        --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
        --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
        --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
        --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
        --model mtlnet_crossattn_dualtower $knobs \
        --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$clog" 2>&1 &
      pid=$!; wait $pid
      ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1 > "$L/rd_${kind}_${mode}" ;;
    stlcat)
      $PY scripts/train.py --task next --state "$ST" --engine "$OVL" --model next_gru \
        --folds "$F" --epochs "$EP" --seed "$SD" --batch-size 2048 --max-lr 3e-3 \
        --gradient-accumulation-steps 1 $knobs --no-checkpoints > "$clog" 2>&1 &
      pid=$!; wait $pid
      ls -d results/$OVL/$ST/next_*ep${EP}_*_${pid} 2>/dev/null | head -1 > "$L/rd_${kind}_${mode}" ;;
    stlreg)
      $PY scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
        --input-type region --region-emb-source "$V14" \
        --override-hparams freeze_alpha=True alpha_init=0.0 \
        --engine-override "$OVL" --per-fold-transition-dir "output/$V14/$ST" \
        --folds "$F" --epochs "$EP" --seed "$SD" --target region $knobs \
        --tag "neut_${ST}_stlreg_${mode}" > "$clog" 2>&1 &
      pid=$!; wait $pid ;;  # p1 writes its own JSON + AGGREGATE line to $clog
  esac
  local _wt=$(( $(date +%s) - _t0 ))
  echo "$_wt" > "$L/wt_${kind}_${mode}"
  say "cell ${kind}_${mode} done (${_wt}s wall)"
}

say "=== neutrality test, concurrency=$CONC ==="
CELLS=("stlcat:off" "stlcat:on" "stlreg:off" "stlreg:on" "mtl:off" "mtl:on")
running=0
for cell in "${CELLS[@]}"; do
  run_cell "${cell%%:*}" "${cell##*:}" &
  running=$((running+1))
  if [ "$running" -ge "$CONC" ]; then wait -n; running=$((running-1)); fi
done
wait
say "all cells done -> aggregating"

$PY - "$ST" "$L" "$CONC" <<'PY' 2>&1 | tee -a "$L/run.log"
import sys, json, glob, re, numpy as np
ST, L, CONC = sys.argv[1], sys.argv[2], int(sys.argv[3])
def wt(name):
    try: return int(open(f"{L}/wt_{name}").read().strip())
    except Exception: return None
def fmt(s): return f"{s//60}m{s%60:02d}s" if s is not None else "n/a"
def rd(name):
    try: return open(f"{L}/rd_{name}").read().strip()
    except Exception: return ""
def mtl_cr(r):
    c=[];g=[]
    for fi in sorted(glob.glob((r or "")+"/folds/fold*_info.json")):
        d=json.load(open(fi))["diagnostic_best_epochs"]
        c.append(d["next_category"]["metrics"]["f1"]*100)
        g.append(d["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]*100)
    return (np.mean(c) if c else float('nan')),(np.mean(g) if g else float('nan'))
def cat_rep(r):
    v=[]
    for f in sorted(glob.glob((r or "")+"/folds/fold*report.json")):
        try:
            d=json.load(open(f)); k="macro avg" if "macro avg" in d else "macro_avg"
            if k in d and "f1-score" in d[k]: v.append(d[k]["f1-score"]*100)
        except Exception: pass
    return np.mean(v) if v else float('nan')
def p1_acc10(mode):
    try:
        m=re.search(r"AGGREGATE:.*Acc@10=([0-9.]+)", open(f"{L}/stlreg_{mode}.log").read())
        return float(m.group(1))*100 if m else float('nan')
    except Exception: return float('nan')
mo_c,mo_r=mtl_cr(rd("mtl_off")); mn_c,mn_r=mtl_cr(rd("mtl_on"))
sco,scn=cat_rep(rd("stlcat_off")),cat_rep(rd("stlcat_on"))
sro,srn=p1_acc10("off"),p1_acc10("on")
print(f"\n========= COMPILE-NEUTRALITY [{ST}] (seed42, 5f) =========")
print(f"  MTL cat off={mo_c:.3f} on={mn_c:.3f} | STLcat off={sco:.3f} on={scn:.3f}")
print(f"  MTL reg off={mo_r:.3f} on={mn_r:.3f} | STLreg off={sro:.3f} on={srn:.3f}")
print(f"  CAT  Δ_off={mo_c-sco:+.3f} Δ_on={mn_c-scn:+.3f} Δ_mixed={mn_c-sco:+.3f} | |Δon-Δoff|={abs((mn_c-scn)-(mo_c-sco)):.3f}")
print(f"  REG  Δ_off={mo_r-sro:+.3f} Δ_on={mn_r-srn:+.3f} Δ_mixed={mn_r-sro:+.3f} | |Δon-Δoff|={abs((mn_r-srn)-(mo_r-sro)):.3f}  (PASS if << ~0.8)")
clean = "CLEAN (serial)" if CONC == 1 else f"CONTENDED ({CONC}-way parallel — NOT a clean speed measure)"
print(f"  --- WALL TIME [{clean}] ---")
for kind in ("mtl","stlcat","stlreg"):
    o,n = wt(f"{kind}_off"), wt(f"{kind}_on")
    sp = f"{(o/n-1)*100:+.1f}% (on vs off)" if (o and n) else ""
    print(f"    {kind:7s} off={fmt(o):>8s}  on={fmt(n):>8s}   {sp}")
PY
say "DONE"
