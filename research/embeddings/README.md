# `research/embeddings/` — embedding engines for MTLnet

Each subdirectory is a self-contained embedding engine that produces a
parquet of POI (or per-checkin) feature vectors consumed by the MTLnet
training pipeline. They share a uniform contract:

1. A top-level `create_embedding(state, args)` entry point.
2. Output written to `output/<engine>/<state>/embeddings.parquet`.
3. Schema `[placeid, category, "0", ..., "{dim-1}"]` for POI-level engines.
4. Registered in `EmbeddingEngine` (`src/configs/paths.py`) and routed by
   `IoPaths`.

| Engine | Level | Description |
|---|---|---|
| `dgi/` | POI | Deep Graph Infomax — 64-dim |
| `hgi/` | POI | Hierarchical Graph Infomax — 256-dim |
| `poi2hgi/` | POI | HGI variant with temporal POI features |
| `check2hgi/` | check-in | HGI applied to per-checkin context |
| `space2vec/` | POI | Sinusoidal grid-cell location encoder |
| **`sphere2vec/`** | **POI** | **Spherical-RBF location encoder** *(added in this session — see below)* |
| `time2vec/` | check-in | Temporal sin/cos encoder |
| `hmrm/` | POI | Heterogeneous Mobility Representation Model |

This document focuses on **what we built and decided during the
Sphere2Vec migration**, since that's the most recent and most thoroughly
documented engine. For deeper technical detail on Sphere2Vec, see
`sphere2vec/README.md` and `sphere2vec/CLAUDE.md`.

---

## Sphere2Vec migration — knowledge transfer

### What it is

Sphere2Vec-sphereM (Mai et al., 2023, [arxiv 2306.17624](https://arxiv.org/abs/2306.17624))
is a location encoder that maps `(lat, lon)` coordinates through a fixed
multi-scale RBF kernel defined on the unit 3-sphere, then through a small
MLP. The position encoder itself is **frozen** (random unit centroids on
the sphere stored as a buffer); only the input projector + MLP + final
projector are trained.

> ⚠️ **Architectural discrepancy with the original paper.** The
> `sphere2vec/` package migrates a Colab notebook labeled "Sphere2Vec-sphereM"
> whose position encoder has **no relationship** to Equation 8 in Mai et al.
> 2023 — it is a custom random-RBF-on-sphere encoder. As of 2026-04-11 the
> package also exposes a paper-faithful `SphereMixScalePositionEncoder`
> (the official `SphereMixScaleSpatialRelationEncoder` from
> `gengchenmai/sphere2vec`), selectable via `--encoder_variant paper`.
> Default stays `rbf` for backward compatibility. See
> `sphere2vec/README.md` for the ablation table and
> `plans/sphere2vec_paper_vs_notebook_analysis.md` for the full derivation.

The training objective is contrastive BCE on cosine similarity:
- **Positive pairs**: `(coord_i, coord_i + N(0, 0.01°))` — same point with
  ~1.1 km Gaussian noise.
- **Negative pairs**: `(coord_i, random_other_coord)`.

This is intentionally a weak signal — the model learns "nearby coordinates
have similar embeddings" and not much more. We document this caveat
loudly in `sphere2vec/README.md` because the downstream F1 numbers reflect
the limitation, not a migration bug.

### How to run it (quick start)

```bash
# Single state, default config (bs=4096, fast vectorized dataset, MPS)
python pipelines/embedding/sphere2vec.pipe.py
# (edit STATES = ['Alabama'] at the top to limit)

# CLI for one-off runs
python -m embeddings.sphere2vec.sphere2vec --state Alabama
PYTHONPATH=src:research python -m embeddings.sphere2vec.sphere2vec --state Florida --epoch 100

# Train MTLnet on the resulting embeddings
python scripts/train.py --task mtl --state alabama --engine sphere2vec
```

Outputs land at `output/sphere2vec/{state}/embeddings.parquet` and the
trained checkpoint at `output/sphere2vec/{state}/sphere2vec_model.pt`.

### What we built end-to-end

1. **Self-contained package** at `research/embeddings/sphere2vec/`:
   - `model/Sphere2VecModule.py` — verbatim port of every model class
     from the source notebook, with three deliberate divergences listed
     below.
   - `model/dataset.py` — two dataset classes (legacy per-item and fast
     vectorized).
   - `sphere2vec.py` — `create_embedding(state, args)` entry point.
   - `README.md` and `CLAUDE.md` — package-level docs.

2. **Wiring into the project**:
   - `EmbeddingEngine.SPHERE2VEC` enum + `_Sphere2VecIoPath` in
     `src/configs/paths.py`.
   - POI-level validation in `src/configs/embedding_fusion.py`.
   - Pipeline runner at `pipelines/embedding/sphere2vec.pipe.py`
     (mirrors `space2vec.pipe.py`, additionally generates downstream
     category + next-from-poi inputs).

3. **Test suite** at `tests/test_embeddings/`:
   - `_sphere2vec_reference.py` — frozen verbatim snapshot of the
     notebook model code (the equivalence oracle, never modified).
   - `test_sphere2vec.py` — 17 tests:
     - 7 layer-level forward equivalence tests (position encoder, location
       encoder, full contrastive model, contrastive loss, dataset)
     - 6 fast-dataset contract tests (shape, dtype, anchor, Bernoulli
       ratio, noise bounds, DataLoader integration)
     - 2 smoke tests (notebook mode + eval mode)
     - 1 **strong end-to-end equivalence test** that runs both an inline
       port of notebook cells 8/11/12/14 and the migrated `create_embedding`
       under locked seeds, asserting per-POI embedding bit-equality
       (`atol=1e-6`).

4. **Real-data validation**: trained on Alabama (113k checkins, 11.7k
   unique POIs), then ran 5-fold MTL training. Final cat F1 is
   statistically tied with the notebook author's own CSV output and
   with my own baseline runs.

---

## Key decisions and the reasoning

### 1. POI-level output, not per-checkin

The notebook's cell 14 contains the intent:

```python
df_mean_embeds = df_location_embeddings.groupby("placeid")[embed_cols].mean().reset_index()
```

…but the dev's saved CSV happened to be the *pre-groupby* per-checkin
intermediate. We discovered this by inspection (93,402 rows for Alabama,
with the same `placeid` repeating up to 963 times) and confirmed with the
user that **POI-level is the desired output**.

`sphere2vec.py` reproduces the cell 14 intent: forward-pass all checkins
through the model (one row per visit), then `groupby("placeid").mean()`
the embeddings and `mode()` the categories. The result is one row per
unique POI, which matches the project's POI-level engine convention
(same as `space2vec`, `dgi`, `hgi`, `poi2hgi`, `hmrm`).

This is the right call for sphere2vec specifically because **the model is
a pure function of `(lat, lon)`** — the same POI always maps to the same
underlying coordinate, so per-checkin storage would be ~10× redundant
duplication of the same embedding (under deterministic inference) or
~10× different dropout samples of the same vector (under train-mode
inference, see decision #2).

### 2. Inference defaults to **train mode** (dropout active), not eval mode

The notebook (cell 12) calls
```python
loc_embeds = model(torch.Tensor(coords))
```
without `model.eval()` and without `torch.no_grad()`. The output tensor
has `grad_fn=<DivBackward0>`, proving the autograd graph is alive and the
two `nn.Dropout(p=0.5)` layers are **active during inference**.

This is a notebook bug from a software-engineering standpoint (almost no
ML codebase runs inference with dropout active), but it materially
affects the per-POI embedding distribution. We empirically verified
that:

- `eval_inference=False` (notebook-faithful): per-checkin forward
  produces unit-norm vectors, but each call is a different stochastic
  sample. After `groupby+mean`, per-POI norms are 0.15–1.0 (median ~0.5
  on Alabama).
- `eval_inference=True` (deterministic fix): per-checkin forward is
  deterministic, so the per-POI mean of identical unit vectors is itself
  unit norm. All norms = 1.0.

We ran the **same model checkpoint** through both inference modes and
trained MTL on each. The notebook-faithful mode was empirically **better**:

| Mode | cat F1 | cat acc |
|---|---|---|
| `eval_inference=False` (default) | 13.59% ± 0.51 | 30.64% ± 2.63 |
| `eval_inference=True`            | 12.35% ± 0.66 | 31.71% ± 1.13 |

Removing the dropout noise lets the classifier collapse onto the
dominant classes more efficiently — accuracy goes up but macro F1
goes down. **The dropout noise is acting as implicit regularization for
the downstream classifier.**

We default to `eval_inference=False` for two reasons:
1. It's faithful to the source notebook (matches the equivalence
   guarantee of the bit-equality test).
2. It empirically produces a slightly better-balanced downstream
   classifier.

`eval_inference=True` is available as an opt-in for users who want
deterministic, unit-norm embeddings.

### 3. Two dataset implementations: keep the legacy for tests, ship the fast one for runtime

The notebook's `ContrastiveSpatialDataset.__getitem__` does ~4 Python
operations per sample (random Bernoulli, random normal, 3 tensor
allocations). For Alabama at bs=64, this is ~17M Python calls per
training run. The vectorized `FastContrastiveSpatialDataset` implements
PyTorch ≥2.0's `__getitems__` to do the same logic in batched tensor ops.

| Dataset | Epoch time @ bs=64 | Epoch time @ bs=4096 |
|---|---|---|
| `ContrastiveSpatialDataset` (per-item) | 23.5s | n/a (would benefit less) |
| `FastContrastiveSpatialDataset` (vectorized) | similar | **2.6s** |

The fast version is the default. **The legacy version is kept for two
reasons**:

1. The bit-equality test against the notebook reference
   (`test_per_poi_embeddings_match_notebook`) needs the per-item dataset
   to match the notebook's exact random call sequence. Without it, we
   can't guarantee the migration is faithful.
2. Users who need 100% notebook reproduction can pass `legacy_dataset=True`.

The two implementations produce the **same statistical distribution** of
sample pairs (Bernoulli(0.5) positive ratio, Gaussian(0, pos_radius)
noise, uniform negative sampling) but in a different per-batch sequence,
so the resulting trained models are statistically equivalent but not
bit-equal across full-training runs.

### 4. Default `batch_size=4096` (was 64 in the notebook)

Profiling on MPS revealed:
- Per-batch dispatch overhead is ~13ms regardless of batch size.
- At bs=64 dispatch is ~96% of per-batch time → 12 batch/s.
- At bs=4096 dispatch is ~15% → 10 batch/s but 64× more samples per
  batch → **9× compute speedup**.

Empirical 50-epoch results on Alabama:
- bs=64: 25 min, final loss 0.483
- bs=4096: 88s, final loss 0.504

The +0.02 final loss gap is the expected trade-off of large-batch
training (~66× fewer optimizer steps). It does **not** translate to
downstream F1 regression — the cat F1 is statistically tied (13.88% vs
13.59%, both within fold-level std).

We default to bs=4096 because the speedup is huge (17× embedding
training, 3.34× end-to-end) and the quality is preserved on the only
real-data benchmark we ran. Larger batches were not tested because the
gain plateaus past bs=4096 (compute-bound).

### 5. MPS, not CPU

Despite the small model and tiny batch sizes, MPS is **faster than CPU at
every batch size we tested** on Apple Silicon:

| Config | MPS | CPU |
|---|---|---|
| bs=64 | 23.5s | 27.7s |
| bs=1024 | 3.9s | 7.3s |
| bs=4096 | 2.6s | 6.6s |

The user's intuition that CPU "might be faster at small batches" was
not borne out. We default to `DEVICE` (auto-detected MPS on macOS), and
the documentation reflects the measured numbers.

### 6. We added seeding (`seed_everything` + `worker_init_fn`)

The notebook sets no seeds at all. Two consequences:
- The 256 random unit centroids in `SphereRBFPositionEncoder` differ across
  runs.
- The dropout pattern during training and inference differs.

We added `seed_everything(args.seed)` (Python `random` + `numpy` + `torch`)
in `create_embedding`, plus a `_worker_init_fn` that propagates a
deterministic seed to each `DataLoader` worker (because the dataset uses
the global numpy RNG, and child workers fork-inherit a copy without
re-seeding).

Reproducibility is now end-to-end deterministic given a fixed `seed`,
which made the bit-equality test possible.

### 7. We do **not** save per-checkin intermediates

The notebook's saved CSV contains per-checkin rows (apparently a
debugging dump from before the cell-14 groupby). We only save the
per-POI parquet because:

- The downstream MTL pipeline expects POI-level inputs.
- For sphere2vec specifically, per-checkin storage is information-redundant
  (the model is a pure function of `(lat, lon)`).
- A separate per-checkin output would double disk usage with no benefit.

If this is ever needed (e.g., for debugging dropout variance), we'd add
an opt-in `--save-checkin-embeddings` flag rather than make it the
default.

---

## Bugs we uncovered in shared infrastructure (and fixed)

The migration's real-data validation runs uncovered two latent bugs in
project-wide MTL infrastructure. Both are now fixed on `main`.

### Bug 1: `src/data/folds.py` MTL category split crashed with `num_samples=0`

**Symptom**: First MTL run on sphere2vec embeddings crashed at fold 1
with `ValueError: num_samples should be a positive integer value, but
got num_samples=0`. The fold log showed `Category: train=0, val=0`
despite the user-based POI splitter correctly producing
`train_excl=5902, ambiguous=4937`.

**Root cause**: dtype mismatch. `category.parquet` stores `placeid` as
`str` (sphere2vec, space2vec — both `.astype(str)` per the notebook
convention). `build_poi_user_mapping` returns the in-memory mapping with
`int` keys (raw checkins are `int64`). `np.isin(str_array, int_set)`
returns all-False, so no placeids matched and the category fold became
empty.

**Why it stayed dormant**: nobody had ever run `--task mtl` against
`space2vec` (the only other engine that stores str placeids), and HGI/DGI
have no `placeid` column at all so they hit a different code path
(legacy `StratifiedKFold` per-task).

**Fix**: defensive str-coercion at the comparison site in
`folds.py:_create_mtl_folds` (≈12 lines around line 606). Both sides cast
to str before `np.isin`. Works for str, int64, and any future dtype.
Validated by 79/79 data tests.

### Bug 2: `src/losses/nash_mtl.py` crashed on MPS with cross-dtype error

**Symptom**: After fixing bug #1, MTL training crashed at the very first
step with
```
TypeError: unsupported operand type(s) for *: 'Tensor' and 'Tensor'
```
…on `losses[i] * alpha[i]` in `nash_mtl.py`. The notebook-mode embedding
runs worked, but the eval-mode embeddings consistently triggered the
crash.

**Root cause**: cvxpy's solver returns numpy `float64` after a multi-iter
solve (the initial `prvs_alpha` is `float32` per the constructor, but
once `self.alpha_param.value` is reassigned mid-loop, it becomes
`float64`). On MPS, multiplying `float32` (loss tensor) against `float64`
(alpha) errors with the misleading "Tensor vs Tensor" message because
**MPS does not support `float64`**.

**Why it stayed dormant**: notebook-mode embeddings produce dropout-noisy
gradients with a "soft" Gram matrix that the cvxpy solver converges in
one iteration → `_stop_criteria` fires before the float64 reassignment →
`prvs_alpha` stays `float32`. Eval-mode embeddings produce a stiffer
Gram matrix that takes multiple iterations → bug triggered.

**Fix (this session)**: cast alpha to `losses.dtype` and place on
`losses.device` via `torch.as_tensor(alpha_np, dtype=losses.dtype,
device=losses.device)`. Handles both the if-branch (newly solved alpha)
and the else-branch (warm-start prvs_alpha).

**Further hardened in [PR #7](https://github.com/VitorHugoOli/.../pull/7)**:
the user added solver fallback (ECOS → SCS), explicit `cp.error.SolverError`
catching with structured logging, and NaN-detection for degenerate Gram
matrices. The original upstream code had a bare `except:` that silently
degraded NashMTL into fixed `[1, 1]` weights — that's now caught and
logged.

---

## Quality numbers (Alabama, 5-fold MTL, 50 epochs)

These are the empirical results from validating the migration end-to-end.
They should serve as a regression baseline for any future change to the
sphere2vec embedding code.

| Source | cat acc | cat F1 | next acc | next F1 | total time |
|---|---|---|---|---|---|
| Notebook author's CSV (10,269 POIs) | 29.72% ± 2.31 | 13.80% ± 1.46 | 34.16% | 7.27% | n/a |
| **Our migration, notebook-mode (bs=64)** | **30.64% ± 2.63** | **13.59% ± 0.51** | 34.16% | 7.27% | 47 min |
| Our migration, eval-mode (bs=64) | 31.71% ± 1.13 | 12.35% ± 0.66 | 34.16% | 7.27% | 47 min |
| **Our migration, optimized (bs=4096)** | **27.92% ± 1.04** | **13.88% ± 1.55** | 34.16% | 7.27% | **14 min** |

Three observations from these runs:

1. **Cat F1 is statistically tied across all 4 runs** (12.35% to 13.88%, all
   within ±1 std). The migration is empirically faithful to the source.
2. **Next-task is byte-equal-dead in all runs** (best_epoch=0 in every
   fold). Sphere2vec carries no useful next-POI signal regardless of how
   it's trained or which inference mode is used. This is the model's
   limitation, not a bug.
3. **The optimized bs=4096 run is 3.34× faster end-to-end** with no F1
   regression — actually a small (insignificant) improvement.

---

## How we'd add a *new* embedding engine (lessons from this migration)

1. **Check the source's intended output level** (POI vs check-in) before
   you start. The notebook's cell 14 shows the intent even if the saved
   file is something else.
2. **Verbatim-port the model code first** with no "improvements". Save the
   verbatim copy as a frozen snapshot under `tests/test_embeddings/`.
   Future drift is measured against this oracle.
3. **Add seeding even if the source has none**. Without deterministic
   buffers and dropout patterns, the bit-equality test cannot work.
4. **Layer the equivalence tests bottom-up**: position encoder → location
   encoder → full model → loss → dataset → end-to-end pipeline. Each
   layer is its own unit test. The end-to-end test ports the source's
   training/inference cells inline and asserts bit-equal output under
   shared seeds.
5. **Run `--task mtl` end-to-end** on a real state before declaring the
   migration done. Synthetic smoke tests will not surface latent
   infrastructure bugs (we found two on sphere2vec's first MTL run).
6. **Profile before optimizing**. We saw a 17× speedup from changing
   defaults that weren't even on our radar until we measured per-batch
   dispatch time.
7. **Keep both fast and faithful paths**. The fast version becomes the
   default; the faithful version backs the equivalence oracle.

---

## Pointers

- `sphere2vec/README.md` — package-level docs (architecture, output
  schema, performance section, dropout-during-inference warning, full
  list of port decisions).
- `sphere2vec/CLAUDE.md` — short agent-facing pointer for when an LLM
  needs to navigate the package.
- `tests/test_embeddings/test_sphere2vec.py` — 17 tests covering
  forward equivalence, fast-dataset contract, smoke tests, and
  end-to-end pipeline equivalence.
- `tests/test_embeddings/_sphere2vec_reference.py` — frozen verbatim
  snapshot of the source notebook model code. **Do not modify.**
- `pipelines/embedding/sphere2vec.pipe.py` — multi-state pipeline runner
  with the canonical default config.
- `src/configs/paths.py` — `EmbeddingEngine.SPHERE2VEC` enum and
  `_Sphere2VecIoPath` registration.
- `src/configs/embedding_fusion.py` — POI-level validation list.

For relevant commits, see `git log --grep=sphere2vec`.
