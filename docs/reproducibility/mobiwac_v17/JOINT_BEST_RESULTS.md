# JOINT_BEST_RESULTS — the deployable single-checkpoint numbers for Table 3

> **Convention discipline (read once).** Every number here is one of two conventions, always named:
> **diag-best** = per-task diagnostic-best (cat at its F1-best epoch, reg at its Acc@10-best epoch — *two*
> epochs/fold; the currently-reported Table 3). **joint-best (deploy)** = the single saved checkpoint, both
> heads read at the `geom_simple = sqrt(cat_macroF1 · reg_top10_acc_indist)`-selected epoch (`min_best_epoch=0`).
> Selection logic SSOT: `src/tracking/scoring.py`; scorer `src/tracking/score_joint_best.py`.
> All cells are **v17 on `check2hgi_dk_ovl`, fp32** — the same runs as Table 3, re-read at one epoch instead of two.

## Headline

**The deployable single checkpoint reproduces the reported Table 3 to within ≤ 0.06 pp (category) and ≤ 0.11 pp
(region) on every one of the six datasets — the largest deviations are 0.051 pp (category) and 0.107 pp
(region), both at AZ. No verdict changes.** Category still beats the dedicated ceiling
everywhere (+5.3 … +9.4); region still beats at Istanbul/FL/TX/CA and stays a within-2-pp match at AL/AZ. The
diag-best cells are, in practice, exactly what one served model delivers — the diag/joint distinction is
numerically negligible for these well-converged v17 runs (every joint epoch lands late, 34–50 of 50).

## The corrected table (diag-best vs joint-best, side by side)

Category = macro-F1, region = Acc@10 (FULL = top10_acc_indist·(1−ood_frac)). "Dedicated" = the n=20 best-vs-best
single-task ceiling (`CEILINGS_N20_FINAL.md`, unchanged). n=20 = 4 seeds {0,1,7,100}×5f (± cross-seed sd).
✅ **CA/TX are now n=20 joint-best too — task T6 DONE 2026-07-13** (`score_joint_best.py` on the 8 A1/seed-0
rundirs → `joint_best_score.json` sidecars). The joint-best ≈ diag-best (Δ joint−diag ≤ 0.006 pp: CA cat −0.006 /
reg −0.003, TX cat −0.000 / reg −0.003), so **no cell moved** and every CA/TX verdict (beats cat + reg) holds at
the single-checkpoint joint-best. A1 (the GPU n=20 top-up) completed 2026-07-11 on the A40.

### Next-category (macro-F1)
| Dataset | Regions | Dedicated | Joint **diag-best** | Joint **joint-best (deploy)** | Δdeploy−diag |
|---|---:|---:|---:|---:|---:|
| Istanbul | 520 | 54.74 | 63.33 ±0.02 | **63.32 ±0.02** | −0.01 |
| AL | 1,109 | 56.82 | 64.54 ±0.10 | **64.51 ±0.09** | −0.04 |
| AZ | 1,547 | 56.43 | 65.84 ±0.02 | **65.79 ±0.02** | −0.05 |
| FL | 4,703 | 74.51 | 79.85 ±0.03 | **79.84 ±0.02** | −0.01 |
| TX | 6,553 | 69.79 | 77.239 ±0.014 | **77.239 ±0.013** | −0.00 |
| CA | 8,501 | 70.60 | 77.052 ±0.006 | **77.046 ±0.005** | −0.01 |

### Next-region (Acc@10)
| Dataset | Regions | Dedicated | Joint **diag-best** | Joint **joint-best (deploy)** | Δdeploy−diag |
|---|---:|---:|---:|---:|---:|
| Istanbul | 520 | 75.16 | 75.44 ±0.04 | **75.35 ±0.04** | −0.09 |
| AL | 1,109 | 70.11 | 69.80 ±0.05 | **69.70 ±0.09** | −0.11 |
| AZ | 1,547 | 59.46 | 59.56 ±0.05 | **59.46 ±0.04** | −0.11 |
| FL | 4,703 | 76.70 | 77.42 ±0.03 | **77.41 ±0.02** | −0.01 |
| TX | 6,553 | 64.95 | 67.062 ±0.007 | **67.059 ±0.008** | −0.00 |
| CA | 8,501 | 63.49 | 65.693 ±0.017 | **65.690 ±0.019** | −0.00 |

## Δ vs the dedicated ceiling — does the verdict change?

| Dataset | Δcat diag | Δcat **deploy** | verdict | Δreg diag | Δreg **deploy** | verdict |
|---|---:|---:|---|---:|---:|---|
| Istanbul | +8.59 | **+8.58** | beats | +0.28 | **+0.19** | beats (thinner) |
| AL | +7.72 | **+7.69** | beats | −0.31 | **−0.41** | matches (≪2 pp) |
| AZ | +9.40 † | **+9.35** | beats | +0.10 | **−0.00** | matches |
| FL | +5.34 | **+5.33** | beats | +0.72 | **+0.71** | beats |
| TX | +7.45 | **+7.45** | beats | +2.11 | **+2.11** | beats |
| CA | +6.45 | **+6.45** | beats | +2.20 | **+2.20** | beats |

† AZ diag Δcat: **+9.40** is the paper/board value (from the rounded 65.83 MTL cell, `CEILINGS_N20_FINAL.md`);
the full-precision Δ from these cells (65.835 − 56.43) is **+9.41**, which is what `score_all.py` / `j1_results.json`
print. Same 0.01-pp rounding wobble as the paper's own prose. The AZ cat ceiling itself carries a pending 2-seed
top-up that could raise it to ~57.0 (Δcat → ~+8.8) — a live paper caveat, unrelated to joint-best.

**Every Table-3 verdict is preserved under the deployable convention:**
- **Category — beats at all six** (+5.33 … +9.35). The joint checkpoint costs ≤ 0.051 pp of category vs diag-best.
- **Region — beats at Istanbul / FL / TX / CA; matches (TOST, ±2 pp) at AL / AZ.** Direction unchanged everywhere.

Two cells to keep honest (both still on the correct side of their claim):
1. **Istanbul region** thins from +0.28 to **+0.19** (still a positive point estimate; still "beats"). This is
   the single most margin-sensitive cell. The independent audit went to the per-fold pairs: the joint-best MTL reg
   still beats the STL ceiling in **20/20 folds** (min +0.074, mean +0.194) — so a formal Wilcoxon/90%-CI would
   still reject. The camera-ready superiority stat should be re-run on the joint-best per-fold pairs (task **T7**);
   the *direction* is preserved and per-fold-robust.
2. **AZ region** moves +0.10 → **−0.00** — but AZ was always a *match*, never a beat (the paper never bolds it),
   so the claim is unchanged. **AL region** moves −0.31 → **−0.41**: the J1 runbook flagged AL as the tail risk
   (a legacy smoke run once saw −1.16); the actual v17 joint-best drop is **−0.11 pp**, landing at −0.41 —
   **nowhere near the −2 pp non-inferiority bound.** The tail risk did not materialize.

## Audit — three parity gates (all pass)

| Gate | What it proves | Result |
|---|---|---|
| **A · diag-best parity** | scorer's diag-best re-derivation == each rundir's committed `a40_matched_score.json` | **18/18 exact** |
| **B · joint-epoch fidelity** | scorer's `e*` == training's `folds/foldN_info.json → primary_checkpoint.epoch` (+1 for 1-based-CSV vs 0-based-loop) | **90/90 folds** |
| **C · paper parity** | aggregated diag-best cell == paper `tbl3_results.tex` | **6/6 exact to 2 dp** |

Gate B was verified down to the value: AL s0 fold-1 training checkpoint (epoch 35, 0-based; cat_f1 0.6455,
reg_top10_indist 0.7241, joint_score 0.6837) == CSV epoch 36 (1-based; identical cat_f1 / indist / geom
0.683666) == sidecar `selector_per_fold[0]`. The joint-best re-score recovers the *exact* checkpoint the training
gate saved — no retraining, no GPU. No fold collapsed (every joint epoch 34–50; no reg best-epoch ≤ 5).

Independent adversarial audit (from-scratch re-derivation, AL tail-risk, Istanbul/FL sensitivity, completeness):
see [`JOINT_BEST_AUDIT.md`](JOINT_BEST_AUDIT.md).

## Decision memo

- **The gap is closed and it is benign.** The served single checkpoint delivers the reported Table 3 within
  ≤ 0.11 pp; the response-letter can now state this as fact instead of "can be provided on request."
- **Recommended camera-ready action** (author's call): either (a) keep Table 3 as diag-best and add one sentence
  in §6.2 — "the single served checkpoint reproduces these cells within 0.1 pp (deployable joint-best,
  `geom_simple` selector)"; or (b) add a joint-best row/column. Numbers for both are here.
- **What must travel with these numbers:** always name the convention; the CA/TX joint-best is now **n=20**
  (T6 ✅ DONE 2026-07-13 on the A1 rundirs — sidecars `docs/results/closing_data/catx_v17_n20/joint_best/`:
  CA 77.046/65.690, TX 77.239/67.059, ≈ diag-best within ≤ 0.006 pp at the aggregate); the Istanbul region
  superiority stat wants a joint-best re-run (T7); AL/AZ region are *matches*, never beats.

## Files
- `data/j1_results.json` — per-run + per-cell machine-readable results (incl. per-fold arrays, epochs, audits).
- `score_all.py` — the reproducer (runs the scorer on all 18 rundirs + all parity gates).
- `JOINT_BEST_PROVENANCE.md` — the rundir→cell map. `JOINT_BEST_AUDIT.md` — the independent audit.
