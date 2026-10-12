#!/usr/bin/env bash
# Fan out the folds of ONE execution as separate processes that share a single
# results rundir, then aggregate. The multi-fold orchestrator on top of
# `train.py --only-folds k --run-id NAME --per-fold-seed`.
#
# Usage:
#   scripts/run_folds_fanout.sh <run_id> <folds_csv> <max_parallel> -- <train.py recipe...>
#
#   run_id        leaf name shared by all fold-processes' rundir (e.g. al_champG_fan_s0)
#   folds_csv     0-indexed canonical folds to run, e.g. 0,1,2,3,4  (or 2,3)
#   max_parallel  concurrent fold-processes on this GPU (small states fit 5; CA/TX 2-3)
#   recipe        the FULL train.py args AFTER `--`, WITHOUT --folds/--only-fold[s]/--run-id
#                 (the orchestrator appends --only-folds k --run-id <run_id> --per-fold-seed)
#
# Example (AL champion-G, all 5 folds, 5-way parallel on the A40):
#   PYTHONPATH=src MTL_DISABLE_AMP=1 MTL_STRICT=1 \
#   scripts/run_folds_fanout.sh al_champG_fan_s0 0,1,2,3,4 5 -- \
#     python scripts/train.py --task mtl --canon none --task-set check2hgi_next_region \
#       --engine check2hgi_dk_ovl --state alabama --seed 0 --epochs 50 --batch-size 2048 \
#       --mtl-loss static_weight --category-weight 0.75 --no-reg-class-weights --no-cat-class-weights \
#       --cat-head next_gru --reg-head next_stan_flow_dualtower \
#       --reg-head-param raw_embed_dim=64 --reg-head-param fusion_mode=aux \
#       --reg-head-param freeze_alpha=True --reg-head-param alpha_init=0.0 \
#       --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
#       --scheduler onecycle --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
#       --model mtlnet_crossattn_dualtower --compile --tf32 \
#       --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/alabama --no-checkpoints
#
# NOTE: in a fan-out the per-process `summary/full_summary.json` is unreliable (each
# process only knows its own fold and they race on that shared file — now stamped with a
# `_fanout` warning). The TRUTH is the per-fold artifacts → read `fold_aggregate.json`
# (written here) or run the canonical scorer (a40_score_matched.py) on the rundir; both
# glob fold*_* by real id.
#
# ⚠ NOT FOR FROZEN-CELL REPRODUCTION. The fan-out implies --per-fold-seed (reseed
# seed+fold_id), so folds 1-4 draw a DIFFERENT RNG stream than a legacy single-global-seed
# sequential run. Fan-out numbers are a reproducible, order-independent baseline of their
# OWN — keep them separately labeled from the frozen sequential §0.1 cells; never use the
# fan-out to regenerate or extend a frozen cell.
set -uo pipefail

RUN_ID="${1:?run_id required}"; FOLDS_CSV="${2:?folds_csv required}"; MAXP="${3:?max_parallel required}"
shift 3
[ "${1:-}" = "--" ] || { echo "expected '--' before the train.py recipe" >&2; exit 2; }
shift
RECIPE=("$@")
[ ${#RECIPE[@]} -gt 0 ] || { echo "empty recipe after '--'" >&2; exit 2; }

IFS=',' read -r -a FOLDS <<< "$FOLDS_CSV"
LOGDIR="${FANOUT_LOGDIR:-logs/fanout/${RUN_ID}}"
mkdir -p "$LOGDIR"
echo "[fanout] run_id=$RUN_ID folds=(${FOLDS[*]}) max_parallel=$MAXP  logs→$LOGDIR"

pids=()
launch() {
  local k="$1"
  # Per-fold inductor cache so concurrent COMPILED fold-processes don't contend on
  # one cache dir (each fold compiles the same graph once into its own dir).
  local cache="${TORCHINDUCTOR_CACHE_DIR:-$HOME/.inductor_cache_fanout}/${RUN_ID}_fold${k}"
  ( export TORCHINDUCTOR_CACHE_DIR="$cache"; "${RECIPE[@]}" \
        --only-folds "$k" --run-id "$RUN_ID" --per-fold-seed ) \
      > "$LOGDIR/fold${k}.log" 2>&1 &
  pids+=("$!")
  echo "[fanout] launched fold $k (pid $!)"
}

# throttle to MAXP concurrent processes
running=0
for k in "${FOLDS[@]}"; do
  launch "$k"
  running=$((running + 1))
  if [ "$running" -ge "$MAXP" ]; then
    wait -n 2>/dev/null || wait "${pids[0]}"   # free a slot (bash 5: wait -n)
    running=$((running - 1))
  fi
done
# wait for the stragglers
FAIL=0
for p in "${pids[@]}"; do wait "$p" || FAIL=$((FAIL + 1)); done
echo "[fanout] all fold-processes done (failures=$FAIL)"

# locate the shared rundir (unique by run_id suffix) and aggregate. NB: the rundir
# leaf is lowercased by HistoryStorage._folder_name, so glob with the lowercased id.
RUN_ID_LC=$(printf '%s' "$RUN_ID" | tr '[:upper:]' '[:lower:]')
RUNDIR=$(ls -d results/*/*/*_"${RUN_ID_LC}" 2>/dev/null | head -1)
if [ -z "$RUNDIR" ]; then
  echo "[fanout] could not locate the shared rundir (results/*/*/*_${RUN_ID_LC})" >&2
  exit 3
fi
echo "[fanout] shared rundir = $RUNDIR"
PYTHONPATH=${PYTHONPATH:-src} python scripts/aggregate_folds.py "$RUNDIR" --expect "$FOLDS_CSV" --tag "$RUN_ID"
exit $([ "$FAIL" -eq 0 ] && echo 0 || echo 1)
