#!/usr/bin/env bash
# After B FL finishes, run I+J in parallel on MPS, then M alone.
PY=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
LOG=logs/design_fl_eval

# Wait for B to finish
while pgrep -f build_design_b_poi_pool >/dev/null; do sleep 30; done
echo "[$(date +%H:%M:%S)] B done, starting I+J in parallel on MPS" >> $LOG/sequential_runner.log

# Launch I and J in parallel on MPS
$PY scripts/probe/build_design_i_lora.py --state florida --epochs 500 --device mps > $LOG/build_i_florida.log 2>&1 &
PID_I=$!
$PY scripts/probe/build_design_j_anchor.py --state florida --epochs 500 --device mps > $LOG/build_j_florida.log 2>&1 &
PID_J=$!

# Wait for both
wait $PID_I
echo "[$(date +%H:%M:%S)] I done" >> $LOG/sequential_runner.log
wait $PID_J
echo "[$(date +%H:%M:%S)] J done, starting M" >> $LOG/sequential_runner.log

$PY scripts/probe/build_design_m_distill.py --state florida --epochs 500 --device mps > $LOG/build_m_florida.log 2>&1
echo "[$(date +%H:%M:%S)] all done" >> $LOG/sequential_runner.log
