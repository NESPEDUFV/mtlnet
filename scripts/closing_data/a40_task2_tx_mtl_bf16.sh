#!/bin/bash
# A40 board lane — Task 2 CORRECTED PRECISION re-run: TX champion-G MTL under bf16.
#
# WHY: the original a40_task2_tx_reg.sh Cell B ran the MTL under the DEFAULT fp16-autocast harness
# (no GradScaler) -> it systematically UNDERSTATED MTL reg vs the always-fp32 STL reg ceiling, giving the
# artifact Δreg = -2.41 pp (commit 449cc9ce). The H100 lane proved the fix: bf16 autocast (MTL_AUTOCAST_BF16=1,
# fp32 exponent range -> no 65504 overflow) closes/reverses the understatement (FL -1.29 -> +0.56 BEATS ceiling;
# AL -> -0.18; CA §4 bf16 BEATS both ceilings). See docs/studies/closing_data/{CA_MTL_DIVERGENCE,FL_PRECISION_GATE}.md.
#
# SCOPE: re-run ONLY the MTL (Cell B). The STL reg ceiling is p1/TRUE-fp32 and CLEAN (64.96, no collapse) ->
# NOT re-run (docs/studies/closing_data/archive/lessons/CA_MTL_DIVERGENCE.md "reg ceiling stands"). Scores bf16 MTL vs that existing fp32 ceiling.
#
# This is the A40's device-class-clean B-A2 pair (A40 ceiling + A40 MTL); an intentional cross-GPU duplicate
# of the H100 TX bf16 cell (user-directed), strengthening confidence the same way FL Task 1 A/B did.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

# shared CUDA board env (HANDOFF_BOARD_A40 §3) + bf16 arm (board_h100_mtl.sh "bf16")
export MTL_CHUNK_VAL_METRIC=1                 # S2 chunked val metric (8.5x overlap scale)
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
# MTL_STRICT is deliberately OFF (was =1 in the first attempt, which ABORTED at fold1 ep36 b69 on a
# backward-pass NaN GRADIENT — finite loss=1.79, NOT an fp16 overflow). With strict OFF the non-finite
# guard does its designed job: SKIP that one batch (no NaN-poison of the shared backbone) and CONTINUE
# (docs/studies/closing_data/archive/lessons/CA_MTL_DIVERGENCE.md fix option 1). bf16 avoids the fp16-OVERFLOW collapse but not this rare grad-NaN.
# MTL_NAN_GUARD=1 logs grad-norm trajectory + every skip so we can judge skip frequency / result quality.
# The GATE guard's fail-loud (lost with MTL_STRICT off) is replaced by the inline provenance assert below.
export MTL_NAN_GUARD=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board
export MTL_AUTOCAST_BF16=1                     # bf16 train autocast (the fp16-overflow fix)
export MTL_DISABLE_AMP_EVAL=1                  # fp32 eval (bf16 arm convention)
# auto-fit: NEVER MTL_DATASET_GPU=1 for TX (forces ~31GB redundant copies -> OOM). Leave unset.
# TX host-RAM guard DOUBLE-COUNTS (PR #35 / docs/studies/closing_data/archive/lessons/EP100_ABLATION_AND_TX_RAM.md §2): it fires after ~25GB is already
# resident but compares the FULL ~66GB peak vs (avail - 16GB headroom), so it false-raises a run that fits.
# Verified fit on this 125GB box: other-user ~17GB + TX peak ~66GB = ~83GB << 125GB (avail ~105GB). Lower the
# headroom so the guard clears the false positive while still protecting the box (blocks if avail < ~56GB).
export MTL_RAM_HEADROOM_GB=-10

ST=texas; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"
mtl_log="$L/task2_tx_mtl_bf16_s${SD}.log"

# GATE safety (replaces the MTL_STRICT hard-fail): assert the overlap engine is correctly gated.
$PY - <<'PY'
import json
d = json.load(open("output/check2hgi_dk_ovl/texas/input/next_build_provenance.json"))
assert d.get("emit_tail") is False and d.get("min_sequence_length") == 10 and d.get("stride") == 1, \
    f"GATE ASSERT FAILED (stale/ungated overlap): {d}"
print("[gate-assert] TX overlap engine gated OK: min_seq=10 emit_tail=False stride=1")
PY
if [ $? -ne 0 ]; then echo "[$(date '+%F %T')] GATE ASSERT FAILED — abort"; exit 9; fi

echo "[$(date '+%F %T')] TX champion-G MTL (bf16) on $OVL, compiled+tf32, auto-fit (~11h)"
$PY scripts/train.py --task mtl --task-set check2hgi_next_region --engine "$OVL" \
    --state "$ST" --seed "$SD" --epochs "$EP" --folds "$F" --batch-size 2048 \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-head next_gru --reg-head next_stan_flow_dualtower \
    --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
    --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
    --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
    --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --model mtlnet_crossattn_dualtower \
    --checkpoint-selector geom_simple --no-reg-class-weights --no-cat-class-weights \
    --canon none \
    --compile --tf32 \
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$mtl_log" 2>&1 &
pid=$!; echo "$pid" > "$L/task2_tx_mtl_bf16_s${SD}.pid"
echo "[$(date '+%F %T')] launched python pid=$pid -> $mtl_log"
wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] MTL FAIL rc=$rc — tail:"; tail -40 "$mtl_log"; exit $rc; fi

rd=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "[$(date '+%F %T')] MTL DONE — rundir: ${rd:-<NOT FOUND; inspect $mtl_log>}"
echo "$rd" > "$L/task2_tx_mtl_bf16_s${SD}.rundir"
[ -z "$rd" ] && exit 3

# ---- matched score (FULL top10 fp32) + corrected Δreg vs the existing fp32 ceiling ----
$PY scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "tx_ovl_mtl_bf16_s${SD}"
$PY - "$rd" <<'PY'
import sys, json, glob
from pathlib import Path
rd = sys.argv[1]
sc = json.load(open(Path(rd) / "a40_matched_score.json"))
mtl_reg, mtl_cat = sc["reg_full_top10_mean"], sc["cat_macro_f1_mean"]
cj = sorted(glob.glob("docs/results/P1/region_head_texas_region_5f_50ep_tx_ovl_stl_reg_s0*.json"))
h = next(iter(json.load(open(cj[-1]))["heads"].values()))
stl = h["aggregate"]["top10_acc_mean"] * 100
dreg = mtl_reg - stl
verdict = ("INSIDE (|Δreg|<=1.5pp)" if abs(dreg) <= 1.5
           else "borderline (<=2pp)" if abs(dreg) <= 2.0
           else "FLAG reg-claim re-scope (>2pp) — NOT a stop")
out = {"state": "texas", "seed": 0, "folds": 5, "engine": "check2hgi_dk_ovl",
       "precision": "bf16 (MTL_AUTOCAST_BF16=1, eval fp32)", "windowing": "gated stride-1 overlap min_seq=10",
       "stl_reg_ceiling_top10": round(stl, 4), "mtl_reg_full_top10": round(mtl_reg, 4),
       "mtl_reg_per_fold": sc.get("reg_per_fold"), "mtl_reg_best_epochs": sc.get("reg_best_epochs"),
       "mtl_cat_macro_f1": round(mtl_cat, 4), "mtl_cat_per_fold": sc.get("cat_per_fold"),
       "delta_reg": round(dreg, 4), "delta_reg_margin": 2.0, "verdict": verdict,
       "prior_fp16_delta_reg": -2.4095, "note": "bf16 re-run of the fp16-understated -2.41 (449cc9ce). "
       "STL reg ceiling is p1/fp32, clean, reused (NOT re-run). Matched scorer FULL top10 fp32 both sides."}
op = "docs/results/closing_data/a40/tx_ba2_bf16_s0.json"
Path("docs/results/closing_data/a40").mkdir(parents=True, exist_ok=True)
json.dump(out, open(op, "w"), indent=2)
print("\n========== TX GATED-OVERLAP B-A2 (bf16, seed 0, 5f) ==========")
print(f"  STL reg ceiling (fp32, clean, reused) = {stl:.4f}")
print(f"  champion-G MTL reg FULL top10 (bf16)  = {mtl_reg:.4f}")
print(f"  champion-G MTL cat macro-F1 (bf16)    = {mtl_cat:.4f}")
print(f"  -> Δreg (bf16 MTL - fp32 ceiling)      = {dreg:+.4f} pp   (was -2.41 fp16; δ_reg=2pp)")
print(f"  -> verdict: {verdict}")
print(f"  -> {op}")
PY
echo "[$(date '+%F %T')] Task2 bf16 ALL DONE"
