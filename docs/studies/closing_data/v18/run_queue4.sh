#!/usr/bin/env bash
# v18 queue 4 — rows 5, 6 (TX dedicated, 1 fold) then row 3b (FL MTL cat-LR, 1 fold).
# Runs after queue3 (row 10). Row 8 is POSTPONED and is NOT here.
#
# 1-FOLD DISCIPLINE: use --only-fold 0, NOT --folds 1 -- but NOT for log_T reasons.
# --folds N overrides k_folds to max(2,N), so --folds 1 silently trains on a 2-FOLD split: a
# different partition from the canonical 5-split, so the result is not comparable to the 5-fold
# cells. --only-fold runs exactly fold 0 OF the canonical 5-split, which is what makes the screen
# comparable.
#
# NOTE: log_T is INERT in this recipe and is never loaded. _log_t_is_inert (mtl_cv.py:552) is true
# when freeze_alpha=True + alpha_init=0.0 + all KD routes off -- exactly our config -- and
# MTL_SKIP_INERT_LOGT defaults to on, so the load and its leak-guards are skipped entirely. Every
# fold logs "[log_T-inert skip]". The transition-dir flag is passed only to match the board driver.
#
# These screens pick a DIRECTION; with one fold there is no dispersion, no paired test and no
# interval, so they cannot certify a winner. Arms are compared on the SAME fold so the contrast is
# paired even if fold 0 is not representative in absolute level.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/q4; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/queue4_DRIVER.log
log(){ echo "[$(date '+%F %T')] Q4: $*" | tee -a "$DRV"; }

ded1f(){ # tag state bs lr epochs extra_flags extra_json
  local tag=$1 st=$2 bs=$3 lr=$4 ep=$5 xf=$6 xj=$7
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [bs=$bs lr=$lr ep=$ep $xf]"
  # shellcheck disable=SC2086
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_NO_TRAIN_DIAGNOSTICS=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18q4_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 --only-fold 0 --epochs "$ep" --seed 0 \
      --batch-size "$bs" --max-lr "$lr" $xf --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc"; return 1; }
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
   "epochs":int(ep),"n_folds":1,"screen":True,"wall_seconds":int(wall),"rundir":rd,
   "precision":"fp32","argmax_mean":s["cat_macro_f1_mean"],"argmax_per_fold":s["cat_per_fold"],
   "argmax_best_epochs":s["cat_best_epochs"],"sm3_mean":round(stx.mean(pf),4) if pf else None,
   "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
   "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]}
d.update(json.loads(xj)); json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} argmax={d['argmax_mean']} sm3={d['sm3_mean']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

mtl1f(){ # tag state catlr epochs
  local tag=$1 st=$2 clr=$3 ep=$4
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [cat-lr=$clr ep=$ep, only-fold 0]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18q4mtl_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed 0 --epochs "$ep" --only-fold 0 --batch-size 8192 \
      --mtl-loss static_weight --category-weight 0.50 --no-reg-class-weights --cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs8192_ep${ep}_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed 0 --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$clr" "$ep" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,clr,ep,wall,side=sys.argv[1:8]
a=json.load(open(f"{rd}/a40_matched_score.json")); pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
json.dump({"tag":tag,"arm":"mtl","state":st_,"seed":0,"row":"3b","cat_lr":float(clr),
  "epochs":int(ep),"n_folds":1,"screen":True,"wall_seconds":int(wall),"rundir":rd,
  "precision":"fp32","cat_argmax":a["cat_macro_f1_mean"],"cat_per_fold":a["cat_per_fold"],
  "cat_best_epochs":a["cat_best_epochs"],"reg":a["reg_full_top10_mean"],
  "reg_per_fold":a["reg_per_fold"],"cat_sm3":round(stx.mean(pf),4) if pf else None},
  open(side,"w"),indent=2)
print(f"DONE {tag} cat={a['cat_macro_f1_mean']} reg={a['reg_full_top10_mean']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

if [ "${SKIP_WAIT:-0}" != "1" ]; then
  log "waiting for row 10"
  while pgrep -f run_mtl_bs_alabama >/dev/null 2>&1; do sleep 120; done
fi
log "proceeding to rows 5, 6, 3b"

# ---- row 5: TX dedicated, grid goes UP (TX does not overfit: train-val gap +0.25) -------------
log "row 5 — TX dedicated, 1 fold"
for lr in 0.005 0.0075 0.01; do
  ded1f "ded1f_texas_bs8192_lr${lr}_ep50" texas 8192 "$lr" 50 "" '{"row":5,"class_weights":true}'
done
ded1f "ded1f_texas_bs8192_lr0.005_ep75" texas 8192 0.005 75 "" '{"row":5,"class_weights":true}'
ded1f "ded1f_texas_bs8192_lr0.0075_ep75" texas 8192 0.0075 75 "" '{"row":5,"class_weights":true}'

# ---- row 6: TX dedicated without class weights, at the row-5 winner ---------------------------
BEST=$(python - <<'PY'
import json,glob
r=[json.load(open(f)) for f in glob.glob('docs/results/closing_data/v18_sweep/ded1f_texas_*.json')]
r=[x for x in r if x.get('row')==5 and x.get('sm3_mean') is not None]
print(f"{max(r,key=lambda x:x['sm3_mean'])['max_lr']} {max(r,key=lambda x:x['sm3_mean'])['epochs']}" if r else "0.005 50")
PY
)
set -- $BEST; BLR=$1; BEP=$2
log "row 6 — TX dedicated, class weights OFF, at the row-5 winner (lr=$BLR ep=$BEP)"
ded1f "ded1f_texas_nocw_lr${BLR}_ep${BEP}" texas 8192 "$BLR" "$BEP" "--no-class-weights" '{"row":6,"class_weights":false}'

# ---- row 3b: FL MTL cat-LR grid, 1 fold -------------------------------------------------------
log "row 3b — FL MTL cat-LR grid, 1 fold"
for clr in 0.0005 0.001 0.002; do mtl1f "mtl1f_florida_catlr${clr}_ep50" florida "$clr" 50; done
mtl1f "mtl1f_florida_catlr0.001_ep25" florida 0.001 25

log "QUEUE4 COMPLETE — rows 5, 6, 3b done. Row 9 next (needs the winner fixed)."
