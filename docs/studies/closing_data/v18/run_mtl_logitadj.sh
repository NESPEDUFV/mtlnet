#!/usr/bin/env bash
# v18 row 12 — LOGIT ADJUSTMENT on the MTL CATEGORY HEAD.
#
# WHY THIS MUST RUN. Row 11 gave the DEDICATED arm +2.7..+3.1 pp at all three small states
# (p<=0.014). mtl_cv.py:481-484 makes the same knob available to the joint model's cat head:
# "When config.loss_calibration is non-empty the CAT criterion is the train-stats calibrated loss
# ..., MUTUALLY EXCLUSIVE with cat class-weighting". Reporting a ~2.9 pp ceiling gain while the joint
# model was never offered the same tool would bias Delta-cat by that amount in the baseline's favour
# -- the "baseline sabotage" CEILINGS_N20_FINAL warns about, pointed the other way.
#
# COMPOSITION (verified): --logit-adjust-tau REPLACES cat class weighting. Do NOT also pass
# --cat-class-weights (stacking cratered in T1.4: AL 30.15 vs 49.97). --no-reg-class-weights stays:
# the reg criterion is separate and unaffected (mtl_cv.py:501-504).
#
# LEAK-SAFE: counts from dataloader_category.train.y -- the TRAIN fold only.
#
# category-weight: 0.75. The pre-registered tie-break is "break a category tie on REGION", and with
# AZ+IST measured region prefers cw0.75 significantly (AZ -0.111 p=0.037, IST -0.170 p=0.006) while
# category is null at all three. Alabama also gets a cw0.50 arm as a cheap interaction check.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/mtl_la; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/mtl_la_DRIVER.log
log(){ echo "[$(date '+%F %T')] MLA: $*" | tee -a "$D"; }

arm(){ # state tau catweight
  local st=$1 tau=$2 cw=$3
  local tag="mla_${st}_tau${tau}_cw${cw}"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [logit-adjust-tau=$tau cw=$cw; replaces cat class weighting]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18mla_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed 0 --epochs 50 --folds 5 --batch-size 8192 \
      --mtl-loss static_weight --category-weight "$cw" --no-reg-class-weights \
      --logit-adjust-tau "$tau" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs8192_ep50_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc (see $lg)"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed 0 --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$tau" "$cw" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,tau,cw,wall,side=sys.argv[1:8]
a=json.load(open(f"{rd}/a40_matched_score.json")); pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
json.dump({"tag":tag,"arm":"mtl","state":st_,"seed":0,"row":12,"logit_adjust_tau":float(tau),
  "category_weight":float(cw),"cat_class_weights":"replaced by logit adjustment",
  "wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "cat_argmax":a["cat_macro_f1_mean"],"cat_argmax_std":a["cat_macro_f1_std"],
  "cat_per_fold":a["cat_per_fold"],"cat_best_epochs":a["cat_best_epochs"],
  "reg":a["reg_full_top10_mean"],"reg_std":a["reg_full_top10_std"],"reg_per_fold":a["reg_per_fold"],
  "cat_sm3":round(stx.mean(pf),4) if pf else None,
  "cat_sm3_per_fold":[round(x,4) for x in pf]},open(side,"w"),indent=2)
print(f"DONE {tag} cat_sm3={round(stx.mean(pf),4)} reg={a['reg_full_top10_mean']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "waiting for row 11 (dedicated logit adjustment) to finish"
until grep -q "row 11 COMPLETE" "$BASE/logs/logitadj_DRIVER.log" 2>/dev/null; do sleep 60; done

TAU=$(python - <<'PY'
import json,glob,statistics as st
S='docs/results/closing_data/v18_sweep'
best,bt=None,0.5
for tau in (0.5,1.0):
    v=[json.load(open(f))['sm3_mean'] for f in glob.glob(f'{S}/la_*_tau{tau}_*.json')]
    if len(v)==3:
        m=st.mean(v)
        if best is None or m>best: best,bt=m,tau
print(bt)
PY
)
log "===== row 12: MTL logit adjustment at tau=$TAU (winner from row 11) ====="
arm alabama  "$TAU" 0.75
arm arizona  "$TAU" 0.75
arm istanbul "$TAU" 0.75
arm alabama  "$TAU" 0.50   # cheap interaction check on the loss split
log "===== row 12 COMPLETE ====="
