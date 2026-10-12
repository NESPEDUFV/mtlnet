#!/bin/bash
# Blocker 2 (Tbl 2) — HGI category-STL ceiling under the OVERLAP windowing, ONE state.
# Mirrors h100_state_cells.sh Cell 1 EXACTLY (the Check2HGI cat ceiling recipe), swapping only
# the substrate: --engine check2hgi_dk_ovl -> hgi_dk_ovl. Same next_gru / 5f / 50ep / seed 0 /
# bs2048 / max-lr 3e-3 / grad-accum 1 / --compile --tf32 --no-checkpoints. Same-device A40.
#
# Usage: run_hgi_ovl_cat_cell.sh <state> [seed] [--build] [--cleanup]
#   --build    : build output/hgi_dk_ovl/<state>/input/next.parquet first (big states)
#   --cleanup  : rm the (large) next.parquet after scoring (disk reclaim; score JSON is kept)
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet; cd "$REPO"
export PYTHONPATH=src
export DISABLE_AMP=1 MTL_DISABLE_AMP=1            # board fp32 gate (cat is robust; keep protocol)
export MTL_STRICT=1 MTL_COMPILE_DYNAMIC=1
export PYTORCH_CUDA_ALLOC_CONF="expandable_segments:True"
export TORCHINDUCTOR_CACHE_DIR=$HOME/.inductor_cache_board
export OMP_NUM_THREADS=8
PY=.venv/bin/python

ST="${1:?usage: run_hgi_ovl_cat_cell.sh <state> [seed] [--build] [--cleanup]}"; shift || true
SD=0; DO_BUILD=0; DO_CLEANUP=0
for a in "$@"; do
  case "$a" in
    --build) DO_BUILD=1 ;;
    --cleanup) DO_CLEANUP=1 ;;
    [0-9]*) SD="$a" ;;
  esac
done
EP=50; F=5; OVL=hgi_dk_ovl
L=/tmp/hgi_ovl_cat/$ST; mkdir -p "$L"
say(){ echo "[$(date '+%F %T')] [$ST] $*"; }

if [ "$DO_BUILD" = "1" ]; then
  say "build $OVL inputs"
  $PY scripts/closing_data/build_hgi_overlap_inputs.py "$ST" > "$L/build.log" 2>&1
  rc=$?; [ $rc -ne 0 ] && { say "BUILD FAIL rc=$rc"; tail -20 "$L/build.log"; exit $rc; }
  say "build done -> $(grep DONE "$L/build.log" | tail -1)"
fi

say "Cell1 STL cat (next_gru) on $OVL, compiled+tf32, fp32, seed $SD"
$PY -u scripts/train.py --task next --state "$ST" --engine "$OVL" \
    --model next_gru --folds "$F" --epochs "$EP" --seed "$SD" \
    --batch-size 2048 --max-lr 3e-3 --gradient-accumulation-steps 1 \
    --compile --tf32 --no-checkpoints > "$L/stl_cat.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "Cell1 FAIL rc=$rc"; tail -30 "$L/stl_cat.log"; exit $rc; }
RD=$(ls -dt results/$OVL/$ST/next_*ep${EP}_* 2>/dev/null | head -1)
say "Cell1 done -> $RD"

say "score"
$PY scripts/closing_data/score_stl_cat_ceiling.py "$RD" --tag "${ST}_hgi_ovl_cat" > "$L/score.log" 2>&1
rc=$?; [ $rc -ne 0 ] && { say "SCORE FAIL rc=$rc"; tail -20 "$L/score.log"; exit $rc; }
grep -E "cat macro" "$L/score.log"

# pair with the board Check2HGI cat ceiling -> Tbl-2 sidecar JSON
$PY - "$ST" "$SD" "$RD" <<'PY'
import sys, json
from pathlib import Path
st, sd, rd = sys.argv[1], int(sys.argv[2]), sys.argv[3]
# board Check2HGI cat-STL ceiling under overlap (RESULTS_BOARD §1, the published comparand)
C2H = {"alabama":55.87,"arizona":57.13,"florida":75.15,"california":70.26,"texas":69.95,"istanbul":53.20}
sc = json.load(open(Path(rd)/"stl_cat_ceiling_score.json"))
hgi = sc["cat_macro_f1_mean"]
c2h = C2H.get(st.lower())
out = {
  "state": st, "seed": sd, "windowing": "gated stride-1 overlap (MIN_SEQ=10)",
  "recipe": "next_gru, 5f, 50ep, bs2048, max-lr 3e-3, grad-accum 1, compile+tf32, fp32 (DISABLE_AMP)",
  "device": "A40", "scorer": "score_stl_cat_ceiling.py (macro-F1 @ f1-best epoch, fold-mean)",
  "hgi_cat_macro_f1": hgi, "hgi_cat_std": sc["cat_macro_f1_std"],
  "hgi_cat_per_fold": sc["cat_per_fold"], "hgi_cat_best_epochs": sc["cat_best_epochs"],
  "check2hgi_cat_macro_f1_board": c2h,
  "substrate_margin_check2hgi_minus_hgi": (round(c2h - hgi, 4) if c2h is not None else None),
  "rundir": rd,
}
dst = Path("docs/results/closing_data/baseline_compare")/f"{st.lower()}_hgi_ovl_cat.json"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(out, indent=2))
mg = out["substrate_margin_check2hgi_minus_hgi"]
print(f"[tbl2] {st}: HGI {hgi:.2f}  vs  Check2HGI(board) {c2h}  -> margin +{mg} pp  ({dst})")
PY

if [ "$DO_CLEANUP" = "1" ]; then
  sz=$(du -h output/$OVL/$ST/input/next.parquet 2>/dev/null | cut -f1)
  rm -f output/$OVL/$ST/input/next.parquet
  say "cleanup: removed next.parquet ($sz reclaimed; score JSON kept)"
fi
say "CELL COMPLETE"
