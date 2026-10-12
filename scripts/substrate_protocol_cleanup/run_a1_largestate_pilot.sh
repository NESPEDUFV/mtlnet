#!/usr/bin/env bash
# Tier A1 large-state pilot driver (sequential, GPU-neighbor-safe).
# FL W=0.0 may already be running as a detached process; this driver runs the
# REMAINING cells: FL W=0.2, then CA W0.0/W0.2 (fold-analysis=1), then TX.
# Each cell: preflight >=15GB free, run, cp results dir into the pilot tree.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
PY=.venv/bin/python
OUT=docs/results/substrate_protocol_cleanup/tier_a1_largestate
MIN_FREE_MB=15000

gpu_free() { nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1; }

wait_for_gpu() {
  for _ in $(seq 1 120); do
    f=$(gpu_free)
    if [ "${f:-0}" -ge "$MIN_FREE_MB" ]; then echo "[gpu] ${f} MiB free — OK to launch"; return 0; fi
    echo "[gpu] only ${f} MiB free (<${MIN_FREE_MB}); waiting 60s..."; sleep 60
  done
  echo "[gpu] FATAL: never reached ${MIN_FREE_MB} MiB free"; return 1
}

run_cell() {
  local state="$1" bs="$2" w="$3" recipe_kind="$4"
  local dir="${OUT}/${state}/W${w}/seed42"
  mkdir -p "$dir"
  if ls "$dir"/mtlnet_* >/dev/null 2>&1; then
    echo "[skip] ${state} W${w} already has a results dir"; return 0
  fi
  wait_for_gpu || return 1
  echo "[gpu-snapshot] $(date -u +%FT%TZ) ${state} W${w}: $(gpu_free) MiB free" | tee -a "${OUT}/gpu_snapshots.log"
  local recipe=(--alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5
                --scheduler cosine --max-lr 3e-3)
  echo "=== ${state} W${w} (bs=${bs}) -> ${dir}/run.log ==="
  $PY scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state "${state}" --engine check2hgi --seed 42 \
    --epochs 50 --folds 5 --batch-size "${bs}" \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    "${recipe[@]}" \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --cat-head next_gru --reg-head next_getnext_hard \
    --task-a-input-type checkin --task-b-input-type region \
    --per-fold-transition-dir "output/check2hgi/${state}" \
    --log-t-kd-weight "${w}" --log-t-kd-tau 1.0 \
    > "${dir}/run.log" 2>&1
  local rc=$?
  # locate the freshly written results dir and copy it under the pilot tree
  local res
  res=$(ls -dt results/check2hgi/${state}/mtlnet_* 2>/dev/null | head -1)
  if [ -n "$res" ] && [ "$rc" -eq 0 ]; then
    cp -r "$res" "$dir/"
    echo "[cp] copied ${res} -> ${dir}/"
  fi
  echo "[done] ${state} W${w} rc=${rc}"
  return $rc
}

echo "### Waiting for any in-flight FL W=0.0 to finish ###"
# wait for the detached FL W0.0 process (if present) to exit
while pgrep -f "train.py.*--state florida.*--log-t-kd-weight 0.0" >/dev/null 2>&1; do sleep 30; done
# copy FL W0.0 results if not already copied
if ls "${OUT}/florida/W0.0/seed42"/mtlnet_* >/dev/null 2>&1; then
  echo "[skip] FL W0.0 results already copied"
else
  res=$(ls -dt results/check2hgi/florida/mtlnet_* 2>/dev/null | head -1)
  [ -n "$res" ] && cp -r "$res" "${OUT}/florida/W0.0/seed42/" && echo "[cp] FL W0.0 ${res}"
fi

run_cell florida    2048 0.2 large
run_cell california 1024 0.0 large
run_cell california 1024 0.2 large
run_cell texas       512 0.0 large
run_cell texas       512 0.2 large

echo "### PILOT DRIVER COMPLETE ###"
