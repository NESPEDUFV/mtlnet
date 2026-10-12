# v18 — RESULTS

> Generated 2026-08-11T03:19:50.729562+00:00 from [`data/v18_results.json`](data/v18_results.json) by `make_results.py`. Every number here is traceable to that JSON, which [`score_all.py`](score_all.py) regenerates from the rundirs.

> Commit `4bc3e1b0` · seeds run: see the n column of each table.

**v18 = the frozen v17 recipe on a leak-free substrate**: the consecutive-visit graph is forward-only in training and at readout, plus 4 elapsed-time node columns (`in_channels` 15). Not an architecture change. See [`METHODOLOGY.md`](METHODOLOGY.md).

## Conventions

- **diag-best** (`db_*`) — per-task diagnostic-best epochs. The Table-3 convention.
- **joint-best** (`jb_*`) — both heads at the single `geom_simple`-selected epoch, `min_best_epoch` 0. What the served checkpoint delivers.
- cat = macro-F1. reg = `top10_acc_indist · (1 − ood_fraction) · 100`, i.e. **Acc@10**.
- "beats" = paired one-sided superiority test. "matches" = TOST non-inferiority within ±2 pp. A non-inferior result is never upgraded to a win.


> ⚠ **Two disclosures that qualify every p-value below.**
>
> **1. The tests pool (seed, fold) pairs as if independent.** `paired_diffs` concatenates the 5 per-fold differences from each seed, so n = seeds × 5. The 5 folds within one seed share ~80 % of their training data, so these are **not** independent replicates and the reported p-values are anti-conservative. At n=10 (2 seeds) the honest independent unit is the **seed**, giving n=2 — underpowered. Read the p-values as descriptive, and do not promote a marginal result on their strength alone.
>
> **2. The dedicated-cat comparator was tuned on this same CV.** Its per-state `max_lr` and the joint `category_weight` were selected at seed 0 on the same 5-fold splits reported here. The dedicated arm got a 4-point per-state LR search while the MTL cat-lr axis was measured null, so the dedicated ceiling is optimistically biased relative to MTL — which makes Δcat a **conservative** estimate of any MTL advantage, and an optimistic one of any MTL deficit. See METHODOLOGY.md.

## 1 · MTL vs its own dedicated ceiling (same substrate, same protocol)

This is the citable contrast: both arms measured on v18, so the comparison is within-protocol.

> The **dedicated** column is restricted to the seeds that also have a joint cell, so Δ, `n` and the p-value all describe the same seeds. A dedicated cell can run ahead of its joint cell (the cheap families are the ones sent to rented hardware), so the all-seed dedicated mean can be based on more seeds than this; it is in `data/v18_results.json` as `stl_cat` / `stl_reg`, against the paired `stl_cat_paired` / `stl_reg_paired` used here.

| state | n | dedicated cat | MTL cat | **Δcat** | verdict | dedicated reg | MTL reg | **Δreg** | verdict |
|---|---:|---:|---:|---:|---|---:|---:|---:|---|
| istanbul | 20 | 35.34 | 35.45 | **+0.11** | **beats** (paired one-sided p=0.001) | 75.16 | 75.27 | **+0.11** | **beats** (paired one-sided p=0.000) |
| alabama | 20 | 30.77 | 30.70 | **-0.08** | matches (TOST +/-2 pp, p=0.000) | 70.12 | 69.67 | **-0.45** | matches (TOST +/-2 pp, p=0.000) |
| arizona | 20 | 34.57 | 34.62 | **+0.04** | matches (TOST +/-2 pp, p=0.000) | 59.48 | 59.26 | **-0.22** | matches (TOST +/-2 pp, p=0.000) |
| florida | 20 | 37.35 | 37.59 | **+0.24** | **beats** (paired one-sided p=0.000) | 76.69 | 77.09 | **+0.39** | **beats** (paired one-sided p=0.000) |
| texas | 20 | 36.33 | 36.37 | **+0.04** | **beats** (paired one-sided p=0.000) | 64.94 | 66.86 | **+1.91** | **beats** (paired one-sided p=0.000) |
| california | 20 | 35.63 | 35.75 | **+0.12** | **beats** (paired one-sided p=0.000) | 63.48 | 65.43 | **+1.95** | **beats** (paired one-sided p=0.000) |

## 2 · Joint model — both epoch-selection conventions

| state | n | cat diag-best | cat joint-best | reg diag-best | reg joint-best |
|---|---:|---:|---:|---:|---:|
| istanbul | 20 | 35.45 ± 0.05 | — | 75.27 ± 0.04 | — |
| alabama | 20 | 30.70 ± 0.06 | — | 69.67 ± 0.07 | — |
| arizona | 20 | 34.62 ± 0.05 | — | 59.26 ± 0.10 | — |
| florida | 20 | 37.59 ± 0.06 | — | 77.09 ± 0.02 | — |
| texas | 20 | 36.37 ± 0.02 | — | 66.86 ± 0.03 | — |
| california | 20 | 35.75 ± 0.04 | — | 65.43 ± 0.02 | — |

## 3 · Against the v17 published board — CROSS-SUBSTRATE, descriptive only

> ⚠ v17 and v18 are **different substrates**. These differences are reported to show the size of the leak's contribution; they are **not** superiority tests and must not be written as one.

| state | Δcat v18 | Δcat v17 | shift | Δreg v18 | Δreg v17 | shift |
|---|---:|---:|---:|---:|---:|---:|
| istanbul | +0.11 | +8.59 | **-8.48** | +0.11 | +0.28 | -0.17 |
| alabama | -0.08 | +7.72 | **-7.80** | -0.45 | -0.31 | -0.14 |
| arizona | +0.04 | +9.40 | **-9.36** | -0.22 | +0.10 | -0.32 |
| florida | +0.24 | +5.34 | **-5.10** | +0.39 | +0.72 | -0.33 |
| texas | +0.04 | +7.45 | **-7.41** | +1.91 | +2.11 | -0.20 |
| california | +0.12 | +6.45 | **-6.33** | +1.95 | +2.20 | -0.25 |

## 4 · Pooled across states

- **Δcat** pooled over 120 (state, seed, fold) pairs: mean **+0.079** — **beats** (paired one-sided p=0.000)
- **Δreg** pooled over 120 pairs: mean **+0.616** — **beats** (paired one-sided p=0.000)

Pooling across states is reported for a single headline figure; the per-state rows in §1 are the primary result, since the states differ in size and in their v17 deltas.

## 5 · Related findings

- [`LOSS_WEIGHT_PROBE.md`](LOSS_WEIGHT_PROBE.md) — the 0.75/0.25 split is **not** a leak artifact and the heads are **orthogonal, not competing** (cos ≈ +0.001). Rebalancing and gradient surgery are both null; the equal split is significantly *harmful* to region at Florida. Keep 0.75/0.25.

- [`READOUT_EQUIVALENCE.md`](READOUT_EQUIVALENCE.md) — the per-window readout is an identity on a forward-only graph; the engine is materialized from the one-shot export.

- [`AUDIT.md`](AUDIT.md) — the §6 self-checks with measured values.

