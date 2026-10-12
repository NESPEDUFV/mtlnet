#!/usr/bin/env bash
# v18 row 11 — LOGIT ADJUSTMENT as a Bayes-consistent replacement for class weighting.
#
# WHY THIS IS THE UNTESTED CELL. Row 4 tested REMOVING class weights with NO replacement and lost
# ~1 pp at alabama. Logit adjustment is the principled substitute: it targets macro-F1 directly by
# shifting logits by tau*log(prior) instead of reweighting the loss.
#
# MECHANISM (verified, not assumed): next_cv.py:123-141 -- when config.loss_calibration is non-empty
# it builds CalibratedLoss and the class-weighted CrossEntropyLoss is the ELSE branch. So passing
# --logit-adjust-tau REPLACES class weighting automatically. Do NOT also pass --no-class-weights or
# --tail-loss balanced; stacking logit-adjust on top of balanced weights cratered in T1.4
# (AL 30.15 vs 49.97).
#
# LEAK-SAFE: class counts come from train_loader.dataset.targets (TRAIN fold only, next_cv.py:127)
# and the offset is applied inside the criterion; shared_evaluate takes no criterion, so evaluation
# logits are unadjusted.
#
# PRIOR EVIDENCE: the mtl_improvement T1.4 re-pin tuned this exact head and found tau=0.5 beat
# --tail-loss balanced at all four states. Caveat: T1.4 ran on the STRIDE-9 substrate (AL 12,709
# windows); v18 is stride-1 (96,326), so transfer is not guaranteed.
#
# Run at each state's RETUNED winner LR so it composes with the adopted recipe.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/logitadj; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/logitadj_DRIVER.log
log(){ echo "[$(date '+%F %T')] LA: $*" | tee -a "$D"; }

arm(){ # state bs lr tau
  local st=$1 bs=$2 lr=$3 tau=$4
  local tag="la_${st}_tau${tau}_bs${bs}_lr${lr}"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [logit-adjust-tau=$tau, replaces class weighting]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_NO_TRAIN_DIAGNOSTICS=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18la_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed 0 \
      --batch-size "$bs" --max-lr "$lr" --logit-adjust-tau "$tau" \
      --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc (see $lg)"; return 1; }
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$bs" "$lr" "$tau" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,bs,lr,tau,wall,side=sys.argv[1:9]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json")); pf=[];eps=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
json.dump({"tag":tag,"arm":"dedicated","state":st_,"seed":0,"row":11,"batch_size":int(bs),
  "max_lr":float(lr),"logit_adjust_tau":float(tau),"class_weights":"replaced by logit adjustment",
  "epochs":50,"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "argmax_mean":s["cat_macro_f1_mean"],"argmax_per_fold":s["cat_per_fold"],
  "argmax_best_epochs":s["cat_best_epochs"],"sm3_mean":round(stx.mean(pf),4),
  "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
  "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]},open(side,"w"),indent=2)
print(f"DONE {tag} argmax={s['cat_macro_f1_mean']} sm3={round(stx.mean(pf),4)}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "waiting for the A-C follow-ups to finish"
until grep -q "NEXT2 steps A-C COMPLETE" "$BASE/logs/next2_DRIVER.log" 2>/dev/null; do sleep 60; done
log "===== row 11: logit adjustment, at each state's retuned winner LR ====="
for tau in 0.5 1.0; do
  arm alabama  8192 0.0025  "$tau"
  arm arizona  8192 0.0005  "$tau"
  arm istanbul 2048 0.0005  "$tau"
done
log "===== row 11 COMPLETE ====="
