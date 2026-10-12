# MTL v17: Complete Architecture and Training Specification

## 1. Scope and source of truth

This document describes the best final joint model used for the dissertation and the MobiWac result board. It covers only the active v17 path: the `check2hgi_dk_ovl` input build, `mtlnet_crossattn_dualtower`, the `next_gru` category head, the `next_stan_flow_dualtower` region head, and the training and evaluation protocol that produced the final six-dataset results.

Historical model variants, failed ablations, unused routing mechanisms, alternative loss balancers, and inactive experimental switches are intentionally omitted. They are not part of the v17 model.

The operational definition is:

> **MTL v17 = the v16 dual-tower champion topology, batch size 8192, and a corrected per-parameter-group OneCycle schedule that keeps the category peak learning rate at 1e-3 instead of silently broadcasting 3e-3 to every group.**

The paper-grade runs use `--canon none` followed by an explicit recipe. This matters because the current `--canon v17` code bundle points to the non-overlap v14 engine, whereas the final result board uses the overlap-gated `check2hgi_dk_ovl` engine. The explicit commands below are therefore the result provenance, not merely a convenient alias.

## 2. Prediction problem

The model performs two sequence-classification tasks jointly:

| Slot | Task | Input at each historical visit | Output space | Primary metric |
|---|---|---|---|---|
| A | Next category | 64-dimensional Check2HGI check-in representation | 7 top-level POI categories | macro-F1 |
| B | Next region | 64-dimensional Check2HGI region representation | dataset-specific region classes | full Acc@10 |

The region label spaces in the final evaluation are 520 mahalle for Istanbul and 1,109, 1,547, 4,703, 6,553, and 8,501 regions for Alabama, Arizona, Florida, Texas, and California, respectively.

Each example contains nine historical visits and predicts the label of the following visit. The `check2hgi_dk_ovl` build uses stride 1, requires at least 10 check-ins per user, and does not emit incomplete tail windows. Its representations come from the design-k Check2HGI build, while its prediction windows are rebuilt with this overlap-gated protocol.

Padding rows are identified by the configured sentinel before encoding, replaced with zeros, supplied as key-padding masks to attention, and zeroed again before the sequential heads.

## 3. End-to-end forward path

```text
Category sequence [B, 9, 64]              Region sequence [B, 9, 64]
             |                                         |
   category-specific MLP                      region-specific MLP
             |                                         |
             +-------- [B, 9, 256] each ---------------+
                               |
                2 bidirectional cross-attention blocks
                  category reads region; region reads category
                               |
              separate final LayerNorm for each stream
                    |                            |
       category stream [B,9,256]       region stream [B,9,256]
                    |                            |
             2-layer GRU                 shared STAN tower
                    |                            |
              7-class logits             shared feature [B,128]
                                                 |
raw region sequence [B,9,64] -> private STAN -> private feature [B,128]
                                                 |
                       private + beta * projection(shared)
                                                 |
                                dataset-region logits
```

### 3.1 Task-specific input encoders

There are two independent encoders, one for each task. No encoder weights are tied. Each encoder maps every 64-dimensional visit vector to 256 dimensions using:

```text
Linear(64,256) -> ReLU -> LayerNorm(256) -> Dropout(0.1)
Linear(256,256) -> ReLU -> LayerNorm(256) -> Dropout(0.1)
Linear(256,256) -> ReLU -> LayerNorm(256)
```

The constructor names this `num_encoder_layers=2`, but the implementation adds a final output projection after the two hidden blocks. The exact active graph therefore contains three linear transformations per task encoder.

### 3.2 Bidirectional cross-attention interaction stack

The encoded task streams enter two `_CrossAttnBlock` instances. Their active dimensions are:

| Property | v17 value |
|---|---:|
| Stream width | 256 |
| Number of blocks | 2 |
| Attention heads per direction | 4 |
| Feed-forward hidden width | 256 |
| Block dropout | 0.15 |

For category stream `a` and region stream `b`, each block computes:

```text
a1 = LN_a1(a + MHA_ab(query=a, key=b, value=b))
b1 = LN_b1(b + MHA_ba(query=b, key=a1, value=a1))
a2 = LN_a2(a1 + FFN_a(a1))
b2 = LN_b2(b1 + FFN_b(b1))
```

The update is bidirectional but ordered: the region-side attention reads the already updated category stream. Both streams then continue to the next block. The v17 path uses full forward and backward coupling: key/value detachment, directional stop-gradient, identity attention, disabled attention, zeroed category key/value tensors, and learned cross-attention gates are all off.

Each direction has its own `MultiheadAttention`, LayerNorms, and feed-forward network. The two tasks do not reuse the same attention projections or FFN weights.

### 3.3 What is hard-shared, exactly

Calling the model either purely hard-sharing or purely soft-sharing loses an important distinction.

At the strict layer-reuse level, v17 is **not classical hard parameter sharing**. It does not pass both tasks through one common encoder or one common FFN. The category and region encoders are separate, `MHA_ab` and `MHA_ba` are separate, `FFN_a` and `FFN_b` are separate, and the two heads are separate.

There is nevertheless a **partial hard-shared interaction subsystem** in the implementation and optimization contract:

- The same `crossattn_blocks` stack jointly transforms the tuple `(category_stream, region_stream)` on every forward pass.
- The model exposes the complete cross-attention stack and the two final stream LayerNorms through `shared_parameters()`.
- AdamW places that set in one named `shared` parameter group.
- The scalar joint loss is backpropagated once through the complete graph. Consequently, gradients from the two task losses meet in this coupled interaction subsystem and can also cross into the opposite task stream through attention.

The most precise classification is therefore:

> **Hybrid asymmetric MTL: task-private encoders and heads, a jointly optimized bidirectional interaction module, content-based cross-task exchange, and an additional region-private tower.**

If “hard sharing” is restricted to identical primitive weights being reused independently by both tasks, the amount is zero. If it means a fixed trainable subsystem owned by both tasks and updated through the joint objective, the cross-attention stack is the model's partial hard-shared component. This dual statement reconciles the source-code docstring, which says that the per-stream FFNs are not shared, with the optimizer API, which explicitly names the interaction stack `shared`.

### 3.4 Category head

The category stream is processed by `next_gru`:

```text
GRU(input=256, hidden=256, layers=4, dropout=0.1, unidirectional)
-> hidden state at the last valid timestep
-> LayerNorm(256) -> Dropout(0.1) -> Linear(256,7)
```

The optional GRM state gate is off. The head produces raw logits for seven categories.

The layer count is **4, not the head's own default of 2**, and the difference is easy to
misread from the head file alone. `NextHeadGRU.__init__` declares `num_layers: int = 2`
(`src/models/next/next_gru/head.py:18`), but that default never applies on the MTL path:
`MTLnet` passes its own model-level `num_layers` down to the category head
(`src/models/mtl/mtlnet/model.py:161-166`, forwarded at `:243`), and the MTL experiment
config sets `"num_layers": 4` (`src/configs/experiment.py:428`). The v17 command in §10.1
passes no `--num-layers`, so the config value stands. Verified by instantiation rather than
by reading: building the head as the MTL path builds it reports `gru.num_layers = 4` with
four `weight_ih` parameter sets, `hidden_size = 256`, `bidirectional = False`.

### 3.5 Region-private dual-tower head

The region head deliberately preserves both a task-private path and the shared interaction path.

#### Private path

The original post-mask region sequence `[B,9,64]` bypasses the MTL encoder and enters a complete private STAN backbone:

```text
STAN(embed_dim=64, d_model=128, heads=4, dropout=0.3,
     sequence_length=9, pairwise_bias_init=alibi)
-> pooled private feature [B,128]
```

This is not a thin residual skip. It is a full region-only sequence model. Its internal classifier is replaced with identity because classification happens once after fusion.

#### Shared path

The region output of the cross-attention stack `[B,9,256]` enters a second STAN backbone:

```text
STAN(embed_dim=256, d_model=128, heads=8, dropout=0.1,
     sequence_length=9, pairwise_bias_init=alibi)
-> pooled shared feature [B,128]
```

Each STAN tower projects its input to 128 dimensions, applies trajectory self-attention with a learned pairwise temporal-position bias initialized with ALiBi-style recency slopes, then applies matching attention and last-valid-step pooling.

#### Active fusion

The selected `fusion_mode=aux` computes:

```text
fused = private_feature + beta * aux_projection(shared_feature)
```

`aux_projection` is `Linear(128,128)`. `beta` is a trainable scalar initialized at `0.1`. It belongs to the region optimizer group and receives the normal AdamW weight decay of 0.05 in the final runs. No environment switch removes its weight decay.

The fused feature is classified by:

```text
LayerNorm(128) -> Dropout(0.1) -> Linear(128, number_of_regions)
```

The alternative private-only, convex-gated, and per-example auxiliary-gated fusion modes are not part of v17.

### 3.6 Inactive priors and couplings

The region transition prior is mathematically disabled:

```text
region_logits = classifier(fused) + alpha * log_T[last_region]
alpha = 0.0, registered as a frozen buffer
```

The command pins `freeze_alpha=True` and `alpha_init=0.0`. Therefore `log_T` cannot affect logits or training even when a per-fold transition path is supplied. Transition-prior knowledge distillation is also disabled with `log_t_kd_weight=0.0`.

Category-conditioned region prediction is off because `cond_coupling` remains its default `none`. There is no category posterior injection, category-to-region logit prior, or cascade in v17.

## 4. Parameter ownership and gradient flow

The optimizer partition is exhaustive and non-overlapping:

| AdamW group | Modules | Role |
|---|---|---|
| `cat` | `category_encoder`, `category_poi` (`next_gru`) | category-private |
| `reg` | `next_encoder`, complete `next_poi` dual-tower head, including both STAN towers, fusion projection, `beta`, and classifier | region-private ownership |
| `shared` | both cross-attention blocks, `cat_final_ln`, `next_final_ln` | joint interaction subsystem |

“Shared path” and “shared optimizer group” are not identical notions inside the region head. The region head's `shared_stan` consumes shared-stream activations, but its weights live inside `next_poi`, so they belong to the `reg` group. Only the cross-attention stack and final stream normalizations belong to the optimizer's `shared` group.

With the active static loss, a normal batch computes both tasks and performs one backward pass. There is no alternating optimizer step and no gradient surgery. The 0.75 category weight makes category gradients three times the scalar weight of region gradients before they combine in any connected parameter path. Cross-attention also permits a task loss to influence the opposite encoder through its key/value activations.

## 5. Loss function

Each task uses mean cross-entropy on raw logits, without class weights, focal terms, label smoothing, logit adjustment, or a tail-specific loss:

```text
L_category = mean CrossEntropy(category_logits, category_target)
L_region   = mean CrossEntropy(region_logits, region_target)

L_total = 0.75 * L_category + 0.25 * L_region
```

The implementation stores losses in `[region, category]` order and applies weights `[1-category_weight, category_weight]`. With `category_weight=0.75`, the formula above is exact.

No learnable loss-weight parameters exist in this configuration. Nash-MTL, uncertainty weighting, GradNorm, PCGrad, CAGrad, FAMO, and other combiners are not used.

## 6. Optimizer and learning-rate schedule

### 6.1 AdamW

The final model uses one AdamW optimizer with three parameter groups:

| Group | Peak LR in current canonical v17 | Peak LR in final AL/AZ/FL board runs |
|---|---:|---:|
| `cat` | 1e-3 | 1e-3 |
| `reg` | 3e-3 | 3e-3 |
| `shared` | 1e-3 | 3e-3 |

Common optimizer settings are:

| Setting | Value |
|---|---:|
| Weight decay | 0.05 |
| Adam beta1 | 0.9 |
| Adam beta2 | 0.999 |
| Epsilon | 1e-8 |
| Gradient clipping | global norm 1.0 |
| Gradient accumulation | 1 step |

Frozen parameters are filtered out before optimizer creation. `alpha` is a frozen buffer and is not optimized. `beta` remains in the normal region group.

### 6.2 OneCycleLR and the defining v17 correction

The scheduler is stepped after every optimizer update. Its step budget is:

```text
steps_per_epoch = max(number_of_category_batches, number_of_region_batches)
total_steps = 50 * steps_per_epoch
```

The longer loader defines an epoch because joint loading uses `max_size_cycle`; the shorter loader cycles until the longer one is exhausted.

Before v17, passing a scalar `max_lr=3e-3` to PyTorch `OneCycleLR` broadcast that value to every AdamW group, silently overriding the intended category LR of 1e-3. v17 activates `MTL_ONECYCLE_PER_HEAD_LR=1` through `--onecycle-per-head-lr`. The scheduler then receives a list built from each optimizer group's LR and preserves distinct peaks.

No `pct_start` override is supplied, so PyTorch's OneCycle defaults are used for warmup and annealing. The command's scalar `--max-lr 3e-3` remains present for configuration completeness but does not replace the per-group peak list when v17's correction is active.

### 6.3 Provenance note on `shared_lr`

The final result set is a v17 family with one documented LR difference:

- Alabama, Arizona, and Florida were produced by the `perhead_lr_n20` driver with category/region/shared peaks `1e-3 / 3e-3 / 3e-3`.
- California, Texas, and Istanbul were produced by their versioned v17 launchers with `1e-3 / 3e-3 / 1e-3`, which also matches the current `--canon v17` bundle.

`joint_best/PROVENANCE.md` currently says that all 18 run directories used `shared_lr=3e-3`, but the committed CA/TX and Istanbul launchers contradict that line and explicitly use `1e-3`. The launchers are the stronger execution evidence. This does not change the architecture, loss, batch-size correction, results, or statistical verdicts, but reproduction must use the dataset-specific value above unless the saved run manifests establish otherwise.

## 7. Training protocol

| Item | Active v17 setting |
|---|---|
| Epochs | 50 |
| Batch size | 8192 per task loader batch |
| Folds | 5 |
| Model seeds | 0, 1, 7, 100 |
| Total paired observations | 20 per dataset, 4 seeds x 5 folds |
| Fold construction | user-disjoint `StratifiedGroupKFold`, shuffled, `random_state` = the run's seed (**not** a fixed 42; the 42 in `folds.py:1061` is the parameter default, and the reported runs pass `--seed` in {0,1,7,100}, so each seed draws its own partition — see `fold_partition_and_seeds.md`) |
| Joint loader | `max_size_cycle` |
| Early stopping | disabled (`-1`) |
| Precision | no autocast via `MTL_DISABLE_AMP=1`; TF32 enabled for supported CUDA matrix operations |
| Compilation | `torch.compile`, dynamic mode enabled by `MTL_COMPILE_DYNAMIC=1` |
| Non-finite handling | strict fail-fast via `MTL_STRICT=1` |
| Validation memory control | chunked metric computation via `MTL_CHUNK_VAL_METRIC=1` |

The fold split is shared across tasks. In fold `k`, both category and region validation rows belong to the same held-out users, and neither task's training set contains those users. The fold construction remains fixed across model seeds, which makes `(seed, fold)` pairing valid.

For each training batch:

1. The loader supplies one category batch and one region batch, cycling the shorter loader if necessary.
2. The model executes both streams and both heads.
3. Two unweighted mean cross-entropies are computed.
4. Static scalarization produces `0.75 L_category + 0.25 L_region`.
5. One backward pass accumulates gradients through all connected task-private and joint paths.
6. The global gradient norm is clipped to 1.0.
7. The strict finite-value guard validates loss and gradients.
8. AdamW performs one update and OneCycleLR advances one step.
9. Gradients are cleared for the next batch.

The board runs used `--no-checkpoints`, which suppresses saved model weight files to reduce storage. Training still records the selected epoch and metrics in fold metadata, enabling exact joint-best rescoring from the recorded histories.

## 8. Validation, checkpoint selection, and reporting conventions

### 8.1 Primary task metrics

- Next category: seven-class macro-F1.
- Next region: full Acc@10. The scorer reconstructs full accuracy from the in-distribution metric and out-of-distribution fraction where required.

### 8.2 Single deployable checkpoint

The active selector is:

```text
geom_simple = sqrt(category_macro_F1 * region_Acc@10)
```

`min_best_epoch=0`, so every epoch is eligible. The best value of `geom_simple` selects one joint checkpoint per fold. The selected epochs for the final v17 runs occur late, between epochs 34 and 50.

### 8.3 Diagnostic-best versus joint-best

Two conventions must remain distinct:

- `diag-best`: category is read at its own macro-F1-best epoch and region at its own Acc@10-best epoch. These can be two different epochs in a fold and form the main diagnostic Table 3 values.
- `joint-best`: both heads are read from the one `geom_simple`-selected epoch. This is the deployable model convention.

The joint-best re-score differs from diag-best by at most 0.06 percentage points for category and 0.11 points for region across all datasets. No result verdict changes. Therefore the task-wise diagnostic table accurately describes what the single deployable checkpoint delivers, within 0.11 points, but the convention must still be named.

## 9. Final n=20 results

The table below reports the deployable joint-best convention against independently tuned dedicated single-task ceilings.

| Dataset | Dedicated cat | Joint cat | Delta cat | Dedicated region | Joint region | Delta region | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| Istanbul | 54.74 | 63.32 | +8.58 | 75.16 | 75.35 | +0.19 | category beats; region beats |
| Alabama | 56.82 | 64.51 | +7.69 | 70.11 | 69.70 | -0.41 | category beats; region matches |
| Arizona | 56.43 | 65.79 | +9.35 | 59.46 | 59.46 | -0.00 | category beats; region matches |
| Florida | 74.51 | 79.84 | +5.33 | 76.70 | 77.41 | +0.71 | category beats; region beats |
| Texas | 69.79 | 77.239 | +7.45 | 64.95 | 67.059 | +2.11 | category beats; region beats |
| California | 70.60 | 77.046 | +6.45 | 63.49 | 65.690 | +2.20 | category beats; region beats |

All six category comparisons are positive in all 20 paired folds and reject after Holm correction. For region, the pre-registered primary claim is non-inferiority with a 2-percentage-point margin. Alabama and Arizona match their dedicated models under TOST. Istanbul, Florida, Texas, and California also have positive effects in all 20 fold pairs; their secondary region-superiority family rejects after Holm correction.

The defensible summary is:

> The joint model outperforms the dedicated category model on all six datasets. For next-region prediction, it is non-inferior at Alabama and Arizona and outperforms the dedicated model at Istanbul, Florida, Texas, and California.

## 10. Reproduction recipes

### 10.1 Current canonical v17 topology and schedule

Use this for California, Texas, and Istanbul, and as the current code-level v17 definition:

```bash
export PYTHONPATH=src
export MTL_DISABLE_AMP=1
export MTL_ONECYCLE_PER_HEAD_LR=1
export MTL_CHUNK_VAL_METRIC=1
export MTL_STRICT=1
export MTL_COMPILE_DYNAMIC=1

python scripts/train.py \
  --task mtl \
  --canon none \
  --task-set check2hgi_next_region \
  --engine check2hgi_dk_ovl \
  --state STATE \
  --seed SEED \
  --epochs 50 \
  --folds 5 \
  --batch-size 8192 \
  --model mtlnet_crossattn_dualtower \
  --cat-head next_gru \
  --reg-head next_stan_flow_dualtower \
  --reg-head-param raw_embed_dim=64 \
  --reg-head-param fusion_mode=aux \
  --reg-head-param freeze_alpha=True \
  --reg-head-param alpha_init=0.0 \
  --task-a-input-type checkin \
  --task-b-input-type region \
  --mtl-loss static_weight \
  --category-weight 0.75 \
  --no-reg-class-weights \
  --no-cat-class-weights \
  --log-t-kd-weight 0.0 \
  --scheduler onecycle \
  --max-lr 3e-3 \
  --cat-lr 1e-3 \
  --reg-lr 3e-3 \
  --shared-lr 1e-3 \
  --checkpoint-selector geom_simple \
  --compile \
  --tf32 \
  --per-fold-transition-dir output/check2hgi_design_k_resln_mae_l0_1/STATE \
  --no-checkpoints
```

Replace `STATE` with the repository state key and run all four seeds `0`, `1`, `7`, and `100`.

### 10.2 Exact AL/AZ/FL board variation

For exact reproduction of the final Alabama, Arizona, and Florida board cells, change only:

```bash
--shared-lr 3e-3
```

All other architecture, loss, precision, batch, fold, seed, and scheduler settings remain the same.

## 11. Active configuration checklist

The following list is the concise definition of what belongs to v17:

- `check2hgi_dk_ovl`, history 9, stride 1, minimum sequence length 10, no tail windows.
- Task A check-in input; task B region input; both 64-dimensional.
- Separate 64-to-256 MLP encoders.
- Two 256-dimensional bidirectional cross-attention blocks with four heads and separate per-stream FFNs.
- `next_gru` category head, hidden width 256, four layers (the head's own default is two; the
  MTL config's `num_layers=4` is injected and wins -- see §3.4).
- Region dual tower: private STAN on raw 64-dimensional input and shared STAN on the 256-dimensional interaction stream.
- STAN feature width 128; private/shared heads 4/8; private/shared dropout 0.3/0.1.
- Additive auxiliary fusion with trainable `beta`, initialized at 0.1.
- Region-transition prior off; transition KD off; category-to-region conditional coupling off.
- Plain unweighted cross-entropy for both tasks.
- Static total loss: 0.75 category plus 0.25 region.
- AdamW, weight decay 0.05, betas `(0.9,0.999)`, epsilon 1e-8, gradient clipping 1.0.
- OneCycle per optimizer group; category peak 1e-3 and region peak 3e-3; shared peak follows the provenance split documented above.
- Batch 8192, 50 epochs, five user-disjoint folds, seeds `{0,1,7,100}`, true no-autocast fp32 with TF32 enabled.
- Joint checkpoint selected by `sqrt(category macro-F1 * region Acc@10)`.

## 12. Code and artifact ledger

Primary implementation:

- `src/models/mtl/mtlnet_crossattn_dualtower/model.py`: raw region path and complete dual-tower forward.
- `src/models/mtl/mtlnet_crossattn/model.py`: bidirectional interaction blocks and parameter partitions.
- `src/models/mtl/mtlnet/model.py`: task encoders and head construction.
- `src/models/next/next_gru/head.py`: active category head.
- `src/models/next/next_stan_flow_dualtower/head.py`: private/shared STAN towers, auxiliary fusion, and disabled transition-prior path.
- `src/models/next/next_stan/head.py`: STAN attention and pooling implementation.
- `src/losses/static_weight/loss.py`: exact 0.25/0.75 scalarization.
- `src/training/helpers.py`: AdamW groups and OneCycle per-group correction.
- `src/training/runners/mtl_cv.py`: joint loading, training step, validation, and checkpoint selector.
- `src/configs/canon.py`: current code-level v17 alias.

Final experiment evidence:

- `docs/studies/closing_data/v17_completion/README.md`: v17 completion status and board definition.
- `docs/studies/closing_data/perhead_lr_n20.md`: AL/AZ/FL batch and LR confirmation.
- `docs/studies/closing_data/v17_completion/a1_catx/run_a1_catx_n20.sh`: exact CA/TX launcher.
- `docs/studies/closing_data/v17_completion/h3_istanbul/run_step3_n20.sh`: exact Istanbul launcher.
- `docs/studies/closing_data/v17_completion/CEILINGS_N20_FINAL.md`: dedicated ceilings and diagnostic-best comparisons.
- `docs/studies/closing_data/joint_best/JOINT_BEST_RESULTS.md`: deployable single-checkpoint results.
- `docs/studies/closing_data/v17_completion/stats_n20/m2_prereg_output.txt`: final per-fold Wilcoxon, TOST, and Holm results.

