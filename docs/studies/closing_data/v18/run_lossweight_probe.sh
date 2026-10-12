#!/usr/bin/env bash
# v18 probe (user request 2026-08-06): is 0.75/0.25 still the right loss split, and are the two
# heads' gradients actually competing, on the LEAK-FREE substrate?
#
# The 0.75 category weight was tuned on the leaked check2hgi. If the leak is what made the category
# head so productive, the tuned split may no longer be right.
#
# Three arms, alabama, seed 0, 5 folds, 50 epochs, v18 engine, everything else the frozen v17 recipe:
#   A  static_weight  --category-weight 0.75   the v18 baseline, re-run WITH diagnostics
#   B  static_weight  --category-weight 0.50   the equal split
#   C  pcgrad                                   gradient surgery (projects conflicting gradients)
#
# All three run MTL_TRAIN_DIAGNOSTICS=1, which enables mtl_cv._compute_gradient_cosine: once per
# epoch, on batch 0, it computes cos(grad L_cat, grad L_reg) over the SHARED parameters plus each
# task's gradient norm, into <rundir>/diagnostics/fold*_diagnostics.csv.
#
# Arm A is re-run rather than reused from the wave because diagnostics disable inductor's donated
# buffers under --compile, so the wave's arm-A numbers are not the same compile configuration.
# Comparing B and C against a same-configuration A keeps the contrast clean.
#
# PRIOR FINDING to test against: scripts/mtl_improvement/plot_grad_cosine.py records
# "cosine ~ 0 -> the two tasks' gradients are orthogonal -> there is no conflict" -- measured on the
# LEAKED substrate. Whether that survives the leak fix is the question.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18; V14=check2hgi_design_k_resln_mae_l0_1; ST=alabama; SD=0
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/lossweight_probe
SIDE=docs/results/closing_data/v18_probe
mkdir -p "$OUT" "$SIDE"
DRV=$BASE/logs/lossweight_probe_DRIVER.log
log(){ echo "[$(date '+%F %T')] $*" | tee -a "$DRV"; }

run_arm(){
  local arm=$1; local lossflags=$2
  local side="$SIDE/${arm}.json"
  if [ -f "$side" ]; then log "SKIP $arm (sidecar exists)"; return 0; fi
  local lg="$OUT/${arm}.log"
  local t0=$SECONDS
  log "START $arm  [$lossflags]"
  export MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
  export MTL_ONECYCLE_PER_HEAD_LR=1 MTL_TRAIN_DIAGNOSTICS=1
  export TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_v18probe_${arm}"
  # shellcheck disable=SC2086
  python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$ENG" \
    --state "$ST" --seed "$SD" --epochs 50 --folds 5 --batch-size 8192 \
    $lossflags --no-reg-class-weights --no-cat-class-weights \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower --checkpoint-selector geom_simple --compile --tf32 \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$lg" 2>&1 &
  local pid=$!
  wait $pid; local rc=$?
  local rd; rd=$(ls -d results/$ENG/$ST/mtlnet_*bs8192_ep50_*_${pid} 2>/dev/null | head -1)
  if [ $rc -ne 0 ] || [ -z "$rd" ]; then log "FAIL $arm rc=$rc rd='$rd' (see $lg)"; return 1; fi
  python scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag v18probe_${arm} \
    > "$OUT/${arm}_score.txt" 2>&1
  python scripts/closing_data/score_joint_best.py "$rd" --seed "$SD" --tag v18probe_${arm} \
    >> "$OUT/${arm}_score.txt" 2>&1 || true
  python - "$arm" "$rd" "$((SECONDS-t0))" "$lossflags" "$side" <<'PY'
import json, sys, glob, csv, statistics as st
arm, rd, wall, flags, side = sys.argv[1:6]
a = json.load(open(f"{rd}/a40_matched_score.json"))
# pull the per-epoch shared-gradient cosine out of the diagnostics CSVs
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
json.dump({"arm": arm, "state": "alabama", "seed": 0, "loss_flags": flags,
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
  log "$(tail -1 "$OUT/${arm}.done" 2>/dev/null || true)"
  log "DONE  $arm ($((SECONDS-t0))s) -> $side"
}

log "===== v18 loss-weight + gradient-conflict probe START (commit $(git rev-parse --short HEAD)) ====="
run_arm A_cw075 "--mtl-loss static_weight --category-weight 0.75" &
P1=$!
run_arm B_cw050 "--mtl-loss static_weight --category-weight 0.50" &
P2=$!
wait $P1; wait $P2
run_arm C_pcgrad "--mtl-loss pcgrad"
log "===== v18 probe COMPLETE ====="
