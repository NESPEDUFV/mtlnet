# G2: frozen-CTLE control re-run on the MATCHED split, Alabama, Arizona and Istanbul (2026-10-02/04, M2 Pro)

**Why.** The June CTLE-SC cells (`docs/results/closing_data/baseline_compare/{alabama,arizona}_ctle.json`,
`MACS_BOARD_RESULTS.md`) were mismatched:
- CTLE was pre-trained on a fold split computed over the canonical `check2hgi` rows
  (`build_ctle_substrate.get_fold_indices` hard-coded `CHECK2HGI`);
- each cell was **scored** by `train.py --only-fold` on the stride-1 `check2hgi_dk_ovl` rows, whose folds differ;
- so 74–82% (AL) and 78–82% (AZ) of each scored fold's validation users were on the pre-training side.

G2 re-runs the cells with `--split-engine check2hgi_dk_ovl`, so pre-training excludes exactly the
scored fold's users.

## Result (category macro-F1, seed 0, 5 folds)

| state | June (mismatched split) | **matched split** | matched − June |
|---|---:|---:|---:|
| Alabama | 17.77 | **16.31 ± 1.02** | **−1.46 ± 0.95** (5/5 folds lower, paired t p = 0.027) |
| Arizona | 19.30 | **17.67 ± 1.13** | **−1.63 ± 1.00** (5/5 lower, t p = 0.022) |

Per fold: `G2_CTLE_matched.csv`.
- AL: 17.17 / 15.24 / 15.89 / 15.66 / 17.61 against June's 18.53 / 17.90 / 16.93 / 15.83 / 19.66.
- AZ: 17.54 / 18.01 / 17.38 / 16.16 / 19.28 against June's 18.10 / 18.92 / 19.77 / 19.08 / 20.63.

**Reading.** The mismatch favoured CTLE: removing it lowers CTLE by about 1.5 pp in every fold.
Against the representations it is compared with, CTLE's gap therefore only grows. The ordering
sentence it supports is strengthened, not reversed. Ch. 5 prints no CTLE number at AL/AZ/IST, so no
printed value changes.
- **Caution:** the `Check2HGI-SC` comparand in `MACS_BOARD_RESULTS.md` (55.59 / 56.31) is a pre-v18
  substrate value. Any CTLE vs Check2HGI Δ should use the v18 dedicated cells, not that column.

## Istanbul (added 2026-10-04)

Same recipe, same asserts, run on the M2 Pro from the internal disk (`/Users/vitor/g2_scratch`), at commit `f0fca061`.
- **Inputs:** the canonical `check2hgi/istanbul` plus `check2hgi_dk_ovl/istanbul`, md5-equal to nespedgpu
  (`logs/ISTANBUL_INPUT_MD5S_box.txt`).
- **Driver:** `drivers_istanbul/`, with a PID-scoped watchdog. No aborts.

| fold | June | **matched split** | matched − June |
|---|---:|---:|---:|
| 0 | 25.7004 | 27.3487 | +1.65 |
| 1 | 25.9156 | 26.5632 | +0.65 |
| 2 | 25.5218 | 25.9805 | +0.46 |
| 3 | 26.1830 | 27.1712 | +0.99 |
| 4 | 26.2653 | 27.8820 | +1.62 |
| **mean** | **25.92** | **26.99 ± 0.73** | **+1.07 ± 0.55** (0/5 lower, t p = 0.012) |

**Asserts, 5/5 passed** (`logs/ASSERTS_g2_ist.log`):
- the `check2hgi_ctle` rows equal `dk_ovl` (271,666);
- `train.py`'s fold val-user sha equals `CTLE_FOLD.txt`;
- report macro-F1 equals the f1-best epoch;
- support equals `n_val` (54,333 / 54,333 / 54,334 / 54,333 / 54,333).

**Cost:** build 4.5 min (peak RSS ≈ 5.0 GB) plus score 7–8 min (≈ 7.0 GB) per fold.

**Reading.**
- **At Istanbul the matched-split CTLE is *higher* than June's, in every fold.** A leak through
  pre-training would make the matched value *lower*, as at AL and AZ.
- So this supports the earlier inference that **June's Istanbul cell was not split-mismatched**. Its rows
  were the 271,666 stride-1 rows that are row- and fold-identical to `dk_ovl`.
- **The text can now state as measured, for all three states, that CTLE is pre-trained per fold on
  training users only:** AL 16.31, AZ 17.67, IST 26.99.
- **The +1.07 is most likely run-to-run or device spread** (not measured separately). Pre-training ran on MPS here; the one June log found
  (AL) shows CPU. It also tempers the AL/AZ reading: part of their −1.5 may be the same kind of shift, so
  the leak's own share there could be larger than 1.5. The direction of every conclusion is unchanged.
- **Ordering at Istanbul, for the D3 sentence:** frozen CTLE 26.99 < place-level HGI 32.54 (paired,
  `istanbul_pair/`) < check-in level 35.35 (the printed dedicated cell). The ordering holds, as at AL and AZ.

## Protocol

Per (state, fold F), driver `drivers/g2_ctle_fold.sh`, strictly serial:
1. **Build.** `scripts/baselines/build_ctle_substrate.py --state <st> --seed 0 --fold F --split-engine check2hgi_dk_ovl --stride 1 --device mps`,
   with defaults `--pretrain-epochs 10 --max-len 64 --batch-size 256 --lr 1e-3`.
   - Pre-training (MLM + masked-hour) uses only the fold's training users. Every row is then embedded
     by the frozen encoder.
   - The builder writes `next`, `sequences_next` and `next_region` (stride 1) and `CTLE_FOLD.txt`,
     which records `split_engine`, `n_val_users` and `val_users_sha256`.
2. **Assertions, fail-stop** (`drivers/g2_assert.py`, `logs/ASSERTS_g2.log`, 10/10 passed):
   - the `check2hgi_ctle` rows equal `check2hgi_dk_ovl`'s: AL 96,326 / AZ 200,895, with userids and
     labels equal in order. The builder's global `min_seq` 5 is therefore a no-op here, as its
     docstring states;
   - an independent StratifiedGroupKFold over `load_next_data(check2hgi_ctle)` int64 rows reproduces
     `CTLE_FOLD.txt`'s `val_users_sha256` for fold F, i.e. `train.py`'s scored fold. AL fold 0's sha
     (`01b7b2e1…`) also equals G1 AL fold 0's split.
3. **Score**, with the board `run_cat` recipe from `scripts/closing_data/mac_baseline_compare.py`, verbatim:
   - `train.py --task next --engine check2hgi_ctle --state <st> --seed 0 --only-fold F --cat-head next_gru --epochs 50 --batch-size 2048`;
   - no logit adjustment, `OMP_NUM_THREADS=4`, MPS;
   - macro-F1 from the single fold report (`macro avg`), as `run_cat` reads it. It equals the f1-best
     epoch of `metrics/fold1_next_val.csv` to within 1e-4 in all 10 cells, and the report support equals
     the fold's `n_val`.

**Device.** CTLE pre-training ran on **MPS** (the builder's default), at the author's request on
2026-10-02. **A June AL CTLE pre-training log shows `device=cpu`**:
`/Volumes/Vitor's SSD/ingred/output/_scratch/log_ctle_alabama_s0_f1.txt`, dated 2026-06-21, line 5:
`CTLE pretrain: vocab=11850 train_trajs=2267 … device=cpu epochs=10`.
- That is one fold-1 log dated before the board cells. **It is not proven to be the scored cell's own log.**
- In any case this re-run does not bit-reproduce June. Its purpose is the matched split, not reproduction.

**Inputs.** The canonical `output/check2hgi/{alabama,arizona}/{embeddings,region_embeddings,poi_embeddings}.parquet`,
which the builder's `_load_checkins` reads, were copied from nespedgpu md5-equal (`logs/CTLE_INPUT_MD5S_box.txt`).
The `check2hgi_dk_ovl` rows are the ones used by G1 and G5, md5-equal to the box.

**Code.** Commit `d01cd2a8` (a `--shared` clone on the external SSD). `--split-engine` landed in `82dbe843`.

**Cost.** Build 44–103 s and score 169–174 s (AL) or ~347 s (AZ) per cell, about 5 and 8 min per fold.
- Peak RSS ≤ 3 GB. At most one MPS process at a time (global lock), with a PID watchdog.
- No aborts.

## Files

- `G2_CTLE_matched.csv` and `G2_CTLE_matched_stats.json`.
- `runs/<st>_f<F>/`: `CTLE_FOLD.txt`, plus `metrics/`, `folds/` and `summary/` of the scoring run, and `SOURCE_RUNDIR.txt`.
- `logs/`: each step's `RUN.txt` and `mem.log`, a `build_summary.txt` (split, pre-training losses,
  rows) per build, and the assertion and driver logs.
- `drivers/`.
- `MANIFEST.md5`.

Scratch (not copied): `/Volumes/Vitor's SSD/ingred_g1/results/g2_ctle/`. The per-fold CTLE engine dir
was overwritten fold by fold, and the AL one was deleted after scoring (`DELETED.txt`).

Uncommitted. Committing needs `git add -f docs/results/closing_data/v18/g2_ctle_matched/`.
