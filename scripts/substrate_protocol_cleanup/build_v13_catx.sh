#!/bin/bash
# v13 substrate build chain for CA + TX (check2hgi_resln_design_b).
# Mirrors the FL EXTENSION chain. Detached, disk-guarded, --no-checkpoints.
# Usage: setsid bash scripts/substrate_protocol_cleanup/build_v13_catx.sh > /tmp/v13_catx/run.log 2>&1 &
set -uo pipefail
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
LOGDIR=/tmp/v13_catx
mkdir -p "$LOGDIR"

disk_guard() {
  local free
  free=$(df -m /home | tail -1 | awk '{print $4}')
  echo "[disk] ${free} MB free before $1"
  if [ "$free" -lt 4000 ]; then
    echo "[FATAL] disk < 4000 MB before $1 — STOP"
    echo "DISKFAIL:$1" > "$LOGDIR/FATAL.DONE"
    exit 9
  fi
}

# state_lc state_cap shapefile
build_state() {
  local SL="$1" SC="$2" SHP="$3"
  echo "===================================================================="
  echo "=== BUILD v13 for $SC ($SL) — $(date -u) ==="
  echo "===================================================================="

  # ---- Stage 1: check2hgi temp graph (checkin_graph.pt + boroughs_area.csv + view2) ----
  disk_guard "${SL}_stage1_c2hgi_preprocess"
  echo "[$SL] Stage 1: check2hgi preprocess (graph + view2)"
  PYTHONPATH=src:research $PY -c "
import sys
from embeddings.check2hgi.preprocess import preprocess_check2hgi, build_view2_graph_file
preprocess_check2hgi(city='$SC', city_shapefile='$SHP', build_view2=True)
print('[stage1] checkin_graph + view2 done for $SC')
" 2>&1
  if [ ! -f "output/check2hgi/$SL/temp/checkin_graph.pt" ]; then
    echo "[FATAL] $SL checkin_graph.pt missing after stage1"; echo "S1FAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi

  # ---- Stage 1b: canonical sequences_next.parquet (from canonical embeddings) ----
  disk_guard "${SL}_stage1b_sequences_next"
  echo "[$SL] Stage 1b: canonical sequences_next.parquet (+ next.parquet, discarded)"
  $PY -c "
import sys; sys.path.insert(0,'src')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('$SL', EmbeddingEngine.CHECK2HGI)
print('[stage1b] canonical sequences_next done for $SL')
" 2>&1
  if [ ! -f "output/check2hgi/$SL/temp/sequences_next.parquet" ]; then
    echo "[FATAL] $SL sequences_next.parquet missing after stage1b"; echo "S1bFAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi

  # ---- Stage 2: HGI preprocess (edges.csv etc — POI2Vec prereq) ----
  disk_guard "${SL}_stage2_hgi_preprocess"
  echo "[$SL] Stage 2: HGI preprocess"
  PYTHONPATH=src:research $PY research/embeddings/hgi/preprocess.py --city "$SC" --shapefile "$SHP" 2>&1
  if [ ! -f "output/hgi/$SL/temp/edges.csv" ]; then
    echo "[FATAL] $SL hgi edges.csv missing after stage2"; echo "S2FAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi

  # ---- Stage 3: POI2Vec teacher ----
  disk_guard "${SL}_stage3_poi2vec"
  echo "[$SL] Stage 3: POI2Vec teacher (GPU)"
  $PY scripts/substrate_protocol_cleanup/run_poi2vec.py --city "$SC" --epochs 100 --device cuda 2>&1
  if [ ! -f "output/hgi/$SL/poi2vec_poi_embeddings_${SC}.csv" ]; then
    echo "[FATAL] $SL poi2vec csv missing after stage3"; echo "S3FAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi

  # ---- Stage 4: v13 substrate build (ResLN + Design B) ----
  disk_guard "${SL}_stage4_design_build"
  echo "[$SL] Stage 4: v13 substrate build (GPU)"
  $PY scripts/probe/build_design_b_poi_pool.py --state "$SL" --encoder resln \
      --out-engine check2hgi_resln_design_b --epochs 500 --device cuda 2>&1
  for f in embeddings poi_embeddings region_embeddings; do
    if [ ! -f "output/check2hgi_resln_design_b/$SL/${f}.parquet" ]; then
      echo "[FATAL] $SL ${f}.parquet missing after stage4"; echo "S4FAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
    fi
  done

  # ---- Stage 5: canonical seed42 log_T + postbuild inputs ----
  disk_guard "${SL}_stage5_logT_postbuild"
  echo "[$SL] Stage 5: canonical seed42 log_T (per-fold)"
  $PY scripts/compute_region_transition.py --state "$SL" --per-fold --seed 42 2>&1
  if [ ! -f "output/check2hgi/$SL/region_transition_log_seed42_fold1.pt" ]; then
    echo "[FATAL] $SL canonical log_T missing after stage5"; echo "S5LOGTFAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi
  echo "[$SL] Stage 5: postbuild (next.parquet + next_region.parquet + cp log_T)"
  bash scripts/substrate_protocol_cleanup/postbuild_design_substrate.sh check2hgi_resln_design_b "$SL" 2>&1
  if [ ! -f "output/check2hgi_resln_design_b/$SL/input/next_region.parquet" ]; then
    echo "[FATAL] $SL next_region.parquet missing after postbuild"; echo "S5FAIL:$SL" > "$LOGDIR/FATAL.DONE"; exit 1
  fi

  echo "[$SL] === v13 BUILD COMPLETE $(date -u) ==="
  echo "DONE:$SL" >> "$LOGDIR/STATES.DONE"
}

build_state california California "data/miscellaneous/tl_2022_06_tract_CA/tl_2022_06_tract.shp"
build_state texas Texas "data/miscellaneous/tl_2022_48_tract_TX/tl_2022_48_tract.shp"

echo "ALLDONE $(date -u)" > "$LOGDIR/ALL.DONE"
echo "=== ALL STATES DONE ==="
