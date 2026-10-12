#!/usr/bin/env bash
# Istanbul check2hgi substrate — CPU prep steps (1-3): parse → graph → inputs.
# Step 4 (GCN substrate) is GPU and runs separately after the card frees.
# Per the map-istanbul-build recipe (wf_6220f213). Runs concurrent with a GPU job.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
source /home/vitor.oliveira/.venv/bin/activate
export PYTHONPATH=src
OUT=docs/studies/closing_data/istanbul_build
mkdir -p "$OUT"
LOG="$OUT/cpu_prep.log"
ts() { date -u +%H:%M:%S; }

echo "[$(ts)] === Step 1: parse_city (regenerate corrected corpus) ===" | tee "$LOG"
python scripts/second_dataset/parse_city.py --city istanbul >> "$LOG" 2>&1
rc1=$?; echo "[$(ts)] step1 rc=$rc1" | tee -a "$LOG"
[ $rc1 -ne 0 ] && { echo "STEP 1 FAILED — abort" | tee -a "$LOG"; exit 1; }

echo "[$(ts)] === Step 2: build_graph (mahalle graph; expect 29945 POIs / 520 regions) ===" | tee -a "$LOG"
python scripts/second_dataset/build_graph.py --city istanbul >> "$LOG" 2>&1
rc2=$?; echo "[$(ts)] step2 rc=$rc2" | tee -a "$LOG"
[ $rc2 -ne 0 ] && { echo "STEP 2 FAILED — abort" | tee -a "$LOG"; exit 1; }
# verify the graph cardinality
python - <<'PY' 2>&1 | tee -a "$LOG"
import pickle, sys
sys.path.insert(0, "src")
from configs.paths import IoPaths
gf = IoPaths.CHECK2HGI.get_graph_data_file("istanbul")
g = pickle.load(open(gf, "rb"))
print(f"[verify] graph POIs={g['num_pois']} regions={g['num_regions']} checkins={g['num_checkins']}")
ok = g["num_pois"] == 29945 and g["num_regions"] == 520
print("[verify] cardinality", "OK (29945/520)" if ok else "MISMATCH — phase_v_substrate guard will fail")
PY

echo "[$(ts)] === Step 3: build_inputs (sequences, labels, folds, priors) ===" | tee -a "$LOG"
python scripts/second_dataset/build_inputs.py --city istanbul >> "$LOG" 2>&1
rc3=$?; echo "[$(ts)] step3 rc=$rc3" | tee -a "$LOG"
[ $rc3 -ne 0 ] && { echo "STEP 3 FAILED — abort" | tee -a "$LOG"; exit 1; }

echo "[$(ts)] === ISTANBUL CPU PREP DONE (steps 1-3) — GPU step 4 (phase_v_substrate) next ===" | tee -a "$LOG"
ls -la output/check2hgi/istanbul/temp/ output/check2hgi/istanbul/input/ 2>/dev/null | tee -a "$LOG"
