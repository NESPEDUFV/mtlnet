#!/usr/bin/env bash
# Task D CTLE-SC @ FL — PARALLEL: 5 single-fold compares, each in an ISOLATED output tree
# (OUTPUT_DIR=output_ctle_f{f}, --only-fold f), so they don't clobber the shared check2hgi_ctle
# engine dir. Leak-safe: each fold keeps its own cell (s0_f{f}) + split + log_T. Then aggregate
# the 5 per-fold JSONs into florida_ctle.json. Cuts the ~2.5h sequential run to ~1 fold's wall.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
ROOT="$PWD"
export PYTHONPATH=src DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 MTL_RAM_HEADROOM_GB=2
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export BASELINE_PY="$(which python)"

echo "=== [Task D parallel] launching 5 isolated single-fold compares $(date -u) ==="
pids=()
for f in 0 1 2 3 4; do
  OD="$ROOT/output_ctle_f$f"
  mkdir -p "$OD"
  ln -sfn "$ROOT/output/check2hgi" "$OD/check2hgi"   # shared canonical substrate (read-only)
  env OUTPUT_DIR="$OD" PYTHONPATH=src DISABLE_AMP=1 MTL_DISABLE_AMP=1 MTL_CHUNK_VAL_METRIC=1 \
      MTL_RAM_HEADROOM_GB=2 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True BASELINE_PY="$(which python)" \
    python scripts/closing_data/mac_baseline_compare.py --state florida --baseline ctle \
      --cells-root "$ROOT/output" --only-fold "$f" --heads cat reg \
      > "logs/taskD_par_f$f.log" 2>&1 &
  pids+=($!)
  echo "  fold $f -> PID $! (OUTPUT_DIR=$OD)"
done

echo "=== [Task D parallel] waiting for 5 folds ==="
fail=0
for p in "${pids[@]}"; do wait "$p" || fail=1; done
echo "=== [Task D parallel] folds done (fail=$fail) $(date -u) ==="

echo "=== [Task D parallel] aggregate per-fold JSONs -> florida_ctle.json ==="
python - <<'PY'
import json, statistics as st
from pathlib import Path
base = Path("docs/results/closing_data/baseline_compare")
recs = []
for f in range(5):
    p = base / f"florida_ctle_f{f}.json"
    if not p.exists():
        print(f"WARN missing {p}"); continue
    d = json.load(open(p))
    recs += d.get("per_fold", [])
recs.sort(key=lambda r: r["fold"])
out = {"state":"florida","baseline":"ctle","engine":"check2hgi_ctle",
       "note":"CTLE-SC (frozen per-fold leak-safe CTLE substrate) under matched heads, dk_ovl base, "
              "checkin-modality reg. Built via 5 parallel isolated-OUTPUT_DIR single-fold runs.",
       "per_fold": recs}
for key in ("macro_f1","top10_acc","mrr"):
    vals=[r[key] for r in recs if key in r]
    if vals:
        out[f"{key}_mean"]=round(st.mean(vals),3)
        out[f"{key}_std"]=round(st.stdev(vals),3) if len(vals)>1 else 0.0
json.dump(out, open(base/"florida_ctle.json","w"), indent=2)
print("WROTE florida_ctle.json  cat_mean=%s reg_mean=%s n=%d"%(out.get("macro_f1_mean"),out.get("top10_acc_mean"),len(recs)))
PY
echo "=== [Task D parallel] COMPLETE $(date -u) ==="
