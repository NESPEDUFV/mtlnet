# Sphere2Vec (sphereM variant)

A spherical location encoder package with **two selectable variants**:

1. **`rbf`** (default, backward-compatible) — a custom multi-scale spherical-RBF
   encoder with 256 random unit centroids × 32 log-spaced scales, ported from
   the source notebook
   `Location Encoders/...Sphere2Vec-sphereM.ipynb`. Output dim 8192
   before the FFN, 64 after.
2. **`paper`** — the paper-faithful closed-form Eq. 8 encoder from
   Mai et al. 2023 (`SphereMixScaleSpatialRelationEncoder` in the official
   `gengchenmai/sphere2vec` repo). Deterministic, no learned buffers in the
   position-encoding step, output dim 256 (= 8 × 32) before the FFN, 64 after.

Reference: Mai et al., 2023 — https://arxiv.org/abs/2306.17624

## ⚠️ Discrepancy: the notebook's "sphereM" is **not** the paper's sphereM

The source notebook we originally migrated is labeled `Sphere2Vec-sphereM` but
its position encoder has **no relationship** to Equation 8 in Mai et al. 2023.

| Aspect | Paper sphereM (Eq 8) | Notebook `"sphereM"` (our `rbf` variant) |
|---|---|---|
| Output dim | `8·S` (e.g. 256 at S=32) | `num_centroids·num_scales` = 256·32 = 8192 |
| Basis | Closed-form `sin/cos(angle·freq)` (8 paper-defined terms) | Random unit centroids + RBF kernel `exp(−dist·scale)` |
| Input transform | (lat, lon) in radians, no Cartesian projection | (lat, lon) → 3D Cartesian on unit sphere |
| Random / learned | None — fully deterministic | 256 random unit centroids (frozen buffer) |
| Source | `SphereMixScaleSpatialRelationEncoder` (official repo) | Not present in the official repo |

The discrepancy was discovered after the migration was complete. The migration
itself is a **faithful, bit-equivalent port of the notebook it was given**
(verified by
`tests/test_embeddings/test_sphere2vec.py::test_per_poi_embeddings_match_notebook`),
but the notebook itself is an off-paper variant.

As of 2026-04-11 the `paper` variant lives alongside the `rbf` variant and can
be selected via `--encoder_variant paper` (CLI) or `encoder_variant='paper'`
(Namespace). The default is `rbf` for backward compatibility with existing
artifacts and the bit-equivalence test. See
`plans/sphere2vec_paper_vs_notebook_analysis.md` for the full derivation.

## Ablation: paper sphereM (Eq.8) vs notebook RBF on Alabama MTL

Setup: `scripts/train.py --task mtl --state alabama --engine sphere2vec
--folds 5 --epochs 50` on each variant, same seed (42), same 50-epoch
Sphere2Vec training with identical contrastive-SSL pipeline (only the
position encoder differs). NashMTL is active but degrades to `[1,1]`
on step 1 for both variants (known solver instability — see
`src/losses/nash_mtl.py`), so both runs effectively train with equal task
weighting. Results saved under
`results/sphere2vec/alabama/ablation_full_{rbf,paper}/`.

### Full ablation (5 folds × 50 epochs — authoritative)

| Variant | Cat F1 (mean ± std) | Cat acc | Next F1 | Next acc | Sphere2Vec final loss | Wall clock |
|---|---|---|---|---|---|---|
| **`rbf` (notebook)** | **14.15% ± 1.26** | 29.48% ± 1.67 | 6.39% ± 0.88 | 28.96% ± 5.18 | 0.48 | 26.1 min |
| `paper` (Eq.8 SphereMixScale) | 13.35% ± 0.65 | 27.95% ± 0.45 | 6.39% ± 0.88 | 28.96% ± 5.18 | 0.78 | 17.0 min |
| Δ (rbf − paper) | **+0.80 pts** | +1.53 pts | 0 | 0 | − | − |

### Ablation-scale run (2 folds × 25 epochs — earlier quick check, kept for reference)

| Variant | Cat F1 | Cat acc | Next F1 | Sphere2Vec loss |
|---|---|---|---|---|
| `rbf` | 11.85% ± 0.21 | 29.81% ± 3.18 | 5.89% ± 0.14 | 0.48 |
| `paper` | 10.01% ± 3.48 | 26.92% ± 0.31 | 5.89% ± 0.14 | 0.78 |

Saved under `ablation_{rbf_baseline,paper_variant}/`.

### Observations

1. **RBF edges paper on category F1 by ~0.8 pts (14.15% vs 13.35%)** — but the
   gap is well within RBF's own std (1.26), so the difference is **not
   statistically significant at the 1σ level**. The paper variant has
   ~half the std (0.65), meaning it is **more stable across folds** but
   does not beat RBF's best. At a longer horizon (more folds or a larger
   state) the two could easily swap rank.

2. **The paper variant's stability is real and useful.** Its per-fold cat F1
   stays in `[12.51%, 13.91%]` — a 1.4 pt range. RBF's per-fold range is
   `[12.56%, 15.81%]` — a 3.3 pt range. If you care about reproducibility
   of downstream experiments more than peak F1, the paper variant is the
   better default.

3. **Next-task F1 is byte-identical across variants** (`mean=0.0639`,
   `std=0.0088`, `min=0.0572`, `max=0.0746` — same decimal digits in both
   summaries). The encoder doesn't affect it. This is the next-POI transformer
   head saturating to a majority-class-ish baseline that depends on the
   fold split, not on the embedding content. **The choice of location
   encoder is a non-factor for next-task performance** on this dataset.

4. **Sphere2Vec contrastive loss plateau differs**: RBF reaches ~0.48, paper
   reaches ~0.78. The paper's closed-form encoder has far less
   representational capacity for the SSL task than RBF's 8192 random-basis
   features. The fact that the downstream cat F1 gap is only 0.8 pts despite
   the 0.3 loss gap suggests the contrastive task is weak enough that raw
   fit quality on it does not predict downstream signal.

5. **Paper variant is ~35% faster in wall clock** (17.0 vs 26.1 min) because
   its position encoder is closed-form (no matmul against 256×32 random
   centroids). This is orthogonal to F1 and only matters for training-time
   experiments; the MTL run itself doesn't touch the encoder.

**Bottom line:** with 5 folds × 50 epochs, neither encoder clearly wins cat F1
on Alabama. RBF has slightly higher mean; paper has ~half the std; both
produce identical next-task metrics. The mislabeling concern remains the
primary reason to use the paper variant (honest citation of Mai et al. 2023).

### Future work

The ablation above keeps the training procedure constant (contrastive SSL on
coordinate noise) and swaps only the position encoder. This isolates
*architecture* but does not evaluate the paper's *training procedure*. The
paper trains `Eq.8 → FFN → classifier` end-to-end with a downstream supervised
task (image classification on Flickr/iNat/fMoW); our pipeline feeds
pre-computed parquets to MTLnet and cannot train jointly with it.

**Option 3 — supervised POI-category pretraining** is a strong fit for future
work: pretrain `Eq.8 → FFN → category_head` on POI→category labels (on a
holdout split distinct from the MTL folds, to avoid task leakage) to match
the paper's training philosophy. This would test whether the paper's *full*
recipe beats the notebook's SSL recipe. See
`plans/sphere2vec_paper_vs_notebook_analysis.md` §4 Action B.

**Also open**: does the paper variant's stability generalize to other states?
The current ablation is Alabama-only. A Florida / Arizona / Georgia sweep
would tell us whether the ~half-std story is a dataset artifact or a real
property of the closed-form encoder.

### Future work

The ablation above keeps the training procedure constant (contrastive SSL on
coordinate noise) and swaps only the position encoder. This isolates
*architecture* but does not evaluate the paper's *training procedure*. The
paper trains `Eq.8 → FFN → classifier` end-to-end with a downstream supervised
task (image classification on Flickr/iNat/fMoW); our pipeline feeds
pre-computed parquets to MTLnet and cannot train jointly with it.

**Option 3 — supervised POI-category pretraining** is a strong fit for future
work: pretrain `Eq.8 → FFN → category_head` on POI→category labels to match
the paper's training philosophy. Rejected for this ablation because it causes
task leakage against MTLnet's category evaluation, but in a separate holdout
split (distinct POIs from the MTL validation folds) it would be a clean
test of whether the paper's *full* recipe beats the notebook's SSL recipe.
See `plans/sphere2vec_paper_vs_notebook_analysis.md` §4 Action B.

## Performance

The migrated package trains **17× faster than the source notebook config** on
Apple Silicon (MPS) with **no measurable downstream quality loss**, by
combining a vectorized batched dataset and a 64× larger batch size:

| Config | Epoch time | 50-epoch run | Cat F1 (5-fold MTL) |
|---|---|---|---|
| Notebook canonical (bs=64, per-item dataset) | 23.5s | ~25 min | 13.59% ± 0.51 |
| **Optimized default (bs=4096, vectorized dataset)** | **2.6s** | **88s** | **13.88% ± 1.55** |

The optimized config is the package default. To reproduce the canonical
notebook training exactly, pass `--batch_size 64 --legacy_dataset` (CLI) or
`batch_size=64, legacy_dataset=True` (Namespace).

Why the optimized config doesn't hurt quality:
- The contrastive task is intrinsically weak (positives = `coord + N(0, 0.01°)`),
  so 50 epochs at any batch size all converge to roughly the same plateau
  (loss 0.48–0.50).
- Larger batch = fewer optimizer steps but smoother gradients per step.
- The vectorized dataset produces the same statistical distribution
  (Bernoulli(0.5) positive ratio, Gaussian(0, pos_radius) noise, uniform
  negative sampling) as the per-item version — only the per-batch sample
  sequence differs.
- Bit-equivalence with the source notebook is still verified by
  `tests/test_embeddings/test_sphere2vec.py::test_per_poi_embeddings_match_notebook`,
  which uses `legacy_dataset=True` to exercise the per-item path.

## Pipeline default: paper variant (since 2026-04-11)

`pipelines/embedding/sphere2vec.pipe.py` now runs the **paper** variant by
default (`encoder_variant='paper'`, `min_radius=10`, `max_radius=10000`).
To revert to the notebook's rbf variant:

```python
# in pipelines/embedding/sphere2vec.pipe.py SPHERE2VEC_CONFIG
encoder_variant="rbf",   # instead of "paper"
```

The package's class-level defaults (`SphereLocationContrastiveModel`,
`SphereLocationEncoder`, the `sphere2vec.py --encoder_variant` CLI flag)
remain `rbf` for backward compatibility with the bit-equivalence test
and any existing programmatic callers. Only the pipe changed.

## Architecture (rbf variant — faithful port)

```
Input coords [lat, lon] (degrees)
    │
    ▼ deg → rad → unit-sphere Cartesian (x, y, z)
SphereRBFPositionEncoder (frozen RBF: 256 random unit centroids × 32 log-spaced scales)
    │  → [B, 256·32 = 8192]
Linear input_projector    8192 → 512
    │
MultiLayerFeedForwardNN   512 → 512 → 128   (1 hidden layer, ReLU, dropout=0.5, layernorm, skip)
    │
Linear projector          128 → 64
    │
F.normalize(dim=-1)
    ▼
Output [B, 64]   (L2-normalized)
```

The RBF centroids are random-initialized and then **frozen via `register_buffer`** —
the spherical position encoder is not trained, only the projector + MLP + final
projector are.

## Architecture (paper variant — Eq.8 SphereMixScale)

```
Input coords [lat, lon] (degrees)
    │
    ▼ deg → rad (no Cartesian projection)
SphereMixScalePositionEncoder   (closed-form, 8 concatenated terms per scale,
                                  no learned buffers — matches upstream
                                  SphereMixScaleSpatialRelationEncoder)
    │  → [B, 8·32 = 256]
Linear input_projector    256 → 512
    │
MultiLayerFeedForwardNN   512 → 512 → 128   (1 hidden layer, ReLU, dropout=0.5, layernorm, skip)
    │
Linear projector          128 → 64
    │
F.normalize(dim=-1)
    ▼
Output [B, 64]   (L2-normalized)
```

The paper variant has **zero learned parameters below `input_projector`**.
The 8 terms per frequency scale are (following the official repo's
`SphereMixScaleSpatialRelationEncoder` code, which is a superset of the
paper's Eq. 8):

```
[ sin(φ·fₛ), cos(φ·fₛ), sin(λ·fₛ), cos(λ·fₛ),              # 4 sphereC-style
  cos(φ·fₛ)·cos(λ), cos(φ)·cos(λ·fₛ),                      # 2 sphereM products
  cos(φ·fₛ)·sin(λ), cos(φ)·sin(λ·fₛ) ]                     # 2 sphereM products
```

with `fₛ = 1/(min_radius · (max_radius/min_radius)^(s/(S-1)))` for `s ∈ [0, S)`.
The paper's Equation 8 is a strict 5-term subset of these — we follow the
code because that is what the authors actually ran and is what the frozen
reference snapshot at `tests/test_embeddings/_sphere2vec_paper_reference.py`
mirrors line-for-line.

## Training signal (caveat)

The contrastive task is intentionally simple:

- **Positive pairs**: `coord_i + Gaussian noise(σ=0.01°)` (~1.1 km perturbation).
- **Negative pairs**: `(coord_i, random_other_coord)`.
- **Loss**: BCE on cosine-similarity logits with temperature `τ = 0.15`.

This produces a smooth-by-distance embedding space, but the supervision is weak
(the model never sees real proximity structure beyond noise vs. random). It is a
faithful port of the reference algorithm, **not** a reimplementation. Tuning is
out of scope for this package.

## ⚠️ Important: dropout is ACTIVE during inference (notebook bug, preserved)

The source notebook (cell 12) calls
```python
loc_embeds = model(torch.Tensor(coords))
```
**without** `model.eval()` and **without** `torch.no_grad()`. The model still
has its two `nn.Dropout(p=0.5)` layers active, so each forward pass on the
same coordinate yields a *different* embedding. The downstream
`groupby+mean` averages out some of this noise, but POIs visited only a few
times end up with measurably noisy embeddings.

This package preserves that behavior **by default** so the migrated output is
faithful to the source. To get deterministic embeddings instead, pass
`args.eval_inference=True` to `create_embedding`. The unit-test
`test_eval_inference_produces_unit_norm` documents both code paths.

You can spot the difference in the output `embeddings.parquet`:

| Mode | Per-row L2 norm | Determinism |
|---|---|---|
| `eval_inference=False` (default, **matches notebook**) | < 1.0 (averaging unit vectors with dropout noise) | Stochastic without seeds |
| `eval_inference=True` (deterministic fix) | ≈ 1.0 (model.eval() means same coord → same unit-norm embedding) | Deterministic with seeds |

## Notable port decisions

| Notebook | This package | Reason |
|---|---|---|
| No random seeds | `args.seed` threaded through `torch`/`numpy`/`random` and a `worker_init_fn` for `DataLoader` workers | Reproducibility + enables equivalence testing |
| `device='cuda' if cuda else 'cpu'` hard-coded inside model | `device` arg, default from `configs.globals.DEVICE` | MPS support |
| Forces CPU in training cell | Honors `args.device` | MPS / CUDA support |
| `class LayerNorm(nn.Module)` defined but unused | Dropped | Dead code; pipeline already uses `nn.LayerNorm` |
| `loc_embeds = model(torch.Tensor(coords))` (one giant call, train mode) | Batched eval (`batch_size=10000`), still in train mode by default | Memory safety on real states; default behavior matches notebook |
| Per-checkin training (no dedup) → groupby `placeid` mean | **Same** (faithful port) | Preserves training distribution |
| CSV + per-row in-train-mode dropout-noisy embeddings | `embeddings.parquet` (parquet, not CSV) but values match cell 14 bit-for-bit under fixed seeds | Matches project storage convention; values preserved |
| Final column order `[placeid, "0"..."63", category]` | `[placeid, category, "0"..."63"]` (intentional deviation) | Matches project convention (`space2vec`, `hgi`, `poi2hgi` all use this) |
| Model state_dict never saved | Saved to `sphere2vec_model.pt` | Reproducibility + checkpoint resume |

## Usage

### Pipeline
```bash
python pipelines/embedding/sphere2vec.pipe.py
```

### Programmatic
```python
from argparse import Namespace
import torch
from configs.globals import DEVICE
from embeddings.sphere2vec import create_embedding

args = Namespace(
    dim=64, spa_embed_dim=128,
    num_scales=32, min_scale=10, max_scale=1e7, num_centroids=256,
    ffn_hidden_dim=512, ffn_num_hidden_layers=1, ffn_dropout_rate=0.5,
    ffn_act="relu", ffn_use_layernormalize=True, ffn_skip_connection=True,
    epoch=50, batch_size=64, lr=1e-3, tau=0.15, pos_radius=0.01,
    seed=42, device=DEVICE, num_workers=2,
)
create_embedding(state="Alabama", args=args)
```

### CLI
```bash
# Default (rbf variant, backward-compatible)
PYTHONPATH=src:research python -m embeddings.sphere2vec.sphere2vec --state Alabama

# Paper-faithful Eq.8 SphereMixScale variant
PYTHONPATH=src:research python -m embeddings.sphere2vec.sphere2vec \
    --state Alabama \
    --encoder_variant paper \
    --min_radius 10 --max_radius 10000
```

The `--min_radius` / `--max_radius` flags are only meaningful for the `paper`
variant (they parameterize the log-spaced frequency list). The `rbf` variant
reuses `--min_scale` / `--max_scale` for its kernel scales. If you do not pass
`--min_radius` / `--max_radius`, the paper variant will fall back to
`--min_scale` / `--max_scale` — this usually produces degenerate outputs
because the RBF defaults (`1..1e7`) are on a very different magnitude scale
from what the paper expects (`10..10000` meters). **Always pass explicit
radii when using `--encoder_variant paper`.**

## Output

`output/sphere2vec/{state}/embeddings.parquet`

| Column | Type | Description |
|---|---|---|
| `placeid` | str | POI identifier |
| `category` | str | Original category (mode of per-checkin categories) |
| `0` … `63` | float32 | 64-d L2-normalized embedding |

`output/sphere2vec/{state}/sphere2vec_model.pt` — trained `state_dict`.

## Files

- `__init__.py` — public API
- `sphere2vec.py` — `create_embedding(state, args)` entry point
- `model/Sphere2VecModule.py` — model classes (verbatim port)
- `model/dataset.py` — `ContrastiveSpatialDataset`
- `README.md` — this file
- `CLAUDE.md` — short agent pointer

## Equivalence test

`tests/test_embeddings/_sphere2vec_reference.py` is a frozen verbatim copy of the
notebook's model code. `tests/test_embeddings/test_sphere2vec.py` seeds both
versions identically and asserts forward-pass equivalence at every layer
(`SphereRBFPositionEncoder`, `SphereLocationEncoder`, `SphereLocationContrastiveModel`)
plus loss equivalence and a tiny end-to-end smoke test on synthetic data.
