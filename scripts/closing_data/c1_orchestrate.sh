#!/bin/bash
# closing_data C1 (confirm-on-G) — full remaining run, SEQUENTIAL (no MPS contention).
#   1. AL seeds {1,7,100}   (seed 0 already done)
#   2. FL v14 build (long)  + prep {0,1,7,100}
#   3. FL seeds {0,1,7,100}
#   4. final aggregate (AL all seeds + FL all seeds)
# Resilient: a failing seed is logged and skipped, not fatal.
#
#   CONC=1 setsid bash scripts/closing_data/c1_orchestrate.sh > /tmp/c1_orch.log 2>&1 &
set -uo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"; cd "$REPO"
PY=.venv/bin/python
ENGINE=check2hgi_design_k_resln_mae_l0_1
ts(){ date '+%H:%M:%S'; }; say(){ echo "[$(ts)] ORCH $*"; }

run_seed(){ # state seed
  local st="$1" sd="$2"
  say ">>> $st seed=$sd"
  if bash scripts/closing_data/c1_run_g.sh "$st" "$sd"; then
    say "<<< $st seed=$sd OK"
  else
    say "!!! $st seed=$sd FAILED (rc=$?) — continuing"
  fi
}

# ---------- 1. AL multi-seed ----------
say "AL prep log_T seeds 1 7 100"
bash scripts/closing_data/c1_prep_substrate.sh alabama 1 7 100 || say "AL prep WARN"
for sd in 1 7 100; do run_seed alabama "$sd"; done
say "AL multi-seed aggregate:"
$PY scripts/closing_data/c1_aggregate.py "results/${ENGINE}/alabama/c1_route_s*/route_fold*.json" || true

# ---------- 2. FL build + prep ----------
FL_EMB="output/${ENGINE}/florida/region_embeddings.parquet"
if [ ! -f "$FL_EMB" ]; then
  say "FL v14 build (MPS, ~500ep) — this is the long pole"
  $PY scripts/probe/build_design_k_delaunay.py --state florida \
      --out-suffix resln_mae_l0_1 --epochs 500 --device mps \
      > /tmp/c1_v14_build/florida.log 2>&1 && say "FL build done" || { say "FL build FAILED"; exit 1; }
else
  say "FL substrate already present — skip build"
fi
say "FL prep (postbuild + log_T seeds 0 1 7 100)"
bash scripts/closing_data/c1_prep_substrate.sh florida 0 1 7 100 || { say "FL prep FAILED"; exit 1; }

# ---------- 3. FL DISCRIMINATOR (seed 0 only) ----------
# FL is the heavy state and the whole premise is that the old FL +2.80 signal
# MIGHT be subsumed on G — so gate FL on seed 0 before spending {1,7,100}.
run_seed florida 0

# ---------- 4. interim aggregate (AL all seeds + FL seed 0) ----------
say "============ INTERIM AGGREGATE (AL all + FL s0) ============"
$PY scripts/closing_data/c1_aggregate.py \
    "results/${ENGINE}/alabama/c1_route_s*/route_fold*.json" \
    "results/${ENGINE}/florida/c1_route_s0/route_fold*.json"
say "PHASE-1 DONE — FL{1,7,100} pending the FL-seed0 read (decide next)"
