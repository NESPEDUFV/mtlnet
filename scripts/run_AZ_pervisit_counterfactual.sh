#!/usr/bin/env bash
# AZ replication of the per-visit counterfactual (paper §6.1, Figure 2).
#
# Purpose
#   The paper currently reports the per-visit counterfactual at Alabama (AL):
#   three matched-head (next_gru, GRU cat head) STL ceilings on the same
#   user-disjoint folds, with a single substrate substitution as the only
#   difference between cells. AL canonical numbers (5f × 50ep, seed 42):
#       canonical Check2HGI : macro-F1 40.76 ± 1.50  (per-visit vectors)
#       POI-pooled Check2HGI: macro-F1 29.57         (mean-pool by placeid)
#       HGI                  : macro-F1 25.26 ± 1.06  (per-place baseline)
#       per-visit component  : +11.19 pp (~72%)
#       training-signal comp.: + 4.31 pp (~28%)
#
#   This script replicates the same three cells at Arizona (AZ) so the paper
#   carries a two-state replicated mechanism finding instead of single-state
#   AL evidence. AZ is the cheapest other state (~10 min / cell on H100).
#
# Protocol — matched to AL exactly (per scripts/run_phase1_cat_stl.sh +
# scripts/probe/build_check2hgi_pooled.py + CH19/SUBSTRATE_COMPARISON_FINDINGS):
#   --task next --model next_gru --folds 5 --epochs 50 --seed 42
#   --no-checkpoints (no other CLI flags, default optimizer/scheduler/batch).
#   user-disjoint StratifiedGroupKFold(seed=42), default batch=1024 (bs1024
#   in run-dir name), AdamW(1e-4) + OneCycleLR(max=1e-2). Best-epoch selector
#   is train.py's default (val macro-F1, no min-best-epoch floor — AL didn't
#   set one, so neither do we).
#
#   The category task is single-task — no transition prior involved. Region
#   transition matrices are not loaded by --task next; they are only used by
#   --task mtl/--reg-head next_getnext_hard.
#
# Expected runtime
#   On H100 80 GB: ~10 min / cell × 3 cells = ~30 min total wall-clock.
#   On Colab T4 (post feat/colab-gpu-perf): ~10–12 min / cell.
#
# Expected output paths (auto-determined by train.py)
#   results/check2hgi/arizona/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   results/check2hgi_pooled/arizona/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   results/hgi/arizona/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   Each contains summary/full_summary.json + folds/foldN_info.json with
#   diagnostic_best_epochs.next.metrics.f1 (per-fold cat F1 macro).
#
# After this script
#   1. Extract per-fold cat F1 macro from each run's folds/foldN_info.json
#      and save to docs/results/phase1_perfold/
#      mirroring AL's naming: AZ_check2hgi_cat_gru_5f50ep.json,
#      AZ_check2hgi_pooled_cat_gru_5f50ep.json, AZ_hgi_cat_gru_5f50ep.json.
#   2. Compute per-visit component (canonical − pooled) and training-signal
#      component (pooled − HGI) — replicate AL row of the §6.1 table at AZ.
#      Target a 30 minute total wall on H100.
#
# Notes
#   - AZ canonical and AZ HGI cat-STL cells already exist in the Phase-1
#     grid (results/{check2hgi,hgi}/arizona/next_lr1.0e-04_bs1024_ep50_
#     20260427_171{8,24}/), but we re-run all three cells fresh on the same
#     run so per-fold comparisons share the same (StratifiedGroupKFold(42))
#     splits and the same hardware. Pooled has never been generated for AZ.
#   - See `docs/CLAIMS_AND_HYPOTHESES.md §CH19` and
#     `docs/findings/SUBSTRATE_COMPARISON_FINDINGS.md §4`
#     for the AL canonical numbers and protocol this replicates.
#   - The pooled engine is registered: `EmbeddingEngine.CHECK2HGI_POOLED`
#     in `src/configs/paths.py`. train.py accepts `--engine check2hgi_pooled`.

set -euo pipefail

WORKTREE="${WORKTREE:-$(pwd)}"
cd "${WORKTREE}"

export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"

PY="${PY:-python3}"
STATE="arizona"

mkdir -p logs

# Sanity check: AZ canonical Check2HGI prerequisites must exist (we read
# from output/check2hgi/arizona/* to build the pooled variant).
for f in \
    "${OUTPUT_DIR}/check2hgi/${STATE}/embeddings.parquet" \
    "${OUTPUT_DIR}/check2hgi/${STATE}/temp/sequences_next.parquet" \
    "${OUTPUT_DIR}/check2hgi/${STATE}/input/next.parquet" \
    "${OUTPUT_DIR}/hgi/${STATE}/input/next.parquet"
do
    if [ ! -f "$f" ]; then
        echo "FATAL: missing prerequisite: $f" >&2
        echo "Generate via pipelines/embedding/{check2hgi,hgi}.pipe.py + pipelines/create_inputs.pipe.py before running this script." >&2
        exit 1
    fi
done

echo "================================================================"
echo "=== AZ per-visit counterfactual — start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"

# Step 0: build POI-pooled Check2HGI for AZ.
# Mean-pools canonical Check2HGI vectors per placeid across all check-ins,
# applied uniformly to all visits at that POI. Kills per-visit variation
# while preserving Check2HGI's training signal. Writes to
# output/check2hgi_pooled/arizona/{embeddings.parquet, input/next.parquet}.
echo ""
echo "[step 0] Building AZ POI-pooled Check2HGI…"
"${PY}" scripts/probe/build_check2hgi_pooled.py --state "${STATE}"

run_cell() {
    local engine="$1"
    local tag="STL_AZ_${engine}_cat_gru_5f50ep"
    echo ""
    echo "----------------------------------------------------------------"
    echo "[${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "----------------------------------------------------------------"
    "${PY}" -u scripts/train.py \
        --task next \
        --state "${STATE}" \
        --engine "${engine}" \
        --model next_gru \
        --folds 5 \
        --epochs 50 \
        --seed 42 \
        --no-checkpoints \
        2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit $? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

# Three cells, sequential (each is the single training run on its own GPU).
# Order is canonical → pooled → HGI to mirror the §6.1 table presentation.
run_cell check2hgi
run_cell check2hgi_pooled
run_cell hgi

echo ""
echo "================================================================"
echo "=== AZ per-visit counterfactual — done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
echo "Compute per-visit and training-signal components, target a 30 minute total wall on H100"
