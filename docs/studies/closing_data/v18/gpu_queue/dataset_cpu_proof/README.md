# D2b: blocking CPU→MPS batch copy for the single-task path: proof package (2026-10-04)

**Patch:** `../d2b_mps_blocking_copy.patch`, against HEAD `c0f1e61c` (which already contains D2, `ab92d07d`).
4 files, +21/−12. **Not applied.** `git apply --check` is clean.

## Why

The FL G1 arm hit kernel critical pressure at training start, when the fold tensors were pre-moved to
MPS (`../d2_proof/`, and the 10-04 00:11 trace). The existing switch `MTL_DATASET_CPU=1` keeps them
CPU-resident. Its docstring called that "byte-identical … verified", **but that was verified on CUDA**.

On MPS, at HEAD, `MTL_DATASET_CPU=1` **corrupts the labels.** AL f0 `cell_cat` crashed after 8 s:
`Detected more unique values in target than expected. Expected only 7 but found 1403 … tensor([-2147450368, …`
(`runs/cpu_f0/failure_excerpt.txt`).

**Cause.** The train and val loops copy each batch CPU→MPS with `.to(device, non_blocking=True)`.
- The source is a fresh pageable `index_select` temporary from `POIDataset.__getitems__`.
- It isn't pinned: `pin_memory` is CUDA-only.
- `X_batch = X_batch.to(...)` rebinds the name, so the CPU source can be freed while the asynchronous
  copy is still pending.
- **That lifetime mechanism is inferred, not instrumented.** The proof is the one-line A/B below: the
  only difference between the crashing and the clean run is the `non_blocking` value.
- There is in-tree precedent: `research/baselines/stan/train.py` already uses `non_blocking=torch.cuda.is_available()`.
- **Labels are only the visible symptom.** Corrupted *features* would train silently, with no exception. The
  guarantee therefore rests on the byte-identity A/B, not on "no crash".

## Patch

1. **`non_blocking=True` → `non_blocking=(device.type == "cuda")`** on the single-task path:
   - `src/training/runners/_single_task_train.py`: train loop (X, y) and val loop (X, y);
   - `src/training/shared_evaluate.py`: X;
   - `src/training/runners/next_cv.py`: eval, X.
   - That covers every CPU→MPS batch copy that training and the scored validation go through
     (`next_cv.run_cv` → `next_trainer.train` → `train_single_task` → `shared_evaluate.evaluate` →
     `_extract_diagnostics`). The remaining moves on the path are blocking or on retained tensors
     (Fable review below).
2. **`src/data/folds.py`: comments only** (AST with docstrings stripped is identical to HEAD).
   - The `_dataset_device` docstring and the `_get_num_workers` comment no longer claim MPS byte-identity.
   - They now say: byte-identical on CUDA; on MPS only via the blocking single-task copy (D2b); MTL not covered.

**Unchanged by construction:**
- **CUDA:** `device.type == "cuda"` is True, so the call is identical.
- **The default GPU-resident path on MPS:** `_dataset_device` returns `DEVICE`, so the tensors are already
  resident. **Note the guard:** `if X_batch.device != device:` does **not** skip on MPS, because
  `device(type='mps')` ≠ `device(type='mps', index=0)`. So `.to()` *is* called, and it returns the **same
  object** (same `data_ptr`, verified on this Mac). It is a no-op whatever `non_blocking` says.

## Proof (AL v18, `cell_cat` `--only-fold 0`, MPS, env `MTL_NO_TRAIN_DIAGNOSTICS=1 MTL_DISABLE_AMP=1`)

- **Probe** (`probe_device_output.txt`, `scripts/probe_device.py`): without the switch the fold-0 loader
  tensors are on `mps:0`; with `MTL_DATASET_CPU=1`, `_dataset_device(0)=None` and they are on `cpu`. So the
  batch-copy path is exercised.

| run | code | `MTL_DATASET_CPU` | result | best F1 | peak RSS | max wired |
|---|---|---|---|---:|---:|---:|
| `base_f0` | HEAD | unset | rc 0 | 32.1061 | 2.15 GB | 8.8 GB |
| `cpu_f0` | HEAD | 1 | **crash, corrupted labels** | — | — | — |
| `base_f0_patched` | HEAD + D2b | unset | rc 0, **per-epoch train+val CSVs byte-identical to `base_f0`** (cmp) | 32.1061 | 2.15 GB | 8.6 GB |
| `cpu_f0_patched` | HEAD + D2b | 1 | rc 0, **per-epoch train+val CSVs byte-identical to `base_f0`** (cmp) | 32.1061 | 2.21 GB | 8.6 GB |

- `base_f0` is also byte-identical to the committed D2 proof's `new_f0`.
- **Memory at AL scale:** no visible difference, because AL's fold tensors are only about 0.2 GB. At FL the
  switch removes about 2 × 2.94 GB of wired memory at training start.
- The race is per-batch and size-independent, so a second fold adds nothing for this defect.
- Records: `runs/*/` (`RUN.txt`, `mem.log`, `metrics/`), `comparison_output.txt`, `scripts/`.

## Independent review (Fable, read-only): APPROVE WITH CHANGES (write-up only; the patch needs no edit)

Its findings:
- The diff hunks equal the patch file; the AST check holds; the records match the narrative.
- **Diagnosis plausible and pinned by the A/B.** No alternative survives: class weights and logit-adjust
  both `.cpu()` their targets.
- **The single-task path is fully covered.**
- **The default and CUDA paths are unchanged.**

The changes it asked for are all in this README:
1. **`MTL_DATASET_CPU=1` on MPS is validated ONLY for single-task (`--task next` / `category`) with D2b.**
   MTL on MPS with it is unverified and would hit the same bug: `mtl_cv.py` (about lines 1559–1565),
   `mtl_eval.py` (254–259) and `mtl_validation.py` still use `non_blocking=True`. They're safe today: the
   default on MPS is pre-moved, so they're a no-op, and on CUDA they're safe. But they're a trap. *Optional
   follow-up, not in D2b:* a one-line WARN in `_dataset_device` when `MTL_DATASET_CPU=1` and DEVICE is MPS.
2. **Two other same-pattern sites outside the path, unpatched:**
   - `src/training/evaluate.py:50`, used only by `scripts/evaluate.py` for checkpoint evaluation;
   - `experiments/scripts/bench_time2vec_configs.py:59-61`.
   They don't affect current runs.
3. **The region arm gets no relief from this switch.** `scripts/p1_region_head_ablation.py` builds
   `POIDataset(x, y, device=DEVICE)` directly and ignores `MTL_DATASET_CPU`. **FL region arms are not made
   to fit by this knob.** That needs its own measurement or change, the open `p1` question.
4. The lifetime mechanism is inferred; the proof is the A/B. Stated above.

## Back-audit (no Mac MPS evidence run exposed)

- **`train.py` runs:** `MTL_DATASET_CPU` was never set (drivers, env dumps, logs, shell env and profiles all
  grepped, with a positive control). `_get_num_workers()` returns 0, so data is pre-moved. This covers
  G1 AL/AZ cat, G2 scoring, G3 `istanbul_pair`, D2, and the FL attempts.
- **`p1`:** pre-moved, no per-batch CPU→MPS copy.
- **`b3_hmt_grn.py` and `build_ctle_substrate.py`:** blocking `.to(device)`.
- The only scripts that set the switch are A40/H100 gate drivers (CUDA).
