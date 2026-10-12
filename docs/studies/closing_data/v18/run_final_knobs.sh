#!/usr/bin/env bash
# v18 — two final knobs, in order (author 2026-08-08):
#   STEP 1  AZ + IST at cw0.50 WITH logit adjustment -> settles the loss-split interaction
#   STEP 2  row 10 RE-RUN (MTL batch size at AL) on the ADOPTED recipe, i.e. logit adjustment +
#           whichever cw step 1 selects
#
# WHY ROW 10 MUST BE RE-RUN. The original row 10 measured batch size on the class-weighted recipe,
# which logit adjustment has since superseded by ~3 pp. A batch-size verdict on a superseded loss is
# not evidence about the recipe we intend to ship.
#
# WHY STEP 1 FIRST. At alabama the split REVERSED under calibration: cw0.50-vs-cw0.75 went from
# -0.273 (null, class-weighted) to +0.445 (p=0.024, calibrated). That is one state at n=5 and it
# contradicts the region-based tie-break, so it must be settled before it is baked into row 10.
#
# --logit-adjust-tau REPLACES cat class weighting (mtl_cv.py:481-484); --cat-class-weights is NOT
# passed. --no-reg-class-weights stays (separate criterion).
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; TAU=0.5
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/final; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/final_DRIVER.log
log(){ echo "[$(date '+%F %T')] FIN: $*" | tee -a "$D"; }

mtl(){ # tag state cw bs catlr reglr sharedlr extra_json
  local tag=$1 st=$2 cw=$3 bs=$4 clr=$5 rlr=$6 slr=$7 xj=$8
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag [cw=$cw bs=$bs cat-lr=$clr tau=$TAU]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18fin_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed 0 --epochs 50 --folds 5 --batch-size "$bs" \
      --mtl-loss static_weight --category-weight "$cw" --no-reg-class-weights \
      --logit-adjust-tau "$TAU" \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr "$rlr" --shared-lr "$slr" \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs${bs}_ep50_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then
    grep -qiE "out of memory|CUDA error" "$lg" && log "FAIL $tag — OOM/CUDA" || log "FAIL $tag rc=$rc"
    return 1
  fi
  python scripts/closing_data/a40_score_matched.py "$rd" --seed 0 --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$cw" "$bs" "$clr" "$xj" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,cw,bs,clr,xj,wall,side=sys.argv[1:10]
a=json.load(open(f"{rd}/a40_matched_score.json")); pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
d={"tag":tag,"arm":"mtl","state":st_,"seed":0,"category_weight":float(cw),"batch_size":int(bs),
   "cat_lr":float(clr),"logit_adjust_tau":0.5,"cat_class_weights":"replaced by logit adjustment",
   "wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
   "cat_argmax":a["cat_macro_f1_mean"],"cat_per_fold":a["cat_per_fold"],
   "cat_best_epochs":a["cat_best_epochs"],"reg":a["reg_full_top10_mean"],
   "reg_per_fold":a["reg_per_fold"],"cat_sm3":round(stx.mean(pf),4) if pf else None,
   "cat_sm3_per_fold":[round(x,4) for x in pf]}
d.update(json.loads(xj)); json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} cat_sm3={d['cat_sm3']} reg={d['reg']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "===== STEP 1: AZ + IST at cw0.50 with logit adjustment (settle the split) ====="
mtl "mla_arizona_tau0.5_cw0.50"  arizona  0.50 8192 0.001 3e-3 1e-3 '{"row":12,"step":1}'
mtl "mla_istanbul_tau0.5_cw0.50" istanbul 0.50 2048 0.001 3e-3 1e-3 '{"row":12,"step":1}'

# CW FIXED BY THE PRE-REGISTERED RULE, not by an automatic category-mean selector.
# Step 1 result: category is a TIE (mean +0.079; significant at alabama only, NEGATIVE at istanbul)
# while region prefers cw0.75 at ALL THREE states (-0.060 / -0.188 p=0.010 / -0.180 p=0.007).
# The pre-registered tie-break is "when category ties, break on REGION" -> cw0.75.
# The earlier auto-selector compared category means only and therefore picked cw0.50, contradicting
# the rule. Fixed 2026-08-09; the wrongly-split run was killed before any arm completed.
CW=0.75
log "===== STEP 2: row 10 RE-RUN at AL on the adopted recipe (cw=$CW + logit adjustment) ====="
# same grid as the original row 10 so the two are comparable; per-head LRs scaled (--max-lr is inert
# under MTL_ONECYCLE_PER_HEAD_LR=1)
mtl "r10b_AL_bs16k_f1.67" alabama "$CW" 16384 0.00167 0.00500 0.00167 '{"row":"10b","lr_factor":1.67}'
mtl "r10b_AL_bs16k_f2.50" alabama "$CW" 16384 0.00250 0.00750 0.00250 '{"row":"10b","lr_factor":2.50}'
mtl "r10b_AL_bs16k_f3.33" alabama "$CW" 16384 0.00333 0.01000 0.00333 '{"row":"10b","lr_factor":3.33}'
mtl "r10b_AL_bs32k_f1.67" alabama "$CW" 32768 0.00167 0.00500 0.00167 '{"row":"10b","lr_factor":1.67}'
mtl "r10b_AL_bs32k_f2.50" alabama "$CW" 32768 0.00250 0.00750 0.00250 '{"row":"10b","lr_factor":2.50}'
mtl "r10b_AL_bs32k_f3.33" alabama "$CW" 32768 0.00333 0.01000 0.00333 '{"row":"10b","lr_factor":3.33}'
log "===== FINAL KNOBS COMPLETE ====="
