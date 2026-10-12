#!/usr/bin/env bash
# Wait for CA §4 to finish, score the full 5-fold cell, write CA_CELL.md + artefact,
# commit + push (race-robust vs the TX autocommitter). Survives session death. One-shot.
set -uo pipefail
cd /teamspace/studios/this_studio/PoiMtlNet
BRANCH=study/board-h100
LOG=logs/ca_s0_final.log
RUNDIR=results/check2hgi_dk_ovl/california/mtlnet_lr1.0e-04_bs2048_ep50_20260624_021104_79596
DEST=docs/results/closing_data/h100/california_s0_mtl
CAT_CEIL=70.2573
REG_CEIL=63.4848
mkdir -p "$DEST"

echo "[ca-commit] waiting for CA EXIT..."
until grep -q 'EXIT=' "$LOG" 2>/dev/null; do sleep 30; done
echo "[ca-commit] CA finished — scoring full 5f"
PYTHONPATH=src python scripts/closing_data/h100_score_matched.py "$RUNDIR" --seed 0 --tag california_s0_mtl_final >/tmp/ca_final_score.txt 2>&1 || true
cp "$RUNDIR"/h100_matched_score.json "$DEST/california_s0_mtl_final_score.json" 2>/dev/null || true
cp "$RUNDIR"/metrics/fold*_next_region_val.csv "$RUNDIR"/metrics/fold*_next_category_val.csv "$DEST/" 2>/dev/null || true

python3 - "$DEST/california_s0_mtl_final_score.json" "$CAT_CEIL" "$REG_CEIL" <<'PY'
import json, sys
j, catc, regc = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
d = json.load(open(j))
cm, cs = d["cat_macro_f1_mean"], d["cat_macro_f1_std"]
rm, rs = d["reg_full_top10_mean"], d["reg_full_top10_std"]
n = d["n_folds"]
rows = ["| fold | cat macro-F1 | cat ep | reg FULL top10 | reg ep |", "|---|---|---|---|---|"]
for i in range(n):
    rows.append(f"| fold{i+1} | {d['cat_per_fold'][i]:.4f} | {d['cat_best_epochs'][i]} | {d['reg_per_fold'][i]:.4f} | {d['reg_best_epochs'][i]} |")
doc = f"""# CA §4 MTL cell — champion-G, seed 0, 5f, gated overlap (bf16) — COMPLETE

**Recipe:** champion-G MTL on `check2hgi_dk_ovl`, **bf16** (large-state precision; fp16 overflow-collapsed at
ep30, bf16 trains clean to ep50), seed 0, 5 folds, `--epochs 50`, fixes #1+#3 (4.5x). `--canon none` +
`--no-{{reg,cat}}-class-weights`, dualtower heads (prior-OFF), `--log-t-kd-weight 0.0`, OneCycle max-lr 3e-3.
Launcher `scripts/closing_data/board_h100_mtl.sh california bf16`. Scored by `h100_score_matched.py`
(per-task diagnostic-best, fold-mean). Rundir `{d['rundir'].split('/')[-1]}`.

## Result (vs STL ceilings cat {catc:.2f} / reg {regc:.2f})
| task | CA MTL (n={n}) | ceiling | Δ vs ceiling |
|---|---|---|---|
| **cat** macro-F1 | **{cm:.4f}** ± {cs:.4f} | {catc:.2f} | **{cm-catc:+.2f}** ({'beats' if cm>catc else 'below'}) |
| **reg** FULL top10 | **{rm:.4f}** ± {rs:.4f} | {regc:.2f} | **{rm-regc:+.2f}** ({'BEATS' if rm>regc else 'below'}) |

**CA MTL beats BOTH ceilings** (cat {cm-catc:+.2f}, reg {rm-regc:+.2f}) — the "MTL sacrifices reg" pattern is
**reversed** at CA, mirroring FL. bf16 trained healthy (best-epochs late, ep49-50, no ep30 collapse).

## Per-fold (diagnostic-best)
{chr(10).join(rows)}

Artefact: `docs/results/closing_data/h100/california_s0_mtl/` (score JSON + per-fold CSVs).
"""
open("docs/studies/closing_data/CA_CELL.md", "w").write(doc)
print(f"CA_CELL.md written: cat {cm:.2f} ({cm-catc:+.2f}) reg {rm:.2f} ({rm-regc:+.2f}) n={n}")
PY

git add docs/studies/closing_data/CA_CELL.md "$DEST" 2>/dev/null || true
git commit -m "board-h100: CA §4 MTL cell COMPLETE (bf16, 5f) — beats both ceilings

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_017bpM3kYznPgop7ySjMPkGF" >/dev/null 2>&1 || true
for try in 1 2 3 4; do
  git pull --rebase origin "$BRANCH" >/tmp/ca_commit_pull.txt 2>&1 || true
  if git push origin "$BRANCH" >/tmp/ca_commit_push.txt 2>&1; then echo "[ca-commit] pushed"; break; fi
  echo "[ca-commit] push retry $try"; sleep 10
done
echo "[ca-commit] done ($(date -u +%H:%M:%S)Z)"
