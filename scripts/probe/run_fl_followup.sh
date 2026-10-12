#!/usr/bin/env bash
# Run after B FL finishes: I → J → M sequentially on MPS.
PY=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
LOG=logs/design_fl_eval

while pgrep -f build_design_b_poi_pool >/dev/null; do sleep 30; done
echo "[$(date +%H:%M:%S)] B done, starting I" >> $LOG/sequential_runner.log
$PY scripts/probe/build_design_i_lora.py --state florida --epochs 500 --device mps > $LOG/build_i_florida.log 2>&1
echo "[$(date +%H:%M:%S)] I done, starting J" >> $LOG/sequential_runner.log
$PY scripts/probe/build_design_j_anchor.py --state florida --epochs 500 --device mps > $LOG/build_j_florida.log 2>&1
echo "[$(date +%H:%M:%S)] J done, starting M" >> $LOG/sequential_runner.log
$PY scripts/probe/build_design_m_distill.py --state florida --epochs 500 --device mps > $LOG/build_m_florida.log 2>&1
echo "[$(date +%H:%M:%S)] all done" >> $LOG/sequential_runner.log
