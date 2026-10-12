#!/usr/bin/env bash
# tier_resln (Design J branch) MTL — mirrors run_resln_mtl.sh recipe EXACTLY.
# Single variant: resln_design_j (check2hgi_resln_design_j) at AL/AZ/FL.
#   AL/AZ = H3-alt (constant sched); FL = B9 (alternating, alpha-no-wd,
#   min-best 5, cosine max-lr 3e-3). --no-checkpoints.
# Output: tier_resln/resln_design_j/<state>/seed42/.
set -u
REPO=/home/vitor.oliveira/PoiMtlNet
cd "$REPO"
PY=.venv/bin/python
LOG=/tmp/tier_reslndj_logs
mkdir -p "$LOG"
RES=docs/results/substrate_protocol_cleanup/tier_resln
MARK="$LOG/mtl.DONE"
rm -f "$MARK"
echo "MTL_PID $$ $(date -u +%FT%TZ)" > "$LOG/mtl.pid"

guard() {
  while true; do
    local gfree dfree
    gfree=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1)
    dfree=$(df -m /home | awk 'NR==2{print $4}')
    if [ "${gfree:-0}" -ge 10000 ] && [ "${dfree:-0}" -ge 4000 ]; then break; fi
    sleep 30
  done
}

run_cell() {  # engine state tag
  local engine="$1" state="$2" tag="$3"
  local outdir="$RES/${tag}/${state}/seed42"
  rm -rf "$outdir"; mkdir -p "$outdir"
  local recipe=()
  if [ "$state" = "florida" ]; then
    recipe=(--alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5
            --scheduler cosine --max-lr 3e-3)
  else
    recipe=(--scheduler constant)
  fi
  echo "[$(date -u +%H:%M:%S)] MTL START $tag $state engine=$engine" >> "$LOG/mtl.log"
  $PY scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state "$state" --engine "$engine" --seed 42 \
    --epochs 50 --folds 5 --batch-size 2048 \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --cat-head next_gru --reg-head next_getnext_hard \
    --task-a-input-type checkin --task-b-input-type region \
    "${recipe[@]}" \
    --per-fold-transition-dir "output/${engine}/${state}" \
    --no-checkpoints \
    > "$outdir/run.log" 2>&1
  local rc=$?
  echo "[$(date -u +%H:%M:%S)] MTL EXIT $tag $state rc=$rc" >> "$LOG/mtl.log"
  local r; r=$(ls -dt results/${engine}/${state}/mtlnet_* 2>/dev/null | head -1)
  [ -n "$r" ] && cp -r "$r" "$outdir/" 2>/dev/null || true
}

CELLS=(
  "check2hgi_resln_design_j|alabama|resln_design_j"
  "check2hgi_resln_design_j|arizona|resln_design_j"
  "check2hgi_resln_design_j|florida|resln_design_j"
)

for spec in "${CELLS[@]}"; do
  IFS='|' read -r engine state tag <<< "$spec"
  if [ ! -f "output/${engine}/${state}/input/next_region.parquet" ]; then
    echo "[$(date -u +%H:%M:%S)] SKIP $tag $state (next_region.parquet missing)" >> "$LOG/mtl.log"
    continue
  fi
  guard
  run_cell "$engine" "$state" "$tag"
done

echo "ALL_MTL_DONE $(date -u +%FT%TZ)" > "$MARK"
echo "[$(date -u +%H:%M:%S)] ALL MTL DONE" >> "$LOG/mtl.log"
