#!/usr/bin/env bash
# v18 queue 2: MTL rows 3+7 at arizona and istanbul (alabama already done), then
# row 4 -- the dedicated-arm class-weight test the author asked for.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
BASE=docs/studies/closing_data/v18
Q=$BASE/logs/queue2_DRIVER.log
log(){ echo "[$(date '+%F %T')] QUEUE2: $*" | tee -a "$Q"; }

log "MTL rows 3+7 at arizona"
SWEEP_STATE=arizona bash "$BASE/run_mtl_state.sh" >> "$BASE/logs/queue2_stdout.log" 2>&1
log "MTL rows 3+7 at istanbul"
SWEEP_STATE=istanbul bash "$BASE/run_mtl_state.sh" >> "$BASE/logs/queue2_stdout.log" 2>&1

# --- row 4: does removing class weights help the DEDICATED arm too? --------------------------
# NOTE the flag: --no-class-weights (dest=use_class_weights). --no-cat-class-weights is INERT on
# --task next -- it sets use_class_weights_cat, which only mtl_cv.py reads.
log "row 4: alabama dedicated, class weights OFF"
SIDE=docs/results/closing_data/v18_sweep
for LR in 0.005 0.0025; do
  TAG="ded_alabama_nocw_bs8192_lr${LR}_ep50_s0"
  [ -f "$SIDE/$TAG.json" ] && { log "  SKIP $TAG"; continue; }
  t0=$SECONDS
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_NO_TRAIN_DIAGNOSTICS=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18sweep_ded_alabama" \
    python scripts/train.py --task next --state alabama --engine check2hgi_v18 \
      --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed 0 \
      --batch-size 8192 --max-lr "$LR" --no-class-weights --compile --tf32 --no-checkpoints \
      > "$BASE/logs/stage1/$TAG.log" 2>&1 &
  pid=$!; wait $pid; rc=$?
  rd=$(ls -d results/check2hgi_v18/alabama/next_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then log "  FAIL $TAG rc=$rc"; continue; fi
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "$TAG" >> "$BASE/logs/stage1/$TAG.log" 2>&1
  python - "$TAG" "$rd" "$LR" "$((SECONDS-t0))" "$SIDE/$TAG.json" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,lr,wall,side=sys.argv[1:6]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json")); pf=[];eps=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
json.dump({"tag":tag,"arm":"dedicated","state":"alabama","seed":0,"batch_size":8192,
  "max_lr":float(lr),"epochs":50,"class_weights":False,"row":4,"wall_seconds":int(wall),
  "rundir":rd,"precision":"fp32","argmax_mean":s["cat_macro_f1_mean"],
  "argmax_std":s["cat_macro_f1_std"],"argmax_per_fold":s["cat_per_fold"],
  "argmax_best_epochs":s["cat_best_epochs"],"sm3_mean":round(stx.mean(pf),4),
  "sm3_std":round(stx.stdev(pf),4) if len(pf)>1 else 0.0,
  "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
  "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]},open(side,"w"),indent=2)
print(f"DONE {tag} argmax={s['cat_macro_f1_mean']} sm3={round(stx.mean(pf),4)}")
PY
  log "  DONE $TAG ($((SECONDS-t0))s)"
done
log "QUEUE2 COMPLETE"
