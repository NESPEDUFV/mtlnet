#!/bin/bash
# A40 board lane — TX STL CAT ceiling (next_gru) on the gated-overlap engine.
# Fills the "cat macro-F1 ceiling: TBD (A40 lane)" in TX_CELL.md — BOTH lanes' TX cells need it for Δcat.
# Verbatim Cell-1 recipe from h100_state_cells.sh (the one that produced FL 75.147 / CA 70.2573):
#   scripts/train.py --task next --model next_gru on $OVL, compiled+tf32, default precision.
# Cat is next_category (7 classes) -> NO fp16-overflow risk, and cat is precision-insensitive
# (AL 63.44->63.48) -> default precision, cross-state-consistent with the other states' cat ceilings.
# Scored by score_stl_cat_ceiling.py (macro-F1 / fold*_next_val.csv f1 col, f1-best epoch, fold-mean).
#
# GPU-SERIAL: launched ONLY after the TX MTL frees the card (handoff §1; also avoids the CA/TX
# big-dataset host-RAM co-residency hazard, BOARD_H100_FINDINGS §5).
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"; export PYTHONPATH=src
PY=.venv/bin/python

export MTL_STRICT=1                 # GATE guard (canon-independent) hard-fails a stale ungated/min_seq!=10 overlap build
export MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export OMP_NUM_THREADS=24
export TORCHINDUCTOR_CACHE_DIR=/home/vitor.oliveira/.inductor_cache_board
export MTL_RAM_HEADROOM_GB=-10      # same double-count override; safe (runs alone, MTL has freed ~66GB)

ST=texas; SD=0; EP=50; F=5; OVL=check2hgi_dk_ovl
L=/tmp/a40_board; mkdir -p "$L"
log="$L/tx_cat_ceiling_s${SD}.log"

echo "[$(date '+%F %T')] TX STL cat ceiling (next_gru) on $OVL, compiled+tf32"
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 \
    --compile --tf32 --no-checkpoints > "$log" 2>&1 &
pid=$!; echo "$pid" > "$L/tx_cat_ceiling_s${SD}.pid"
echo "[$(date '+%F %T')] launched python pid=$pid -> $log"
wait "$pid"; rc=$?
if [ $rc -ne 0 ]; then echo "[$(date '+%F %T')] cat ceiling FAIL rc=$rc — tail:"; tail -40 "$log"; exit $rc; fi

rd=$(ls -d results/$OVL/$ST/next_*ep${EP}_*_${pid} 2>/dev/null | head -1)
[ -z "$rd" ] && rd=$(ls -dt results/$OVL/$ST/next_*ep${EP}_* 2>/dev/null | head -1)
echo "[$(date '+%F %T')] cat ceiling DONE — rundir: ${rd:-<NOT FOUND>}"
[ -z "$rd" ] && exit 3
echo "$rd" > "$L/tx_cat_ceiling_s${SD}.rundir"

$PY scripts/closing_data/score_stl_cat_ceiling.py "$rd" --tag "tx_ovl_stl_cat_s${SD}"
$PY - "$rd" <<'PY'
import sys, json
from pathlib import Path
rd = Path(sys.argv[1])
sc = json.load(open(rd / "stl_cat_ceiling_score.json"))
out = {"state": "texas", "seed": 0, "folds": 5, "engine": "check2hgi_dk_ovl",
       "windowing": "gated stride-1 overlap min_seq=10", "head": "next_gru (STL)",
       "cat_macro_f1_ceiling": sc["cat_macro_f1_mean"], "cat_macro_f1_std": sc["cat_macro_f1_std"],
       "cat_per_fold": sc["cat_per_fold"], "cat_best_epochs": sc["cat_best_epochs"], "rundir": str(rd)}
op = "docs/results/closing_data/a40/tx_stl_cat_ceiling_s0.json"
Path("docs/results/closing_data/a40").mkdir(parents=True, exist_ok=True)
json.dump(out, open(op, "w"), indent=2)
print(f"\n  TX STL cat ceiling (macro-F1) = {sc['cat_macro_f1_mean']} ± {sc['cat_macro_f1_std']}  -> {op}")
PY
echo "[$(date '+%F %T')] TX cat ceiling ALL DONE"
