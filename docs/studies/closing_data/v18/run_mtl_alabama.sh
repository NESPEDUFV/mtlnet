#!/usr/bin/env bash
# v18 SWEEP_PLAN rows 3 + 7, ALABAMA ONLY (user decision 2026-08-07).
#
# Scope: decide the MTL-side knobs at the cheapest state, then carry only well-justified settings to
# a bigger state. Row 3 = category-head LR + schedule length. Row 7 = the class-weight asymmetry and
# the loss split, at the row-3 winner's LR.
#
# WHY class weights are in here: the DEDICATED arm trains class-weighted CE (default_next,
# use_class_weights=True) while the MTL arm does not (C25, default_mtl use_class_weights_cat=False).
# The metric is macro-F1, which class weighting helps. So the baseline gets an advantage the joint
# model is denied, inside the very comparison we report. Row 7 measures that.
#
# All fp32, per-command env (never a bare export), 1-wide.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; ST=alabama; SD=0
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/mtl_al; SIDE=docs/results/closing_data/v18_sweep
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/mtl_al_DRIVER.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

mtl(){ # tag catlr catweight epochs extra_flags extra_json
  local tag=$1; local clr=$2; local cw=$3; local ep=$4; local xf=$5; local xj=$6
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag  [cat-lr=$clr cw=$cw ep=$ep $xf]"
  # shellcheck disable=SC2086
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18mtlal" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$ST" --seed "$SD" --epochs "$ep" --folds 5 --batch-size 8192 \
      --mtl-loss static_weight --category-weight "$cw" --no-reg-class-weights $xf \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr "$clr" --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$ST/mtlnet_*bs8192_ep${ep}_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$xj" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,extra,wall,side=sys.argv[1:6]
a=json.load(open(f"{rd}/a40_matched_score.json"))
pf=[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_category_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi])
d={"tag":tag,"arm":"mtl","state":"alabama","seed":0,"wall_seconds":int(wall),"rundir":rd,
   "precision":"fp32","cat_argmax":a["cat_macro_f1_mean"],"cat_argmax_std":a["cat_macro_f1_std"],
   "cat_per_fold":a["cat_per_fold"],"cat_best_epochs":a["cat_best_epochs"],
   "reg":a["reg_full_top10_mean"],"reg_std":a["reg_full_top10_std"],"reg_per_fold":a["reg_per_fold"],
   "cat_sm3":round(stx.mean(pf),4) if pf else None,
   "cat_sm3_per_fold":[round(x,4) for x in pf]}
d.update(json.loads(extra))
json.dump(d,open(side,"w"),indent=2)
print(f"DONE {tag} cat={d['cat_argmax']} sm3={d['cat_sm3']} reg={d['reg']} ({wall}s)")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "===== v18 MTL rows 3+7 at ALABAMA (baseline champion-G: cat 27.3836 / reg 69.6831) ====="

# --- row 3: category-head LR + schedule length -------------------------------------------------
mtl "mtlAL_r3_catlr0.0005_ep50" 0.0005 0.75 50 "--no-cat-class-weights" '{"row":3,"cat_lr":0.0005}'
mtl "mtlAL_r3_catlr0.001_ep50"  0.001  0.75 50 "--no-cat-class-weights" '{"row":3,"cat_lr":0.001,"anchor":true}'
mtl "mtlAL_r3_catlr0.002_ep50"  0.002  0.75 50 "--no-cat-class-weights" '{"row":3,"cat_lr":0.002}'
mtl "mtlAL_r3_catlr0.001_ep25"  0.001  0.75 25 "--no-cat-class-weights" '{"row":3,"cat_lr":0.001,"epochs":25}'

# --- row 7: class-weight asymmetry x loss split, at the anchor LR ------------------------------
# (the cw0.75/no-cat-weights cell IS the row-3 anchor above and is not repeated)
mtl "mtlAL_r7_cw0.75_catwON"  0.001 0.75 50 "--cat-class-weights"    '{"row":7,"cat_class_weights":true,"category_weight":0.75}'
mtl "mtlAL_r7_cw0.50_catwOFF" 0.001 0.50 50 "--no-cat-class-weights" '{"row":7,"cat_class_weights":false,"category_weight":0.50}'
mtl "mtlAL_r7_cw0.50_catwON"  0.001 0.50 50 "--cat-class-weights"    '{"row":7,"cat_class_weights":true,"category_weight":0.50}'

log "===== MTL rows 3+7 at ALABAMA COMPLETE ====="
