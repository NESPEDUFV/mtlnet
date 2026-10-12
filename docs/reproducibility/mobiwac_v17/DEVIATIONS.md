# Frozen statistical deviations

This is the durable copy of the four deviations recorded on 2026-07-25 under
Section 8 of `STATISTICAL_PROTOCOL.md`.

1. The paper reports paired tests on four per-seed five-fold means (`n=4`), while
   the registered superiority footing pools matched folds across seeds (`n=20`).
   Per-fold artifacts were not initially available; the registered footing was
   later executed as described in item 3.
2. A paired t test was reported alongside the registered Wilcoxon because the
   exact one-sided Wilcoxon has a minimum attainable p-value of 0.0625 at `n=4`.
3. After the missing Istanbul per-fold category ceiling was recovered, the
   registered `n=20` test ran at all six datasets. The category Holm family
   rejected at every dataset; the worst adjusted p-value was 5.72e-06.
4. Next-region superiority at Istanbul, Florida, Texas, and California is
   post-hoc. The registered region analysis is non-inferiority by TOST. The four
   secondary superiority results therefore use a separate Holm family and are
   labeled as outside the registered plan.

The executable record is `research/reproducibility/mobiwac_v17/`; the frozen
outputs are under `outputs/`. No estimate or scientific verdict changed when
these deviations were made explicit.
