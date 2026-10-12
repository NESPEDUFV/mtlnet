#!/usr/bin/env bash
# tier_resln (Design J branch) STL — mirrors run_resln_stl.sh protocol EXACTLY
# (same harness/flags) so numbers are directly comparable to ResLN+design_b.
# Single variant: resln_design_j (check2hgi_resln_design_j) at AL/AZ/FL.
#   STL-reg : next_getnext_hard, --input-type region, --region-emb-source engine,
#             --per-fold-transition-dir output/<engine>/<state> (leak-free).
#   STL-cat : next_gru, --target category, --input-type checkin,
#             --engine-override <engine>.
# Output: tier_resln/<axis>/resln_design_j/<state>/seed42/.
set -u
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
LOG=/tmp/tier_reslndj_logs
mkdir -p "$LOG"
RES=docs/results/substrate_protocol_cleanup/tier_resln
MARK="$LOG/stl.DONE"
rm -f "$MARK"
echo "STL_PID $$ $(date -u +%FT%TZ)" > "$LOG/stl.pid"

guard() {
  while true; do
    local gfree dfree
    gfree=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
    dfree=$(df -m /home | awk 'NR==2{print $4}')
    if [ "${gfree:-0}" -ge 10000 ] && [ "${dfree:-0}" -ge 4000 ]; then break; fi
    sleep 30
  done
}

snap() {  # tag celldir
  local tag="$1" celldir="$2"
  local j; j=$(ls -dt docs/results/P1/*"${tag}"*.json 2>/dev/null | grep -v checkpoint | head -1)
  [ -n "$j" ] && cp "$j" "$celldir/" 2>/dev/null || true
}

stl_reg() {  # engine state variant
  local engine="$1" state="$2" variant="$3"
  local tag="RESLN_STL_REG_${variant}_${state}"
  local celldir="$RES/stl_reg/${variant}/${state}/seed42"
  mkdir -p "$celldir"
  echo "[$(date -u +%H:%M:%S)] STL-REG START $variant $state src=$engine" >> "$LOG/stl.log"
  $PY scripts/p1_region_head_ablation.py \
      --state "$state" --heads next_getnext_hard \
      --folds 5 --epochs 50 --seed 42 --input-type region \
      --batch-size 2048 \
      --region-emb-source "$engine" \
      --per-fold-transition-dir "output/${engine}/${state}" \
      --override-hparams d_model=256 num_heads=8 \
      --tag "$tag" \
      > "$celldir/run.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] STL-REG EXIT $variant $state rc=$?" >> "$LOG/stl.log"
  snap "$tag" "$celldir"
}

stl_cat() {  # engine state variant
  local engine="$1" state="$2" variant="$3"
  local tag="RESLN_STL_CAT_${variant}_${state}"
  local celldir="$RES/stl_cat/${variant}/${state}/seed42"
  mkdir -p "$celldir"
  echo "[$(date -u +%H:%M:%S)] STL-CAT START $variant $state override=$engine" >> "$LOG/stl.log"
  $PY scripts/p1_region_head_ablation.py \
      --state "$state" --heads next_gru \
      --folds 5 --epochs 50 --seed 42 --input-type checkin \
      --batch-size 2048 \
      --engine-override "$engine" \
      --target category \
      --tag "$tag" \
      > "$celldir/run.log" 2>&1
  echo "[$(date -u +%H:%M:%S)] STL-CAT EXIT $variant $state rc=$?" >> "$LOG/stl.log"
  snap "$tag" "$celldir"
}

ENG=check2hgi_resln_design_j
VARIANT=resln_design_j

for state in alabama arizona florida; do
  [ -f "output/${ENG}/${state}/region_embeddings.parquet" ] || {
    echo "[$(date -u +%H:%M:%S)] SKIP STL $VARIANT $state (no region_embeddings)" >> "$LOG/stl.log"; continue; }
  guard; stl_reg "$ENG" "$state" "$VARIANT"
  guard; stl_cat "$ENG" "$state" "$VARIANT"
done

echo "ALL_STL_DONE $(date -u +%FT%TZ)" > "$MARK"
echo "[$(date -u +%H:%M:%S)] ALL STL DONE" >> "$LOG/stl.log"
