#!/usr/bin/env bash
# parallel_sweep_runner.sh — runs ONE variant's full pipeline (regen AL+AZ in
# parallel → rebuild next_region/log_T for both → run MTL B9full AL+AZ in
# parallel → record JSON) inside an isolated tagged output/results dir tree.
#
# Multiple instances of this script can run concurrently AS LONG AS each
# gets a distinct $TAG: env-var OUTPUT_DIR / RESULTS_ROOT redirect every
# IoPaths read+write to the tagged location, so no two instances ever
# touch the same on-disk file.
#
# Usage:
#   parallel_sweep_runner.sh TAG REGEN_CMD_FRAGMENT
# where:
#   TAG               unique slug for this variant (e.g. 't15_v1_warmup5')
#   REGEN_CMD_FRAG    everything after `python <regen_helper>.py --state X`
#                     that the variant-specific regen helper needs. Example:
#                     for T1.5: "docs/infra/a40/regen_emb_t15.py
#                       --scheduler cosine --warmup-pct 0 --weight-decay 0"
# Optional env:
#   N_FOLDS (default 5), EPOCHS (default 50), SEED (default 42), BATCH (default 2048).
#   B9_FLAGS — full MTL invocation extras. Default = canonical B9full (NORTH_STAR).
#   STATES   — space-separated list of states (default "alabama arizona").
#
# Writes:
#   $TAGGED_ROOT/output/check2hgi/{state}/...   (regen, log_T, next_region.parquet)
#   $TAGGED_ROOT/results/check2hgi/{state}/...  (MTL run dir)
#   $RESULT_JSON                                (per-variant summary)

set -uo pipefail

if [ $# -lt 2 ]; then
    echo "usage: $0 TAG 'REGEN_HELPER + ARGS (without --state)'" >&2
    exit 2
fi

TAG=$1
REGEN_CMD=$2

# ── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT=/home/vitor.oliveira/PoiMtlNet
WORKTREE=/home/vitor.oliveira/PoiMtlNet
TAGGED_ROOT=${PROJECT_ROOT}/runs/${TAG}            # all per-variant disk state lives here
LOG_ROOT=${PROJECT_ROOT}/logs
RESULTS_REGISTRY=${PROJECT_ROOT}/docs/results/canonical_improvement

# Per-variant isolated dirs (IoPaths reads OUTPUT_DIR / RESULTS_ROOT at import).
export OUTPUT_DIR=${TAGGED_ROOT}/output
export RESULTS_ROOT=${TAGGED_ROOT}/results
mkdir -p "${OUTPUT_DIR}/check2hgi" "${RESULTS_ROOT}" "${LOG_ROOT}"

# ── Defaults ──────────────────────────────────────────────────────────────
STATES=${STATES:-"alabama arizona"}
N_FOLDS=${N_FOLDS:-5}
EPOCHS=${EPOCHS:-50}
SEED=${SEED:-42}
BATCH=${BATCH:-2048}

# F51 leak-bug guardrail (2026-05-15): refuse N_FOLDS < 2 to prevent the
# trainer's max(2, --folds) clamp from creating a split-structure mismatch
# vs the per-fold log_T built below at exactly N_FOLDS splits. See
# docs/findings/F51_MULTI_SEED_FINDINGS.md §0 + docs/CONCERNS.md C19.
if [ "$N_FOLDS" -lt 2 ]; then
    echo "[parallel_sweep_runner] FATAL: N_FOLDS=$N_FOLDS (<2) would trigger the F51 log_T leak bug." >&2
    echo "                        The trainer uses max(2,--folds) for n_splits, but compute_region_transition.py" >&2
    echo "                        --n-splits N_FOLDS would build at $N_FOLDS splits — mismatch leaks val transitions." >&2
    exit 2
fi
B9_FLAGS=${B9_FLAGS:-"--task mtl --task-set check2hgi_next_region --model mtlnet_crossattn --mtl-loss static_weight --category-weight 0.75 --scheduler cosine --max-lr 3e-3 --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 --cat-head next_gru --reg-head next_getnext_hard --task-a-input-type checkin --task-b-input-type region --no-checkpoints"}
RESULT_JSON=${RESULTS_REGISTRY}/${TAG}.json
TS=$(date +%Y%m%d_%H%M%S)

echo "[$(date +%H:%M:%S)] [$TAG] TAGGED_ROOT=${TAGGED_ROOT}"
echo "[$(date +%H:%M:%S)] [$TAG] OUTPUT_DIR=${OUTPUT_DIR}  RESULTS_ROOT=${RESULTS_ROOT}"

# ── Stage 1: pre-stage canonical preprocessed graph (per-state) ────────────
# The check2hgi graph is the EXPENSIVE part of preprocessing (Delaunay + region
# join). Across α / hygiene variants it does NOT change — only the training
# loss weights or optimizer change. Copy the canonical temp/checkin_graph.pt
# so each variant skips the preprocess step (force_preprocess=False).
for STATE in $STATES; do
    SRC=${PROJECT_ROOT}/output/check2hgi/${STATE}/temp
    DST=${OUTPUT_DIR}/check2hgi/${STATE}/temp
    mkdir -p "$DST"
    if [ ! -f "${DST}/checkin_graph.pt" ]; then
        cp "${SRC}/checkin_graph.pt" "${DST}/checkin_graph.pt" || {
            echo "[$TAG] FAILED to copy canonical graph for $STATE — bailing"; exit 1; }
        cp "${SRC}"/*.parquet "$DST"/ 2>/dev/null || true
        cp "${SRC}/boroughs_area.csv" "$DST"/ 2>/dev/null || true
    fi
done

# ── Stage 2: regen embeddings for all states IN PARALLEL ────────────────────
echo "[$(date +%H:%M:%S)] [$TAG] regen embeddings (parallel, all states)..."
REGEN_PIDS=()
for STATE in $STATES; do
    LOG="${LOG_ROOT}/PSWEEP_REGEN_${TAG}_${STATE}_${TS}.log"
    ( cd "$WORKTREE" && source .venv/bin/activate \
        && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" \
           python ${REGEN_CMD} --state "$STATE" > "$LOG" 2>&1 ) &
    REGEN_PIDS+=("$!")
done
for pid in "${REGEN_PIDS[@]}"; do
    wait "$pid" || { echo "[$TAG] regen pid $pid FAILED"; exit 1; }
done
echo "[$(date +%H:%M:%S)] [$TAG] regen done"

# ── Stage 3: rebuild next_region.parquet + per-fold log_T per state ────────
echo "[$(date +%H:%M:%S)] [$TAG] building next_region.parquet + log_T..."
for STATE in $STATES; do
    ( cd "$WORKTREE" && source .venv/bin/activate \
        && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" \
           python scripts/regenerate_next_region.py --state "$STATE" > /dev/null 2>&1 ) || true
    ( cd "$WORKTREE" && source .venv/bin/activate \
        && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" \
           python scripts/compute_region_transition.py --state "$STATE" --per-fold --n-splits $N_FOLDS --seed $SEED > /dev/null 2>&1 ) || true
done

# ── Stage 4: launch MTL B9full per state IN PARALLEL ──────────────────────
echo "[$(date +%H:%M:%S)] [$TAG] launching MTL (parallel, all states)..."
declare -A MTL_PID
declare -A MTL_FAIL
for STATE in $STATES; do
    LOG="${LOG_ROOT}/PSWEEP_MTL_${TAG}_${STATE}_${TS}.log"
    ( cd "$WORKTREE" && source .venv/bin/activate \
        && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" \
           python scripts/train.py $B9_FLAGS \
               --state "$STATE" --engine check2hgi --seed $SEED \
               --epochs $EPOCHS --folds $N_FOLDS --batch-size $BATCH \
               --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
               > "$LOG" 2>&1 ) &
    MTL_PID[$STATE]=$!
done
# Wait per-state and capture rc; record skip flag per-state instead of crashing.
for STATE in $STATES; do
    wait "${MTL_PID[$STATE]}"
    rc=$?
    if [ $rc -eq 0 ]; then
        MTL_FAIL[$STATE]=0
        echo "[$(date +%H:%M:%S)] [$TAG] MTL $STATE pid ${MTL_PID[$STATE]} rc=0"
    else
        MTL_FAIL[$STATE]=1
        echo "[$(date +%H:%M:%S)] [$TAG] MTL $STATE pid ${MTL_PID[$STATE]} FAILED rc=$rc (will skip in recorder)"
    fi
done

# ── Stage 5: record metrics (uses canonical T1-3_record.py with tagged output) ─
# T1-3_record.py reads embeddings.parquet for the leak probe; point it at the
# tagged dir explicitly via env override. Path inside record script is
# hard-coded to /home/vitor.oliveira/PoiMtlNet/output/... — we have to patch
# that call path. Since we can't edit the record script per-variant, we wrap
# it: stash the canonical canonical paths, symlink tagged → canonical, run
# record, restore.
echo "[$(date +%H:%M:%S)] [$TAG] recording per-state JSON..."
for STATE in $STATES; do
    if [ "${MTL_FAIL[$STATE]:-1}" -ne 0 ]; then
        echo "[$TAG] $STATE skipped (MTL failed)"
        export "RUN_DIR_${STATE}"=""
        continue
    fi
    rd=$(ls -td ${RESULTS_ROOT}/check2hgi/${STATE}/mtlnet_*/ 2>/dev/null | head -1)
    echo "[$TAG] $STATE run_dir=$rd"
    # export per-state run-dir env var for the inline python recorder
    export "RUN_DIR_${STATE}"="$rd"
done
export TAG RESULT_JSON STATES OUTPUT_DIR

# T1-3_record.py:leak_probe is hard-coded to /home/vitor.oliveira/PoiMtlNet/output/check2hgi/{state}/input/next.parquet.
# We compute leak probe inline here to keep the record script untouched, then
# write the JSON in the same schema.
mkdir -p "$(dirname "$RESULT_JSON")"
( cd "$WORKTREE" && source .venv/bin/activate && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" python - <<'PYEOF'
import json, os, sys
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold

TAG = os.environ["TAG"]
RESULT_JSON = Path(os.environ["RESULT_JSON"])
OUTPUT_DIR = Path(os.environ["OUTPUT_DIR"])
STATES_RAW = os.environ.get("STATES", "alabama arizona").split()

def leak_probe(state: str) -> dict:
    p = OUTPUT_DIR / "check2hgi" / state / "input" / "next.parquet"
    if not p.exists():
        return {"error": f"missing {p}"}
    df = pd.read_parquet(p)
    last_cols = [str(i) for i in range(8 * 64, 9 * 64)]
    X = df[last_cols].to_numpy(np.float32)
    y_raw = df["next_category"]
    y = pd.Categorical(y_raw).codes if y_raw.dtype == object else y_raw.to_numpy()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1s = []
    for tr, va in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[tr], y[tr])
        f1s.append(f1_score(y[va], clf.predict(X[va]), average="macro", zero_division=0))
    return {"f1_mean_pct": float(np.mean(f1s) * 100), "f1_std_pct": float(np.std(f1s, ddof=1) * 100)}

def gather_run(run_dir: Path, n_folds: int = 5) -> dict:
    cat_f1, reg_top10 = [], []
    for fold in range(1, n_folds + 1):
        p = run_dir / "folds" / f"fold{fold}_info.json"
        info = json.loads(p.read_text())
        cat_f1.append(float(info["primary_checkpoint"]["task_metrics"]["next_category"]["f1"]))
        reg_top10.append(float(info["diagnostic_best_epochs"]["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]))
    return {
        "cat_f1_per_fold": cat_f1, "reg_top10_per_fold": reg_top10,
        "cat_f1_mean_pct": float(np.mean(cat_f1) * 100), "cat_f1_std_pct": float(np.std(cat_f1, ddof=1) * 100),
        "reg_top10_mean_pct": float(np.mean(reg_top10) * 100), "reg_top10_std_pct": float(np.std(reg_top10, ddof=1) * 100),
    }

record = {"tag": TAG, "tagged_root": str(OUTPUT_DIR.parent)}
for state in STATES_RAW:
    rd_env = os.environ.get(f"RUN_DIR_{state}")
    if rd_env:
        rd = Path(rd_env.rstrip("/"))
        record[state[:2]] = {"run_dir": str(rd), **gather_run(rd), "leak_probe": leak_probe(state)}
    else:
        record[state[:2]] = {"error": f"no RUN_DIR for {state}"}

RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
RESULT_JSON.write_text(json.dumps(record, indent=2))
print(f"[record] wrote {RESULT_JSON}")
for state in STATES_RAW:
    e = record.get(state[:2], {})
    if "cat_f1_mean_pct" in e:
        print(f"  {state[:2]}: cat={e['cat_f1_mean_pct']:.2f}±{e['cat_f1_std_pct']:.2f}  reg={e['reg_top10_mean_pct']:.2f}±{e['reg_top10_std_pct']:.2f}  leak={e['leak_probe'].get('f1_mean_pct','?'):.2f}")
PYEOF
)
RC=$?

echo "[$(date +%H:%M:%S)] [$TAG] DONE (record_rc=$RC). JSON=${RESULT_JSON}"

# Optional disk cleanup (set CLEANUP_AFTER=1 in env to enable).
if [ "${CLEANUP_AFTER:-0}" = "1" ] && [ $RC -eq 0 ]; then
    echo "[$(date +%H:%M:%S)] [$TAG] CLEANUP_AFTER=1, removing ${TAGGED_ROOT}"
    rm -rf "$TAGGED_ROOT"
fi
exit $RC
