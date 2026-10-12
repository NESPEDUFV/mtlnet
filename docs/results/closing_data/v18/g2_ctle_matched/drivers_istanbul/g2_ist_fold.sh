#!/usr/bin/env bash
# G2 CTLE matched split, ISTANBUL, internal disk. usage: g2_ist_fold.sh <fold>. Same recipe as G2 AL/AZ. PID-scoped watchdog.
G2=/Users/vitor/g2_scratch; C=$G2/ingred; F=$1; ST=istanbul; VENV=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
export OUTPUT_DIR=$G2/output DATA_ROOT=$G2/data PYTHONPATH=$C/src:$C/research:$C/scripts:$C MTL_RAM_HEADROOM_GB=4 MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 PYTHONDONTWRITEBYTECODE=1
OUTF=$G2/results/${ST}_f$F; mkdir -p $OUTF
step(){ local tag=$1; shift; local L=$G2/logs/$tag; if grep -q "^rc=0" $L/RUN.txt 2>/dev/null; then echo "SKIP $tag"; return 0; fi; [ -d $L ] && mv $L ${L}_aborted_$(date +%H%M%S); mkdir -p $L; cd $C
  echo "start $(date '+%F %T') commit $(git rev-parse --short HEAD)" > $L/RUN.txt; echo "cmd: $*" >> $L/RUN.txt
  /usr/bin/time -l "$@" > $L/out.log 2>&1 & local CP=$!
  ( while kill -0 $CP 2>/dev/null; do pl=$(sysctl -n kern.memorystatus_vm_pressure_level); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}'); di=$(df -g / | awk 'NR==2{print $4}')
      echo "$(date +%T) pressure=$pl free=$fr disk_int=$di" >> $L/mem.log
      if [ "$pl" -ge 4 ] || [ "$fr" -lt 15 ] || [ "$di" -lt 5 ]; then echo "ABORT $(date +%T) pressure=$pl free=$fr disk=$di" >> $L/RUN.txt; pkill -TERM -P $CP; kill -TERM $CP; break; fi; sleep 5; done ) & local WD=$!
  wait $CP; local RC=$?; kill $WD 2>/dev/null; echo "rc=$RC peakRSS_bytes=$(grep 'maximum resident' $L/out.log | awk '{print $1}')" >> $L/RUN.txt; [ $RC = 0 ] || { echo "STEP FAIL $tag"; exit 1; }; }
step g2_${ST}_f${F}_build $VENV scripts/baselines/build_ctle_substrate.py --state $ST --seed 0 --fold $F --split-engine check2hgi_dk_ovl --stride 1 --device mps
cd $C && $VENV $G2/g2_assert.py $ST $F >> $G2/logs/ASSERTS_g2_ist.log 2>&1 || { echo "G2 ASSERT FAIL $ST f$F"; exit 1; }
cp $G2/output/check2hgi_ctle/$ST/CTLE_FOLD.txt $OUTF/CTLE_FOLD.txt
step g2_${ST}_f${F}_cat env RESULTS_ROOT=$OUTF/run OMP_NUM_THREADS=4 $VENV scripts/train.py --task next --engine check2hgi_ctle --state $ST --seed 0 --only-fold $F --cat-head next_gru --epochs 50 --batch-size 2048
echo "G2 FOLD DONE $ST f$F $(date '+%F %T')"
