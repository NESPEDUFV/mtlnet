#!/bin/bash
# A40 board lane — Task 2: matched B-A2 reg pair on TX gated-overlap (HANDOFF_BOARD_A40.md §3d).
# Two GPU cells, STRICTLY SEQUENTIAL on the single A40:
#   Cell A: STL next_stan_flow reg ceiling on overlap windowing (p1, compiled+tf32, --engine-override OVL)
#   Cell B: champion-G v16 MTL on overlap (state=texas; same recipe as Task 1, --canon none + explicit pins)
# Then Δreg = (MTL reg FULL top10) − (STL reg ceiling FULL top10), reported vs δ_reg = 2 pp.
# Launch ONLY after Task 1 has freed the GPU.
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

# shared CUDA board env (§3)
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board
# auto-fit: never MTL_DATASET_GPU=1 for TX (forces ~31GB redundant copies -> OOM). Leave unset.

ST=texas; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"

# ---------------- Cell A: STL reg ceiling (next_stan_flow, region, alpha0) on OVERLAP -------------
stl_log="$L/task2_tx_stl_reg_s${SD}.log"
echo "[$(date '+%F %T')] Task2 Cell A — TX STL reg ceiling (next_stan_flow a0) on $OVL, compiled+tf32"
$PY -u scripts/p1_region_head_ablation.py --state "$ST" --heads next_stan_flow \
    --input-type region --region-emb-source "$V14" \
    --override-hparams freeze_alpha=True alpha_init=0.0 \
    --engine-override "$OVL" \
    --per-fold-transition-dir "output/$V14/$ST" \
    --folds "$F" --epochs "$EP" --seed "$SD" --target region \
    --compile --tf32 \
    --tag "tx_ovl_stl_reg_s${SD}" > "$stl_log" 2>&1
rc=$?; if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] Cell A FAIL rc=$rc — tail:"; tail -25 "$stl_log"; exit $rc; fi
STL_CEIL=$(grep -aoE "AGGREGATE:.*Acc@10=[0-9.]+" "$stl_log" | grep -aoE "Acc@10=[0-9.]+" | head -1 | cut -d= -f2)
echo "[$(date '+%F %T')] Cell A DONE — STL reg ceiling Acc@10(full) = ${STL_CEIL:-PARSE_FAIL} (frac); JSON in docs/results/P1/"

# ---------------- Cell B: champion-G v16 MTL on OVERLAP (TX) --------------------------------------
mtl_log="$L/task2_tx_mtl_s${SD}.log"
echo "[$(date '+%F %T')] Task2 Cell B — TX champion-G MTL on $OVL, compiled+tf32 (~11h, auto-fit)"
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
pid=$!; wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] Cell B FAIL rc=$rc — tail:"; tail -30 "$mtl_log"; exit $rc; fi
rd=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "[$(date '+%F %T')] Cell B DONE — TX MTL rundir: ${rd:-<not found; inspect $mtl_log>}"
echo "$rd" > "$L/task2_tx_mtl_s${SD}.rundir"

# ---------------- Δreg ---------------------------------------------------------------------------
echo "[$(date '+%F %T')] Task2 — matched score + Δreg"
$PY scripts/closing_data/a40_score_matched.py "$rd" --seed "$SD" --tag "tx_ovl_mtl_s${SD}"
$PY - "$rd" "${STL_CEIL:-nan}" <<'PY'
import sys, json
from pathlib import Path
rd, stl = sys.argv[1], sys.argv[2]
sc = json.load(open(Path(rd) / "a40_matched_score.json"))
mtl_reg = sc["reg_full_top10_mean"]            # already in %
stl_ceil = float(stl) * 100 if stl not in ("nan", "") else float("nan")
dreg = mtl_reg - stl_ceil
print("\n================= TX GATED-OVERLAP B-A2 (seed 0, 5f) =================")
print(f"  STL reg ceiling (next_stan_flow a0) Acc@10 = {stl_ceil:.4f}")
print(f"  champion-G MTL  reg FULL top10_acc         = {mtl_reg:.4f}")
print(f"  champion-G MTL  cat macro-F1               = {sc['cat_macro_f1_mean']:.4f}")
print(f"  -> Δreg (MTL − STL ceiling)                = {dreg:+.4f} pp   (δ_reg = 2 pp)")
verdict = "INSIDE (|Δreg|<=~1.5pp)" if abs(dreg) <= 1.5 else ("borderline (<=2pp)" if abs(dreg) <= 2.0 else "FLAG reg-claim re-scope (>2pp) — NOT a stop")
print(f"  -> verdict: {verdict}")
PY
echo "[$(date '+%F %T')] Task2 ALL DONE"
