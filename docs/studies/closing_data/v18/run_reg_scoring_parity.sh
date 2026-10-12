#!/usr/bin/env bash
# v18 — does the NEW scoring default reproduce the BANKED region numbers? (author request)
#
# WHY THIS EXISTS. On 2026-08-10 the val-metric default changed under us: streamed + rank-derived
# hits + GPU, replacing full-logit + topk on CPU. Every banked v18 region cell used the OLD path.
# The change was validated on one arizona cell on an H100 and declared "identical to 4 dp" — but the
# first cell we ran under it (california seed 7, C=8501) ABORTED on the ambiguity certificate:
#
#   1 row AMBIGUOUS at the 5/6 boundary   (top10, the metric we actually report: 0/585092)
#
# So the equivalence is NOT free at our class counts, and the honest move is to measure it on our own
# states rather than inherit a claim. This re-runs two states at a seed we ALREADY have banked and
# compares, which is the only test that answers "do the numbers bump?" directly.
#
# ARMS, per state (arizona, istanbul), both at seed 0 — a cell we have banked:
#   legacy  P1_STREAM_VAL=0  -> full-logit + topk, exactly what the banked cell used
#   stream  (new default)    -> streamed + rank-derived + GPU, certificate armed but NOT strict,
#                              so it WARNS and completes instead of aborting; we want the number
#                              even when a row is ambiguous, because the size of the disagreement
#                              is the whole question.
#
# ⚠ WRITE ISOLATION: distinct --tag per arm, so neither run can overwrite the banked
# docs/results/P1/..._v18_<state>_reg_s0.json, and NO sidecar is written into
# docs/results/closing_data/v18/. Nothing already logged is touched.
#
# Cost: arizona ~190 s/arm, istanbul ~490 s/arm -> ~23 min for all four.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"

ENG=check2hgi_v18
V14=check2hgi_design_k_resln_mae_l0_1
BASE=docs/studies/closing_data/v18
LOGS=$BASE/logs/scoring_parity
DRV=$BASE/logs/scoring_parity_DRIVER.log
mkdir -p "$LOGS"
log(){ echo "[$(date '+%F %T')] PARITY: $*" | tee -a "$DRV"; }

arm(){ # state arm_name extra_env
  local st=$1
  local nm=$2
  local extra=$3
  local tag="scoreparity_${st}_s0_${nm}"
  local lg="$LOGS/${tag}.log"
  local t0=$SECONDS
  log "  RUN $st [$nm] ${extra:-<new default>}"
  # MTL_STRICT is deliberately NOT set: we want a completed number even if a row is ambiguous.
  env MTL_CHUNK_VAL_METRIC=1 MTL_DISABLE_AMP=1 $extra \
    python -u scripts/p1_region_head_ablation.py --state "$st" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$ENG" --folds 5 --epochs 50 --seed 0 --target region \
    --max-lr 0.003 --compile --tf32 --tag "$tag" > "$lg" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local rj="docs/results/P1/region_head_${st}_region_5f_50ep_${tag}.json"
  [ $rc -ne 0 -o ! -f "$rj" ] && { log "  FAIL $st [$nm] rc=$rc (see $lg)"; return 1; }
  log "  DONE $st [$nm] ($((SECONDS-t0))s)"
}

log "===== region scoring parity: legacy(topk/CPU) vs new default(stream/rank/GPU), seed 0 ====="
for st in arizona istanbul; do
  arm "$st" legacy "P1_STREAM_VAL=0" || true
  arm "$st" stream ""                || true
done

log "===== COMPARISON vs the BANKED cell ====="
python - <<'PY' 2>&1 | tee -a "$DRV"
import json, os
def load(p):
    if not os.path.exists(p): return None
    return json.load(open(p))["heads"]["next_stan_flow"]
def acc10(h):
    return None if h is None else h["aggregate"]["top10_acc_mean"]*100
def folds(h):
    return [] if h is None else [f["top10_acc"]*100 for f in h.get("per_fold", [])]
P="docs/results/P1/region_head_{s}_region_5f_50ep_{t}.json"
print(f"\n{'state':<10}{'banked':>12}{'legacy':>12}{'stream':>12}{'legacy-bank':>13}{'stream-bank':>13}")
for s in ("arizona","istanbul"):
    b = load(P.format(s=s, t=f"v18_{s}_reg_s0"))
    l = load(P.format(s=s, t=f"scoreparity_{s}_s0_legacy"))
    n = load(P.format(s=s, t=f"scoreparity_{s}_s0_stream"))
    ab, al, an = acc10(b), acc10(l), acc10(n)
    f = lambda v: f"{v:12.6f}" if v is not None else f"{'—':>12}"
    d = lambda x,y: f"{x-y:+13.6f}" if (x is not None and y is not None) else f"{'—':>13}"
    print(f"{s:<10}{f(ab)}{f(al)}{f(an)}{d(al,ab)}{d(an,ab)}")
    for lbl, h in (("banked", b), ("legacy", l), ("stream", n)):
        v = folds(h)
        if v: print(f"    {lbl:<8} per-fold " + " ".join(f"{x:.6f}" for x in v))
print("\nverdict: legacy MUST reproduce banked exactly (same code path, same seed).")
print("         stream-bank is the number that decides whether the new default is poolable.")
PY
log "===== COMPLETE ====="
