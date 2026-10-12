# G1 Arizona: train-only vs full representation, the delivered v18 protocol (2026-10-02)

Same protocol as `../g1_integrity_al/README.md` (read that first), applied to Arizona.

## Result (Arizona, seed 0, all 5 folds)

| | train-only (TO) | full, same seed and device (FULL) | TO − FULL | printed (delivered, CUDA) |
|---|---:|---:|---:|---:|
| category macro-F1 | 34.3872 | 34.5611 | **−0.174 ± 0.110** (0/5 folds positive, paired t p = 0.024, Wilcoxon p = 0.0625) | 34.508 |
| region Acc@10 | 59.4017 | 59.2693 | **+0.132 ± 0.193** (4/5 positive, t p = 0.20) | 59.4813 |

Per fold (`G1_AZ_5fold.csv`; folds are 0-indexed):

| fold | cat TO | cat FULL | cat printed | reg TO | reg FULL | reg printed |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 34.2309 | 34.3917 | 34.3688 | 62.5750 | 62.4580 | 62.6223 |
| 1 | 35.2622 | 35.5428 | 35.5292 | 59.2897 | 59.0980 | 59.7999 |
| 2 | 33.0822 | 33.3473 | 33.2126 | 59.6033 | 59.7053 | 59.5311 |
| 3 | 33.4590 | 33.6142 | 33.6091 | 57.7093 | 57.6719 | 57.5002 |
| 4 | 35.9019 | 35.9094 | 35.8203 | 57.8312 | 57.4131 | 57.9532 |

**Reading.** The pattern is the same as Alabama's.
- **Category.** Excluding the validation users lowers category macro-F1 by about 0.17 pp, in every fold.
  That is well under one fold sd (≈ 1.1). Alabama measured −0.11.
- **Region.** No drop: +0.13, which is the opposite direction from a leak.
- **FULL − printed.** Category +0.05 and region −0.21. FULL is CPU-built and trained on MPS, while the
  printed cells were CUDA-built and trained with compile. This is device and re-run spread, not a validity
  check: the delivered arm was not re-run here (see below).

## Differences from the Alabama run

- **No delivered validity arm (DEL=0).** Alabama already showed that the delivered arm re-run on this
  Mac reproduces the printed means (+0.003 category, +0.05 region). Skipping it saved about 1.2 h of
  GPU time. Fold 0's delivered category arm was started and then stopped by the watchdog
  (`logs/arizona_f0_cat_del/`). It is not a result.
- **FULL arms.** Built once per state by `drivers/g1_prelude.sh`:
  - category: `build_study_repr.py --cell FULL_CPU --repr-seed 42`, CPU, then readout and materialize to `check2hgi_v18_fullcpu`;
  - region: `build_design_k_delaunay.py --seed 0 --device cpu --out-suffix resln_mae_l0_1_fullcpu_s0`.
  - The prelude checked that FULL_CPU is unrestricted and that its rows and labels equal delivered v18 (200,895 windows).
- **Two steps were stopped by the watchdog and resumed.** The resumable driver (`drivers/g1_lib.sh`)
  re-ran each from scratch after moving the aborted attempt aside (`logs/*_aborted_*`):
  - fold 1's build was stopped by a system-wide memory spike caused by another job (the FL G1 attempt);
  - fold 4's category TO arm was killed when its parent shell hit a 2 h limit.
- **The fold-4 TO category result** is the clean re-run. The partial attempt was moved aside, to
  `results/g1_cat_f4/to/check2hgi_v18_to_f4/arizona_aborted_*`, outside the glob the aggregator reads.
- **Disk.** Each fold's TO engine `input/*.parquet` was deleted after the fold was scored
  (`G1_DELETE_TO=1`). The npz, `build.json` and `materialize.json` are kept, so the engines can be rebuilt.

## Assertions

Each fold passed, fail-stop (`logs/ASSERTS_arizona.log`):
- **A5:** an independent StratifiedGroupKFold over `load_next_data` int64 rows reproduces the split, on `check2hgi_dk_ovl` and `check2hgi_v18`.
- **A1 and A2:** the build excludes exactly the val users (count and sha), the graph is restricted, 500 epochs, and zero val users are in training.
- **A3:** fresh output dirs.
- **A4:** 200,895 windows, with userids and labels equal to delivered v18.
- **Region record:** val sha, zero val users in training, seed 0, CPU.
- **Report support:** each category run's report support equals its fold's `n_val_rows` (checked by `drivers/g1_aggregate.py`).

## Caveat: per-fold random state under `--only-fold` (added 2026-10-03)

Single-task training has **no per-fold reseed**:
- `seed_everything` runs once at `train.py` start;
- `per_fold_seed` reaches only the MTL runners.

The delivered `cell_cat` ran all 5 folds in one process, so delivered fold F (F ≥ 1) starts from the
random state left after folds 0..F−1. Every arm here ran with `--only-fold F`, so each fold starts
from the fresh seed. Consequences:
- **Only fold 0's absolute numbers follow the delivered fold's random trajectory.**
- For folds 1–4, the absolute values are not the delivered trajectory. MPS vs CUDA also rules out
  bitwise matching.
- **The train-only vs full contrast is unaffected.** Both arms of every fold ran under the same
  `--only-fold` protocol and seed, so the comparison is paired.
- The comparison against the printed values is a sanity band, not a reproduction, beyond fold 0.

(Raised by the independent review of the D2 patch,
`docs/studies/closing_data/v18/gpu_queue/d2_lean_single_task_folds.patch`.)

## Machine and safety

- Apple M2 Pro, 32 GB. Builds ran on CPU, training on MPS (fp32, no compile).
- Watchdog per step, killing by PID: free memory below 20%, swap growth over 1000 MB, or SSD below 5 GB.
- Global lock: at most one MPS training process at a time.
- After 03:15 everything ran strictly serially.

## Files

Same layout as the Alabama directory:
- `G1_AZ_5fold.csv` and `G1_AZ_5fold_stats.json`;
- `splits/`, `builds/`;
- `runs/cat/{to,full_cpu}_f<F>/`, `runs/reg/` (10 `p1` JSONs);
- `logs/`, `drivers/`;
- `MANIFEST.md5`.

Uncommitted. Committing needs `git add -f docs/results/closing_data/v18/g1_integrity_az/`.
