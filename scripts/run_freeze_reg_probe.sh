#!/usr/bin/env bash
# W6 — category-side encoder-isolation probe (the MIRROR of F49's frozen-cat).
#
# Closes REVIEW_PANEL W6 / R3 (structural-bottleneck): the paper claims the
# joint CATEGORY win is "a stronger shared encoder, NOT region->category
# transfer." This probe tests it directly. It freezes the REGION stream
# (next_encoder + next_poi, requires_grad=False) and zeroes the reg loss
# (--category-weight 1.0), then trains champion-G. If cat macro-F1 STILL beats
# the STL cat ceiling with the region stream frozen-at-init (so it provides no
# learned region signal and cannot co-adapt as a cat-helper via cross-attn
# K/V), the cat win is the shared TRUNK (architecture/capacity), not transfer.
#
#   probe-cat ~ full-MTL-cat  >> STL-cat-ceiling  => trunk, not transfer  (W6 closed)
#   probe-cat ~ STL-cat-ceiling                   => the win WAS region->cat transfer
#
# Recipe = champion-G (the RESULTS_BOARD §1 invocation) on check2hgi_dk_ovl,
# seed 0 x 5f, true fp32, MINUS the cascade pins, PLUS:
#   --category-weight 1.0  (reg loss off)  +  --freeze-reg-stream
# Comparand = the STL cat ceiling already on disk
#   (docs/results/closing_data/h100/<state>_s0_stl_cat_ceiling.json) — the cat
#   ceiling is precision/device-robust (7 classes), so the A40 is fine.
#
# Usage:
#   STATES="alabama arizona florida" bash scripts/run_freeze_reg_probe.sh
#   # smoke (1 fold x 2 ep, AL only):  MODE=smoke bash scripts/run_freeze_reg_probe.sh
#
set -euo pipefail
export PYTHONPATH="${PYTHONPATH:-src}"
PY="${PY:-python}"                       # conda/CUDA: BASELINE_PY or the active interpreter
export DISABLE_AMP=1 MTL_DISABLE_AMP=1   # PR #43 fp16 gate — fp32, no autocast (board protocol)
export MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

STATES="${STATES:-alabama arizona florida}"   # >=3 states incl one large (FL) per the gap audit
SEED="${SEED:-0}"
FOLDS="${FOLDS:-5}"; EPOCHS="${EPOCHS:-50}"
if [[ "${MODE:-}" == "smoke" ]]; then STATES="alabama"; FOLDS=1; EPOCHS=2; fi

run_one() {
  local state="$1"
  echo "=== W6 reg-freeze probe — ${state} (seed ${SEED}, ${FOLDS}f, fp32, region stream frozen + reg-weight 0) ==="
  # per-fold seeded log_T is unused (reg loss off + alpha frozen) but the engine
  # is happy with the v14 dir; build the dk_ovl base + log_T first if absent
  # (same as the board: build_overlap_probe_engine.py ${state} 1 ; compute_region_transition ... --per-fold).
  "${PY}" scripts/train.py --task mtl --task-set check2hgi_next_region --engine check2hgi_dk_ovl \
      --state "${state}" --seed "${SEED}" --epochs "${EPOCHS}" --folds "${FOLDS}" --batch-size 2048 \
      --mtl-loss static_weight --category-weight 1.0 \
      --freeze-reg-stream \
      --cat-head next_gru --reg-head next_stan_flow_dualtower \
      --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
      --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
      --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
      --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
      --model mtlnet_crossattn_dualtower --compile --tf32 \
      --checkpoint-selector geom_simple --no-reg-class-weights --no-cat-class-weights \
      --canon none \
      --per-fold-transition-dir "output/check2hgi_dk_ovl/${state}" --no-checkpoints
  # Score cat macro-F1 (the only head that matters here) and compare to the STL cat ceiling.
  echo "  -> score cat macro-F1 from the rundir; compare to ${state}_s0_stl_cat_ceiling.json"
}

for s in ${STATES}; do run_one "${s}"; done
echo "DONE — W6 probe. Read: does probe cat F1 still beat the STL cat ceiling with the region stream frozen?"
echo "  YES (probe ~ full-MTL cat >> ceiling) => stronger-shared-encoder, NOT transfer (W6 closed)."
echo "  NO  (probe ~ ceiling)                 => the cat win was region->category transfer."
