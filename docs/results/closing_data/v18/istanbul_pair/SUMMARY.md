# G3: paired Istanbul place arm, 2026-10-01 (M2 Pro, MPS)

- **Validity check:** the MPS check-in arm reproduces the printed CUDA cell. It gives 35.3453 against
  35.3539; the mean difference is −0.009 and the largest per-fold difference 0.029, inside the fold sd
  of 0.88.
- **Paired place arm:** 32.54 ± 1.03, on the same 271,666 rows, labels and folds. The printed unpaired
  cell was 29.07 (343,795 rows).
- **Paired delta, check-in minus place: +2.81** (folds 2.33 / 2.34 / 2.85 / 3.55 / 2.99, all positive;
  paired t p = 0.00025; Wilcoxon p = 0.0625, the minimum possible at n = 5). **The printed delta was
  +6.29.**
- **Label alignment:** 2,852 targets (1.05%) differed between the builder's labels (derived from
  `Istanbul.parquet`) and the v18/`dk_ovl` labels. The place arm was aligned to v18's labels, and the
  builder's output is kept as `next.builder_labels.parquet`.
- **Resources:** about 51 min per arm, peak RSS 6.9 GB, no swap growth, lowest free memory 37%.

Details: `SUMMARY.json`. Logs: `logs/`. Runs: `results/`.
