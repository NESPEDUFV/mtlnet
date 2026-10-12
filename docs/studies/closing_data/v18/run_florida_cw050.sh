#!/usr/bin/env bash
# v18 probe, part 2 (user request 2026-08-06): repeat the 0.50/0.50 loss split at FLORIDA.
#
# Alabama said the split is not where the lost category advantage went (+0.29 pp, p=0.42) and that
# the heads are orthogonal (cos ~ +0.001). Alabama is the SMALLEST state with the shortest per-user
# histories, so the open question is whether that holds where the category signal is stronger.
#
# Only the 0.50 arm is run. The 0.75 comparand already exists from wave 1
# (docs/results/closing_data/v18/florida_s0_joint.json: cat 35.8785, reg 77.2552) and the wave-1
# cell was produced WITHOUT MTL_TRAIN_DIAGNOSTICS. That is safe to compare against because at
# alabama the diagnostics were proven numerically inert: probe arm A reproduced the wave-1 cell
# EXACTLY (27.3836 / 69.6831 to four decimals) with diagnostics on and donated buffers off.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; ST=florida; SD=0; ARM=FL_cw050
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/lossweight_probe
SIDE=docs/results/closing_data/v18_probe
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/lossweight_probe_DRIVER.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

side="$SIDE/${ARM}.json"
if [ -f "$side" ]; then log "SKIP $ARM (sidecar exists)"; exit 0; fi
lg="$OUT/${ARM}.log"; t0=$SECONDS
log "START $ARM  [florida, static_weight 0.50/0.50, diagnostics ON]"
export MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export MTL_ONECYCLE_PER_HEAD_LR=1 MTL_TRAIN_DIAGNOSTICS=1
export MTL_RAM_HEADROOM_GB=12
export TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_v18probe_${ARM}"
python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
  --state "$ST" --seed "$SD" --epochs 50 --folds 5 --batch-size 8192 \
  --mtl-loss static_weight --category-weight 0.50 --no-reg-class-weights --no-cat-class-weights \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
  --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$lg" 2>&1 &
pid=$!
wait $pid; rc=$?
rd=$(ls -d results/$ENG/$ST/mtlnet_*bs8192_ep50_*_${pid} 2>/dev/null | head -1)
if [ $rc -ne 0 ] || [ -z "$rd" ]; then log "FAIL $ARM rc=$rc rd='$rd' (see $lg)"; exit 1; fi
python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag v18probe_${ARM} \
  > "$OUT/${ARM}_score.txt" 2>&1
python scripts/closing_data/score_joint_best.py "$rd" --seed "$SD" --tag v18probe_${ARM} \
  >> "$OUT/${ARM}_score.txt" 2>&1 || true
python - "$ARM" "$rd" "$((SECONDS-t0))" "$side" <<'PY'
import json, sys, glob, csv, statistics as st
arm, rd, wall, side = sys.argv[1:5]
a = json.load(open(f"{rd}/a40_matched_score.json"))
cos, gn_cat, gn_reg = [], [], []
for f in sorted(glob.glob(f"{rd}/diagnostics/fold*_diagnostics.csv")):
    for r in csv.DictReader(open(f)):
        def g(*names):
            for n in names:
                v = r.get(n)
                if v not in (None, "", "nan"):
                    try: return float(v)
                    except ValueError: return None
            return None
        c = g("grad_cosine_shared")
        if c is not None: cos.append(c)
        a_ = g("grad_norm_next_category_shared", "grad_norm_category_shared")
        b_ = g("grad_norm_next_region_shared", "grad_norm_region_shared")
        if a_ is not None: gn_cat.append(a_)
        if b_ is not None: gn_reg.append(b_)
def summ(v):
    if not v: return None
    return {"n": len(v), "mean": round(st.mean(v), 5),
            "sd": round(st.stdev(v), 5) if len(v) > 1 else 0.0,
            "min": round(min(v), 5), "max": round(max(v), 5),
            "frac_negative": round(sum(1 for x in v if x < 0) / len(v), 4)}
json.dump({"arm": arm, "state": "florida", "seed": 0,
           "loss_flags": "--mtl-loss static_weight --category-weight 0.50",
           "rundir": rd, "wall_seconds": int(wall),
           "cat": a.get("cat_macro_f1_mean"), "cat_sd": a.get("cat_macro_f1_std"),
           "reg": a.get("reg_full_top10_mean"), "reg_sd": a.get("reg_full_top10_std"),
           "cat_per_fold": a.get("cat_per_fold"), "reg_per_fold": a.get("reg_per_fold"),
           "grad_cosine_shared": summ(cos),
           "grad_norm_cat_shared": summ(gn_cat),
           "grad_norm_reg_shared": summ(gn_reg)}, open(side, "w"), indent=2)
c = summ(cos)
print(f"DONE {arm} cat={a.get('cat_macro_f1_mean')} reg={a.get('reg_full_top10_mean')} "
      f"cos_mean={(c or {}).get('mean')} frac_neg={(c or {}).get('frac_negative')} ({wall}s)")
PY
log "DONE  $ARM ($((SECONDS-t0))s) -> $side"
