#!/usr/bin/env bash
# v18 — independent PARITY CHECK of one already-completed cell, run alongside the live wave.
#
# Author request 2026-08-10: re-run alabama seed 1 dedicated-cat as a spot check, in parallel with
# the wave, WITHOUT touching any logged value.
#
# WRITE ISOLATION (the whole point):
#   - the sidecar goes to docs/results/closing_data/v18_paritycheck/, NOT .../v18/
#   - so run_wave.sh's skip logic is unaffected and the wave's own sidecar is never overwritten
#   - the rundir is a fresh results/check2hgi_v18/alabama/next_*_<pid>, colliding with nothing
#
# RECIPE: byte-identical to run_wave.sh cell_cat for alabama at seed 1 --
#   cat_bs() = 8192, cat_lr(alabama) = 0.0025, 5 folds, 50 epochs, tau 0.5, fp32, compile+tf32.
#
# ONE DELIBERATE DIFFERENCE: a private TORCHINDUCTOR_CACHE_DIR. The wave's cat cells use the default
# cache, and texas reg is writing to it right now; a private dir avoids any interaction with the live
# job. That makes this a cross-compile-session check, so the pass criterion is NOT bit-equality:
# CLAUDE.md records compiled numbers as within-fold-sigma rather than bit-reproducible, and the two
# cross-cache comparisons measured in this study came in at 0.000 (alabama joint) and 0.053
# (istanbul joint). Treat <= ~0.05 pp as a pass; a larger gap is worth investigating.
#
# COST: alabama cat is ~325 s alone. Sharing a 98%-busy card with texas reg, expect ~1.2-1.5x that.
# It will slow texas reg somewhat -- accepted, the author asked for a parallel run.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate

ENG=check2hgi_v18
BASE=docs/studies/closing_data/v18
OUT=$BASE/logs/parity; SIDE=docs/results/closing_data/v18_paritycheck
mkdir -p "$OUT" "$SIDE"
D=$BASE/logs/parity_DRIVER.log
log(){ echo "[$(date '+%F %T')] PARITY: $*" | tee -a "$D"; }

ST=alabama; SD=1; BS=8192; LR=0.0025; TAU=0.5
TAG="parity_${ST}_s${SD}_cat"
LG="$OUT/${TAG}.log"; T0=$SECONDS

log "RUN $TAG  (bs=$BS lr=$LR tau=$TAU, 5 folds, 50 ep) -- parallel with the live wave"
env MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 \
    PYTHONPATH=src PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_v18parity_${ST}" \
  python scripts/train.py --task next --state "$ST" --engine "$ENG" \
    --model next_gru --embedding-dim 64 --folds 5 --epochs 50 --seed "$SD" \
    --batch-size "$BS" --max-lr "$LR" --logit-adjust-tau "$TAU" \
    --compile --tf32 --no-checkpoints > "$LG" 2>&1 &
PID=$!; wait $PID; RC=$?
RD=$(ls -d results/$ENG/$ST/next_*_${PID} 2>/dev/null | head -1)
[ $RC -ne 0 -o -z "$RD" ] && { log "FAIL rc=$RC rd='$RD' (see $LG)"; exit 1; }

python scripts/closing_data/score_stl_cat_ceiling.py "$RD" --tag "$TAG" >> "$LG" 2>&1
python - "$TAG" "$RD" "$ST" "$SD" "$BS" "$LR" "$TAU" "$((SECONDS-T0))" "$SIDE/${TAG}.json" <<'PY'
import json,sys,glob,csv,statistics as stx
tag,rd,st_,sd,bs,lr,tau,wall,side=sys.argv[1:10]
s=json.load(open(f"{rd}/stl_cat_ceiling_score.json"))
pf,eps=[],[]
for f in sorted(glob.glob(f"{rd}/metrics/fold*_next_val.csv")):
    v=[float(r["f1"])*100 for r in csv.DictReader(open(f)) if r.get("f1") not in (None,"")]
    if not v: continue
    best,bi=float("-inf"),0
    for i in range(len(v)):
        w=v[max(0,i-1):i+2]; m=sum(w)/len(w)
        if m>best: best,bi=m,i
    pf.append(v[bi]); eps.append(bi+1)
json.dump({"tag":tag,"arm":"dedicated-parity-check","state":st_,"seed":int(sd),
  "batch_size":int(bs),"max_lr":float(lr),"logit_adjust_tau":float(tau),"epochs":50,
  "wall_seconds":int(wall),"rundir":rd,"precision":"fp32",
  "note":"independent re-run for parity; private inductor cache; does NOT replace the wave sidecar",
  "cat":s["cat_macro_f1_mean"],"cat_per_fold":s["cat_per_fold"],
  "cat_best_epochs":s["cat_best_epochs"],
  "sm3_mean":round(stx.mean(pf),4),"sm3_per_fold":[round(x,4) for x in pf]},open(side,"w"),indent=2)
print(f"parity {tag} cat={s['cat_macro_f1_mean']}")
PY

python - <<'PY'
import json
a=json.load(open('docs/results/closing_data/v18/alabama_s1_cat.json'))['cat']
b=json.load(open('docs/results/closing_data/v18_paritycheck/parity_alabama_s1_cat.json'))['cat']
print(f"\n  wave-logged : {a:.4f}")
print(f"  parity re-run: {b:.4f}")
print(f"  delta        : {b-a:+.4f}   -> {'PASS' if abs(b-a)<=0.06 else 'INVESTIGATE'} (tolerance 0.06 pp, cross-compile-session)")
PY
log "DONE $TAG ($((SECONDS-T0))s)"
