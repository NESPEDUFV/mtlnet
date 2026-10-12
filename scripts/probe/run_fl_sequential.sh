#!/usr/bin/env bash
# Sequential FL builds on MPS for B, I, J, M.
set -e
PY=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
LOGDIR=logs/design_fl_eval
mkdir -p $LOGDIR

run() {
  local d=$1
  local script=$2
  local log=$LOGDIR/build_${d}_florida.log
  echo "[$(date +%H:%M:%S)] starting $d FL on MPS → $log"
  $PY scripts/probe/$script --state florida --epochs 500 --device mps > $log 2>&1
  echo "[$(date +%H:%M:%S)] finished $d"
}

run b build_design_b_poi_pool.py
run i build_design_i_lora.py
run j build_design_j_anchor.py
run m build_design_m_distill.py

echo "[$(date +%H:%M:%S)] all 4 FL engines built"
