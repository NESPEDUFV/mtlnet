# G3: Istanbul place-vs-check-in, PAIRED (2026-10-01)

**Why.** Ch. 5's representation table pairs a check-in-level cell with a place-level (HGI) cell per
dataset. At Istanbul the printed place cell (29.07, `docs/results/closing_data/v18_place_level/istanbul_s0_cat_placelevel.json`)
ran on `hgi_dk_ovl/istanbul` built 2026-06-26 on **343,795** rows. The v18 check-in cell runs on the
**271,666** rows of the 2026-07-06 `dk_ovl` rebuild. So the printed +6.29 compares different rows.
AL/AZ/FL are paired (identical rows, labels and folds, checked 2026-10-01). CA/TX could not be checked.

**What was run.** Both arms on this Mac, same session, the table's recipe:
`scripts/train.py --task next --state istanbul --engine <check2hgi_v18 | hgi_dk_ovl> --model next_gru
--embedding-dim 64 --folds 5 --epochs 50 --seed 0 --batch-size 8192 --max-lr 0.0005 --logit-adjust-tau 0.5
--no-checkpoints`, with env `MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1 MTL_RAM_HEADROOM_GB=4`.
- **Device:** Apple M2 Pro 32 GB, **MPS, fp32, no `torch.compile`, no tf32**, `num_workers` 0, torch 2.11.0.
  The printed cells ran on CUDA with compile + tf32.
- **Scratch root** (outside the repo): `/Volumes/Vitor's SSD/istanbul_pair/`, via `OUTPUT_DIR`,
  `DATA_ROOT` and `RESULTS_ROOT`. The repo's `output/` and `data/` were untouched.
- **Inputs:** copied read-only from nespedgpu, each **md5-equal to the box** (`INPUT_MD5S.txt`).
- **Place inputs:** built by `scripts/closing_data/build_hgi_overlap_inputs.py istanbul`, which reuses
  the frozen `check2hgi_dk_ovl` window sequences and swaps in the HGI place vector (`build/`).
- **`MTL_RAM_HEADROOM_GB=4`:** `load_next_data`'s guard refuses at its default 16 GB headroom. The
  dataset is 1.2 GB; the Mac board runs used 2.

**Metric.** Category macro-F1 at the f1-best epoch per fold, the `score_stl_cat_ceiling.py` rule.

## Validity check: the MPS check-in arm against the printed CUDA cell

| fold | MPS (this run) | CUDA (printed, `v18_results.json`, Istanbul seed 0) | diff |
|---|---:|---:|---:|
| 1 | 36.4853 | 36.5132 | −0.0279 |
| 2 | 34.9125 | 34.9152 | −0.0027 |
| 3 | 34.1560 | 34.1353 | +0.0207 |
| 4 | 35.7527 | 35.7571 | −0.0044 |
| 5 | 35.4202 | 35.4487 | −0.0285 |
| **mean** | **35.3453** | **35.3539** | **−0.0086** |

The largest per-fold difference is 0.029, against a fold sd of 0.88. The device change does not move
the number.

## Result

| | folds 1–5 | mean ± sd |
|---|---|---|
| check-in (v18) | 36.4853 / 34.9125 / 34.1560 / 35.7527 / 35.4202 | 35.35 ± 0.88 |
| place, **paired** | 34.1602 / 32.5775 / 31.3084 / 32.2075 / 32.4319 | **32.54 ± 1.03** |
| place, printed (unpaired) | 29.9846 / 28.4006 / 29.0030 / 29.3552 / 28.5989 | 29.07 |
| **paired Δ** | +2.33 / +2.34 / +2.85 / +3.55 / +2.99 | **+2.81 ± 0.51** |

All five folds favour the check-in representation. Paired t p = 0.00025; Wilcoxon p = 0.0625, the
minimum possible at n = 5. **The printed Δ is +6.29.**

## Label alignment

The built place arm's `next_category` disagreed with the v18 labels on **2,852 of 271,666 targets
(1.05%, 1,651 users)**, spread across all seven categories. The builder takes each target's category
from `data/checkins/Istanbul.parquet` (the box's copy, md5 `90cec3fc30d1b9ffb07efa8cbf2d8469`). The v18
labels, which the printed check-in cell used, come from the `dk_ovl` build. With unequal labels the folds
also differ (0/5 equal), so the arms are not paired.

**What was done:** the place arm's `next_category` was replaced by v18's, rows aligned by userid as int64.
After that, through `train.py`'s own `load_next_data` and StratifiedGroupKFold: userids equal, labels
equal, **5/5 folds identical**, and the inputs differ genuinely (max |Δ| 24.9). The builder's original
output is kept in the scratch root as `next.builder_labels.parquet`; the record is `build/LABELS_ALIGNED.json`.

**Open question:** which category map produced the v18/`dk_ovl` Istanbul labels, and which one the
printed unpaired place cell used.

## Files

- `SUMMARY.md` / `SUMMARY.json`: the result, the validity check, resources.
- `runs/full/{checkin_v18, place_hgi_dk_ovl_paired}/`: `metrics/`, `summary/` and `folds/` of the 5-fold runs.
- `runs/smoke/*_fold0/`: the one-fold smokes (`--only-fold 0`). **These are smokes, not results.**
- `build/`: the builder log, its provenance sidecar, `LABELS_ALIGNED.json`.
- `logs/`: the driver `run_pair.sh` and each run's `RUN.txt` (wall, peak RSS) and `mem.log` (swap and free
  memory every 5 s).
- `INPUT_MD5S.txt`: md5 of every input and built file in the scratch root. The `next_region` and
  `sequences_next` files are byte-identical across `dk_ovl`, v18 and the place engine.
- `MANIFEST.md5`: md5 of every file here.

**Resources:** about 51 min per arm, peak RSS 6.9 GB, zero swap growth, lowest free memory 37%.

Uncommitted. Committing needs `git add -f docs/results/closing_data/v18/istanbul_pair/`.
