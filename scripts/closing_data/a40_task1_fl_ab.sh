#!/bin/bash
# A40 board lane — Task 1: FL champion-G MTL A/B half (HANDOFF_BOARD_A40.md §3c).
# Byte-identical recipe the A100 runs on its half; PASS = |Δ| ≤ ±0.05pp on cat
# macro-F1 + reg top10_acc (4dp). Gated-overlap engine, seed 0, 5 folds, compiled+tf32.
# PID-suffix rundir capture (C28; never ls -dt|head).
#
# GUARD NOTE (gap found 2026-06-21): the handoff §2 mandates MTL_STRICT=1 for the GATE
# guard (folds._warn_if_ungated_overlap), but train.py auto-injects --canon v16 whose
# wrong-substrate guard then HARD-FAILS because the deliberate overlap engine
# check2hgi_dk_ovl != v16's pinned v14 substrate. Resolution: pass --canon none (disables
# the canon guards) and pin the FULL champion-G recipe via explicit flags instead — incl.
# --checkpoint-selector geom_simple + --no-{reg,cat}-class-weights (the class-weight flags
# default to None, NOT False, so they MUST be explicit to match v16 / avoid the C25 confound).
# Effective config == auto-v16 + engine override → byte-identical to the A100 half. The GATE
# guard stays active under MTL_STRICT=1 (it is canon-independent).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

# --- shared CUDA board env (HANDOFF_BOARD_A40.md §3) ---
export MTL_CHUNK_VAL_METRIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export MTL_STRICT=1                       # hard-fail on stale ungated/min_seq!=10 overlap build
export MTL_COMPILE_DYNAMIC=1
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board

ST=florida; SD=0; EP=50; F=5
V14=check2hgi_design_k_resln_mae_l0_1; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"
log="$L/task1_fl_ab_s${SD}.log"

echo "[$(date '+%F %T')] A40 Task1 START FL champion-G MTL A/B half seed=$SD ($EP ep, $F folds, compiled+tf32)"
echo "[$(date '+%F %T')] torch=$($PY -c 'import torch;print(torch.__version__)')"

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
    --per-fold-transition-dir "output/$V14/$ST" --no-checkpoints > "$log" 2>&1 &
pid=$!; wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] FAIL rc=$rc — tail:"; tail -30 "$log"; exit $rc; fi

rd=$(ls -d results/$OVL/$ST/mtlnet_*ep${EP}_*_${pid} 2>/dev/null | head -1)
echo "[$(date '+%F %T')] A40 Task1 DONE FL seed=$SD -> ${rd:-<rundir-by-PID not found; inspect $log>}"
echo "$rd" > "$L/task1_fl_ab_s${SD}.rundir"

# per-task DIAGNOSTIC-BEST aggregate (fold_info.json; quick read — matched 4dp rescore done separately)
$PY - "$rd" <<'PY'
import sys, json, glob, os, numpy as np
rd=sys.argv[1]
cat=[]; reg=[]
for fi in sorted(glob.glob(os.path.join(rd, "**/fold*_info.json"), recursive=True)):
    d=json.load(open(fi)); db=d.get("diagnostic_best_epochs", d)
    try: cat.append(db["next_category"]["metrics"]["f1"]*100)
    except Exception: pass
    try: reg.append(db["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]*100)
    except Exception: pass
def ms(x): return (np.mean(x), np.std(x), len(x)) if x else (float('nan'),float('nan'),0)
cm,cs,cn=ms(cat); rm,rs,rn=ms(reg)
print(f"  [diag-best quick read] cat macro-F1 = {cm:.4f} ± {cs:.4f} (n={cn})")
print(f"  [diag-best quick read] reg top10_indist = {rm:.4f} ± {rs:.4f} (n={rn})")
PY
echo "[$(date '+%F %T')] A40 Task1 aggregate printed; NEXT: r0_matched_rescore for FULL top10_acc 4dp"
