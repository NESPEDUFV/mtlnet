#!/bin/bash
# Lane 1 — run ONE champion-G arm (baseline / aligned-pairing / loss-scale) at one state+seed,
# then SNAPSHOT its diagnostic outputs into a capture dir before the next same-state run overwrites
# the shared results/{engine}/{state}/ tree (--no-checkpoints writes top-level, shared across runs).
#
# Usage: bash scripts/pre_freeze_gates/lane1_run.sh <state> <seed> <arm> ["<extra flags>"]
#   arm ∈ {baseline, aligned, lossscale}; extra flags appended verbatim (the lever flag).
#   bash scripts/pre_freeze_gates/lane1_run.sh florida 0 baseline ""
#   bash scripts/pre_freeze_gates/lane1_run.sh florida 0 aligned   "--aligned-pairing"
#   bash scripts/pre_freeze_gates/lane1_run.sh florida 0 lossscale "--loss-scale-norm"
set -euo pipefail

# P2 (advisor-vetted, math/determinism-inert): reduce CUDA allocator fragmentation.
# Ignored on non-CUDA (MPS/CPU) → MPS-compatible.
export PYTORCH_CUDA_ALLOC_CONF="${PYTORCH_CUDA_ALLOC_CONF:-expandable_segments:True}"

STATE="$1"; SEED="$2"; ARM="$3"; EXTRA="${4:-}"
# Engine override via env (Lane 2 overlap uses check2hgi_dk_ovl); default = v14 design_k.
ENGINE="${LANE1_ENGINE:-check2hgi_design_k_resln_mae_l0_1}"
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PY=.venv/bin/python; [ -x "$PY" ] || PY=python3

# torch-build guard (perf-audit S-pin): the canonical reg Acc@10 is defined by fp16-CUDA
# topk tie-breaking; torch 2.12 rewrote the TopK kernel (RadixSelect) + dropped cu128 wheels,
# so a silent build change would re-baseline the frozen numbers. Warn loudly on mismatch
# (set MTL_STRICT_TORCH=1 to hard-fail for freeze-grade runs).
_TVER="$($PY -c 'import torch;print(torch.__version__)' 2>/dev/null || echo unknown)"
if [ "$_TVER" != "2.11.0+cu128" ]; then
  echo "⚠ WARN: torch build is '$_TVER', expected '2.11.0+cu128' — fp16 topk tie-breaking may differ → frozen Acc@10 could shift."
  [ "${MTL_STRICT_TORCH:-0}" = "1" ] && { echo "MTL_STRICT_TORCH=1 → abort"; exit 1; }
fi

RES="results/${ENGINE}/${STATE}"
TDIR="output/${ENGINE}/${STATE}"
CAP="results/lane1_g01/${STATE}_s${SEED}__${ARM}"
LOGROOT=/tmp/lane1; mkdir -p "$LOGROOT" "$CAP"
RUNLOG="$LOGROOT/${STATE}_s${SEED}_${ARM}.log"
say(){ echo "[lane1 $STATE s$SEED $ARM] $*"; }

# --- freshness preflight (centralized rule; Linux stat -c) ---
nr="$TDIR/input/next_region.parquet"
[ -f "$nr" ] || { echo "ERR next_region missing: $nr"; exit 1; }
nr_m=$(stat -c %Y "$nr")
for f in 1 2 3 4 5; do
  lt="$TDIR/region_transition_log_seed${SEED}_fold${f}.pt"
  [ -f "$lt" ] || { echo "ERR missing log_T $lt"; exit 1; }
  [ "$(stat -c %Y "$lt")" -ge "$nr_m" ] || { echo "ERR STALE log_T $lt < next_region"; exit 1; }
done
say "log_T freshness OK (5 folds seed=$SEED)"

say "launching champion G + extra='$EXTRA' -> $RUNLOG"
# Background python so we can capture its PID — train.py names its run dir
# mtlnet_..._{TS}_{PID}, so the PID disambiguates from any concurrent run (C28; no ls -dt|head).
$PY scripts/train.py --task mtl --task-set check2hgi_next_region \
  --engine "$ENGINE" --state "$STATE" --seed "$SEED" \
  --epochs 50 --folds 5 --batch-size 2048 \
  --model mtlnet_crossattn_dualtower \
  --mtl-loss static_weight --category-weight 0.75 \
  --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin --task-b-input-type region \
  --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --log-t-kd-weight 0.0 \
  --per-fold-transition-dir "$TDIR" \
  --no-checkpoints $EXTRA \
  > "$RUNLOG" 2>&1 &
PYPID=$!
echo "$PYPID" > "$CAP/PYPID.txt"
say "python PID=$PYPID — waiting…"
wait "$PYPID"; rc=$?
say "train exit=$rc — snapshotting diagnostics -> $CAP"
[ "$rc" -eq 0 ] || { echo "ERR train failed (exit $rc); see $RUNLOG"; tail -15 "$RUNLOG"; exit "$rc"; }

# --- locate THIS run's dir by PID suffix, snapshot diagnostics (per-task-best, selector-independent) ---
RUNDIR=$(ls -d "$RES"/mtlnet_*_"$PYPID" 2>/dev/null | head -1)
[ -n "$RUNDIR" ] || { echo "ERR no run dir matching *_$PYPID under $RES"; ls -dt "$RES"/mtlnet_* | head; exit 1; }
say "run dir = $RUNDIR"
cp "$RUNDIR"/summary/full_summary.json "$CAP/" 2>/dev/null || say "WARN no full_summary.json"
cp "$RUNDIR"/folds/fold*_info.json     "$CAP/" 2>/dev/null || say "WARN no fold*_info.json"
cp "$RUNDIR"/config.json               "$CAP/" 2>/dev/null || true
echo "$RUNDIR" > "$CAP/RUNDIR.txt"
echo "$EXTRA"  > "$CAP/EXTRA_FLAGS.txt"
say "DONE — capture in $CAP"
ls -1 "$CAP"
