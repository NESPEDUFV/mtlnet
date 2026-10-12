#!/usr/bin/env bash
# v18 row 13 — LARGE-STATE VALIDATION of logit adjustment, + the region-head check.
#
# WHY. Row 11/12 adopted logit-adjust tau=0.5 at AL/AZ/IST (dedicated +2.86, MTL +3.18, p<=0.0014).
# It has NEVER run at a large state. The Fable review flagged a SPECIFIC risk, not generic caution:
# class weighting and logit adjustment correct the SAME prior-imbalance problem, and class weighting
# REVERSES SIGN at texas (SS11.2: OFF beats ON by +1.556, p=0.030). So texas is the state where the
# family of correction is known to misbehave -- it is the informative test, not california.
#
# BATCH SIZE (author asked for bs16384 "to be faster"). Measured at SS11.3: bs16384 is NOT faster --
# TX walls are 1116 / 1119 / 1117 s at bs 8192 / 16384 / 32768, i.e. identical. And it is WORSE:
# sm3 -0.111 (16k) and -0.552 (32k). So the speed rationale does not hold, and running the
# validation off-recipe would confound it. All arms here run bs8192 = the shipped config.
#
# ARMS
#   B  texas  cat  fold0  tau=0.5    <- baselines already on disk: cwON 33.6127, cwOFF 35.1696
#   C  calif. cat  fold0  tau=0 (cwON baseline) and tau=0.5
#   A  alabama REGION 5-fold tau=0 and tau=0.5  <- author request; region IS wired for it
#      (p1_region_head_ablation.py:652-662 builds CalibratedLoss on the REGION criterion from
#       y_train only). NOTE the theory says this should HURT: logit adjustment is Bayes-consistent
#       for BALANCED error (macro-F1), but region is reported by Acc@10, a frequency-weighted
#       metric, whose Bayes-optimal predictor is the UNADJUSTED posterior. mtl_cv.py:477-479 already
#       records that class-balancing hurts this head. Running it as an empirical check of that
#       prediction, cheap at 189 s/arm.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/ls_la; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/ls_la_DRIVER.log
log(){ echo "[$(date '+%F %T')] LSLA: $*" | tee -a "$D"; }

# ---- dedicated CATEGORY, one fold -------------------------------------------------
cat_arm(){
  local st=$1
  local bs=$2
  local lr=$3
  local tau=$4
  local cw=$5          # "on" | "off" ; ignored when tau>0 (logit-adjust replaces it)
  local tag="r13_${st}_tau${tau}_cw${cw}_f0"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"
  local t0=$SECONDS
  # NOTE: no `bc` on this box -- a `bc`-based numeric test silently evaluated to empty and ran a
  # PLAIN BASELINE with no --logit-adjust-tau. Pure-bash string test instead; tau is always passed
  # literally as "0.0" or "0.5" from the call sites below.
  local extra=""
  if [ "$tau" != "0.0" ]; then extra="--logit-adjust-tau $tau"
  elif [ "$cw" = "off" ]; then extra="--no-class-weights"; fi
  log "RUN  $tag  [${extra:-plain CE, class weights $cw}]"
  case "$tau:$extra" in
    0.5:) log "ABORT $tag -- tau=0.5 produced an empty flag"; return 1 ;;
  esac
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_NO_TRAIN_DIAGNOSTICS=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18la_${st}" \
    python scripts/train.py --task next --state "$st" --engine "$ENG" \
      --model next_gru --embedding-dim 64 --only-fold 0 --epochs 50 --seed 0 \
      --batch-size "$bs" --max-lr "$lr" $extra \
      --compile --tf32 --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/next_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc (see $lg)"; return 1; }
  python - "$tag" "$rd" "$st" "$bs" "$lr" "$tau" "$cw" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,bs,lr,tau,cw,wall,side=sys.argv[1:10]
pf=[];eps=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
json.dump({"tag":tag,"arm":"dedicated","row":13,"state":st_,"seed":0,"fold":0,
  "batch_size":int(bs),"max_lr":float(lr),"logit_adjust_tau":float(tau),
  "class_weights":("replaced by logit adjustment" if float(tau)>0 else cw),
  "epochs":50,"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "sm3_mean":round(stx.mean(pf),4),"sm3_per_fold":[round(x,4) for x in pf],
  "sm3_best_epochs":eps,"argmax_mean":round(max(pf),4)},open(side,"w"),indent=2)
print(f"DONE {tag} sm3={round(stx.mean(pf),4)}")
PY
  log "DONE $tag ($((SECONDS-t0))s)  $(python -c "import json;print(json.load(open('$side'))['sm3_mean'])")"
}

# ---- dedicated REGION, 5 folds ----------------------------------------------------
reg_arm(){
  local st=$1
  local tau=$2
  local tag="v18_${st}_reg_la${tau}_s0"
  local lg="$OUT/${tag}.log"
  local t0=$SECONDS
  log "RUN  region $tag [logit-adjust-tau=$tau]"
  env PYTHONPATH=src MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18reg_${st}" \
    python -u scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
      --input-type region --region-emb-source check2hgi_design_k_resln_mae_l0_1 \
      --override-hparams freeze_alpha=True alpha_init=0.0 \
      --engine-override "$ENG" --folds 5 --epochs 50 --seed 0 --target region \
      --max-lr 0.003 --logit-adjust-tau "$tau" --compile --tf32 --tag "$tag" > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  [ $rc -ne 0 ] && { log "FAIL region $tag rc=$rc (see $lg)"; return 1; }
  log "DONE region $tag ($((SECONDS-t0))s)"
}

log "===== row 13: large-state logit-adjust validation ====="
# B first: texas is the decisive state (its baselines are already on disk -> 1 arm, ~19 min)
cat_arm texas      8192 0.005 0.5 na
# C: california needs its own baseline + the tau arm
cat_arm california 8192 0.005 0.0 on
cat_arm california 8192 0.005 0.5 na
# A: the region check at alabama (cheap)
reg_arm alabama 0.0
reg_arm alabama 0.5
log "===== row 13 COMPLETE ====="
