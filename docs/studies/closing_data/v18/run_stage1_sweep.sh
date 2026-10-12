#!/usr/bin/env bash
# v18 Stage 1 — re-tune the category schedule for the LEAK-FREE substrate, BOTH ARMS.
#
# WHY. The per-state dedicated-cat recipe (bs2048/8192 @ max_lr 0.005, 50 ep OneCycle) was tuned on
# the LEAKED substrate, where category was a much stronger signal. On v18 both arms peak early and
# then degrade:  dedicated median best epoch 8/50, MTL 21/50, vs v17's 44/50.
# In v17's own 76-arm sweep, an early-peaking arm (median best epoch <= 15) was NEVER a ceiling
# (0/27) and averaged -2.59 pp below it. All ten v18 dedicated cells are early-peaking, so under the
# study's own best-vs-best rule the current "ceiling" is not a ceiling.
#
# BOTH arms are re-tuned (user decision): fixing only the baseline would bias Delta-cat against MTL,
# since the MTL category head is early-peaking too.
#
# PRECISION. Everything here is fp32 (MTL_DISABLE_AMP=1) on BOTH arms (user decision), which also
# removes the AMP-leak inconsistency documented in PRECISION_CAVEAT.md.
#
# ENV HYGIENE. Every training command gets its environment as a PER-COMMAND PREFIX. No bare
# `export` anywhere in this script -- that is precisely the bug that made run_wave.sh's cat cells
# fp16-or-fp32 depending on resume state.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate

ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/stage1; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/stage1_DRIVER.log
SEED=${SEED:-0}
STATES=${STATES:-"alabama arizona istanbul"}
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

COMMON_ENV=(PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1
            PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True)

# ---------------------------------------------------------------- dedicated category arm
ded_arm(){
  local st=$1; local bs=$2; local lr=$3; local ep=$4
  local tag="ded_${st}_bs${bs}_lr${lr}_ep${ep}_s${SEED}"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "  SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "  RUN  $tag"
  env "${COMMON_ENV[@]}" MTL_NO_TRAIN_DIAGNOSTICS=1 \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18sweep_ded_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 --folds 5 --epochs "$ep" --seed "$SEED" \
      --batch-size "$bs" --max-lr "$lr" --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "  FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$bs" "$lr" "$ep" "$SEED" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,bs,lr,ep,sd,wall,side=sys.argv[1:10]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json"))
# de-noised selector, same rule as stage0_rescore.py: raw value at smoothed-argmax epoch
pf,eps=[],[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
json.dump({"tag":tag,"arm":"dedicated","state":st_,"batch_size":int(bs),"max_lr":float(lr),
  "epochs":int(ep),"seed":int(sd),"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "argmax_mean":s["cat_macro_f1_mean"],"argmax_std":s["cat_macro_f1_std"],
  "argmax_per_fold":s["cat_per_fold"],"argmax_best_epochs":s["cat_best_epochs"],
  "sm3_mean":round(stx.mean(pf),4),"sm3_std":round(stx.stdev(pf),4) if len(pf)>1 else 0.0,
  "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
  "median_best_epoch":sorted(s["cat_best_epochs"])[len(s["cat_best_epochs"])//2]},
  open(side,"w"),indent=2)
print(f"DONE {tag} argmax={s['cat_macro_f1_mean']} sm3={round(stx.mean(pf),4)} "
      f"med_ep={sorted(s['cat_best_epochs'])[len(s['cat_best_epochs'])//2]} ({wall}s)")
PY
  log "  $(tail -1 "$lg" 2>/dev/null | head -c 0)DONE $tag ($((SECONDS-t0))s)"
}

# ---------------------------------------------------------------- joint (MTL) category arm
mtl_arm(){
  local st=$1; local catlr=$2; local ep=$3
  local tag="mtl_${st}_catlr${catlr}_ep${ep}_s${SEED}"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "  SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "  RUN  $tag"
  env "${COMMON_ENV[@]}" MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 MTL_ONECYCLE_PER_HEAD_LR=1 \
      MTL_RAM_HEADROOM_GB=12 TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18sweep_mtl_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed "$SEED" --epochs "$ep" --folds 5 --batch-size 8192 \
      --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$catlr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs8192_ep${ep}_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "  FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SEED" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$catlr" "$ep" "$SEED" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,catlr,ep,sd,wall,side=sys.argv[1:9]
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
json.dump({"tag":tag,"arm":"mtl","state":st_,"cat_lr":float(catlr),"epochs":int(ep),
  "seed":int(sd),"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "argmax_mean":a["cat_macro_f1_mean"],"argmax_std":a["cat_macro_f1_std"],
  "argmax_per_fold":a["cat_per_fold"],"argmax_best_epochs":a["cat_best_epochs"],
  "reg_mean":a["reg_full_top10_mean"],"reg_per_fold":a["reg_per_fold"],
  "sm3_mean":round(stx.mean(pf),4),"sm3_std":round(stx.stdev(pf),4) if len(pf)>1 else 0.0,
  "sm3_per_fold":[round(x,4) for x in pf],"sm3_best_epochs":eps,
  "median_best_epoch":sorted(a["cat_best_epochs"])[len(a["cat_best_epochs"])//2]},
  open(side,"w"),indent=2)
print(f"DONE {tag} cat_argmax={a['cat_macro_f1_mean']} sm3={round(stx.mean(pf),4)} "
      f"reg={a['reg_full_top10_mean']} ({wall}s)")
PY
  log "  DONE $tag ($((SECONDS-t0))s)"
}

log "===== v18 STAGE 1 sweep START (seed $SEED, states: $STATES, fp32 both arms) ====="

# --- dedicated arm: LR grid (the failure is early-peak, so the grid goes DOWN from 0.005),
#     both batch sizes, plus the 0.005 anchor re-run at fp32 for a like-for-like reference.
for st in $STATES; do
  log "-- dedicated: $st"
  for bs in 2048 8192; do
    for lr in 0.0005 0.001 0.0025 0.005; do
      ded_arm "$st" "$bs" "$lr" 50 || true
    done
  done
done

# --- dedicated arm: schedule-shape probe at the per-state anchor batch
for st in $STATES; do
  case $st in arizona) bs=8192 ;; *) bs=2048 ;; esac
  for ep in 15 25; do ded_arm "$st" "$bs" 0.005 "$ep" || true; done
done

# --- MTL arm: category-head LR grid + a shorter schedule at the anchor LR
for st in $STATES; do
  log "-- mtl: $st"
  for catlr in 0.0005 0.001 0.002; do mtl_arm "$st" "$catlr" 50 || true; done
  mtl_arm "$st" 0.001 25 || true
done

log "===== v18 STAGE 1 sweep COMPLETE ====="
