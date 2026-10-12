# v17 STL ceilings — FINAL, n=20, best-vs-best (dk_ovl, 5 Gowalla states)

> **Closed 2026-07-03; AZ ceiling corrected 2026-07-08 (post-merge audit of PR #58).** Supersedes the seed-0
> provisional ceilings in `RESULTS_BOARD §1` and the (rejected) matched-knob H2 attempt. Category ceiling re-tuned
> **best-vs-best** (each arm at its own optimum); region ceiling topped up to n=20. Istanbul was added 2026-07-06 once
> the H3 `dk_ovl` substrate landed (the original close predates it — see the Istanbul note below).
>
> ⚠ **AZ correction (2026-07-08):** the originally-published AZ ceiling **56.24** (bs2048@0.005) violated this doc's
> own "per-state max over the tried recipes" rule — the committed full-n=20 arm **bs8192@0.005 = 56.43 ±0.10** is
> higher (`sweep_results/arizona_bs8192_lr0.005_s{0,1,7,100}.json`). AZ ceiling = **56.43**, **Δcat AZ = +9.40** (not
> +9.60). Two n=10 screens sit higher still (bs2048@0.0025 = 57.04, @0.0075 = 56.93, seeds {0,1} only) — **pending a
> 2-seed top-up** (A40 queue; ~4 runs × ~100 s). If 57.04 holds at n=20 the AZ ceiling becomes ~57.0 → Δcat ≈ +8.8.
> Until then +9.40 is the citable value and the AZ Δ carries this note. AL/FL/CA/TX verified max-rule-clean.

## Final board (n=20 = 4 seeds {0,1,7,100} × 5 folds)

| State | STL cat | MTL cat (v17) | **Δcat** | STL reg | MTL reg (v17) | **Δreg** |
|---|---:|---:|---:|---:|---:|---:|
| AL | 56.82 ±0.03 | 64.54 | **+7.72** ✅beats | 70.11 | 69.80 | **−0.31** ≈matches |
| AZ | 56.43 ±0.10 † | 65.83 | **+9.40** ✅beats † | 59.46 | 59.56 | **+0.10** ≈matches |
| FL | 74.51 ±0.03 | 79.85 | **+5.34** ✅beats | 76.70 | 77.42 | **+0.72** ✅beats |
| CA | 70.60 ±0.07 | 77.05 | **+6.45** ✅beats | 63.49 | 65.69 | **+2.20** ✅beats |
| TX | 69.79 ±0.08 | 77.24 | **+7.45** ✅beats | 64.95 | 67.06 | **+2.11** ✅beats |
| Istanbul | 54.74 ±0.09 | 63.33 | **+8.59** ✅beats | 75.16 | 75.44 | **+0.28** ✅beats |

**Story:** MTL beats the dedicated **category** ceiling at every state (+5.3 … +9.4 pp); **matches** the region ceiling at
the small US states (AL −0.31, AZ +0.10, within δ=2 pp) and **beats** it at the larger ones (FL +0.72, CA +2.20, TX +2.11)
**and at Istanbul** (+0.28, non-US corpus, 520 mahalle — H3 dk_ovl+v17 rebuild; see `h3_istanbul/RESULTS.md`).

> **Istanbul (added 2026-07-06, H3)** is v17 n=20 on the **rebuilt `dk_ovl` substrate** (v14/design_k re-windowed at
> stride-1), so it is now on the SAME substrate identity as the 5 Gowalla states — the old "stride-1 GCN base check2hgi"
> cross-substrate caveat is retired. Cat ceiling = small-state recipe bs2048@0.005; the rebuild lifted both heads vs the
> old base (cat +6.69→+8.59, reg −0.52→+0.28).

> ✅ **MTL cat/reg are now n=20 at ALL states** — CA/TX completed 2026-07-11 (A1 on the A40, `{1,7,100}` top-up;
> per-cell scores `docs/results/closing_data/catx_v17_n20/`). The n=20 **confirms** the seed-0 values with tight
> variance (CA cat 77.052 ±0.006 / reg 65.693 ±0.017; TX cat 77.239 ±0.014 / reg 67.062 ±0.007), so the CA/TX Δs
> are now n=20-vs-n=20 (the seed-0 asterisks are dropped). Ceilings were already n=20 at all states. **The v17 board
> is complete.**

## Category ceiling — recipe (best-vs-best, state-size-dependent)

The STL cat optimum depends on state size (proven by the sweep, `cat_ceiling_sweep/`):

| tier | states | recipe | why |
|---|---|---|---|
| small | AL | **bs2048 @ max_lr 0.005** | small batch + low LR peaks highest; bs8192 loses ~0.35 pp |
| small† | AZ | **bs8192 @ max_lr 0.005** (corrected 2026-07-08) | at AZ the n=20 max is the bs8192 arm (56.43 > bs2048@0.005's 56.24); the "small = bs2048" generalization held at AL only. Two n=10 bs2048 screens (0.0025/0.0075 = 57.04/56.93) pending top-up. |
| large | FL, CA, TX | **bs8192 @ max_lr 0.005** | +1.7 pp over bs2048 (healthy late best-epochs vs bs2048's early-peak overfit) |

Single-task `next_gru`, `--engine check2hgi_dk_ovl`, 50 ep, 5f, OneCycle. Scored by `score_stl_cat_ceiling.py`
(macro-F1 at f1-best epoch, fold-mean). Ceiling = per-state max over the tried recipes, n=20 mean (no per-fold/seed
cherry-pick). Full LR-response curves: `cat_ceiling_sweep/sweep_results/` + `aggregate.py`.

**Rejected: the "matched-knob" H2 (STL forced to the MTL's bs8192@1e-3).** It gave AL 53.58 — *below* the STL optimum,
inflating Δcat to +10.96. That is baseline sabotage (advisor panel unanimous); kept only as a labeled iso-budget
ablation, never the headline. See `A40.md §A40-1` + the panel record.

## Region ceiling — recipe + n=20 top-up

`p1_region_head_ablation.py --heads next_stan_flow --input-type region --region-emb-source
check2hgi_design_k_resln_mae_l0_1 --engine-override check2hgi_dk_ovl --override-hparams freeze_alpha=True
alpha_init=0.0 --max-lr 0.003 --target region`, 50 ep, 5f. Prior is **OFF** (α frozen at 0) → log_T inert → the
top-up omits `--per-fold-transition-dir` (parity-validated: AL s0 no-dir = 70.00 vs board 69.99). n=20 = board seed-0 +
`{1,7,100}` (`reg_ceiling_n20/`). Reg is seed-invariant (n=20 vs seed-0 diff < 0.13 pp everywhere) — the seed-0 board
verdict was correct; this makes the paired test rigorous.

## Provenance
- cat: `cat_ceiling_sweep/{sweep.sh,aggregate.py,sweep_results/}` · driver logs `cat_ceiling_sweep/DRIVER.log`
- reg: `reg_topup/{finalize_reg.sh,DRIVER.log}` · values `docs/results/closing_data/reg_ceiling_n20/`
- MTL cat/reg: `perhead_lr_n20.md` (AL/AZ/FL n=20) · `catx_v17_seed0_5f/RESULTS.md` + `docs/results/closing_data/catx_v17_n20/` (CA/TX n=20, A1 complete 2026-07-11)
