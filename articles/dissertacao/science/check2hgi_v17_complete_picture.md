# Check2HGI Used by MTL v17: Complete Representation Specification

## 1. Identity and scope

There is no independent embedding model named **Check2HGI v17** in this codebase. The version numbers refer to two different layers of the final system:

| Layer | Scientific identity | Operational identity |
|---|---|---|
| Representation | **Check2HGI v14**, the Design-K dual-axis champion | `check2hgi_design_k_resln_mae_l0_1` |
| Windowed downstream substrate | The same frozen v14 vectors, re-windowed | `check2hgi_dk_ovl` |
| Joint predictor | **MTL v17** | `mtlnet_crossattn_dualtower` with the v17 training recipe |

Therefore, the precise name for the representation used by the best final model is:

> **Check2HGI v14 / Design K, consumed through `check2hgi_dk_ovl` by MTL v17.**

`check2hgi_dk_ovl` does not train a new representation. It symlinks v14's three embedding tables and changes only supervised sequence construction to gated stride-1 overlap. Calling it "Check2HGI v17" would incorrectly merge the representation version, the windowing protocol, and the downstream MTL recipe.

This document covers only the active path that supplies MTL v17. Historical Check2HGI variants and inactive experiment switches are excluded except for a short explicit exclusion table.

Primary implementation sources:

- `scripts/probe/build_design_k_delaunay.py`: authoritative frozen v14 builder.
- `research/embeddings/check2hgi/model/Check2HGIModule.py`: hierarchical forward pass and losses.
- `research/embeddings/check2hgi/model/variants.py`: residual check-in encoder and masked-POI decoder.
- `research/embeddings/check2hgi/model/Checkin2POI.py`: check-in-to-POI attention pooling.
- `research/embeddings/hgi/model/RegionEncoder.py`: POI-to-region attention and region GCN.
- `research/embeddings/check2hgi/preprocess.py`: canonical graph and node-feature construction.
- `scripts/mtl_improvement/build_overlap_probe_engine.py`: v14 to `dk_ovl` conversion.
- `docs/studies/closing_data/archive/provenance/SUBSTRATE_VERSION_MAP.md`: scientific versus operational version map.

## 2. Purpose and outputs

Check2HGI is a transductive, self-supervised hierarchical graph representation. Its central change relative to a place-level embedding is that every **visit** receives its own vector.

The hierarchy has four levels:

```text
check-in event -> POI/place -> geographic region -> city
```

After training, v14 exports three 64-dimensional tables:

| File | Unit | Role in the final system |
|---|---|---|
| `embeddings.parquet` | One row per check-in | Historical input to MTL v17 next-category stream |
| `poi_embeddings.parquet` | One row per POI | Trained Design-K spatial POI representation; retained as an artifact but not read directly by the v17 MTL forward pass |
| `region_embeddings.parquet` | One row per region | Looked up for every historical visit and supplied to the MTL v17 next-region stream |

The representation builder never receives the supervised **next-category** or **next-region** targets. A visit's own category is nevertheless an input feature, and aggregated current-visit category features are used by the masked reconstruction auxiliary. "Label-free" here means no downstream future target, not absence of categorical information from the graph input.

## 3. Raw data and canonical graph

### 3.1 Required check-in fields

The preprocessor requires:

```text
userid, placeid, datetime, category, latitude, longitude
```

Rows are sorted by `userid` and `datetime`. A POI is assigned to a polygon by a geographic `intersects` join. POIs outside every polygon are dropped, and all check-ins at those POIs are consequently removed.

The region is a census tract for the U.S. datasets and a mahalle for Istanbul. Region IDs are local contiguous integer indices, not globally stable identifiers.

### 3.2 Check-in nodes and features

Each retained check-in becomes one graph node. Its feature vector is:

```text
[category one-hot,
 sin(2*pi*hour/24), cos(2*pi*hour/24),
 sin(2*pi*day_of_week/7), cos(2*pi*day_of_week/7)]
```

The final datasets use seven categories, so the active input width is `7 + 4 = 11`. Categories are label-encoded from the dataset vocabulary; missing values are filled as `Unknown` before encoding.

The node has no learnable user-ID, POI-ID, latitude, or longitude feature on the active check-in path. Spatial information enters through hierarchy mappings, geographic region adjacency, and the POI-level Delaunay branch.

### 3.3 Active check-in graph

The v14 builder reads the frozen canonical graph:

```text
output/check2hgi/<state>/temp/checkin_graph.pt
```

That graph uses the canonical `user_sequence` relation. Consecutive visits by the same user are connected in both directions. For two consecutive visits separated by `delta_t` seconds, the raw weight is:

```text
w = exp(-delta_t / 3600)
```

After all edges are built, weights are globally min-max normalized when their range is nonzero. Same-POI check-ins are not connected by a separate active check-in edge; they meet through the shared POI node one hierarchy level above.

The graph cache also contains:

- `checkin_to_poi`: check-in row to POI index.
- `poi_to_region`: POI index to region index.
- `region_adjacency`: directed edge list produced from polygon intersection, excluding self-pairs.
- `region_area`: polygon area as calculated from the loaded geographic geometry.
- `coarse_region_similarity`: cosine similarity between per-region POI-category distributions.
- metadata and the `placeid`/region index maps.

As a concrete shape check, the local Alabama cache has 113,846 check-ins, 11 input features, 219,976 directed sequence edges, 11,848 POIs, and 1,109 regions.

### 3.4 External POI-level spatial inputs

Design K adds two inputs produced by the HGI pipeline and remapped by `placeid` into Check2HGI's POI index space:

1. A 64-dimensional POI2Vec table from
   `output/hgi/<state>/poi2vec_poi_embeddings_<State>.csv`.
2. Weighted Delaunay POI edges from
   `output/hgi/<state>/temp/{pois.csv,edges.csv}`.

POI2Vec rows absent from the Check2HGI mapping are ignored; Check2HGI POIs absent from POI2Vec retain a zero row. Delaunay edges with an unmapped endpoint are dropped. Every retained edge is inserted in both directions.

The active edge controls are neutral:

```text
cross_region_weight = 1.0
edge_power = 1.0
```

Thus no extra cross-region penalty or edge sharpening is applied.

## 4. End-to-end architecture

```text
11-d check-in features on temporal user graph
                 |
        ResidualLNEncoder, 2 GCN layers
                 |
      64-d contextual check-in vectors
                 |
       Checkin2POI attention pooling
                 |
        canonical 64-d POI pool
           /                  \
 category/semantic path       detach + gamma * trainable POI2Vec table
           |                                  |
      c2p + masked-POI                  Delaunay POI GCN
        objectives                              |
                                      POI2Region attention
                                                |
                                      region adjacency GCN
                                                |
                                     64-d region vectors
                                                |
                                     area-weighted city vector
```

### 4.1 Check-in encoder: two-layer ResidualLN GCN

The active encoder is `ResidualLNEncoder(in_channels=11, hidden_channels=64, num_layers=2, dropout=0.1)`.

Its exact forward path is:

```text
x1 = Dropout(PReLU(LayerNorm(GCNConv_1(x, temporal_edges, weights))))
h2 = GCNConv_2(LayerNorm(x1), temporal_edges, weights)
z_checkin = x1 + h2
```

The second and final layer has no post-convolution activation or dropout. Both graph convolutions have bias. They are not cached because feature corruption produces multiple feature views over the same topology during training.

Every check-in therefore gets a contextual 64-dimensional vector. Visits at the same place can differ because their own category/time features and temporal graph neighborhoods differ.

### 4.2 Check-in-to-POI attention pooling

`Checkin2POI` pools all check-ins assigned to each POI using one learned seed query and four attention heads.

Active dimensions:

| Quantity | Value |
|---|---:|
| Input/output width | 64 |
| Heads | 4 |
| Width per head | 16 |
| POI-specific attention bias | Off |

The module learns independent `Q`, `K`, `V`, and output linear projections. For check-in `i` assigned to POI `p`, each head computes a score against the shared seed query. The implementation scales by `sqrt(64)`, not by `sqrt(16)`. A segmented softmax normalizes scores only over check-ins assigned to the same POI.

The weighted values are scatter-summed by POI, the shared query is added as a residual, and the result passes through:

```text
O = Q_shared + attention_pool
O = O + ReLU(Linear(O))
z_poi_canonical = PReLU(O)
```

This canonical POI pool is the semantic/category representation and is captured before Design-K spatial augmentation.

### 4.3 The Design-K branch and the exact hard separation

The regional path starts from:

```text
z_pre = stop_gradient(z_poi_canonical) + gamma * E_poi
```

where:

- `E_poi` is a trainable `Embedding(num_pois, 64)`.
- It is initialized exactly from the remapped frozen POI2Vec table.
- `gamma` is a trainable scalar initialized at `1.0`.
- The POI2Vec source table is retained as an immutable anchor buffer.

`z_pre` passes through one weighted POI-level graph convolution over the remapped HGI Delaunay graph:

```text
z_poi_region = PReLU_64(GCNConv_64x64(z_pre, delaunay_edges, delaunay_weights))
```

The `detach()` is load-bearing. It creates an explicit one-way boundary:

- the regional losses may use the semantic POI content numerically;
- their gradients cannot update the check-in encoder or `Checkin2POI` through that content;
- semantic losses can still update the shared canonical pool;
- spatial losses train the POI table, `gamma`, Delaunay GCN, and upper hierarchy.

This is stronger than ordinary soft sharing. It is an **asymmetric hybrid with hard gradient isolation at the POI boundary**. The two branches share the same forward value up to the canonical POI pool, but do not share all backward paths.

### 4.4 POI-to-region encoder

The spatial POI vectors are grouped by `poi_to_region` and pooled with a four-head PMA-style attention module. It again uses one learned seed query shared across groups, projections for query/key/value, segmented softmax within each region, weighted value aggregation, a query residual, and a residual ReLU output projection.

The PMA layer has layer normalization disabled. The resulting 64-dimensional region vectors then pass through:

```text
GCNConv(64, 64, cached=True, bias=True) over polygon adjacency
-> channelwise PReLU(64)
```

NaNs are replaced with zero. The final tensor is the exported `region_embeddings.parquet` representation.

### 4.5 Region-to-city summary

The city summary is a single 64-dimensional vector:

```text
z_city = sigmoid(sum_r region_area[r] * z_region[r])
```

The active function performs a weighted sum, not a normalized weighted mean. This city vector exists to support the region-to-city contrastive boundary; it is not exported as a downstream artifact.

## 5. What is shared: precise classification

Check2HGI is not the downstream two-task MTL network. It is one hierarchical representation trained by several objectives. Still, its objective topology has meaningful sharing and isolation.

The most precise classification is:

> **Multi-objective hard parameter sharing inside each branch, with a hard stop-gradient separating the semantic lower hierarchy from the spatial upper hierarchy.**

The parameter/gradient map is:

| Loss | Check-in GCN | Checkin2POI | POI table + gamma | POI Delaunay GCN | POI2Region | Its discriminator/decoder |
|---|---:|---:|---:|---:|---:|---:|
| `L_c2p` | Yes | Yes | No | No | No | `W_c2p` |
| `L_masked_poi` | Yes | Yes | No | No | No | masked decoder |
| `L_p2r` | **No, detached** | **No, detached** | Yes | Yes | Yes | `W_p2r` |
| `L_r2c` | **No, detached** | **No, detached** | Yes | Yes | Yes | `W_r2c` |
| `L_anchor` | No | No | table only | No | No | none |

Consequences:

- `L_c2p` and masked-POI reconstruction hard-share the same check-in encoder and POI attention pool.
- `L_p2r` and `L_r2c` hard-share the complete spatial POI/region path.
- The spatial objectives cannot overwrite the check-in encoder through the regional branch.
- The exported check-in representation is trained by the semantic objectives, while the exported region representation is trained by the spatial objectives plus the anchored POI substrate.

This dual-axis design is why v14 can improve the spatial substrate without sacrificing the check-in/category geometry.

## 6. Self-supervised objectives

### 6.1 Corruption and bilinear discriminators

The corruption function randomly permutes the rows of the check-in feature matrix while preserving graph topology and edges. The same check-in encoder and pooling modules process real and corrupted features.

Each hierarchy boundary has a learned `64 x 64` bilinear matrix. For aligned vectors `a` and `b`:

```text
D(a,b;W) = sigmoid((a W) dot b)
L_boundary = -mean(log D_positive) - mean(log(1 - D_negative))
```

The base hierarchical objective is:

```text
L_hier = 0.4 * L_c2p + 0.3 * L_p2r + 0.3 * L_r2c
```

### 6.2 Check-in-to-POI boundary

For every check-in, the positive pair is its contextual check-in vector and its own canonical pooled POI vector.

The active negative is a uniformly sampled **different POI** from the positive canonical POI matrix. Same-region hard negatives are off (`c2p_hard_neg_prob=0`) and corrupted-feature negatives are off (`c2p_corrupted_neg=False`).

Thus `L_c2p` directly shapes the exported check-in vectors and canonical POI attention pool.

### 6.3 POI-to-region boundary

For every spatial-path POI vector, the positive is its own region vector. The negative is another region vector.

Negative-region sampling begins with a uniform region different from the positive. Under the canonical default, 25% of samples are eligible to be replaced by a harder region whose POI-category-distribution cosine similarity lies strictly between `0.6` and `0.8`, provided the number of POIs in the full batch is below 50,000 and a candidate exists. Otherwise the random negative remains.

The active loss is the binary/JSD-style bilinear loss. Full-region InfoNCE is off.

### 6.4 Region-to-city boundary

Positive region vectors are scored against the real city summary. Negative region vectors come from a second hierarchy evaluated from the shuffled check-in features.

In Design K, the canonical positive and corrupted POI pools are both detached before entering the regional branch. The corrupted lower encoder therefore changes the numerical negative region view but does not receive regional gradients through it.

### 6.5 Masked-POI category reconstruction

The active auxiliary samples 15% of POIs independently each epoch and zeroes their canonical pooled POI vectors. It then mean-aggregates neighboring POI embeddings over the Delaunay graph and decodes only the masked rows with:

```text
Linear(64, 128) -> PReLU -> Linear(128, 7)
```

The target for each POI is the mean category one-hot vector of all its check-ins, equivalent to its empirical seven-category visit distribution.

The reconstruction loss is scaled cosine error with exponent 3:

```text
L_masked_poi = mean((1 - cosine(prediction, target))^3)
```

Its coefficient is `0.3`. It operates on the pre-augmentation canonical POI pool, so its gradients train the check-in GCN and Checkin2POI semantic path, not the Design-K regional POI table.

The builder supplies an already symmetrized Delaunay edge list, and the decoder symmetrizes its input again. With active mean aggregation this duplicates numerator and degree equally, so it does not change the resulting neighbor mean.

### 6.6 POI2Vec anchor

The trainable regional POI table is regularized toward its frozen initialization:

```text
L_anchor = mean((E_poi - E_poi2vec_frozen)^2)
```

Its coefficient is `0.1`. The anchor allows the table to adapt while penalizing drift away from the pretrained POI geometry.

### 6.7 Complete active loss

The exact v14 objective is:

```text
L_total =
    0.4 * L_c2p
  + 0.3 * L_p2r
  + 0.3 * L_r2c
  + 0.3 * L_masked_poi
  + 0.1 * L_anchor
```

No downstream next-step target appears in this loss.

## 7. Training recipe

### 7.1 Full-batch optimization

One epoch consists of one forward and backward pass over the complete graph for one dataset. There is no node mini-batching, neighbor sampling, fold split, or downstream label split during representation training.

Active hyperparameters:

| Setting | Value |
|---|---:|
| Epochs | 500 |
| Representation width | 64 |
| Check-in GCN layers | 2 |
| Attention heads in both hierarchy poolers | 4 |
| Check-in encoder dropout | 0.1 |
| Masked POI rate | 0.15 |
| Masked POI SCE exponent | 3.0 |
| Design-K `gamma` initialization | 1.0, trainable |
| Seed | 42 |

`torch.manual_seed(42)` and `numpy.random.seed(42)` are set before model construction and stochastic negative/mask sampling.

### 7.2 Optimizer and schedule

The builder uses one optimizer over every trainable parameter:

```text
Adam(lr=1e-3, weight_decay=0.0)
```

This is Adam, not AdamW. PyTorch's default Adam beta and epsilon values remain in effect.

A `StepLR(step_size=1)` is constructed only when the command-line `gamma` differs from `1.0`. The v14 default is `gamma=1.0`, so there is **no scheduler** and the learning rate stays at `1e-3` for all 500 epochs.

After backpropagation, all model gradients are clipped to global norm `0.9`, then Adam steps once.

The builder does not use AMP, gradient accumulation, early stopping, or a validation set.

### 7.3 Model selection

The selected state is the epoch with the minimum **same full-graph training objective** among all 500 epochs:

```text
if current_total_loss < lowest_loss:
    clone model.state_dict() in memory
```

After training, the best state is reloaded and one evaluation forward pass produces the exported vectors. This is training-loss selection, not validation-loss selection.

The builder exports embeddings and a copy of the graph cache but does not persist the selected model `state_dict`. The exact trained network cannot be resumed from the output directory alone; the frozen Parquet files and their hashes are the durable representation artifacts.

## 8. Export contract

### 8.1 Check-in table

`embeddings.parquet` contains:

```text
userid, placeid, category, datetime, 0, 1, ..., 63
```

Rows remain aligned with the canonical preprocessed metadata. The 64 numeric columns are the output of the residual check-in GCN, before POI pooling and before Design-K regional augmentation.

### 8.2 POI table

`poi_embeddings.parquet` contains:

```text
placeid, 0, 1, ..., 63
```

These are the active regional-path POI vectors **after** the Delaunay POI GCN. They are not the canonical semantic POI pool and are not simply the original POI2Vec rows.

### 8.3 Region table

`region_embeddings.parquet` contains:

```text
region_id, reg_0, reg_1, ..., reg_63
```

These are the outputs after POI-to-region attention and region adjacency GCN. MTL v17 converts a history of visited POIs into a history of these region vectors through the canonical `placeid -> poi_idx -> region_idx` mapping.

### 8.4 Provenance

The frozen engine directory is:

```text
output/check2hgi_design_k_resln_mae_l0_1/<state>/
```

`docs/studies/closing_data/archive/provenance/V14_HASH_MANIFEST.json` records SHA-256 hashes for the frozen artifacts in Alabama, Arizona, California, Florida, Georgia, and Texas. The manifest is the strongest local identity check because seed pinning does not guarantee byte-identical output across devices or GPU implementations.

Istanbul was added later through the H3 completion chain. Its final substrate was built with the same `build_design_k_delaunay.py` v14 recipe over the 520-mahalle graph, then converted with `build_overlap_probe_engine.py istanbul 1 10`. It is therefore scientifically the same Design-K representation, although it is not included in the earlier six-state hash manifest.

## 9. Conversion to the v17 operational substrate

The final MTL board reads:

```text
output/check2hgi_dk_ovl/<state>/
```

`build_overlap_probe_engine.py` performs two distinct operations.

First, it creates symlinks to the v14 representation files:

```text
embeddings.parquet         -> v14/embeddings.parquet
poi_embeddings.parquet     -> v14/poi_embeddings.parquet
region_embeddings.parquet  -> v14/region_embeddings.parquet
```

Second, it creates real downstream files specific to the overlap protocol:

```text
input/next.parquet
temp/sequences_next.parquet
input/next_region.parquet
```

The active window contract is:

| Property | Value |
|---|---:|
| History length | 9 visits |
| Target | Following, tenth visit |
| Stride | 1 |
| Minimum user sequence | 10 check-ins |
| Tail emission | False, auto-gated at stride 1 |

For a user with `n >= 10` check-ins, valid examples begin at consecutive positions and require a real next item after all nine history positions. Tail windows that would reuse the last observed POI as a synthetic target are excluded.

`next_region.parquet` derives the target `region_idx` from each sequence's real `target_poi`. It also derives `last_region_idx` from the last valid POI among `poi_0` through `poi_8`. The builder checks row-count and per-row user alignment between `next.parquet` and `sequences_next.parquet`, and rejects target POIs absent from the canonical graph vocabulary.

No Check2HGI parameter is retrained during this conversion.

## 10. How MTL v17 consumes Check2HGI

For every nine-visit history:

```text
Category stream:
  sequence of nine rows from v14 embeddings.parquet
  -> [9, 64] contextual check-in vectors

Region stream:
  each historical placeid -> canonical region_idx
  -> lookup in v14 region_embeddings.parquet
  -> [9, 64] region vectors
```

The category stream therefore preserves visit-level context. The region stream intentionally repeats a region vector whenever multiple visits map to the same region; sequential variation then comes from the visited-region trajectory and the downstream positional/trajectory model.

The POI export is not directly fed to `mtlnet_crossattn_dualtower`. Its influence is already incorporated into the trained region vectors.

Representation training and MTL training are separate stages:

1. Check2HGI v14 learns frozen check-in/POI/region vectors using the full graph and self-supervised objectives.
2. `dk_ovl` builds supervised nine-to-one windows without changing those vectors.
3. MTL v17 trains its dual-stream predictor under user-disjoint cross-validation using the frozen vectors.

## 11. Transductive integrity and limitations

### 11.1 What is protected downstream

The supervised MTL evaluation uses user-disjoint stratified five-fold splits. All windows belonging to one user remain in one fold, so stride-1 overlap cannot place windows from the same user in both training and held-out folds.

The Check2HGI objective never sees the next-category or next-region target attached to a supervised window. It learns from current visit features, graph hierarchy, shuffled negatives, the Delaunay graph, and the POI2Vec anchor.

### 11.2 What remains transductive

The representation is trained once on the complete graph for each dataset before downstream cross-validation. Consequently, graph message passing and hierarchy construction can include held-out users' visits during representation learning.

The dissertation's fold-only representation audit measured this channel by rebuilding from training users. Across Alabama, Arizona, and Florida, reported downstream shifts were bounded by approximately:

```text
next-region:   -0.33 to +0.01 percentage points
next-category:  0.00 to +0.29 percentage points
```

Those differences were within fold noise for visits whose places were represented in the training-only graph. Coverage of such visits was 67% to 87%; truly unseen places are outside that audit's representable subset.

The correct scientific statement is therefore not "fully inductive" or "no possible cross-fold channel." It is:

> The downstream labels and windows are user-disjoint, the representation has no future-task objective, and the measured whole-graph transductive effect was small; however, Check2HGI itself is a full-dataset transductive representation and cannot encode unseen users or places without rebuilding/retraining.

## 12. Empirical evidence and interpretation

### 12.1 Representation comparison for next category

Under the matched single-task recipe and folds used by the final paper, check-in-level Check2HGI versus place-level HGI produced:

| Dataset | Check2HGI macro-F1 | HGI macro-F1 | Difference |
|---|---:|---:|---:|
| Istanbul | 54.65 | 26.56 | +28.09 |
| Alabama | 55.87 | 26.56 | +29.31 |
| Arizona | 57.13 | 29.50 | +27.63 |
| Florida | 75.15 | 35.53 | +39.62 |
| Texas | 69.95 | 32.48 | +37.47 |
| California | 70.26 | 32.31 | +37.95 |

These numbers support the value of one vector per visit for the semantic sequence task. They do not isolate every v14 component because the primary comparison also changes representation granularity from place to check-in.

### 12.2 v14 substrate selection evidence

The archived controlled substrate study selected v14 as the dual-axis champion. On its multi-seed Florida single-task evaluation it records:

```text
next-category macro-F1: 67.36
next-region Acc@10:      0.7024
HGI next-region Acc@10: 0.7060
```

The recorded interpretation is that v14 closed about 69% of the canonical-Check2HGI-to-HGI region gap while retaining the strong category axis; HGI kept a 0.36 percentage-point region edge in that study.

This result selected the representation substrate. It must not be conflated with the later MTL v17 gain: archived pilots found v14 approximately tied with canonical Check2HGI inside the earlier MTL regime. The final MTL improvement came from the downstream topology/training recipe, while v14 remained the chosen frozen representation.

## 13. Active versus inactive implementation paths

The shared classes contain many historical experiment hooks. For the v14 artifacts consumed by MTL v17, the following are **not active**:

| Inactive mechanism | Active value/status |
|---|---|
| Check-in-level GraphMAE | `mae_lambda=0` |
| Native learned POI-ID injection | Off |
| POI side features | Off |
| POI co-visit InfoNCE boundary | `p2p_lambda=0` |
| Joint Node2Vec skip-gram head | Off |
| Full-region p2r InfoNCE | Off |
| Two-pass corruption | Off |
| c2p same-region hard negatives | Probability 0 |
| c2p corrupted-feature negative | Off |
| HGI embedding distillation decoder | Coefficient 0 |
| Delaunay cross-region reweighting | Neutral 1.0 |
| Delaunay edge-power sharpening | Neutral 1.0 |
| Learning-rate decay | `gamma=1`, no scheduler |

These options should not appear in a scientific description of the final representation as if they were ensemble components. They are leftover ablation surfaces around the active Design-K path.

## 14. Reproduction commands

### 14.1 Build the v14 representation

From the repository root, after the canonical Check2HGI graph and HGI POI artifacts exist:

```bash
PYTHONPATH=src:research .venv/bin/python \
  scripts/probe/build_design_k_delaunay.py \
  --state alabama \
  --epochs 500 \
  --dim 64 \
  --num-layers 2 \
  --attention-head 4 \
  --alpha-c2p 0.4 \
  --alpha-p2r 0.3 \
  --alpha-r2c 0.3 \
  --encoder resln \
  --mae-poi-lambda 0.3 \
  --anchor-lambda 0.1 \
  --gamma-init 1.0 \
  --lr 0.001 \
  --gamma 1.0 \
  --max-norm 0.9 \
  --weight-decay 0.0 \
  --seed 42 \
  --out-suffix resln_mae_l0_1 \
  --device <cpu-or-accelerator>
```

The bare defaults currently encode these values, but an archival reproduction should keep them explicit.

### 14.2 Build the overlap-gated engine

```bash
PYTHONPATH=src .venv/bin/python \
  scripts/mtl_improvement/build_overlap_probe_engine.py \
  alabama 1 10
```

Repeat both operations independently for every dataset. The builder does not create one global model shared across states; each dataset has its own graph, POI inventory, region inventory, trained parameters, and embedding tables.

## 15. Validation checklist

Before treating an engine as the substrate for MTL v17, verify:

1. The scientific source directory is exactly `check2hgi_design_k_resln_mae_l0_1`.
2. All three `check2hgi_dk_ovl` embedding symlinks resolve into that v14 state directory.
3. Each embedding table has exactly 64 numeric dimensions and no non-finite values.
4. `next_build_provenance.json` records stride 1, minimum sequence length 10, history width 9, and `emit_tail=false`.
5. `next.parquet`, `sequences_next.parquet`, and `next_region.parquet` have identical row counts and row-aligned user IDs.
6. Every target POI maps through the canonical `placeid_to_idx` and `poi_to_region` tables.
7. The v14 source files match the frozen hash manifest where a manifest entry exists.
8. Downstream folds group by `userid`; overlap alone is not a valid split strategy.

## 16. Compact final definition

The representation below MTL v17 is a dataset-specific, transductive four-level graph encoder. It maps category/time-aware check-in nodes through a two-layer residual GCN, pools them into POIs with multi-head attention, and then splits its learning signal. The semantic path directly trains visit vectors with check-in-to-POI discrimination and masked POI-category reconstruction. The spatial path receives a stop-gradient copy of that POI pool, adds a trainable POI2Vec-anchored table, diffuses it over weighted Delaunay POI edges, pools into regions, and diffuses again over polygon adjacency. It is optimized full-batch for 500 epochs with Adam at `1e-3`, no weight decay or LR decay, gradient norm clipping at `0.9`, and minimum-training-loss checkpoint selection.

The resulting v14 check-in and region vectors are frozen. `check2hgi_dk_ovl` only reuses them under nine-visit, stride-1, minimum-length-10 supervised windows. Those two frozen modalities then feed the separate category and region streams of the MTL v17 predictor.
