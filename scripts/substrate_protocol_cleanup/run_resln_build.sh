#!/usr/bin/env bash
# tier_resln Stage 2+3 — build 6 ResLN substrates + postbuild glue.
#   ResLN-canonical (check2hgi_resln) @ AL/AZ/FL
#   ResLN+Design B  (check2hgi_resln_design_b) @ AL/AZ/FL
# 500 epochs, --device cuda, seed=42. AL/AZ ~6 min, FL ~30-40 min.
# Postbuild per substrate: next.parquet + next_region.parquet + cp canonical
# seed42 log_T (touch after parquet, C22 mtime guard).
# Detached megascript; GPU>=10GB + disk>=4GB guard; markers/PIDs logged.
set -u
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
LOG=/tmp/tier_resln_logs
mkdir -p "$LOG"
MARK="$LOG/build.DONE"
rm -f "$MARK"
echo "BUILD_PID $$ $(date -u +%FT%TZ)" > "$LOG/build.pid"

guard() {  # wait for GPU>=10GB free AND disk>=4GB free
  while true; do
    local gfree dfree
    gfree=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
    dfree=$(df -m /home | awk 'NR==2{print $4}')
    if [ "${gfree:-0}" -ge 10000 ] && [ "${dfree:-0}" -ge 4000 ]; then break; fi
    echo "[$(date -u +%H:%M:%S)] guard wait gfree=${gfree} dfree=${dfree}" >> "$LOG/build.log"
    sleep 30
  done
}

build_canonical() {  # state
  local state="$1"
  echo "[$(date -u +%H:%M:%S)] BUILD resln-canonical $state START" >> "$LOG/build.log"
  $PY scripts/substrate_protocol_cleanup/build_resln_canonical.py \
      --state "$state" --epochs 500 --num-layers 2 --device cuda --seed 42 \
      >> "$LOG/build_resln_${state}.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] BUILD resln-canonical $state EXIT rc=$?" >> "$LOG/build.log"
}

build_design_b() {  # state
  local state="$1"
  echo "[$(date -u +%H:%M:%S)] BUILD resln-design_b $state START" >> "$LOG/build.log"
  $PY scripts/probe/build_design_b_poi_pool.py \
      --state "$state" --epochs 500 --num-layers 2 --device cuda \
      --encoder resln --out-engine check2hgi_resln_design_b \
      >> "$LOG/build_reslndb_${state}.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] BUILD resln-design_b $state EXIT rc=$?" >> "$LOG/build.log"
}

postbuild() {  # engine state
  local engine="$1" state="$2"
  local out_dir="output/${engine}/${state}"
  echo "[$(date -u +%H:%M:%S)] POSTBUILD $engine $state START" >> "$LOG/build.log"
  [ -f "$out_dir/embeddings.parquet" ] || { echo "ERR $out_dir/embeddings.parquet missing" >> "$LOG/build.log"; return 1; }
  # 1. next.parquet
  $PY -c "
import sys; sys.path.insert(0,'src')
from configs.paths import EmbeddingEngine
from data.inputs.builders import generate_next_input_from_checkins
generate_next_input_from_checkins('${state}', EmbeddingEngine('${engine}'))
print('[postbuild] next.parquet OK')
" >> "$LOG/postbuild_${engine}_${state}.log" 2>&1
  # 2. next_region.parquet
  $PY scripts/substrate_protocol_cleanup/build_design_next_region.py \
      --state "$state" --engine "$engine" >> "$LOG/postbuild_${engine}_${state}.log" 2>&1
  # 3. cp canonical seed=42 log_T (n_regions identical — graph copied verbatim)
  local canon="output/check2hgi/${state}"
  for fold in 1 2 3 4 5; do
    cp "$canon/region_transition_log_seed42_fold${fold}.pt" \
       "$out_dir/region_transition_log_seed42_fold${fold}.pt" || { echo "ERR log_T cp fold$fold" >> "$LOG/build.log"; return 1; }
  done
  sleep 1
  touch "$out_dir"/region_transition_log_seed42_fold*.pt
  echo "[$(date -u +%H:%M:%S)] POSTBUILD $engine $state DONE" >> "$LOG/build.log"
}

# ---- AL/AZ: build both variants in parallel (small, fast) ----
for state in alabama arizona; do
  guard; build_canonical "$state" &
  guard; build_design_b "$state" &
  wait
  postbuild check2hgi_resln "$state"
  postbuild check2hgi_resln_design_b "$state"
done

# ---- FL: build serially (large) ----
guard; build_canonical florida
postbuild check2hgi_resln florida
guard; build_design_b florida
postbuild check2hgi_resln_design_b florida

echo "ALL_BUILD_DONE $(date -u +%FT%TZ)" > "$MARK"
echo "[$(date -u +%H:%M:%S)] ALL DONE" >> "$LOG/build.log"
