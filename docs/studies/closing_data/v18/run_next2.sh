#!/usr/bin/env bash
# v18 follow-ups (author plan 2026-08-08), in order:
#   A. AZ + IST dedicated --no-class-weights (5 folds)  -- map the size-dependence BEFORE trusting TX
#   B. TX class weights at 50 ep, folds 0/1/2           -- 1 fold can be biased; same seed, 3 folds
#   C. TX dedicated bs {16384, 32768}, 1 fold, at the best setting
#   D. FL MTL bs {16384, 32768}, 1 fold, at the best row-3b cat-lr
#
# WHY A COMES FIRST: alabama (5 folds) says class weights ON is +1.20; texas (1 fold) says OFF is
# +1.18. Same knob, opposite sign. AZ (201k windows) and IST (272k) sit between AL (96k) and
# FL/TX (1.3M/3.8M), so they show whether the flip is size-GRADED or a texas peculiarity.
#
# Epochs pinned to 50 for TX (author): row 5 showed 50 vs 75 inside the margin of error.
# NO pgrep waiting on script names -- waits on a log marker instead.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/next2; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/next2_DRIVER.log
log(){ echo "[$(date '+%F %T')] N2: $*" | tee -a "$D"; }

ded(){ # tag state bs lr epochs foldflag extra_flags extra_json
  local tag=$1 st=$2 bs=$3 lr=$4 ep=$5 ff=$6 xf=$7 xj=$8
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [bs=$bs lr=$lr ep=$ep $ff $xf]"
  # shellcheck disable=SC2086
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_NO_TRAIN_DIAGNOSTICS=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18n2_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 $ff --epochs "$ep" --seed 0 \
      --batch-size "$bs" --max-lr "$lr" $xf --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then
    grep -qiE "out of memory|CUDA error" "$lg" && log "FAIL $tag — OOM/CUDA (expected for the largest batch)" || log "FAIL $tag rc=$rc"
    return 1
  fi
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$bs" "$lr" "$ep" "$xj" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,bs,lr,ep,xj,wall,side=sys.argv[1:10]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json")); pf=[];eps=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
d={"tag":tag,"arm":"dedicated","state":st_,"seed":0,"batch_size":int(bs),"max_lr":float(lr),
   "epochs":int(ep),"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
   "argmax_mean":s["cat_macro_f1_mean"],"argmax_per_fold":s["cat_per_fold"],
   "argmax_best_epochs":s["cat_best_epochs"],"sm3_mean":round(stx.mean(pf),4) if pf else None,
   "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
   "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]}
d.update(json.loads(xj)); json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} argmax={d['argmax_mean']} sm3={d['sm3_mean']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "waiting for the current sweep to finish (row 3b)"
until grep -q "REST COMPLETE" "$BASE/logs/rest_DRIVER.log" 2>/dev/null; do sleep 60; done
log "sweep finished — starting the follow-ups"

# ---- A. AZ + IST dedicated, class weights OFF (5 folds) --------------------------------------
log "A — AZ/IST dedicated, class weights OFF (maps the size-dependence)"
ded "n2_arizona_nocw_bs8192_lr0.0005" arizona 8192 0.0005 50 "--folds 5" "--no-class-weights" '{"step":"A","class_weights":false}'
ded "n2_arizona_nocw_bs8192_lr0.005"  arizona 8192 0.005  50 "--folds 5" "--no-class-weights" '{"step":"A","class_weights":false}'
ded "n2_istanbul_nocw_bs2048_lr0.0005" istanbul 2048 0.0005 50 "--folds 5" "--no-class-weights" '{"step":"A","class_weights":false}'
ded "n2_istanbul_nocw_bs2048_lr0.005"  istanbul 2048 0.005  50 "--folds 5" "--no-class-weights" '{"step":"A","class_weights":false}'

# ---- B. TX class weights at 50 ep, folds 0/1/2 (fold 0 ON already exists from row 5) ----------
log "B — TX class weights, 50 ep, folds 0/1/2 (same seed)"
ded "n2_texas_cwON_f0"  texas 8192 0.005 50 "--only-fold 0" "" '{"step":"B","class_weights":true,"fold":0}'
ded "n2_texas_cwOFF_f0" texas 8192 0.005 50 "--only-fold 0" "--no-class-weights" '{"step":"B","class_weights":false,"fold":0}'
ded "n2_texas_cwON_f1"  texas 8192 0.005 50 "--only-fold 1" "" '{"step":"B","class_weights":true,"fold":1}'
ded "n2_texas_cwOFF_f1" texas 8192 0.005 50 "--only-fold 1" "--no-class-weights" '{"step":"B","class_weights":false,"fold":1}'
ded "n2_texas_cwON_f2"  texas 8192 0.005 50 "--only-fold 2" "" '{"step":"B","class_weights":true,"fold":2}'
ded "n2_texas_cwOFF_f2" texas 8192 0.005 50 "--only-fold 2" "--no-class-weights" '{"step":"B","class_weights":false,"fold":2}'

# ---- C. TX dedicated batch size at the best setting (1 fold) ----------------------------------
CWFLAG=$(python - <<'PY'
import json,glob,statistics as st
S='docs/results/closing_data/v18_sweep'
on=[json.load(open(f)) for f in glob.glob(f'{S}/n2_texas_cwON_f*.json')]
off=[json.load(open(f)) for f in glob.glob(f'{S}/n2_texas_cwOFF_f*.json')]
if len(on)>=2 and len(off)>=2:
    a=st.mean([x['sm3_mean'] for x in on]); b=st.mean([x['sm3_mean'] for x in off])
    print("--no-class-weights" if b>a else "")
else:
    print("")
PY
)
log "C — TX dedicated batch size, 1 fold, class-weight flag from step B: '${CWFLAG:-ON}'"
ded "n2_texas_bs16k" texas 16384 0.005 50 "--only-fold 0" "$CWFLAG" '{"step":"C"}'
ded "n2_texas_bs32k" texas 32768 0.005 50 "--only-fold 0" "$CWFLAG" '{"step":"C"}'

log "===== NEXT2 steps A-C COMPLETE (step D, FL MTL batch size, is launched separately) ====="
