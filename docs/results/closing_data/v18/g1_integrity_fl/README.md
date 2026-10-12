# G1 Florida: train-only vs full representation, the delivered v18 protocol (2026-10-04)

Same protocol as `../g1_integrity_al/README.md` (read that first) and `../g1_integrity_az/README.md`,
applied to Florida. FL had been blocked on this Mac (32 GB). It fits only with the memory changes listed
under "Differences" below.

## Result (Florida, seed 0, all 5 folds)

| | train-only (TO) | full, same seed and device (FULL) | TO − FULL | printed (delivered, CUDA) |
|---|---:|---:|---:|---:|
| category macro-F1 | 37.3665 | 37.3547 | **+0.012 ± 0.076** (2/5 folds positive, paired t p = 0.75, Wilcoxon p = 1.0) | 37.363 |
| region Acc@10 | 76.6879 | 76.7720 | **−0.084 ± 0.083** (1/5 positive, t p = 0.086, Wilcoxon p = 0.125) | 76.6998 |

**Printed source.** The printed column is `docs/studies/closing_data/v18/data/v18_results.json` →
`per_run[12]` (`state` = florida, `seed` = 0):
- `stl_cat_folds` = [37.7463, 37.2184, 36.7075, 37.6194, 37.5234], whose mean is `stl_cat` = 37.363;
- `stl_reg_folds` = [76.9868, 76.7671, 75.6191, 75.8246, 78.3014], whose mean is `stl_reg` = 76.6998.

`G1_FL_5fold.csv` has the per-fold values below (folds are 0-indexed), and `G1_FL_5fold_stats.json` has
the statistics.

| fold | cat TO | cat FULL | cat printed | reg TO | reg FULL | reg printed |
|---|---:|---:|---:|---:|---:|---:|
| 0 | 37.7920 | 37.7179 | 37.7463 | 77.0366 | 77.1261 | 76.9868 |
| 1 | 37.2479 | 37.2481 | 37.2184 | 76.7416 | 76.7635 | 76.7671 |
| 2 | 36.6187 | 36.6251 | 36.7075 | 75.5524 | 75.5359 | 75.6191 |
| 3 | 37.8333 | 37.9332 | 37.6194 | 75.7889 | 75.9290 | 75.8246 |
| 4 | 37.3405 | 37.2490 | 37.5234 | 78.3202 | 78.5054 | 78.3014 |

**Reading.**
- **Category.** No measurable effect: +0.01, with mixed signs. The fold sd of the printed cells is 0.42.
  AL measured −0.11 and AZ −0.17.
- **Region.** TO sits below FULL in 4 of 5 folds, by 0.08 pp on average. That is the direction a leak
  would push, but it is not significant (t p = 0.086, Wilcoxon p = 0.125 with n = 5). It is also
  about 1/13 of the fold sd (1.07). AL showed none and AZ +0.13. Read it as "at most about 0.1 pp", not as zero.
- **FULL − printed.** Category −0.008 ± 0.213, region +0.072 ± 0.115. FULL is CPU-built and trained on
  MPS, while the printed cells were CUDA-built with compile. This is device and re-run spread, a sanity
  band and not a reproduction (see the caveat below).

## Differences from the Arizona run

- **Memory: what made FL fit on 32 GB.** FL has 1,274,418 windows × 576 features.
  - **D2** (`ab92d07d`): for `--only-fold`, `FoldCreator` builds folds lazily instead of all 5.
    Proof in `docs/studies/closing_data/v18/gpu_queue/d2_proof/`.
  - **D2b** (`17571c16`): the single-task CPU→MPS batch copy is blocking on MPS. Without it,
    `MTL_DATASET_CPU=1` corrupts labels on MPS. Proof in `docs/studies/closing_data/v18/gpu_queue/dataset_cpu_proof/`.
  - **`MTL_DATASET_CPU=1` on both category arms** (TO and FULL), so the fold tensors stay CPU-resident
    and are copied to MPS per batch. On AL that is byte-identical to the default (same proof). The
    probe line in `logs/ASSERTS_florida.log` confirms it is active for every fold
    (`_dataset_device(0)=None`, features on cpu).
  - **Region arms: `p1` unchanged.** It still pre-moves its tensors to MPS, and it fit as is (max pressure 2).
- **No delivered validity arm (DEL=0)**, as in AZ.
- **Commits.** The 37 fold steps from 10-04 ran at `17571c16`. The 7 earlier CPU steps ran at
  `d01cd2a8` on 10-02: the FULL prelude (`fl_full_*`, `fl_full_s0_regbuild`) and fold 0's TO build,
  readout and materialize. D2 and D2b touch only the `train.py` single-task path, not the builders.
- **Earlier aborted attempts are kept,** under `logs/*_aborted_<time moved aside>/`. None is a result.
  - `florida_f0_cat_to_aborted_20261003_111256`: 10-02 03:05, swap guard (pre-D2).
  - `florida_f0_cat_to_aborted_20261004_034701`: 10-03 11:12, critical pressure at 17 s (pre-D2 load).
  - `florida_f0_cat_full_aborted_20261004_025736`: 10-04 00:11, critical pressure at 17 s (D2 only, MPS
    pre-move, with 7 GB of swap inherited from earlier builds).
  - `fl_full_mat_aborted_20261002_021650`: the FULL materialize, re-run cleanly.
- **The first fold-0 split assertion failed** on 10-02 with a `MemoryError` from `load_next_data`'s RAM
  guard (`logs/ASSERTS_florida.log` lines 1–10). It was re-run, and A5 passed (line 12). Fold 0's A4
  line repeats because its steps were restarted, and no other line in the log is a failure.
- **Disk.** Each fold's TO `next.parquet` was deleted after that fold was fully scored (each has a `DELETED.txt`
  note in the scratch engine dir). The npz, `build.json` and `materialize.json` are kept, so the engines can
  be rebuilt. The inputs lived on the internal disk (`/Users/vitor/g1_fl_scratch`), and the SSD clone was the
  code and results root.

## Assertions

Each fold passed, fail-stop (`logs/ASSERTS_florida.log`, 83 lines):
- **A5:** the split equals an independent int64 StratifiedGroupKFold over `load_next_data` rows.
  Val sizes: 254,884 rows for folds 0–2 and 254,883 for folds 3–4. Val users: 2,138 / 2,131 / 2,132 / 2,119 / 2,102.
- **A1 and A2:** the TO build excludes exactly the fold's val users (count and sha), the graph is restricted,
  500 epochs, and no val user appears among the build's embedded users.
- **FULL_CPU:** unrestricted build, 1,274,418 windows, rows equal `dk_ovl`.
- **A4:** 1,274,418 windows, and the `next_region` symlink rows equal arange.
- **No frozen fold cache on the FL paths,** checked before each category arm (D2 review gap (i)).
- **"Generating folds on the fly"** appears in every category arm's log, so the lazy D2 path ran.
- **FL inputs are md5-equal to nespedgpu,** checked per fold before the region arms.
- **Region record,** per fold: val sha, zero val users in training, seed 0, CPU. Regions absent from
  training: 46 / 41 / 48 / 37 / 42 of 4,703.
- **Report support** equals `n_val_rows` for every category run (checked by `drivers/g1_aggregate.py`).

## Machine, safety and memory

- Apple M2 Pro, 32 GB. Builds and readouts ran on CPU, training on MPS (fp32, no compile).
  `MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1` are exported by `drivers/g1_run_crit.sh`.
- **Critical-tier watchdog per step, killing by PID**, with 1 s sampling to `logs/<step>/trace.log`.
  It fires on kernel memory pressure level 4 (critical), free memory below 10%, swap total above 14 GB,
  or internal disk below 3 GB. It never fired in the 37 fold steps.
- **Gate before each fold** (`drivers/fl_gate_start_v2_fold.sh`): internal disk at least 15 GB, pressure
  below 4, and no other MPS job. A chain (`drivers/fl_chain_folds.sh`) ran folds 2–4 and would have stopped
  at the first non-zero rc or failed gate. Logs: `logs/fl_gate_v2.log`, `logs/fl_chain.log`.
- **`G1_FL_step_memory.csv`** has, per step: wall time, swap used at start / peak / end, maximum swap
  total, maximum pressure, minimum free %, maximum wired and maximum child RSS. It covers the 37 steps
  with a `trace.log`. The 7 earlier CPU steps have `mem.log` only.
  - Over all 37: max pressure 2, min free 29%, all rc 0.
  - **Per fold:** about 3 h 45 min. Category arms take about 48 min each, region arms about 33 min, the TO
    build 17 min, the readout 22 min and the region TO build 21 min.
  - **One swap step:** at 14:37, during fold 3's cat FULL, swap used rose from 2.8 to 4.7 GB within
    seconds, and macOS added a fifth GB of swap file. Swap then held flat, and drifted back to 3.6 GB by
    fold 4. Pressure stayed at 2. Cause not identified. The Mac was probably in interactive use (PyCharm was open).

## Caveat: per-fold random state under `--only-fold`

As in AZ: single-task training has **no per-fold reseed**. Every arm here ran with `--only-fold F`, so
each fold starts from the fresh seed, while the delivered run's fold F (F ≥ 1) inherits the random state
left by folds 0..F−1.
- **Only fold 0's absolute numbers follow the delivered fold's random trajectory.**
- **The TO vs FULL contrast is unaffected:** both arms of every fold ran under the same protocol, seed and
  env (both with `MTL_DATASET_CPU=1`), so the comparison is paired.

## Files

Same layout as the Arizona directory:
- `G1_FL_5fold.csv`, `G1_FL_5fold_stats.json`, `aggregate_output.txt`, `G1_FL_step_memory.csv`;
- `splits/` (split metadata; the index lists are left out, as in AZ);
- `builds/`: `cat_{FULL_CPU,TO_F0..4}` (`build.json` and npz meta), `engine_v18_{fullcpu,to_f0..4}`
  (`materialize.json`), `reg_to_f0..4` (`build.json`);
- `runs/cat/{to,full_cpu}_f<F>/` (`metrics/`, `folds/`, `summary/`, `SOURCE_RUNDIR.txt`), and `runs/reg/` (10 `p1` JSONs);
- `logs/` and `drivers/`;
- `MANIFEST.md5`.

Scratch (not copied): the clone `/Volumes/Vitor's SSD/ingred_g1fl` and the inputs `/Users/vitor/g1_fl_scratch`.

Uncommitted. Committing needs `git add -f docs/results/closing_data/v18/g1_integrity_fl/`.
