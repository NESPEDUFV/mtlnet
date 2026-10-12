#!/usr/bin/env bash
# REGION-side mechanism probes -- TRIAGE PASS, one fold per arm.
#
# WHY ONE FOLD, and what it can and cannot settle: this pass is a screen, not a measurement. One fold
# gives ONE number per arm -- no dispersion, no paired test, no interval -- so it can only detect a LARGE
# effect. The useful asymmetry: if rg2 collapses toward the region ceiling (a several-point drop), one
# fold shows it unambiguously and the conclusion is settled early. If the arms land within a few tenths
# of each other, that is NOT a null result -- it is an inconclusive screen, and the five-fold pass is
# then required, because the fold-to-fold spread of this metric (FL category folds span 79.04-80.67) is
# wider than the effects at stake.
#
# CRITICAL -- the flag is --only-fold 0, NOT --folds 1. mtl_cv.py:680-688 documents the trap: "--folds N
# overrides config.k_folds to max(2,N), so a 1-fold smoke against a 5-fold-built log_T silently leaks
# ~30-40% of val transitions into the prior (the alpha scalar amplifies this, inflating reg
# top10_acc_indist by 13-23 pp)". Since the metric under study here IS region top10, that leak would
# manufacture the very effect we are looking for. --only-fold runs exactly fold 0 OF the canonical
# n_splits=5 split (train.py:1092-1103) and is mutually exclusive with --folds, so --folds is dropped.
#
# Datasets: the four that beat the dedicated region ceiling (CEILINGS_N20_FINAL.md:19-28) --
# Istanbul +0.28 (1.7G), FL +0.72 (7.7G), CA +2.20 (17G), TX +2.11 (21G). Cheapest first.
# AL (-0.31) and AZ (+0.10) excluded: region merely MATCHES there, so there is no gain to explain.
# Expected wall clock at one fold: Istanbul ~18m, FL ~75m, CA ~2.8h, TX ~3.4h for all three arms.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
PY=/home/vitor.oliveira/PoiMtlNet/.venv/bin/python
export PYTHONPATH=src
export MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_COMPILE_DYNAMIC=1 MTL_ONECYCLE_PER_HEAD_LR=1 MTL_STRICT=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_region1f
OVL=check2hgi_dk_ovl; V14=check2hgi_design_k_resln_mae_l0_1
ROOT=/home/vitor.oliveira/region_1fold; mkdir -p "$ROOT"

"$PY" -c 'import torch,sys; sys.exit(0 if torch.cuda.is_available() else 3)' || { echo "FATAL: no torch/cuda"; exit 3; }

run_arm () {                       # $1=state $2=shared_lr $3=tag ; rest = extra flags
  local ST="$1" SHLR="$2" TAG="$3"; shift 3
  local OUT="$ROOT/$ST"; mkdir -p "$OUT"
  [ -s "$OUT/${TAG}_score.json" ] && { echo "=== SKIP $ST/$TAG (already scored) ==="; return 0; }
  local AV=$(df --output=avail -BG /home | tail -1 | tr -dc '0-9')
  [ "${AV:-0}" -lt 12 ] && { echo "FATAL: disk ${AV}G before $ST/$TAG"; return 9; }
  echo "=== [$(date -Is)] START $ST/$TAG (disk ${AV}G) ==="
  "$PY" scripts/train.py --task mtl --canon none --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed 0 --epochs 50 --only-fold 0 --batch-size 8192 \
    --model mtlnet_crossattn_dualtower --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region \
    --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
    --log-t-kd-weight 0.0 --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr "$SHLR" \
    --checkpoint-selector geom_simple --compile --tf32 \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints "$@" \
    > "$OUT/${TAG}_train.log" 2>&1 &
  local pid=$!; wait $pid; local rc=$?
  local RD=$(ls -d results/$OVL/$ST/mtlnet_*_${pid} 2>/dev/null | head -1)   # attribute by OWN pid
  echo "=== [$(date -Is)] DONE $ST/$TAG rc=$rc pid=$pid rundir=${RD:-NONE} ==="
  if [ $rc -ne 0 ] || [ -z "$RD" ]; then echo "FATAL: $ST/$TAG rc=$rc rundir=${RD:-NONE}"; return 1; fi
  "$PY" scripts/closing_data/a40_score_matched.py "$RD" --seed 0 --tag "${TAG}_${ST}_s0_f0" > "$OUT/${TAG}_score.txt" 2>&1
  cp "$RD/a40_matched_score.json" "$OUT/${TAG}_score.json" 2>/dev/null
  echo "--- $ST/$TAG ---"; cat "$OUT/${TAG}_score.json" 2>/dev/null
}

do_state () {
  local ST="$1" SHLR="$2"
  echo "##################### $ST (1 fold) #####################"
  run_arm "$ST" "$SHLR" baseline                                                        || return 1
  run_arm "$ST" "$SHLR" rg1 --model-param disable_cross_attn=True                       || return 1
  run_arm "$ST" "$SHLR" rg2 --model-param disable_cross_attn=True --category-weight 0.0  || return 1
  local h=$(md5sum "$ROOT/$ST"/{baseline,rg1,rg2}_score.json | awk '{print $1}' | sort -u | wc -l)
  echo "$ST distinct score hashes: $h of 3"
  [ "$h" -ne 3 ] && { echo "FATAL: $ST arms not distinct -- harvest fault"; return 5; }
  # n_folds MUST be 1 here; anything else means --only-fold did not take effect
  "$PY" - <<PYEOF
import json
for t in ("baseline","rg1","rg2"):
    j = json.load(open("$ROOT/$ST/%s_score.json" % t))
    print("  %-8s n_folds=%s cat=%s reg=%s" % (t, j["n_folds"], j["cat_macro_f1_mean"], j["reg_full_top10_mean"]))
    assert j["n_folds"] == 1, "EXPECTED 1 fold, got %s -- --only-fold did not take" % j["n_folds"]
PYEOF
  echo "$ST OK"
}

do_state istanbul   1e-3 || echo "SKIP-ON-FAIL istanbul"
do_state florida    3e-3 || echo "SKIP-ON-FAIL florida"
do_state california 1e-3 || echo "SKIP-ON-FAIL california"
do_state texas      1e-3 || echo "SKIP-ON-FAIL texas"
echo "ALL STATES ATTEMPTED"
