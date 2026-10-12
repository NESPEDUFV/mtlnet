#!/usr/bin/env bash
# MTL_DATASET_CPU proof: AL cell_cat --only-fold 0 at HEAD, without (base) vs with (cpu) MTL_DATASET_CPU=1. Sequential, PID watchdog.
D=/Users/vitor/dcpu_scratch; VENV=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python; C=$D/ingred
run(){ local tag=$1 extra=$2; local L=$D/logs/$tag; mkdir -p $L; cd $C
  echo "start $(date '+%F %T') commit=$(git rev-parse --short HEAD) extra_env=[$extra]" > $L/RUN.txt
  env $extra OUTPUT_DIR=$D/output DATA_ROOT=$D/data RESULTS_ROOT=$D/results/$tag PYTHONPATH=$C/src:$C/research:$C MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 MTL_RAM_HEADROOM_GB=4 PYTHONDONTWRITEBYTECODE=1 \
    /usr/bin/time -l $VENV scripts/train.py --task next --state alabama --engine check2hgi_v18 --model next_gru --embedding-dim 64 --folds 5 --only-fold 0 --epochs 50 --seed 0 --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5 --no-checkpoints > $L/out.log 2>&1 & local CP=$!
  ( while kill -0 $CP 2>/dev/null; do pl=$(sysctl -n kern.memorystatus_vm_pressure_level); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}'); wi=$(vm_stat | awk '/wired down/{gsub("\\.","",$4); printf "%.1f",$4*16384/1e9}')
      echo "$(date +%T) pressure=$pl free=$fr wired_GB=$wi" >> $L/mem.log
      if [ "$pl" -ge 4 ] || [ "$fr" -lt 15 ]; then echo "ABORT $(date +%T) pressure=$pl free=$fr" >> $L/RUN.txt; pkill -TERM -P $CP; kill -TERM $CP; break; fi; sleep 2; done ) & local WD=$!
  wait $CP; local RC=$?; kill $WD 2>/dev/null
  echo "rc=$RC peakRSS_bytes=$(grep 'maximum resident' $L/out.log | awk '{print $1}') max_wired_GB=$(awk -F'wired_GB=' '{print $2}' $L/mem.log | sort -n | tail -1) wall_s=$(grep ' real' $L/out.log | awk '{print $1}')" >> $L/RUN.txt
  [ $RC = 0 ] || { echo "FAIL $tag"; return 1; }; echo "DONE $tag $(date +%T)"; }
run base_f0 "" && run cpu_f0 "MTL_DATASET_CPU=1" && echo "DCPU E2E ALL RUNS DONE"
