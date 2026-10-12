#!/usr/bin/env bash
# Deferred TX STL cat-ceiling: wait for the TX MTL run to free RAM, then run the next_gru STL
# ceiling SOLO (co-scheduling OOM-killed it, EXIT=137), score, append to TX_CELL.md, commit+push.
# Fully autonomous — survives session death. One-shot.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
MTL_LOG=logs/tx_s0_ep50.log
RUN_LOG=logs/tx_cat_ceiling_solo.log
DEST=docs/results/closing_data/h100
REG_CEIL=64.96
mkdir -p "$HOME/.inductor_cache_tx_cat"

# skip if the parallel run already produced the cat-ceiling artefact
[ -f "$DEST/texas_s0_stl_cat_ceiling.json" ] && { echo "[tx-cat-deferred] cat ceiling already done (parallel run) — skip"; exit 0; }

echo "[tx-cat-deferred] waiting for TX MTL to finish (frees ~56 GB)..."
until grep -q 'EXIT=' "$MTL_LOG" 2>/dev/null; do sleep 60; done
echo "[tx-cat-deferred] TX MTL done — waiting for RAM to free"
sleep 60
for i in $(seq 1 40); do
  av=$(python3 -c "import psutil;print(int(psutil.virtual_memory().available/1024**3))" 2>/dev/null || echo 0)
  echo "[tx-cat-deferred] avail=${av}G"
  [ "${av:-0}" -gt 80 ] && break
  sleep 30
done

echo "[tx-cat-deferred] launching cat ceiling (next_gru STL, dk_ovl, seed0, 5f) SOLO"
{ echo "WALLCLOCK_START=$(date +%s)"
  MTL_CHUNK_VAL_METRIC=1 PYTHONPATH=src TORCHINDUCTOR_CACHE_DIR="$HOME/.inductor_cache_tx_cat" \
  python scripts/train.py --task next --state texas --engine check2hgi_dk_ovl \
    --model next_gru --folds 5 --epochs 50 --seed 0 --batch-size 2048 --max-lr 3e-3 \
    --gradient-accumulation-steps 1 --no-checkpoints --tf32
  echo "EXIT=$? WALLCLOCK_END=$(date +%s)"; } > "$RUN_LOG" 2>&1

RD=$(ls -dt results/check2hgi_dk_ovl/texas/next_* 2>/dev/null | head -1)
echo "[tx-cat-deferred] scoring $RD"
PYTHONPATH=src python scripts/closing_data/score_stl_cat_ceiling.py "$RD" --tag texas_cat_ceiling >/tmp/tx_cat_solo_score.txt 2>&1 || true
cat /tmp/tx_cat_solo_score.txt
if [ -f "$RD/stl_cat_ceiling_score.json" ]; then
  cp "$RD/stl_cat_ceiling_score.json" "$DEST/texas_s0_stl_cat_ceiling.json"
  python3 - "$DEST/texas_s0_stl_cat_ceiling.json" "$REG_CEIL" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); regc = float(sys.argv[2])
cm, cs, n = d["cat_macro_f1_mean"], d["cat_macro_f1_std"], len(d["cat_per_fold"])
block = f"""

## TX STL ceilings — RESULT (scored {n}f, solo post-MTL)
- **cat macro-F1 ceiling = {cm:.4f} ± {cs:.4f}** (next_gru STL, dk_ovl, seed0; per-fold {d['cat_per_fold']}, epochs {d['cat_best_epochs']}).
- reg FULL top10 ceiling = {regc:.2f} (a40 fp32).
- Compare against the TX MTL running-mean in the per-fold table above (MTL beats cat ceiling if mean > {cm:.2f}).
"""
open("docs/studies/closing_data/TX_CELL.md", "a").write(block)
print(f"[tx-cat-deferred] cat ceiling = {cm:.2f} ± {cs:.2f} (n={n})")
PY
fi
git add docs/studies/closing_data/TX_CELL.md "$DEST/texas_s0_stl_cat_ceiling.json" 2>/dev/null || true
git commit -m "board-h100: TX STL cat ceiling scored (next_gru, dk_ovl, seed0, solo post-MTL) — TX ceilings complete

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017bpM3kYznPgop7ySjMPkGF" >/dev/null 2>&1 || true
for try in 1 2 3 4; do
  git pull --rebase origin "$BRANCH" >/tmp/tx_catd_pull.txt 2>&1 || true
  if git push origin "$BRANCH" >/tmp/tx_catd_push.txt 2>&1; then echo "[tx-cat-deferred] pushed"; break; fi
  echo "[tx-cat-deferred] push retry $try"; sleep 10
done
echo "[tx-cat-deferred] done ($(date -u +%H:%M:%S)Z)"
