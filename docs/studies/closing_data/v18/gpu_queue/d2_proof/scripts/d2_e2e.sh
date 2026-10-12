#!/usr/bin/env bash
# D2 end-to-end equivalence: AL cell_cat --only-fold F, OLD clone vs NEW clone, same inputs/env, MPS, one run at a time.
# usage: d2_e2e.sh   (runs old_f0 new_f0 old_f3 new_f3 old_f0_rep sequentially, fail-stop)
D=/Users/vitor/d2_scratch; VENV=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
run(){ local tag=$1 clone=$2 F=$3; local L=$D/logs/$tag; mkdir -p $L; [ -e $D/results/$tag ] && { echo "exists $tag"; return 1; }
  cd $D/$clone || return 9
  echo "start $(date '+%F %T') clone=$clone commit=$(git rev-parse --short HEAD) patched=$(git diff --quiet && echo no || echo yes) fold=$F" > $L/RUN.txt
  env OUTPUT_DIR=$D/output DATA_ROOT=$D/data RESULTS_ROOT=$D/results/$tag PYTHONPATH=$D/$clone/src:$D/$clone/research:$D/$clone MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 MTL_RAM_HEADROOM_GB=4 PYTHONDONTWRITEBYTECODE=1 \
    /usr/bin/time -l $VENV scripts/train.py --task next --state alabama --engine check2hgi_v18 --model next_gru --embedding-dim 64 --folds 5 --only-fold $F --epochs 50 --seed 0 --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5 --no-checkpoints > $L/out.log 2>&1 & local CP=$!
  ( while kill -0 $CP 2>/dev/null; do pl=$(sysctl -n kern.memorystatus_vm_pressure_level); fr=$(memory_pressure | awk '/free percentage/{gsub("%","",$5); print $5}'); wi=$(vm_stat | awk '/wired down/{gsub("\\.","",$4); printf "%.1f",$4*16384/1e9}')
      echo "$(date +%T) pressure=$pl free=$fr wired_GB=$wi" >> $L/mem.log
      if [ "$pl" -ge 4 ] || [ "$fr" -lt 15 ]; then echo "ABORT $(date +%T) pressure=$pl free=$fr" >> $L/RUN.txt; pkill -TERM -P $CP; kill -TERM $CP; break; fi; sleep 2; done ) & local WD=$!
  wait $CP; local RC=$?; kill $WD 2>/dev/null
  echo "rc=$RC peakRSS_bytes=$(grep 'maximum resident' $L/out.log | awk '{print $1}') max_wired_GB=$(awk -F'wired_GB=' '{print $2}' $L/mem.log | sort -n | tail -1)" >> $L/RUN.txt
  [ $RC = 0 ] || { echo "FAIL $tag rc=$RC"; return 1; }; echo "DONE $tag $(date +%T)"; }
run old_f0 old 0 && run new_f0 new 0 && run old_f3 old 3 && run new_f3 new 3 && run old_f0_rep old 0 && echo "D2 E2E ALL RUNS DONE"
