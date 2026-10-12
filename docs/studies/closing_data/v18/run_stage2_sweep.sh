#!/usr/bin/env bash
# v18 Stage 2 — rows 4-8 of SWEEP_PLAN.md: class weights, the large-state grid, and MTL knobs.
#
# Runs AFTER run_stage1_sweep.sh. Reads nothing from it automatically: pass the winning LRs in via
# BEST_DED_LR / BEST_CAT_LR so the choice is explicit and recorded in the log.
#
#   BEST_DED_LR=0.001 BEST_CAT_LR=0.001 bash run_stage2_sweep.sh
#
# KEY CORRECTION baked in here: to disable class weights on the DEDICATED arm you must pass
# `--no-class-weights`. The `--no-cat-class-weights` flag is INERT on `--task next`: it sets
# use_class_weights_cat, which only mtl_cv.py:497 reads, while next_cv.py:140 reads
# config.use_class_weights (set True by default_next). Verified 2026-08-07.
#
# All fp32 both arms; per-command env, never a bare export.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate

ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/stage2; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/stage2_DRIVER.log
SEED=${SEED:-0}
BEST_DED_LR=${BEST_DED_LR:-0.005}
BEST_CAT_LR=${BEST_CAT_LR:-0.001}
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }
COMMON_ENV=(PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1
            PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True)

score_ded(){ # tag rundir state extra_json_kv wall side
  python - "$1" "$2" "$3" "$4" "$5" "$6" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,extra,wall,side=sys.argv[1:7]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json"))
pf,eps=[],[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
d={"tag":tag,"arm":"dedicated","state":st_,"seed":int(__import__("os").environ.get("SEED","0")),
   "wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
   "argmax_mean":s["cat_macro_f1_mean"],"argmax_std":s["cat_macro_f1_std"],
   "argmax_per_fold":s["cat_per_fold"],"argmax_best_epochs":s["cat_best_epochs"],
   "sm3_mean":round(stx.mean(pf),4),"sm3_std":round(stx.stdev(pf),4) if len(pf)>1 else 0.0,
   "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
   "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]}
d.update(json.loads(extra))
json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} argmax={d['argmax_mean']} sm3={d['sm3_mean']} med_ep={d['median_best_epoch']} ({wall}s)")
PY
}

ded_run(){ # tag state bs lr epochs extra_flags extra_json
  local tag=$1; local st=$2; local bs=$3; local lr=$4; local ep=$5; local xf=$6; local xj=$7
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "  SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "  RUN  $tag  [bs=$bs lr=$lr ep=$ep $xf]"
  # shellcheck disable=SC2086
  env "${COMMON_ENV[@]}" MTL_NO_TRAIN_DIAGNOSTICS=1 \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18sweep_ded_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 --folds 5 --epochs "$ep" --seed "$SEED" \
      --batch-size "$bs" --max-lr "$lr" $xf --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "  FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "$tag" >> "$lg" 2>&1
  SEED=$SEED score_ded "$tag" "$rd" "$st" "$xj" "$((SECONDS-t0))" "$side" | tee -a "$DRV"
}

mtl_run(){ # tag state catlr catweight epochs extra_flags extra_json
  local tag=$1; local st=$2; local clr=$3; local cw=$4; local ep=$5; local xf=$6; local xj=$7
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "  SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "  RUN  $tag  [cat-lr=$clr cw=$cw ep=$ep $xf]"
  # shellcheck disable=SC2086
  env "${COMMON_ENV[@]}" MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 MTL_ONECYCLE_PER_HEAD_LR=1 \
      MTL_RAM_HEADROOM_GB=12 TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18sweep_mtl_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed "$SEED" --epochs "$ep" --folds 5 --batch-size 8192 \
      --mtl-loss static_weight --category-weight "$cw" --no-reg-class-weights $xf \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs8192_ep${ep}_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "  FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SEED" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$xj" "$((SECONDS-t0))" "$side" "$SEED" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,extra,wall,side,sd=sys.argv[1:8]
a=json.load(open(f"{rd}/a40_matched_score.json"))
pf,eps=[],[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
d={"tag":tag,"arm":"mtl","state":st_,"seed":int(sd),"wall_seconds":int(wall),"rundir":rd,
   "precision":"fp32","argmax_mean":a["cat_macro_f1_mean"],"argmax_std":a["cat_macro_f1_std"],
   "argmax_per_fold":a["cat_per_fold"],"argmax_best_epochs":a["cat_best_epochs"],
   "reg_mean":a["reg_full_top10_mean"],"reg_per_fold":a["reg_per_fold"],
   "sm3_mean":round(stx.mean(pf),4),"sm3_std":round(stx.stdev(pf),4) if len(pf)>1 else 0.0,
   "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps}
d.update(json.loads(extra))
json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} cat_argmax={d['argmax_mean']} sm3={d['sm3_mean']} reg={d['reg_mean']} ({wall}s)")
PY
}

log "===== v18 STAGE 2 START (seed $SEED, BEST_DED_LR=$BEST_DED_LR BEST_CAT_LR=$BEST_CAT_LR) ====="

# --- row 4: alabama dedicated WITHOUT class weights (the correct flag is --no-class-weights) ---
log "-- row 4: AL dedicated, class weights OFF"
ded_run "ded_alabama_nocw_lr0.005_ep50_s${SEED}"       alabama 2048 0.005          50 "--no-class-weights" '{"class_weights":false,"row":4}'
ded_run "ded_alabama_nocw_lr${BEST_DED_LR}_ep50_s${SEED}" alabama 2048 "$BEST_DED_LR" 50 "--no-class-weights" '{"class_weights":false,"row":4}'

# --- row 5: TEXAS dedicated, grid goes UP (large states do not overfit: train-val gap +0.25) ---
log "-- row 5: TX dedicated, upward grid"
for lr in 0.005 0.0075 0.01; do
  ded_run "ded_texas_bs8192_lr${lr}_ep50_s${SEED}" texas 8192 "$lr" 50 "" '{"class_weights":true,"row":5}'
done
for ep in 75; do
  ded_run "ded_texas_bs8192_lr0.005_ep${ep}_s${SEED}" texas 8192 0.005 "$ep" "" '{"class_weights":true,"row":5}'
done

# --- row 6: TEXAS dedicated without class weights (effect may be size-dependent) ---
log "-- row 6: TX dedicated, class weights OFF"
ded_run "ded_texas_nocw_lr0.005_ep50_s${SEED}" texas 8192 0.005 50 "--no-class-weights" '{"class_weights":false,"row":6}'

# --- row 7: alabama MTL knobs — cat class weights x category weight ---
log "-- row 7: AL MTL knobs"
mtl_run "mtl_alabama_cw0.75_nocatw_s${SEED}" alabama "$BEST_CAT_LR" 0.75 50 "--no-cat-class-weights" '{"cat_class_weights":false,"category_weight":0.75,"row":7}'
mtl_run "mtl_alabama_cw0.75_catw_s${SEED}"   alabama "$BEST_CAT_LR" 0.75 50 "--cat-class-weights"    '{"cat_class_weights":true,"category_weight":0.75,"row":7}'
mtl_run "mtl_alabama_cw0.50_nocatw_s${SEED}" alabama "$BEST_CAT_LR" 0.50 50 "--no-cat-class-weights" '{"cat_class_weights":false,"category_weight":0.50,"row":7}'
mtl_run "mtl_alabama_cw0.50_catw_s${SEED}"   alabama "$BEST_CAT_LR" 0.50 50 "--cat-class-weights"    '{"cat_class_weights":true,"category_weight":0.50,"row":7}'

log "===== v18 STAGE 2 rows 4-7 COMPLETE — row 8 (TX MTL) is CONDITIONAL, launch separately ====="
