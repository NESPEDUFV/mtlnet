#!/usr/bin/env bash
# usage: g2_ctle_fold.sh <state> <fold>  -- G2 CTLE matched-split cell, RESUMABLE, fail-stop, serial
set -u; C="/Volumes/Vitor's SSD/ingred_g1"; cd "$C"; G="$C/g1_logs/g1_run.sh"; source "$C/g1_logs/g1_lib.sh"
ST=$1; F=$2; export PYTHONPATH="$C/src:$C/research:$C/scripts:$C" MTL_RAM_HEADROOM_GB=4
T=g2_${ST}_f$F; OUTF="$C/results/g2_ctle/${ST}_f$F"; mkdir -p "$OUTF"
G1_HEAVY=1 step ${T}_build - .venv/bin/python scripts/baselines/build_ctle_substrate.py --state $ST --seed 0 --fold $F --split-engine check2hgi_dk_ovl --stride 1 --device mps
.venv/bin/python g1_logs/g2_assert.py $ST $F >> g1_logs/ASSERTS_g2.log 2>&1 || { echo "G2 ASSERT FAIL $ST f$F"; tail -3 g1_logs/ASSERTS_g2.log; exit 1; }
cp "output/check2hgi_ctle/$ST/CTLE_FOLD.txt" "$OUTF/CTLE_FOLD.txt"
G1_HEAVY=1 step ${T}_cat "$OUTF/run/check2hgi_ctle/$ST" env RESULTS_ROOT="$OUTF/run" OMP_NUM_THREADS=4 .venv/bin/python scripts/train.py --task next --engine check2hgi_ctle --state $ST --seed 0 --only-fold $F --cat-head next_gru --epochs 50 --batch-size 2048
echo "G2 FOLD DONE $ST f$F $(date '+%F %T')"
