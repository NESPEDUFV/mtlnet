# CA/TX v17 seed-0 5-fold — results (A40, 2026-07-01)

Champion **v17** (= v16 + bs8192 + per-head cat-lr 1e-3 via `MTL_ONECYCLE_PER_HEAD_LR`), seed 0 × 5 folds,
engine `check2hgi_dk_ovl` (gated stride-1 overlap), **fp32** (`MTL_DISABLE_AMP=1`), matched scorer
`a40_score_matched.py`. Serial on the A40 (2-wide infeasible: 2×~27 GB VRAM > 46; fold-construction RAM guard).

> ✅ **n=20 COMPLETE (A1 on the A40, 2026-07-11).** Seeds `{1,7,100}` added to seed-0 → full n=20 (4 seeds × 5 folds).
> Per-cell scores: `docs/results/closing_data/catx_v17_n20/{california,texas}_s{1,7,100}.json`. Driver
> `v17_completion/a1_catx/run_a1_catx_n20.sh` (1-wide fp32, RAM-gated, resumable — TX s100 auto-recovered a transient
> rc=132 crash via the 2× retry). The n=20 **CONFIRMS** the seed-0 values below with tight cross-seed variance:
>
> | state | v17 cat (n=20) | v17 reg (n=20) | Δcat vs ceiling | Δreg vs ceiling |
> |---|---|---|---|---|
> | **CA** | **77.052 ± 0.006** | **65.693 ± 0.017** | **+6.45** ✅beats | **+2.20** ✅beats |
> | **TX** | **77.239 ± 0.014** | **67.062 ± 0.007** | **+7.45** ✅beats | **+2.11** ✅beats |
>
> (Δ vs the n=20 STL ceilings in `CEILINGS_N20_FINAL.md`: CA cat 70.60/reg 63.49, TX cat 69.79/reg 64.95.) The
> seed-0 table below is retained for provenance; **the n=20 above is the number of record.**

## Cells (seed-0, original — superseded by the n=20 banner above)

| state (regions) | v17 cat macro-F1 | board cat | Δcat | v17 reg top10 | board reg | Δreg | board prec |
|---|---|---|---|---|---|---|---|
| **CA** (8501) | **77.04 ± 0.20** | 77.33 | −0.29 | **65.69 ± 0.30** | 65.66 | **+0.03** | bf16 |
| **TX** (6553) | **77.23 ± 0.12** | 77.51 | −0.28 | **67.07 ± 0.45** | 67.02 | **+0.05** | fp32 |

Per-fold (diag-best epoch):
- **CA cat** [76.95, 77.28, 76.70, 77.17, 77.11] · **CA reg** [65.40, 65.56, 65.65, 65.57, 66.28]
- **TX cat** [77.42, 77.06, 77.19, 77.29, 77.17] · **TX reg** [66.98, 67.36, 66.24, 67.27, 67.50]

Runs clean: 0 NaN/OOM, swap 0 throughout, healthy late best-epochs (48–50). CA wall ~4.9 h, TX ~6.3 h.

## Finding — v17's per-head cat-LR is a STATE-SIZE trade, not a strict board-wide win

- **Small/mid states** (AL/AZ/FL, n=20 `perhead_lr_n20.md`): cat **+0.99 / +2.45 / +0.17** — clear wins.
- **Largest states** (CA/TX): cat **−0.28 / −0.29**; **reg ties/beats** (+0.03 / +0.05).

**This is NOT a bf16 artifact.** TX's board cell is **fp32** (clean same-precision, same seed, same 5 folds) and
still shows −0.28 cat (~2× its fold-std 0.12) — matching CA's −0.29. So the large-state cat dip is **real and
consistent**. Mechanism read: lowering cat-LR fixes cat *overshoot* at small states (exposed by the bigger batch),
but the two largest states have enough data that the cat head wanted the higher LR → slight cat underfit. reg is
unaffected everywhere. (Credit: user flagged the CA-only-decrease asymmetry, which led to isolating this via TX.)

## Decision (user, 2026-07-01): **keep v17 board-wide**

Accept the small large-state cat cost (~0.28 pp, reg-neutral) for the large small-state gains + single-champion
simplicity. **v17 stays `DEFAULT_CANON`.** The large-state cat trade is documented here + in the board callout so
it travels with the numbers.

## Next — ✅ DONE
Seeds **{1,7,100}** completed on the **A40** (2026-07-11, A1; the H100 lane was retired) → CA/TX at **n=20**. The
fp32 n=20 firmed the large-state Δ significance: the v17-vs-v16-board cat trade holds (CA −0.28 / TX −0.27) and
reg ties+ (CA +0.03 / TX +0.04), now at n=20 with cross-seed σ ≤ 0.017. **The v17 board is complete** — folded into
`CEILINGS_N20_FINAL.md`, `RESULTS_BOARD §1`, and `stats_n20/RESULTS.md` (M1-full unblocked).
