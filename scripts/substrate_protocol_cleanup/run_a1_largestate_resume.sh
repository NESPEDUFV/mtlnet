#!/usr/bin/env bash
# Tier A1 large-state pilot RESUME driver (post disk-full recovery).
# FL W0.0 already salvaged. Re-runs: FL W0.2, CA W0.0/W0.2, TX W0.0/W0.2.
# Uses --no-checkpoints (disk pressure: only metrics CSVs are needed).
# CA/TX run --folds 5 (log_T n_splits=5) but only fold 1 is analysed; the
# driver early-stops CA/TX after fold 1 completes to conserve compute+disk.
set -uo pipefail
cd /home/vitor.oliveira/PoiMtlNet
PY=.venv/bin/python
OUT=docs/results/substrate_protocol_cleanup/tier_a1_largestate
MIN_FREE_MB=15000
MIN_DISK_MB=1500

gpu_free() { nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1; }
disk_free() { df -m --output=avail . | tail -1 | tr -d ' '; }

preflight() {
  local f d
  f=$(gpu_free); d=$(disk_free)
  echo "[preflight] gpu ${f} MiB free, disk ${d} MiB free"
  if [ "${d:-0}" -lt "$MIN_DISK_MB" ]; then echo "[preflight] FATAL: disk < ${MIN_DISK_MB} MiB"; return 1; fi
  for _ in $(seq 1 60); do
    f=$(gpu_free)
    [ "${f:-0}" -ge "$MIN_FREE_MB" ] && { echo "[gpu] ${f} MiB free — OK"; return 0; }
    echo "[gpu] only ${f} MiB; wait 60s"; sleep 60
  done
  echo "[gpu] FATAL: never reached ${MIN_FREE_MB} MiB"; return 1
}

# early_stop_folds: if >0, watch run.log in background and kill train.py after
# fold N completes (we only need fold 1 for CA/TX).
run_cell() {
  local state="$1" bs="$2" w="$3" stop_after="$4"
  local dir="${OUT}/${state}/W${w}/seed42"
  mkdir -p "$dir"
  if ls "$dir"/mtlnet_* >/dev/null 2>&1; then echo "[skip] ${state} W${w} done"; return 0; fi
  preflight || return 1
  echo "[gpu-snapshot] $(date -u +%FT%TZ) ${state} W${w}: $(gpu_free) MiB free, disk $(disk_free) MiB" | tee -a "${OUT}/gpu_snapshots.log"
  echo "=== ${state} W${w} (bs=${bs}, stop_after=${stop_after}) -> ${dir}/run.log ==="
  $PY scripts/train.py \
    --task mtl --task-set check2hgi_next_region \
    --state "${state}" --engine check2hgi --seed 42 \
    --epochs 50 --folds 5 --batch-size "${bs}" \
    --model mtlnet_crossattn \
    --mtl-loss static_weight --category-weight 0.75 \
    --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
    --scheduler cosine --max-lr 3e-3 \
    --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
    --cat-head next_gru --reg-head next_getnext_hard \
    --task-a-input-type checkin --task-b-input-type region \
    --per-fold-transition-dir "output/check2hgi/${state}" \
    --log-t-kd-weight "${w}" --log-t-kd-tau 1.0 \
    --no-checkpoints \
    > "${dir}/run.log" 2>&1 &
  local trainpid=$!

  if [ "${stop_after}" -gt 0 ]; then
    # wait until fold (stop_after+1) starts OR training exits; then kill.
    while kill -0 "$trainpid" 2>/dev/null; do
      local nf
      nf=$(grep -c "= FOLD" "${dir}/run.log" 2>/dev/null || echo 0)
      if [ "${nf:-0}" -gt "${stop_after}" ]; then
        echo "[early-stop] ${state} W${w}: fold ${stop_after} done (fold $((stop_after+1)) started); killing train.py ${trainpid}"
        kill "$trainpid" 2>/dev/null; sleep 3; kill -9 "$trainpid" 2>/dev/null
        break
      fi
      sleep 15
    done
  fi
  wait "$trainpid" 2>/dev/null
  local rc=$?
  # locate freshly written results dir and copy it
  local res
  res=$(ls -dt results/check2hgi/${state}/mtlnet_* 2>/dev/null | head -1)
  if [ -n "$res" ]; then
    # copy only metrics + summary (no bulky blobs)
    mkdir -p "$dir/$(basename "$res")"
    cp -r "$res/metrics" "$dir/$(basename "$res")/" 2>/dev/null
    cp -r "$res/summary" "$dir/$(basename "$res")/" 2>/dev/null
    echo "[cp] ${state} W${w}: metrics+summary from $(basename "$res")"
  else
    echo "[warn] ${state} W${w}: no results dir found (rc=${rc})"
  fi
  echo "[done] ${state} W${w} rc=${rc} (early-stop expected non-zero if killed)"
}

run_cell florida    2048 0.2 0   # full 5-fold
run_cell california 1024 0.0 1   # fold-1 only
run_cell california 1024 0.2 1
run_cell texas       512 0.0 1
run_cell texas       512 0.2 1
echo "### RESUME DRIVER COMPLETE ###"
