#!/usr/bin/env bash
# FL+CA+TX replication of the per-visit counterfactual (paper §6.1, Figure 2).
#
# Purpose
#   The paper currently reports the per-visit counterfactual at AL+AZ (CH19,
#   commits bdc0cf5 + 61b44c3). Two-state replication is descriptive at AZ
#   (no paired Wilcoxon across AZ folds) and the §6.1 figure visualises AL
#   only. This script extends the counterfactual to FL+CA+TX so the §6.1
#   panel can become 5-state replicated and the mechanism claim spans the
#   same five states as the substrate-axis ablation in §5.1.
#
# Reference numbers (paper-canonical, seed=42, 5f × 50ep, matched-head GRU STL):
#   AL  canonical Check2HGI : macro-F1 40.76 ± 1.50
#       POI-pooled Check2HGI: macro-F1 29.57
#       HGI                  : macro-F1 25.26 ± 1.06
#       per-visit  +11.19 pp (~72%)   training-signal  +4.31 pp (~28%)
#   AZ  canonical Check2HGI : macro-F1 43.17 ± 0.28
#       POI-pooled Check2HGI: macro-F1 34.09 ± 0.63
#       HGI                  : macro-F1 28.99 ± 0.51
#       per-visit  +9.08 pp (~64%)    training-signal  +5.10 pp (~36%)
#
# Predictions for FL/CA/TX (will be measured by this script):
#   canonical Check2HGI is in substrate-Table 1(a) at FL=63.43, CA=59.94,
#   TX=60.24; HGI is at FL=34.41, CA=31.13, TX=31.89. Pooled is the only
#   missing cell at each state. Substrate gap (canonical − HGI) is +29.02
#   (FL), +28.81 (CA), +28.34 (TX), so the per-visit share is bounded above
#   by 100% and below by 0%; AL/AZ ran ~64-72%, so a similar share at FL/CA
#   /TX would land pooled in the 35-50 macro-F1 region. We will know once
#   the runs land.
#
# Protocol — matched to AL+AZ exactly:
#   --task next --model next_gru --folds 5 --epochs 50 --seed 42
#   --no-checkpoints (no other CLI flags). user-disjoint StratifiedGroupKFold
#   (seed=42), default batch=1024 (bs1024 in run-dir name), AdamW(1e-4) +
#   OneCycleLR(max=1e-2). Best-epoch selector is train.py's default
#   (val macro-F1, no min-best-epoch floor).
#
#   Each state runs all three cells fresh (canonical / pooled / HGI) so the
#   per-fold comparison shares the exact same StratifiedGroupKFold(42) splits
#   and the same hardware. This mirrors the AZ counterfactual protocol.
#
# Expected runtime (single H100 80 GB, sequential)
#   FL  : ~50 min/cell × 3 = ~2.5 h
#   CA  : ~80 min/cell × 3 = ~4.0 h
#   TX  : ~70 min/cell × 3 = ~3.5 h
#   Total: ~10 H100-hours sequential. This is the upper bound; FL/CA/TX
#   sometimes converge earlier on the per-fold timer. Round 5b A1 estimate
#   was 3-6 H100-hours; the higher number here reflects sequential 9-cell
#   execution rather than parallel.
#
#   Tip: if you have multiple GPUs, fork three copies of this script with
#        STATES=florida / STATES=california / STATES=texas to parallelise.
#
# Expected output paths (auto-determined by train.py)
#   results/check2hgi/<state>/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   results/check2hgi_pooled/<state>/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   results/hgi/<state>/next_lr1.0e-04_bs1024_ep50_<TIMESTAMP>/
#   Each contains summary/full_summary.json + folds/foldN_info.json with
#   diagnostic_best_epochs.next.metrics.f1 (per-fold cat F1 macro).
#
# After this script
#   1. Run scripts/probe/extract_pervisit_perfold.py to extract per-fold
#      cat F1 macro to docs/results/phase1_perfold/
#      mirroring AZ's naming (STATE_check2hgi_cat_gru_5f50ep_<TIMESTAMP>.json
#      etc).
#   2. Render the 5-state §6.1 figure with
#      articles/[BRACIS]_Beyond_Cross_Task/src/figs/render_per_visit_5state.py.
#   3. Update §6.1 mechanism.tex prose to cover all five states + replace
#      the AL-only Figure 2 with the 5-state panel; update the figure
#      caption and the §6.1 closing sentence accordingly.
#   4. (Optional) Run paired Wilcoxon across the FL/CA/TX folds — this
#      converts "five-state replication" into "five-state inferential
#      confirmation" by reaching paired p=0.0312 at the n=5 ceiling each.
#
# Notes
#   - Pooled engine is registered: `EmbeddingEngine.CHECK2HGI_POOLED` in
#     `src/configs/paths.py`. train.py accepts `--engine check2hgi_pooled`.
#     The pooled embeddings are built by `scripts/probe/build_check2hgi_pooled.py`
#     which mean-pools canonical Check2HGI per placeid and writes to
#     output/check2hgi_pooled/<state>/.
#   - Memory note: FL has ~4700 regions, CA has ~8500, TX has ~6500 —
#     larger than AL/AZ but still well within H100 memory at bs=1024.
#     The category task is single-task; no transition prior is loaded.
#     If the GPU is a T4 or A10 instead, set BATCH=512 below or pass
#     --batch-size 512 to train.py.
#   - If a state's canonical or HGI run already exists at seed-42 from the
#     substrate ablation (Phase 1), this script will produce a *fresh*
#     timestamped run anyway — that mirrors the AZ protocol and removes any
#     hardware/version drift question. To skip the redundant cells and
#     reuse Phase-1 numbers, set REUSE_EXISTING=1 in the environment; the
#     script will then only run the pooled cell at each state.

set -euo pipefail

WORKTREE="${WORKTREE:-$(pwd)}"
cd "${WORKTREE}"

export PYTHONPATH="src"
export DATA_ROOT="${DATA_ROOT:-${WORKTREE}/data}"
export OUTPUT_DIR="${OUTPUT_DIR:-${WORKTREE}/output}"

PY="${PY:-python3}"
STATES="${STATES:-florida california texas}"
REUSE_EXISTING="${REUSE_EXISTING:-0}"

mkdir -p logs

echo "================================================================"
echo "=== FL+CA+TX per-visit counterfactual"
echo "=== States       : ${STATES}"
echo "=== Reuse-existing canonical/HGI cells: ${REUSE_EXISTING}"
echo "=== Start        : $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"

run_cell() {
    local state="$1"
    local engine="$2"
    local short_state
    short_state="$(echo "${state}" | tr '[:lower:]' '[:upper:]' | cut -c1-2)"
    local tag="STL_${short_state}_${engine}_cat_gru_5f50ep"
    echo ""
    echo "----------------------------------------------------------------"
    echo "[${tag}] start $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    echo "----------------------------------------------------------------"
    "${PY}" -u scripts/train.py \
        --task next \
        --state "${state}" \
        --engine "${engine}" \
        --model next_gru \
        --folds 5 \
        --epochs 50 \
        --seed 42 \
        --no-checkpoints \
        2>&1 | tee "logs/${tag}.log"
    echo "[${tag}] exit $? at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
}

for STATE in ${STATES}; do
    echo ""
    echo "================================================================"
    echo "=== State: ${STATE}"
    echo "================================================================"

    # Sanity check: substrate prerequisites must exist for this state.
    for f in \
        "${OUTPUT_DIR}/check2hgi/${STATE}/embeddings.parquet" \
        "${OUTPUT_DIR}/check2hgi/${STATE}/temp/sequences_next.parquet" \
        "${OUTPUT_DIR}/check2hgi/${STATE}/input/next.parquet" \
        "${OUTPUT_DIR}/hgi/${STATE}/input/next.parquet"
    do
        if [ ! -f "$f" ]; then
            echo "FATAL: missing prerequisite for ${STATE}: $f" >&2
            echo "Generate via pipelines/embedding/{check2hgi,hgi}.pipe.py + pipelines/create_inputs.pipe.py before running this script." >&2
            exit 1
        fi
    done

    # Step 0: build POI-pooled Check2HGI for this state.
    # Mean-pools canonical Check2HGI vectors per placeid across all check-ins,
    # applied uniformly to all visits at that POI. Kills per-visit variation
    # while preserving Check2HGI's training signal.
    echo ""
    echo "[step 0] Building ${STATE} POI-pooled Check2HGI…"
    "${PY}" scripts/probe/build_check2hgi_pooled.py --state "${STATE}"

    # Three cells, sequential. Order: canonical → pooled → HGI.
    if [ "${REUSE_EXISTING}" = "1" ]; then
        echo ""
        echo "[note] REUSE_EXISTING=1: skipping canonical and HGI cells; running pooled only."
        echo "[note] Make sure Phase-1 canonical and HGI per-fold JSONs exist for ${STATE}."
        run_cell "${STATE}" check2hgi_pooled
    else
        run_cell "${STATE}" check2hgi
        run_cell "${STATE}" check2hgi_pooled
        run_cell "${STATE}" hgi
    fi
done

echo ""
echo "================================================================"
echo "=== FL+CA+TX per-visit counterfactual — done $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. python3 scripts/probe/extract_pervisit_perfold.py --states ${STATES}"
echo "  2. python3 articles/[BRACIS]_Beyond_Cross_Task/src/figs/render_per_visit_5state.py"
echo "  3. Update mechanism.tex §6.1 prose + figure to 5-state coverage."
