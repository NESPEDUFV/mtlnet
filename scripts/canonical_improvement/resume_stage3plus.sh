#!/bin/bash
# Resume a parallel_sweep_runner from stage 3 (next_region + log_T) onwards,
# assuming the embeddings are already in <OUTPUT_DIR>/check2hgi/{state}/.
#
# Usage:
#   TAG=<tag> SEED=<seed> STATES="alabama arizona" \
#     bash docs/infra/a40/resume_stage3plus.sh
#
# Recovery harness for the 2026-05-15 19:35 incident: bash mid-flight
# re-read corrupted parallel_sweep_runner.sh when the file was hot-cp'd
# during stage 2 (regen completed before crash; embeddings survived).
# The sandboxes at runs/<TAG>/ have valid encoders; we just need stages 3-5.

set -e

if [ -z "$TAG" ] || [ -z "$SEED" ] || [ -z "$STATES" ]; then
    echo "Usage: TAG=<tag> SEED=<seed> STATES='alabama arizona' bash $0" >&2
    exit 2
fi

PROJECT_ROOT=/home/vitor.oliveira/PoiMtlNet
WORKTREE=/home/vitor.oliveira/worktree-check2hgi-canonical-improve
TAGGED_ROOT=${PROJECT_ROOT}/runs/${TAG}
OUTPUT_DIR=${TAGGED_ROOT}/output
RESULTS_ROOT=${TAGGED_ROOT}/results
RESULT_JSON=${PROJECT_ROOT}/docs/results/canonical_improvement/${TAG}.json
LOG_ROOT=${PROJECT_ROOT}/logs
TS=$(date +%Y%m%d_%H%M%S)
N_FOLDS=5
EPOCHS=50
BATCH=2048

B9_FLAGS="--task mtl --task-set check2hgi_next_region --model mtlnet_crossattn \
  --mtl-loss static_weight --category-weight 0.75 \
  --scheduler cosine --max-lr 3e-3 \
  --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3 \
  --alternating-optimizer-step --alpha-no-weight-decay --min-best-epoch 5 \
  --cat-head next_gru --reg-head next_getnext_hard \
  --task-a-input-type checkin --task-b-input-type region --no-checkpoints"

echo "[$(date +%H:%M:%S)] [$TAG] resume from stage 3"
echo "[$(date +%H:%M:%S)] [$TAG] TAGGED_ROOT=${TAGGED_ROOT}"
echo "[$(date +%H:%M:%S)] [$TAG] STATES=${STATES}  SEED=${SEED}"

# Sanity: embeddings.parquet must exist for every state.
for STATE in $STATES; do
    f=${OUTPUT_DIR}/check2hgi/${STATE}/embeddings.parquet
    if [ ! -f "$f" ]; then
        echo "[$TAG] FATAL: missing $f — cannot resume; re-run regen first" >&2
        exit 3
    fi
done

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

# ── Stage 4: MTL B9 per state in parallel ──────────────────────────────────
echo "[$(date +%H:%M:%S)] [$TAG] launching MTL (parallel, all states)..."
declare -A MTL_PID
declare -A MTL_FAIL
for STATE in $STATES; do
    LOG="${LOG_ROOT}/RESUME_MTL_${TAG}_${STATE}_${TS}.log"
    ( cd "$WORKTREE" && source .venv/bin/activate \
        && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" \
           python scripts/train.py $B9_FLAGS \
               --state "$STATE" --engine check2hgi --seed $SEED \
               --epochs $EPOCHS --folds $N_FOLDS --batch-size $BATCH \
               --per-fold-transition-dir "${OUTPUT_DIR}/check2hgi/${STATE}" \
               > "$LOG" 2>&1 ) &
    MTL_PID[$STATE]=$!
done
for STATE in $STATES; do
    wait "${MTL_PID[$STATE]}"
    rc=$?
    if [ $rc -eq 0 ]; then
        MTL_FAIL[$STATE]=0
        echo "[$(date +%H:%M:%S)] [$TAG] MTL $STATE pid ${MTL_PID[$STATE]} rc=0"
    else
        MTL_FAIL[$STATE]=1
        echo "[$(date +%H:%M:%S)] [$TAG] MTL $STATE pid ${MTL_PID[$STATE]} FAILED rc=$rc"
    fi
done

# ── Stage 5: record per-state JSON (inline python; same schema as runner) ──
echo "[$(date +%H:%M:%S)] [$TAG] recording per-state JSON..."
for STATE in $STATES; do
    if [ "${MTL_FAIL[$STATE]:-1}" -ne 0 ]; then
        echo "[$TAG] $STATE skipped (MTL failed)"
        export "RUN_DIR_${STATE}"=""
        continue
    fi
    rd=$(ls -td ${RESULTS_ROOT}/check2hgi/${STATE}/mtlnet_*/ 2>/dev/null | head -1)
    echo "[$TAG] $STATE run_dir=$rd"
    export "RUN_DIR_${STATE}"="$rd"
done
export TAG RESULT_JSON STATES OUTPUT_DIR

mkdir -p "$(dirname "$RESULT_JSON")"
( cd "$WORKTREE" && source .venv/bin/activate && OUTPUT_DIR="$OUTPUT_DIR" RESULTS_ROOT="$RESULTS_ROOT" python - <<'PYEOF'
import json, os
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

def leak_probe(state):
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

def gather_run(run_dir, n_folds=5):
    cat_f1, reg_top10 = [], []
    for fold in range(1, n_folds + 1):
        info = json.loads((run_dir / "folds" / f"fold{fold}_info.json").read_text())
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
        print(f"  {state}: cat={e['cat_f1_mean_pct']:.2f}±{e['cat_f1_std_pct']:.2f}  "
              f"reg={e['reg_top10_mean_pct']:.2f}±{e['reg_top10_std_pct']:.2f}  "
              f"leak={e['leak_probe'].get('f1_mean_pct', float('nan')):.2f}")
PYEOF
)
record_rc=$?
echo "[$(date +%H:%M:%S)] [$TAG] DONE (record_rc=$record_rc). JSON=$RESULT_JSON"
if [ "${CLEANUP_AFTER:-0}" = "1" ] && [ "$record_rc" = "0" ]; then
    echo "[$(date +%H:%M:%S)] [$TAG] CLEANUP_AFTER=1, removing $TAGGED_ROOT"
    rm -rf "$TAGGED_ROOT"
fi
