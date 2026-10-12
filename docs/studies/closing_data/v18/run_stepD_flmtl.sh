#!/usr/bin/env bash
# v18 step D (finally run) + the alabama region logit-adjust check.
#
# WHY STEP D EXISTS. The author proposed bs16384 @ cat-lr 0.002 for LARGE-STATE MTL. That cell has
# never been measured. The batch evidence we have is:
#   - SS11.3 step C = TEXAS, but that is the DEDICATED next-category model: ONE head, no region
#     output, so it has NO geom. bs8192 wins there on the only metric that exists (sm3 cat).
#   - rows 10/10b = ALABAMA MTL, which does have geom, and bs8192 wins (all six larger-batch arms
#     below it, four significantly).
# Neither is large-state MTL. Step D was planned in the follow-up table and never ran; this is it.
#
# RECIPE. Run under the recipe we are ADOPTING (logit-adjust tau=0.5, category_weight 0.50), not the
# superseded class-weighted one -- otherwise we would be tuning batch size for a config we are about
# to stop shipping. That means bs8192 needs its own arm here: no FL MTL baseline exists under
# logit adjustment yet. Three arms, one fold, only batch size varies.
#
# Cat-lr is pinned at 0.002 (the author's choice) in ALL THREE arms, so this isolates batch size.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18
V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/stepD; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/stepD_DRIVER.log
log(){ echo "[$(date '+%F %T')] STEPD: $*" | tee -a "$D"; }

mtl_bs(){ # state bs catlr
  local st=$1
  local bs=$2
  local clr=$3
  local tag="d_${st}_bs${bs}_catlr${clr}_la0.5_f0"
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"
  local t0=$SECONDS
  log "RUN  $tag [bs=$bs cat-lr=$clr tau=0.5 cw=0.50, only-fold 0]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18stepd_${st}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$st" --seed 0 --epochs 50 --only-fold 0 --batch-size "$bs" \
      --mtl-loss static_weight --category-weight 0.50 --no-reg-class-weights \
      --logit-adjust-tau 0.5 \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$st" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$st/mtlnet_*bs${bs}_ep50_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc (see $lg)"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed 0 --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$st" "$bs" "$clr" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,math,statistics as stx
tag,rd,st_,bs,clr,wall,side=sys.argv[1:8]
a=json.load(open(f"{rd}/a40_matched_score.json")); pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
cat=round(stx.mean(pf),4); reg=a["reg_full_top10_mean"]
json.dump({"tag":tag,"arm":"mtl","state":st_,"seed":0,"row":"D","batch_size":int(bs),
  "cat_lr":float(clr),"logit_adjust_tau":0.5,"category_weight":0.50,"epochs":50,"n_folds":1,
  "screen":True,"wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "cat_sm3":cat,"cat_sm3_per_fold":[round(x,4) for x in pf],
  "cat_argmax":a["cat_macro_f1_mean"],"cat_per_fold":a["cat_per_fold"],
  "reg":reg,"reg_per_fold":a["reg_full_top10_per_fold"],
  "geom":round(math.sqrt(cat*reg),4)},open(side,"w"),indent=2)
print(f"DONE {tag} cat={cat} reg={reg} geom={round(math.sqrt(cat*reg),4)}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

reg_arm(){ # state tau
  local st=$1
  local tau=$2
  local tag="v18_${st}_reg_la${tau}_s0"
  local lg="$OUT/${tag}.log"
  local t0=$SECONDS
  log "RUN  region $tag [tau=$tau]"
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

log "===== step D: FL MTL batch size under the ADOPTED recipe ====="
mtl_bs florida 8192  0.002
mtl_bs florida 16384 0.002
mtl_bs florida 32768 0.002
log "===== alabama region logit-adjust check ====="
reg_arm alabama 0.0
reg_arm alabama 0.5
log "===== step D COMPLETE ====="
