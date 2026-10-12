#!/usr/bin/env bash
# Parallel TX STL cat-ceiling: launch ASAP alongside the MTL resume, but SAFELY.
# The earlier co-scheduled attempt OOM-died on the on-the-fly 5-fold split spike. Fix:
#   (1) wait until the MTL resume is PAST its construction peak (in training),
#   (2) FREEZE the next-task folds (precompute split → no runtime spike),
#   (3) run next_gru STL (now ~18GB, fits with MTL's ~56GB on the 108GB box),
#   (4) a RAM-watcher kills THIS cat-ceiling (never the MTL) if avail<5GB,
#   (5) score + append to TX_CELL.md + commit+push. Autonomous; survives session death.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
MTL_LOG=logs/tx_resume.log
RUN_LOG=logs/tx_cat_ceiling_solo.log
DEST=docs/results/closing_data/h100
REG_CEIL=64.96
ART="$DEST/texas_s0_stl_cat_ceiling.json"
mkdir -p "$HOME/.inductor_cache_tx_cat"

# already done? skip.
[ -f "$ART" ] && { echo "[tx-cat-par] cat ceiling artefact already exists — skip"; exit 0; }

echo "[tx-cat-par] waiting for MTL resume to reach training (past construction)..."
until tr '\r' '\n' < "$MTL_LOG" 2>/dev/null | grep -qE 'Epoch [0-9]+/50'; do
  grep -q 'EXIT=' "$MTL_LOG" 2>/dev/null && { echo "[tx-cat-par] MTL already finished"; break; }
  sleep 20
done
echo "[tx-cat-par] MTL in training — waiting 40s for construction temporaries to free"
sleep 40

echo "[tx-cat-par] freezing next-task folds (precompute split → avoids OOM spike)"
PYTHONPATH=src python scripts/study/freeze_folds.py --state texas --engine check2hgi_dk_ovl --task next >/tmp/tx_freeze_next.txt 2>&1 || echo "[tx-cat-par] freeze warn (continuing)"

# RAM-watcher: protect the MTL resume — kill THIS cat-ceiling (task next) if avail<5GB twice
nohup bash -c '
  low=0
  while true; do
    av=$(python3 -c "import psutil;print(int(psutil.virtual_memory().available/1024**3))" 2>/dev/null||echo 99)
    [ "${av:-99}" -lt 5 ] && low=$((low+1)) || low=0
    if [ "$low" -ge 2 ]; then
      for p in $(pgrep -x python); do cl=$(tr "\0" " " < /proc/$p/cmdline 2>/dev/null); echo "$cl"|grep -q "task next" && echo "$cl"|grep -q texas && { echo "[ramwatch-cat] avail=${av}G KILL cat-ceiling pid=$p (protect MTL)"; kill -9 $p; }; done
      break
    fi
    grep -q "EXIT=" logs/tx_cat_ceiling_solo.log 2>/dev/null && break
    sleep 8
  done' > logs/tx_cat_ramwatch.log 2>&1 &

echo "[tx-cat-par] launching cat ceiling (next_gru STL, dk_ovl, seed0, 5f)"
{ echo "WALLCLOCK_START=$(date +%s)"
  MTL_CHUNK_VAL_METRIC=1 PYTHONPATH=src TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_tx_cat" \
  python scripts/train.py --task next --state texas --engine check2hgi_dk_ovl \
    --model next_gru --folds 5 --epochs 50 --seed 0 --batch-size 2048 --max-lr 3e-3 \
    --gradient-accumulation-steps 1 --no-checkpoints --compile --tf32
  echo "EXIT=$? WALLCLOCK_END=$(date +%s)"; } > "$RUN_LOG" 2>&1

RD=$(ls -dt results/check2hgi_dk_ovl/texas/next_* 2>/dev/null | head -1)
nfold=$(ls "$RD"/metrics/fold*_next_category_val.csv 2>/dev/null | wc -l)
echo "[tx-cat-par] cat-ceiling ended (folds=$nfold) — scoring $RD"
PYTHONPATH=src python scripts/closing_data/score_stl_cat_ceiling.py "$RD" --tag texas_cat_ceiling >/tmp/tx_cat_par_score.txt 2>&1 || true
cat /tmp/tx_cat_par_score.txt
if [ -f "$RD/stl_cat_ceiling_score.json" ] && [ "$nfold" -ge 5 ]; then
  cp "$RD/stl_cat_ceiling_score.json" "$ART"
  python3 - "$ART" "$REG_CEIL" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); regc = float(sys.argv[2])
cm, cs, n = d["cat_macro_f1_mean"], d["cat_macro_f1_std"], len(d["cat_per_fold"])
block = f"""

## TX STL ceilings — RESULT (scored {n}f, parallel w/ MTL resume)
- **cat macro-F1 ceiling = {cm:.4f} ± {cs:.4f}** (next_gru STL, dk_ovl, seed0; per-fold {d['cat_per_fold']}, epochs {d['cat_best_epochs']}).
- reg FULL top10 ceiling = {regc:.2f} (a40 fp32).
- Compare to the TX MTL running-mean (table above): MTL cat beats this ceiling if mean > {cm:.2f}.
"""
open("docs/studies/closing_data/TX_CELL.md", "a").write(block)
print(f"[tx-cat-par] cat ceiling = {cm:.2f} +/- {cs:.2f} (n={n})")
PY
  git add docs/studies/closing_data/TX_CELL.md "$ART" 2>/dev/null || true
  git commit -m "board-h100: TX STL cat ceiling scored (next_gru, dk_ovl, seed0) — TX ceilings complete

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017bpM3kYznPgop7ySjMPkGF" >/dev/null 2>&1 || true
  for try in 1 2 3 4; do
    git pull --rebase origin "$BRANCH" >/tmp/tx_catpar_pull.txt 2>&1 || true
    if git push origin "$BRANCH" >/tmp/tx_catpar_push.txt 2>&1; then echo "[tx-cat-par] pushed"; break; fi
    sleep 10
  done
else
  echo "[tx-cat-par] cat ceiling incomplete (folds=$nfold) — likely RAM-killed; deferred fallback (post-MTL) will retry"
fi
echo "[tx-cat-par] done ($(date -u +%H:%M:%S)Z)"
