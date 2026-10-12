#!/usr/bin/env bash
# v18 T1/T2 — is the shared trunk ACTIVELY HARMFUL at small data?
#
# At alabama the joint model is WORSE than the dedicated one on BOTH heads (Δcat -0.65/-1.04,
# Δreg -0.31/-0.33) while the dedicated arm memorizes (train macro-F1 66.4 vs val 24.0).
# Hypothesis: the shared trunk adds capacity that feeds memorization at small data.
#
# This is the OPPOSITE hypothesis to the CA/TX triage, where severing the trunk cost nothing
# (region_1fold_triage/FINDING.md). Here we ask whether severing HELPS.
#
#   T1  A   --model-param disable_cross_attn=True   two independent towers, no sharing
#   T2  A'  --model-param identity_cross_attn=True  keeps per-stream FFN depth, zeroes only mixing
#
# CAVEAT (Fable review): A' keeps ~1.05M attention weights present-but-unused, so it controls for
# per-stream FFN DEPTH, not attention capacity. A vs A' decomposes mixing vs depth. Neither controls
# the 2.5-5.9x dual-tower region pathway.
#
# Run 1-WIDE, matching the conditions of the champion-G baseline it is compared against
# (alabama s0: cat 27.3836 / reg 69.6831, 1094 s).
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/trunk_fl; SIDE=docs/results/closing_data/v18_trunk
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/trunk_fl_DRIVER.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

arm(){
  local tag=$1; local mp=$2
  local side="$SIDE/${tag}.json"
  [ -f "$side" ] && { log "SKIP $tag"; return 0; }
  local lg="$OUT/${tag}.log"; local t0=$SECONDS
  log "RUN  $tag  [$mp]"
  # shellcheck disable=SC2086
  env PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1 \
      MTL_ONECYCLE_PER_HEAD_LR=1 MTL_RAM_HEADROOM_GB=12 \
      PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
      TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18trunk_${tag}" \
    python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
      --state "$ST" --seed "$SD" --epochs 50 --folds 5 --batch-size 8192 \
      --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
      $mp --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$ST/mtlnet_*bs8192_ep50_*_${pid} 2>/dev/null | head -1)
  [ $rc -ne 0 -o -z "$rd" ] && { log "FAIL $tag rc=$rc"; return 1; }
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "$tag" >> "$lg" 2>&1
  python - "$tag" "$rd" "$mp" "$((SECONDS-t0))" "$side" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,mp,wall,side=sys.argv[1:6]
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
json.dump({"tag":tag,"state":"florida","seed":0,"model_param":mp,"rundir":rd,
  "wall_seconds":int(wall),"precision":"fp32",
  "cat_argmax":a["cat_macro_f1_mean"],"cat_argmax_std":a["cat_macro_f1_std"],
  "cat_per_fold":a["cat_per_fold"],"cat_best_epochs":a["cat_best_epochs"],
  "reg":a["reg_full_top10_mean"],"reg_std":a["reg_full_top10_std"],
  "reg_per_fold":a["reg_per_fold"],
  "cat_sm3":round(stx.mean(pf),4) if pf else None,
  "cat_sm3_per_fold":[round(x,4) for x in pf]},open(side,"w"),indent=2)
print(f"DONE {tag} cat={a['cat_macro_f1_mean']} reg={a['reg_full_top10_mean']} ({wall}s)")
PY
  log "DONE $tag ($((SECONDS-t0))s)"
}

log "===== v18 TRUNK arms at florida (florida baseline champion-G: cat 35.8785 / reg 77.2552) ====="
arm T1_A_nosharing_FL "--model-param disable_cross_attn=True"
# T2 at florida is CONDITIONAL on T1 -- see POSTPONED.md P5
log "===== TRUNK arms COMPLETE ====="
