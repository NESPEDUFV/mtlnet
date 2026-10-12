# D2: memory-lean single-task folds for `--only-fold` / `--only-folds`: proof package (2026-10-03)

**Patch:** `../d2_lean_single_task_folds.patch`, against `f0fca061`, two files, +52/−5. **Not applied.**
`git apply --check` is clean on HEAD.

## Why

The FL G1 category arm (`train.py --task next --engine check2hgi_v18_to_f0 --only-fold 0`) drove the
macOS kernel memory pressure to **critical in 17 s** on the M2 Pro (32 GB). The 1-second trace is in
`ingred_g1fl/g1_logs/florida_f0_cat_to_aborted_*/trace.log`.

`FoldCreator._create_single_task_folds` eagerly builds **all 5 folds**:
- for each fold, the `x_tensor[train_idx]` / `x_tensor[val_idx]` advanced-index copies, which stay in `FoldData`;
- a DataLoader whose `POIDataset(..., device=_dataset_device(...))` **pre-moves the tensors to MPS**
  (`_dataset_device` returns `DEVICE` unconditionally off-CUDA).

`--only-fold` restricts the mapping only afterwards (`_RestrictedFoldMapping`). At FL (2.94 GB per
copy) the old path holds about 11× the dataset (≈ 32 GB); the patched path holds about 3×.

## Patch (minimal, opt-in)

1. **`FoldCreator(..., lazy_single_task=False)`, off by default.** The eager loop is **textually unchanged**.
2. **When on:** the split list, `_fold_indices` records and log lines are made eagerly as before, and each
   fold is built on demand by the existing `_LazyFoldMapping` (the check2hgi-MTL path already uses it).
3. **`scripts/train.py` `_resolve_folds._from_scratch`** turns it on only for `--only-fold` / `--only-folds`.
4. **`_run_single_task`** reads `fold_results[i]` once per fold instead of twice. A lazy mapping rebuilds on
   every access; for the eager dict, both reads returned the same object.

## Proof

**(1) Unit equivalence (CPU, no training):** `scripts/d2_unit_equiv.py` → `unit_equivalence_output.txt`.
**PASS.**
- AL v18 inputs, md5-equal to nespedgpu (`scripts/AL_v18_inputs_box.md5`).
- For all 5 folds, eager vs lazy: identical indices and tensors (`torch.equal`), identical loader batch
  size and samplers, `generator=None`.
- **Global torch, numpy and python RNG states are unchanged** by eager construction of all 5 folds, by
  lazy `create_folds`, and by each lazy fold build.
- Fold sizes 19,265 / 19,264 / 19,265 / 19,267 / 19,265, the delivered int64 folds.

**(2) End-to-end, MPS:** `scripts/d2_e2e.sh` → `runs/`, compared by `scripts/d2_compare.py` →
`e2e_comparison_output.txt`. **PASS.**
- AL, the `cell_cat` recipe: `--task next --engine check2hgi_v18 --model next_gru --embedding-dim 64
  --folds 5 --only-fold F --epochs 50 --seed 0 --batch-size 8192 --max-lr 0.0025 --logit-adjust-tau 0.5
  --no-checkpoints`, env `MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1`.
- Old clone (`f0fca061`) vs new clone (`f0fca061` + patch): same inputs, same env, one process at a time.

| run | per-epoch CSVs (train + val, every column, every epoch) | best F1 | peak RSS | max wired |
|---|---|---:|---:|---:|
| fold 0, old vs new | **identical** | 32.1061 / 32.1061 | 2.71 → **2.15 GB** | 9.2 → **7.9 GB** |
| fold 3, old vs new | **identical** | 29.8362 / 29.8362 | 2.86 → **2.15 GB** | 9.1 → **8.0 GB** |
| fold 0, old vs old (determinism control) | **identical** | 32.1061 / 32.1061 | 2.71 / 2.88 GB | 9.2 / 9.0 GB |

- **Patch exercised:** every run's log contains "Generating folds on the fly" (no frozen fold cache).
- **Memory:** even at AL's size (96k rows) the lean path saves about 0.6 GB RSS and 1.2 GB wired. At FL
  the saving scales with the dataset (≈ 4 folds × 2 copies × 2.94 GB).
- **Consistency:** fold 0's best F1 (32.1061) equals the G1 AL delivered-arm value measured on this Mac.

## Independent review (Fable, read-only): APPROVE WITH CHANGES, all addressed

- **Diagnosis confirmed and dominant.** `load_next_data`'s transient copies (≈ 3× dataset) become the
  new peak; they are freed at return. Fine on 32 GB.
- **Correct and minimal:**
  - no other `FoldCreator(` caller passes the flag, so the full 5-fold path and `freeze_folds.py` are unchanged;
  - SGKF uses its own RandomState;
  - no RNG is drawn in fold build (`RandomSampler` seeds in `__iter__`);
  - all consumers fit the lazy mapping;
  - the single-read fix is necessary;
  - `X` shares memory with `x_tensor`, so freeing it would gain nothing.
- **Changes requested and done:**
  - (1) the "Generating folds on the fly" assertion, added above;
  - (2) the delivered env vars, used.
- **Noted gaps, not defects:**
  - (i) the frozen-cache / `--folds-path` route (`rebuild_dataloaders`) is still eager. **Before any FL run,
    assert no signature-matching `folds/fold_indices_next.pt` exists on the FL engine paths.**
  - (ii) `_run_single_task` still materializes every *selected* fold, so `--only-folds` with many folds
    regains the footprint. Single-fold use is unaffected.

## Caveat: per-fold random state

Single-task has **no per-fold reseed**: `seed_everything` runs once, and `per_fold_seed` reaches only the
MTL runners. Under `--only-fold F`, fold F starts from the fresh seed. The delivered all-folds-in-one-process
run's fold F (F ≥ 1) inherits the state left by folds 0..F−1. So:
- only fold 0 under `--only-fold` follows the delivered fold's trajectory;
- old vs new remain exactly comparable, as shown;
- MPS vs CUDA rules out bitwise matching to delivered values.

## Not covered by this patch

`scripts/p1_region_head_ablation.py` (the region arm) has its own loader and already restricts to the
selected fold. But it still loads the full 576-column `dk_ovl` through `load_next_data` for
`--engine-override`, even with `--input-type region`. That is the next FL memory question: measure, or
propose a minimal fix with the same proof standard.
