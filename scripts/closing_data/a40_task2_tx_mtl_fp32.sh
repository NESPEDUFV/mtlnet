#!/bin/bash
# A40 board lane — Task 2 DEFINITIVE: TX champion-G MTL under TRUE fp32 (MTL_DISABLE_AMP=1).
#
# WHY fp32: the fp16 run (-2.41) and the bf16 run (-2.37) AGREE — TX reg peaks at ep4-5 then degrades
# in BOTH low-precision formats (identical best-epochs), so the gap looks real, not a precision artifact.
# bf16 also showed a pervasive late-training grad-NaN pathology (74,812 skips from ep33). fp32 (full 23-bit
# mantissa) is the definitive test: if it runs clean (0 skips) it gives a citable number and conclusively
# rules out precision; if it STILL NaNs/degrades, the instability is structural and -2.4 is real beyond doubt.
# Board-consistent: fp32 is the non-CA small/mid-state decision (AL_PRECISION_GATE.md).
#
# SCOPE: MTL only. STL reg ceiling 64.96 is p1/true-fp32, clean, reused (NOT re-run).
# Skip-guard ON (MTL_STRICT off) so the run COMPLETES regardless; MTL_NAN_GUARD=1 logs any skip
# (expect 0 in fp32). GATE safety via the inline provenance assert (MTL_STRICT hard-fail replaced).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

export MTL_CHUNK_VAL_METRIC=1                 # S2 chunked val metric (8.5x overlap scale)
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_NAN_GUARD=1                         # log grad-norm trajectory + any non-finite skip (expect 0 in fp32)
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board
export MTL_DISABLE_AMP=1                       # TRUE fp32 — disables BOTH train and eval autocast (no fp16/bf16)
# auto-fit: NEVER MTL_DATASET_GPU=1 for TX. TX host-RAM guard double-counts -> -10 headroom (verified fit).
export MTL_RAM_HEADROOM_GB=-10

ST=texas; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"
mtl_log="$L/task2_tx_mtl_fp32_s${SD}.log"

# GATE safety (replaces the MTL_STRICT hard-fail): assert the overlap engine is correctly gated.
$PY - <<'PY'
import json
d = json.load(open("output/check2hgi_dk_ovl/texas/input/next_build_provenance.json"))
assert d.get("emit_tail") is False and d.get("min_sequence_length") == 10 and d.get("stride") == 1, \
    f"GATE ASSERT FAILED (stale/ungated overlap): {d}"
print("[gate-assert] TX overlap engine gated OK: min_seq=10 emit_tail=False stride=1")
PY
if [ $? -ne 0 ]; then echo "[$(date '+%F %T')] GATE ASSERT FAILED — abort"; exit 9; fi

echo "[$(date '+%F %T')] TX champion-G MTL (TRUE fp32) on $OVL, compiled+tf32, auto-fit (~13-16h)"
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
pid=$!; echo "$pid" > "$L/task2_tx_mtl_fp32_s${SD}.pid"
echo "[$(date '+%F %T')] launched python pid=$pid -> $mtl_log"
wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] MTL FAIL rc=$rc — tail:"; tail -40 "$mtl_log"; exit $rc; fi

rd=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "[$(date '+%F %T')] MTL DONE — rundir: ${rd:-<NOT FOUND; inspect $mtl_log>}"
echo "$rd" > "$L/task2_tx_mtl_fp32_s${SD}.rundir"
[ -z "$rd" ] && exit 3

skips=$(tr '\r' '\n' < "$mtl_log" | grep -cE "Skipping optimizer\+scheduler step" || true)
echo "[$(date '+%F %T')] non-finite skip count = ${skips:-0} (0 = clean fp32)"

$PY scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "tx_ovl_mtl_fp32_s${SD}"
$PY - "$rd" "${skips:-0}" <<'PY'
import sys, json, glob
from pathlib import Path
rd, skips = sys.argv[1], int(sys.argv[2])
sc = json.load(open(Path(rd) / "a40_matched_score.json"))
mtl_reg, mtl_cat = sc["reg_full_top10_mean"], sc["cat_macro_f1_mean"]
cj = sorted(glob.glob("docs/results/P1/region_head_texas_region_5f_50ep_tx_ovl_stl_reg_s0*.json"))
h = next(iter(json.load(open(cj[-1]))["heads"].values()))
stl = h["aggregate"]["top10_acc_mean"] * 100
dreg = mtl_reg - stl
# sign-aware: a POSITIVE Δreg is MTL beating the ceiling (superiority), NOT a deficit to re-scope.
verdict = (f"MTL BEATS reg ceiling +{dreg:.2f}pp (superiority)" if dreg >= 0
           else "INSIDE (|Δreg|<=1.5pp)" if abs(dreg) <= 1.5
           else "borderline (<=2pp)" if abs(dreg) <= 2.0
           else "FLAG reg-claim re-scope (Δreg<-2pp) — NOT a stop")
out = {"state": "texas", "seed": 0, "folds": 5, "engine": "check2hgi_dk_ovl",
       "precision": "TRUE fp32 (MTL_DISABLE_AMP=1)", "windowing": "gated stride-1 overlap min_seq=10",
       "nonfinite_skip_count": skips, "stl_reg_ceiling_top10": round(stl, 4),
       "mtl_reg_full_top10": round(mtl_reg, 4), "mtl_reg_per_fold": sc.get("reg_per_fold"),
       "mtl_reg_best_epochs": sc.get("reg_best_epochs"), "mtl_cat_macro_f1": round(mtl_cat, 4),
       "mtl_cat_per_fold": sc.get("cat_per_fold"), "mtl_cat_best_epochs": sc.get("cat_best_epochs"),
       "delta_reg": round(dreg, 4), "delta_reg_margin": 2.0, "verdict": verdict,
       "prior_fp16_delta_reg": -2.4095, "prior_bf16_delta_reg": -2.3705,
       "note": "Definitive true-fp32 TX MTL. STL reg ceiling p1/fp32, reused. Matched scorer FULL top10 fp32 both sides."}
op = "docs/results/closing_data/a40/tx_ba2_fp32_s0.json"
Path("docs/results/closing_data/a40").mkdir(parents=True, exist_ok=True)
json.dump(out, open(op, "w"), indent=2)
print("\n========== TX GATED-OVERLAP B-A2 (TRUE fp32, seed 0, 5f) ==========")
print(f"  non-finite skips = {skips}  (0 = clean)")
print(f"  STL reg ceiling (fp32, clean, reused) = {stl:.4f}")
print(f"  champion-G MTL reg FULL top10 (fp32)  = {mtl_reg:.4f}")
print(f"  champion-G MTL cat macro-F1 (fp32)    = {mtl_cat:.4f}")
print(f"  -> Δreg (fp32 MTL - fp32 ceiling)      = {dreg:+.4f} pp   (fp16 -2.41 / bf16 -2.37; δ_reg=2pp)")
print(f"  -> verdict: {verdict}")
print(f"  -> {op}")
PY
echo "[$(date '+%F %T')] Task2 fp32 ALL DONE"
