# G1 Alabama: train-only vs full representation, the delivered v18 protocol (2026-10-01/02)

**Question.** Does training the representation on all users, including the users of each fold's
validation split, inflate Ch. 5's category and region numbers? Each validation fold's users are
removed from representation training, and the result is compared with a full-data build that is
otherwise identical. This is the integrity re-run of `docs/studies/closing_data/v18/integrity_rerun/README.md`,
with the delivered folds (`freeze_split --group-dtype int`), the delivered rows (`check2hgi_dk_ovl`,
stride-1) and the delivered recipes (`run_wave.sh` `cell_cat` / `cell_reg`) plus `--only-fold F`.

## Result (Alabama, seed 0, all 5 folds)

| | train-only (TO) | full, same seed and device (FULL) | TO − FULL | delivered, re-run here | printed |
|---|---:|---:|---:|---:|---:|
| category macro-F1 | 30.7725 | 30.8804 | **−0.108 ± 0.099** (4/5 folds negative, paired t p = 0.07, Wilcoxon p = 0.125) | 30.7685 | 30.7654 |
| region Acc@10 | 69.9468 | 69.9603 | **−0.014 ± 0.376** (2/5 negative, t p = 0.94) | 70.0475 | 69.9956 |

Per fold (`G1_AL_5fold.csv`; folds are 0-indexed here, so fold 0 is "fold 1" in the logs):

| fold | cat TO | cat FULL | cat delivered | cat printed | reg TO | reg FULL | reg delivered | reg printed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 32.2291 | 32.3678 | 32.1061 | 32.2618 | 72.1671 | 71.9543 | 72.2035 | 72.1412 |
| 1 | 30.4890 | 30.5920 | 30.5525 | 30.8034 | 68.9836 | 68.8382 | 69.2224 | 68.9940 |
| 2 | 29.3179 | 29.5641 | 29.4766 | 29.6064 | 73.4129 | 73.1690 | 73.2935 | 73.5219 |
| 3 | 29.8702 | 29.9486 | 29.8362 | 29.6361 | 70.6026 | 71.2669 | 70.9451 | 71.1216 |
| 4 | 31.9562 | 31.9295 | 31.8712 | 31.5193 | 64.5679 | 64.5731 | 64.5731 | 64.1993 |

**Reading.**
- **Category: a small, consistent drop, an order of magnitude below the effect it was checking for.**
  Excluding the validation users from representation training lowers category macro-F1 by about
  0.1 pp. 4 of 5 folds are negative, but the drop is not significant at n = 5 and is smaller than one
  fold sd (≈ 1.1).
- **Region: no effect** (−0.01, with a sign split across folds).
- **Validity.** The delivered arm, re-run on this Mac (MPS, fp32, no compile, single-fold runs),
  reproduces the printed 5-fold means to +0.003 (category) and +0.05 (region). Per-fold differences
  are within ±0.37.

## What "FULL" is, and why it is not the delivered engine

The contrast must differ only in the excluded users.
- **Category.** The delivered v18 Alabama representation is integrity_v2 cell **E2**
  (`run_phase0_build.sh:10,153-158`; box record `results/check2hgi_integrity_v2/alabama/E2/build.json`).
  It was built with `--repr-seed 42 --epochs 500 --encoder resln --forward-only --add-continuous-time`
  on **CUDA**. TO and FULL are both seed 42, the same flags, on **CPU**; FULL has no exclusion.
  FULL − delivered (+0.11 ± 0.09 category, 5/5 positive) is the device effect. The 576-dim windows
  of FULL vs E2 have a row cosine median of 0.998.
- **Region.** `a4_build.py` passes the split seed (0) to `build_design_k_delaunay.py`. Delivered v14
  was built with the builder's default seed 42 on CUDA (`scripts/_v14_run/driver.sh:34`). So FULL
  here is `build_design_k_delaunay.py --seed 0 --device cpu --out-suffix resln_mae_l0_1_fullcpu_s0`.
  The suffix only renames the output dir.

## Protocol

- **Code.** A `git clone --shared` of main at `d01cd2a8`, on the external SSD. The integrity scripts
  hard-code `REPO/"output"`, and `p1` reads `output/` relative to the working directory, so
  `OUTPUT_DIR` alone could not route their writes. The clone's `output/` and `data/` were symlinks to
  an SSD scratch root.
- **Repo-write guard.** After every step, a `find -newer` over the main checkout's
  `output/ data/ results/ docs/results/` was empty (`logs/*/RUN.txt`).
- **Splits.** `freeze_split.py --state alabama --seed 0 --fold F --n-folds 5 --engine check2hgi_dk_ovl --group-dtype int`.
  The `splits/*.meta.json` files keep the counts, the shas and the val users; the index lists were dropped.
- **Category half, per fold:**
  1. `build_study_repr.py --cell TO_F<F> --repr-seed 42 --epochs 500 --device cpu --encoder resln --forward-only --add-continuous-time --exclude-users-file <split>`
  2. `infer_checkins.py --readout prefix_forward_only --self-test`
  3. `materialize_engine.py --dest-engine check2hgi_v18_to_f<F>`, plus the `sequences_next` copy and the v14 `region_embeddings` symlink, as in `run_phase0_build.sh`
  4. `train.py --task next --model next_gru --embedding-dim 64 --folds 5 --only-fold F --epochs 50 --seed 0 --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5 --no-checkpoints`,
     with env `MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 MTL_RAM_HEADROOM_GB=4`, on MPS.
     The FULL arm used a separate `OUTPUT_DIR` root that holds the FULL engine under the name
     `check2hgi_v18`, so no code changed.
  5. Metric: macro-F1 at the f1-best epoch (the `score_stl_cat_ceiling.py` rule).
- **Region half, per fold:**
  1. `a4_build.py --state alabama --seed 0 --fold F --split-json <split> --device cpu`
  2. `p1_region_head_ablation.py --heads next_stan_flow --input-type region --override-hparams freeze_alpha=True alpha_init=0.0 --engine-override check2hgi_v18 --folds 5 --only-fold F --epochs 50 --seed 0 --target region --max-lr 0.003`,
     with env `MTL_CHUNK_VAL_METRIC=1 MTL_STRICT=1`, on MPS, no compile and no tf32.
  3. Metric: `per_fold[0].top10_acc`.
- **Scoring semantics (one deviation).** Fold 0's first TO region run **aborted under `MTL_STRICT=1`**:
  in one epoch, one val row was ambiguous at the top-5 boundary (`logs/reg_to_f0/`).
  - It was re-run with `P1_HITS_FROM_RANK=0 P1_STREAM_GPU=0`, the banked semantics the error names (`logs/reg_to_f0_r2/`).
  - Folds 1–4 used those flags for all arms.
  - Fold 0's FULL and delivered arms used streamed scoring and had 0 ambiguous rows, so their values are
    the same under either semantics.
- **Assertions, each fail-stop (`logs/ASSERTS_alabama.log`; fold 0 was checked interactively):**
  1. **A1:** the build excludes exactly the split's val users (count and sorted-int64 sha), `restricted`, 500 epochs.
  2. **A2:** zero val users among the training check-ins, for both the category embeddings and `a4_build`'s record.
  3. **A3:** fresh output dirs.
  4. **A4:** 96,326 windows, with userids and labels equal to delivered v18.
  5. **A5:** an independent StratifiedGroupKFold over `load_next_data` int64 rows reproduces the split's
     train and val shas and its val users, on both `check2hgi_dk_ovl` and `check2hgi_v18`.
  6. Each category run's report support equals its fold's `n_val_rows`.
- **Machine.** Apple M2 Pro, 32 GB, torch 2.11.0. Builds ran on CPU; training ran on MPS.

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

## Cost (per fold, wall)

| step | wall | peak RSS |
|---|---:|---:|
| category build | 134–162 s | 1.4–1.5 GB |
| readout | 72 s | 1.4 GB |
| category arm | ~230 s | 3.0 GB |
| `a4_build` | 150 s | 1.5 GB |
| `p1` arm | ~138 s | 2.5 GB |

About 25 min per fold with the delivered validity arms. No swap growth; lowest free memory ≥ 39%.

## Files

- `G1_AL_5fold.csv` and `G1_AL_5fold_stats.json`: the table and the paired tests.
- `splits/`: split metadata.
- `builds/`: every build record, readout sidecar and `materialize.json`.
- `runs/cat/<arm>_f<F>/`: `metrics/`, `folds/` and `summary/` of each category run, plus `SOURCE_RUNDIR.txt`.
- `runs/reg/`: the 15 `p1` result JSONs.
- `logs/<step>/`: `RUN.txt` (command, rc, wall, peak RSS, repo-write guard) and `mem.log`.
- `drivers/`: `g1_run.sh` (watchdog), `g1_fold.sh` (per-fold driver), `g1_assert.py`.
- `MANIFEST.md5`.

Scratch (not copied, about 6 GB): `/Volumes/Vitor's SSD/ingred_g1/` (results, engines, checkpoints)
and `/Volumes/Vitor's SSD/gpu_queue_scratch/` (inputs, md5-equal to nespedgpu).

Uncommitted. `docs/results/` is hidden by `.git/info/exclude` on the laptop, so committing needs
`git add -f docs/results/closing_data/v18/g1_integrity_al/`.
