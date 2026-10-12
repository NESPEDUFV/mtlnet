#!/usr/bin/env bash
# v18 SWEEP_PLAN row 10 — MTL BATCH SIZE at alabama (author curiosity, 2026-08-08).
#
# ⚠ WHY THIS IS NOT A `--max-lr` SWEEP. With MTL_ONECYCLE_PER_HEAD_LR=1 (our recipe),
# helpers.py:350-353 builds OneCycle with max_lr = [pg["lr"] for pg in param_groups] -- i.e. the
# PER-HEAD lrs. `--max-lr` is IGNORED. Sweeping it would have produced 6 runs differing only in
# batch size. So the requested LR grid {0.005, 0.0075, 0.01} is applied as a SCALE FACTOR on the
# per-head lrs (x1.67, x2.5, x3.33 vs the champion's max-lr 3e-3), preserving the champion's
# cat:reg:shared ratio of 1 : 3 : 1.
#
#   factor  cat-lr    reg-lr    shared-lr
#    1.67   0.00167   0.00500   0.00167
#    2.50   0.00250   0.00750   0.00250
#    3.33   0.00333   0.01000   0.00333
#
# ⚠ STEP STARVATION AT ALABAMA. train/fold ~77,060 windows:
#     bs  8192 -> 9.4 batches/epoch -> 470 steps over 50 epochs   (current)
#     bs 16384 -> 4.7               -> 235
#     bs 32768 -> 2.4               -> 118
# bs 32768 gives OneCycle ~118 total steps. A poor result there is expected from step count, not
# from batch size, and must NOT be read as "large batches hurt". The question is better posed at a
# large state; at alabama it is confounded.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; ST=alabama; SD=0
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/mtl_bs; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/mtl_bs_DRIVER.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

run(){ # tag bs catlr reglr sharedlr factor
  local tag=$1 bs=$2 clr=$3 rlr=$4 slr=$5 fac=$6
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag  [bs=$bs cat-lr=$clr reg-lr=$rlr shared-lr=$slr]"
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18mtlbs" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$ST" --seed "$SD" --epochs 50 --folds 5 --batch-size "$bs" \
      --mtl-loss static_weight --category-weight 0.50 --no-reg-class-weights --cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr "$rlr" --shared-lr "$slr" \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$ST/mtlnet_*bs${bs}_ep50_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$bs" "$clr" "$fac" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,bs,clr,fac,wall,side=sys.argv[1:8]
a=json.load(open(f"{rd}/a40_matched_score.json")); pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
json.dump({"tag":tag,"arm":"mtl","state":"alabama","seed":0,"row":10,"batch_size":int(bs),
  "cat_lr":float(clr),"lr_factor":float(fac),"category_weight":0.50,"cat_class_weights":True,
  "wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "cat_argmax":a["cat_macro_f1_mean"],"cat_argmax_std":a["cat_macro_f1_std"],
  "cat_per_fold":a["cat_per_fold"],"cat_best_epochs":a["cat_best_epochs"],
  "reg":a["reg_full_top10_mean"],"reg_std":a["reg_full_top10_std"],"reg_per_fold":a["reg_per_fold"],
  "cat_sm3":round(stx.mean(pf),4) if pf else None,
  "cat_sm3_per_fold":[round(x,4) for x in pf]},open(side,"w"),indent=2)
print(f"DONE {tag} cat={a['cat_macro_f1_mean']} sm3={round(stx.mean(pf),4)} reg={a['reg_full_top10_mean']}")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "===== v18 row 10: MTL batch size at alabama (on the tie-broken recipe: cw0.50 + class-weights ON) ====="
run mtlAL_r10_bs16k_f1.67 16384 0.00167 0.00500 0.00167 1.67
run mtlAL_r10_bs16k_f2.50 16384 0.00250 0.00750 0.00250 2.50
run mtlAL_r10_bs16k_f3.33 16384 0.00333 0.01000 0.00333 3.33
run mtlAL_r10_bs32k_f1.67 32768 0.00167 0.00500 0.00167 1.67
run mtlAL_r10_bs32k_f2.50 32768 0.00250 0.00750 0.00250 2.50
run mtlAL_r10_bs32k_f3.33 32768 0.00333 0.01000 0.00333 3.33
log "===== row 10 COMPLETE ====="
