# 71 — Check2HGI node features and training targets (AUT-20 / AUT-23 / AUT-21)

**Scope.** What the check-in-level representation actually uses as node features and as training
targets, so one honest sentence can replace the false absence claim at `2_fundamentals.tex:383`.
**No `.tex` file was edited. `PENDENCIAS.md` was not edited.** Drafts in §7 are proposals only.

**Repo root for every command below:** `/Users/vitor/Desktop/mestrado/ingred`.

**Tree used.** `research/embeddings/...` is the live tree. Verified identical to the `.temp/mobiwac`
copy for the four files this report depends on:

```bash
for f in embeddings/check2hgi/preprocess.py embeddings/check2hgi/model/variants.py \
         embeddings/check2hgi/model/Check2HGIModule.py embeddings/hgi/poi2vec.py; do
  echo -n "$f: "; diff -q research/$f .temp/mobiwac/research/$f >/dev/null && echo SAME || echo DIFFER; done
# -> all four SAME
```

---

## 0 · The headline answer to the author's sentence

The author's words: *"we use the category and the region (lat and long) on the graph node."*

Split into the two things it conflates, the truth is:

| The author's clause | Verdict | What is actually true |
|---|---|---|
| "we use the category ... on the graph node" | **TRUE** | The current visit's category is a 7-way one-hot, columns 0 to 6 of the check-in node feature vector. `preprocess.py:623-624`. |
| "the region ... on the graph node" | **FALSE as a node feature** | The region label is not in any node feature vector. It enters as a **grouping assignment** (`poi_to_region`), which defines the positive pair of the place-to-region term, and as polygon adjacency between region nodes. `Check2HGIModule.py:847`, `preprocess.py:129-133`. |
| "(lat and long) on the graph node" | **FALSE** | No latitude or longitude value is a node feature anywhere on the active path. Coordinates are consumed at build time in two places only: the point-in-polygon join that assigns a place to a region (`preprocess.py:113-118, 145-152`), and the Delaunay triangulation plus haversine distance that set the **edge weights** of the place-level graph (`hgi/preprocess.py:163-176`). |

So the defensible sentence is: the current visit's **category** and **time** are node features; the
region and the coordinates are **not** node features, they shape the graph (which place belongs to
which region, and how strongly two places are connected).

Measured, not inferred. The shipped Alabama graph cache carries exactly eleven feature columns and
all eleven are reconstructed exactly from category and timestamp, leaving zero residual columns:

```python
# python, on output/check2hgi/alabama/temp/checkin_graph.pt
node_features shape (113846, 11)
temporal max abs deviation per col: [0.0, 0.0, 0.0, 0.0]     # cols 7..10 == sin/cos(hour), sin/cos(dow)
category argmax agreement with metadata label-encoding: 1.0  # cols 0..6 == the visit's own category
accounting: 11 = 7 one-hot + 4 temporal -> residual columns: 0
```

**V3, instrument validation.** The accounting test above is only trustworthy if it can see an
unexplained column. Appending one synthetic column in the same cell moved the residual from 0 to 1,
so the test does detect a smuggled coordinate-like feature. Separately, the comment-stripping filter
required by V4 was validated on this chapter: `grep -c 'masked'` over
`src/chapters/2_fundamentals.tex` returns **1** raw and **0** comment-stripped, and `grep -c '0\.3'`
returns **4** raw and **1** stripped, so the filter is doing real work here and an unfiltered sweep
would have over-reported.

---

## 1 · Node features of the check-in node

Construction, quoted in full (`research/embeddings/check2hgi/preprocess.py:615-642`):

```python
    def _build_node_features(self):
        """Build check-in node features: category one-hot + temporal encoding."""
        num_categories = len(self.le_category.classes_)
        category_onehot = np.zeros((num_checkins, num_categories), dtype=np.float32)
        category_onehot[np.arange(num_checkins), self.checkins['category_encoded'].values] = 1.0
        dt = pd.to_datetime(self.checkins['datetime'])
        hour = dt.dt.hour.values
        dow = dt.dt.dayofweek.values
        temporal[:, 0] = np.sin(2 * np.pi * hour / 24)  # hour_sin
        temporal[:, 1] = np.cos(2 * np.pi * hour / 24)  # hour_cos
        temporal[:, 2] = np.sin(2 * np.pi * dow / 7)    # dow_sin
        temporal[:, 3] = np.cos(2 * np.pi * dow / 7)    # dow_cos
        node_features = np.concatenate([category_onehot, temporal], axis=1)
```

Enumerated against the six classes the task asked for:

| # | Field | Width | Class | Evidence |
|---|---|--:|---|---|
| 1 | Category one-hot of the **current** visit | 7 | (i) category of the current visit | `preprocess.py:623-624`; label-encoded from the dataset vocabulary at `:107-109`, missing filled `Unknown` |
| 2 | `sin(2*pi*hour/24)` | 1 | (iv) time | `preprocess.py:633` |
| 3 | `cos(2*pi*hour/24)` | 1 | (iv) time | `preprocess.py:634` |
| 4 | `sin(2*pi*dow/7)` | 1 | (iv) time | `preprocess.py:635` |
| 5 | `cos(2*pi*dow/7)` | 1 | (iv) time | `preprocess.py:636` |
| — | Region label (discrete class) | 0 | (ii) **ABSENT** | not in `_build_node_features`; the width accounting above leaves no room for it |
| — | Latitude / longitude, raw or encoded | 0 | (iii) **ABSENT** | not in `_build_node_features`; `grep` for `latitude|longitude|coord` over the four model files, `check2hgi.py`, `reg_poi_aug.py` and `build_design_k_delaunay.py` returns **zero** lines |
| — | User ID, place ID | 0 | (v) **ABSENT** on the active path | the per-place attention-bias hook is off by default (`Checkin2POI.__init__`, `t63_enabled: bool = False`) |

Total active width 11, matching the shipped cache and the builder's own read
(`build_design_k_delaunay.py:198`, `in_channels = d["node_features"].shape[1]`).

**Where coordinates and the region DO enter, precisely.** Both at graph-construction time, never as a
feature:

- Region assignment. A place is placed in a polygon by an `intersects` join on its coordinates, and
  places outside every polygon are dropped together with their check-ins
  (`preprocess.py:113-118`, `:145-152`, `:160-167`). The result is the integer map `poi_to_region`.
- Edge weights of the check-in graph. Consecutive visits of one user are joined **in both
  directions** with weight `exp(-delta_t / temporal_decay)`, `temporal_decay = 3600.0`
  (`preprocess.py:172-199`, default at `:20`). This is temporal, not spatial.
- Edge weights of the place-level Delaunay graph. Built upstream in HGI from the coordinates
  themselves: Delaunay triangulation over the points, haversine distance, a log distance-decay, and a
  cross-region factor (`hgi/preprocess.py:163-176`). This is the one place where latitude and
  longitude have numeric influence, and it lands on **edges**.

---

## 2 · Node features of the other levels

None of the three upper levels has an input feature vector at all. Each is produced by aggregating
the level below, which is the point of the hierarchy.

| Level | Input features | How the vector is produced | Evidence |
|---|---|---|---|
| **Place (POI)** | none | Attention pooling of the vectors of the check-ins assigned to that place: one shared learned seed query, four heads, segmented softmax within a place, query residual, residual output projection, PReLU. | `Checkin2POI` (`model/Checkin2POI.py:9-60`); called at `build_design_k_delaunay.py:261` |
| **Place, spatial branch** | one trainable 64-d table per place | `z_pre = detach(z_poi_canonical) + gamma * E_poi`, `E_poi` initialized from the frozen POI2Vec table, `gamma` trainable from 1.0, then one weighted graph convolution over the Delaunay place graph. **The place identity is the only "feature" here, and it is an index into a learned table, not an observed attribute.** | `variants.py:653-654` (`pos_pre_gcn = pos_poi_emb.detach() + self.reg_gamma * poi_residual`); table and anchor wired at `build_design_k_delaunay.py:273-276`; loader `reg_poi_aug.py:27-50` |
| **Region** | none | Four-head attention pooling of the spatial place vectors grouped by `poi_to_region`, then one graph convolution over polygon adjacency, then PReLU. | `POI2Region.forward(x, zone, region_adjacency)` (`hgi/model/RegionEncoder.py:40-54`); grouping passed at `Check2HGIModule.py:689` |
| **City** | polygon **area** per region | `z_city = sigmoid(sum_r area[r] * z_region[r])`, a weighted sum and not a normalized mean. Area is computed from the loaded geometry. | `build_design_k_delaunay.py:263-264`; area at `preprocess.py:652-657` |

Two region-level quantities are derived from categories and are worth naming because they are inputs
to training even though they are not node features:

- `region_adjacency`, a self-pair-excluding directed edge list from polygon intersection
  (`preprocess.py:667-677`).
- `coarse_region_similarity`, the cosine similarity between the per-region **place-category
  distributions** (`preprocess.py:683-700`). It is read only to choose harder negative regions at the
  place-to-region boundary (`Check2HGIModule.py:850-853`), so a current-visit category statistic
  influences negative sampling.

---

## 3 · Training targets: every term of the active loss

The assembled objective (`Check2HGIModule.py:1192-1195`, plus the three conditional additions at
`:1247-1254`), with the weights that the shipped builder passes by default
(`build_design_k_delaunay.py:363-367, 387`):

| # | Term | Weight | Reads a label? | Evidence |
|---|---|---|---|---|
| 1 | `L_c2p`, check-in to place | **0.4** | **Neither.** The positive pair is a check-in vector and the pooled vector of its own place; the negative is a uniformly sampled different place. | weight `build_design_k_delaunay.py:363`; assembly `Check2HGIModule.py:1193`; pairs at `:828, :845`; sampler `:840-845`. The category one-hot is in the *input*, not in this target |
| 2 | `L_p2r`, place to region | **0.3** | **The region as a current property**, not as a task label. The positive is the place's own region vector, indexed by `poi_to_region`; the negative is another region, with the 25 percent harder-negative path keyed on the category-distribution cosine. | weight `:364`; assembly `:1194`; positive `:847`; negatives `:850-853` |
| 3 | `L_r2c`, region to city | **0.3** | **Neither.** Real region vectors are scored against the real city summary; negatives come from a second hierarchy computed from row-permuted check-in features. | weight `:365`; assembly `:1195`; `corruption` is `x[torch.randperm(x.size(0))]` at `Check2HGIModule.py:17-27` |
| 4 | `L_masked_poi`, masked-place category reconstruction | **0.3** | **A category quantity, YES, and it is a current-visit aggregate.** 15 percent of places are masked per step; the decoder predicts the masked place's **mean category one-hot over its own check-ins** from its Delaunay neighbors, under a scaled cosine error with exponent 3. | weight `build_design_k_delaunay.py:387` (`default=0.3`); target built at `:248` from `_compute_poi_category_aggregate` (`:95-110`), which prefers the cached `poi_category_aggregate` computed at `preprocess.py:457-498`; decoder `variants.py:203-249`; added at `Check2HGIModule.py:1247-1250` |
| 5 | `L_anchor`, POI2Vec anchor | **0.1** | **Neither.** `mean((E_poi - E_poi2vec_frozen)^2)`: a drift penalty on the trainable place table toward its own frozen initialization. **No category or region term.** | weight `build_design_k_delaunay.py:367`; `anchor_loss` at `Check2HGIModule.py:1125-1135`; added at `:1253-1254` |

Every other hook is off by default and stays off in this recipe: `mae_lambda: float = 0.0`
(`:68`), `n2v_lambda: float = 0.0` (`:81`), `p2r_use_infonce: bool = False` (`:122`),
`p2p_lambda: float = 0.0` (`:141`), `c2p_hard_neg_prob=0.0` and `c2p_corrupted_neg=False`
(`:54-55`), `hgi_decoder_gamma` default `0.0` (`build_design_k_delaunay.py:390`),
`use_side_features` a bare `store_true` flag, so off unless passed (`:377`).

### 3.1 The two previously established numbers: one CONFIRMED, one CORRECTED

- **0.3, masked-place category reconstruction: CONFIRMED**, and it is one of five active terms.
  `build_design_k_delaunay.py:387` sets `default=0.3` with the help string *"v14 DEFAULT=0.3; pass
  0.0 to disable"*; the term is added as `self.mae_poi_lambda * self._mae_poi_loss`
  (`Check2HGIModule.py:1250`). Spec agrees at `check2hgi_v17_complete_picture.md:331` and `:354`.

- **1e-8: CORRECTED in its attribution.** The prior audit's phrasing places a "category L2 term at
  weight 1e-8" on the **anchor**. That is wrong on two counts, and both matter for the wording.
  (a) Check2HGI's anchor term is weight **0.1** and contains no label of any kind
  (`Check2HGIModule.py:1135`). (b) The `1e-8` term lives one stage **upstream**, inside POI2Vec's own
  pretraining loss, as the category-to-fine-class hierarchical L2:
  `loss_hierarchy = 0.5 * self.le_lambda * (diff * diff).sum()` with
  `le_lambda=1e-8` (`hgi/poi2vec.py:124, 136, 182`, and `:333` for the same default on the training
  entry point). The code comment the prior audit quoted is real and is at `hgi/poi2vec.py:341-342`:
  *"Set to 0.0 to disable the only explicit category-label path into fclass embeddings (leakage
  ablation arm A)."*
  The shipped runner does **not** pass `le_lambda`, so the `1e-8` default is what was trained
  (`scripts/substrate_protocol_cleanup/run_poi2vec.py:38-46`, which forwards `city, epochs,
  embedding_dim, batch_size, lr, k, device, save_intermediate` and nothing else). Note also what
  `1e-8` buys: on the same loss scale as a skip-gram term, this is a numerically negligible pull, and
  the repository's own probe scripts call it *"hierarchical L2 effectively off"*
  (`scripts/probe/summarize_hgi_category_variants.py:111`) and *"canonical lambda, effectively zero"*
  (`scripts/probe/build_hgi_category_variants.py:311`). It is a real label path and it is a
  vanishing one; both halves belong in any sentence that names it.

---

## 4 · THE DECISIVE QUESTION

**Does any representation-training objective or node feature read the category or the region of a
FUTURE visit, that is, the prediction target of the next-category or next-region task?**

### 4.1 Objectives: NO

None of the five terms in §3 is a function of a next-step target. Terms 1, 3 and 5 read no label.
Term 2 reads the region of the place **being encoded**, and term 4 reads the category distribution of
the check-ins **at the place being reconstructed**. Both are properties of the current row, and the
supervised window's target never enters: the builder constructs its `Data` object from
`node_features, edge_index, edge_weight, checkin_to_poi, poi_to_region, region_adjacency,
region_area, coarse_region_similarity` and nothing else (`build_design_k_delaunay.py:229-239`), and
the supervised target is constructed in a separate stage entirely, at `src/data/inputs/core.py:266-268`
(`target_idx = start_idx + window_size; target_poi = places_visited[target_idx]`). The spec states the
same at `:358`, *"No downstream next-step target appears in this loss"*, and the code agrees.

### 4.2 Node features, by way of the graph: YES for the next category, and this is the finding

The category one-hot is a node feature (§1), consecutive visits are joined **bidirectionally**
(`preprocess.py:195-199`), the encoder is a **two-layer** graph convolution (`--num-layers` default
`2` at `build_design_k_delaunay.py:361`; `pipelines/embedding/check2hgi.pipe.py:41`;
`ResidualLNEncoder` stacks `num_layers` convolutions at `variants.py:461-496`), and the exported
vectors are computed on the full graph in one pass (`build_design_k_delaunay.py:323-326`). The
supervised target of a window is the visit immediately after the window. So the vector of the last
history visit aggregates the node of the target visit, whose feature vector contains the target
visit's category.

**Measured, not argued.** Reconstructing the nine-visit stride-1 windows over the shipped Alabama
graph, using the graph's own row order (asserted to be `(userid, datetime)` sorted, per
`preprocess.py:103`) and the graph's own edge list:

```
windows tested = 96326
last-history-visit adjacent to TARGET visit, both directions present : 96326
not adjacent                                                        : 0
negative control, far-apart same-user pairs found as edges           : 0
```

The negative control is there for V3: the same test finds zero edges where none should exist, so the
96,326 is not an artifact of a test that says yes to everything.

**Region: NO as a per-window read, with one transductive qualification.** The region label is in no
node feature, so nothing propagates it along check-in edges. The downstream region stream looks up
region vectors for the **historical** places of the window
(`check2hgi_v17_complete_picture.md:506-509`). What is true, and is the honest qualification, is that
the representation is trained once over the whole graph, so the place that will be some window's
target is a node during training and its own `poi_to_region` pair contributes to term 2. That is the
transductive channel the document already discloses, not a read of a future label.

### 4.3 What protects against it, and what does not

- **The split does not protect against this channel.** The five folds are user-disjoint
  (`5_mobiwac/05_setup.tex:30`), and the leaking edge is *inside one user's own trajectory*, so it
  lies entirely within a fold.
- **No masking or windowing is applied at representation-training time.** The graph carries every
  edge; the builder passes the full `edge_index` (`build_design_k_delaunay.py:231`).
- **What does exist is a measurement, and the dissertation already reports it.** Chapter 5 states the
  mechanism plainly at `5_mobiwac/05_setup.tex:70` (*"A visit's node is linked to the visit that
  follows it, and category is a node input feature, so a per-visit vector could in principle absorb
  the category of the next visit"*), names the screening audit, and at `:87` gives its three limits:
  the probe is linear, it was run at Florida alone at one random initialization, and it was run on
  ancestor builds rather than on the shipped one.

**So the chapter-level defect is a contradiction inside the document, not a new discovery.** Chapter 5
discloses the channel; §2.2.2 at `:383` and §2.2.3.2 at `:602-603` deny it. The Fundamentals sentences
are the ones that must move.

---

## 5 · POI2Vec in this repository (AUT-21)

What the component named `poi2vec` in the live path **does**, from
`research/embeddings/hgi/poi2vec.py`:

1. It runs random walks over the **place-level Delaunay graph** built from coordinates,
   using node2vec walk generation with `walk_length=10, context_size=5, walks_per_node=5`
   (`:220-223`, `:263-274`; edges read at `:248`).
2. It **rewrites each walk of places as a walk of fine classes** (the per-place fine-grained label,
   `Airport`, `Coffee Shop`, and so on), and trains a skip-gram model at the **fine-class** level, so
   all places sharing a fine class share one vector (`:277-283`, `:300-307`, `docstring :17-22`).
3. Its loss is skip-gram with **hard negatives**, fine classes that never co-occurred with the center
   in any walk (`:43-56`, `:95-107`, `:159-168`), plus the hierarchical category-to-fine-class L2 at
   `le_lambda=1e-8` described in §3.1 (`:170-182`).
4. Each place then receives its fine class's vector by lookup, which is the reconstruction step
   (`:449-456`: *"poi_embedding[i] = fclass_embeddings[poi.fclass[i]]"*).

Inside Check2HGI this 64-d table is remapped by `placeid` into the place index space, places absent
from it keep a zero row (`reg_poi_aug.py:27-50`), it initializes the trainable spatial place table,
and the frozen copy is retained as the target of the 0.1 anchor term (§3, term 5).

**Is it the published POI2Vec of Feng et al.? NO.** The module says so itself, in a naming note dated
2026-06-19 at `hgi/poi2vec.py:3-9`: *"despite the module/class name, this is an fclass-level
hierarchical Node2Vec teacher used INSIDE HGI, it is NOT the AAAI'17 POI2Vec baseline (Feng et al.
2017)"*, and it points at `scripts/baselines/poi2vec_lib/` for the faithful implementation, whose own
header lists the four defining mechanisms of the published method: a fixed recursive rectangular
midpoint tree over the bounding box, overlap-area phi, CBOW, and hierarchical softmax
(`scripts/baselines/poi2vec_lib/model.py:1-16`).

**The published record, opened this session.** OpenAlex `W2604411573`: Shanshan Feng, Gao Cong, Bo An,
Yeow Meng Chee, *POI2Vec: Geographical Latent Representation for Predicting Future Visitors*,
Proceedings of the AAAI Conference on Artificial Intelligence, 2017, DOI
`10.1609/aaai.v31i1.10500`. Its abstract, read from that record, states the problem as predicting
*users who will visit a given POI in a given future period* and the contribution as a latent
representation model that incorporates geographical influence. **The one-sentence difference:** the
published method encodes geography through a binary-tree partition of space with overlap-weighted
routing and trains place vectors jointly with user preference for a visitor-prediction task, whereas
this repository's component of the same name trains **fine-class** vectors by skip-gram over walks on
a Delaunay place graph and assigns each place its fine class's vector. **Nothing is proposed for
citation**, per the author's ruling; the mechanism is named and no reference is added.

---

## 6 · §2.2.3.2 "The check-in level", assertion by assertion (AUT-23)

Source: `articles/dissertacao/src/chapters/2_fundamentals.tex`. Live prose of the subsubsection is
lines 601-626 and 662-666; lines 628-660 are a provenance comment block and carry no prose. Verdicts
are per assertion, with that assertion's own evidence.

| # | Line | The dissertation's sentence, quoted | Verdict | Evidence |
|---|---|---|---|---|
| A1 | 601-602 | "Check2HGI completes the move from contextualized inputs to one learned representation per visit." | **SUPPORTED** | One row per check-in is exported: `embeddings.parquet` has 113,846 rows for Alabama's 113,846 check-ins, with 64 dimension columns, all non-null (opened this session). Builder at `build_design_k_delaunay.py:328-333` |
| A2 | 602 | "It adds a fourth level below the place" | **SUPPORTED** | Four levels check-in, place, region, city; spec `:36-40`; encoder, `Checkin2POI`, `POI2Region`, `region2city` all constructed at `build_design_k_delaunay.py:255-264` |
| A3 | 602-603 | "learns one vector per visit **without using task labels**" | **OVERSTATED** | Two distinct problems. (a) The current visit's category is an input feature, `preprocess.py:623-624`. (b) A weight-0.3 term reconstructs a place's mean category one-hot, `build_design_k_delaunay.py:248, 387`. Under the narrow reading "no next-step target in the objective" it is true (§4.1); under the plain reading a reader will take, it is false |
| A4 | 603-605 | "The hierarchy has three adjacent-level boundaries: check-in to place, place to region, and region to city." | **SUPPORTED as a statement about the hierarchy; INCOMPLETE as a statement about the objective** | The three boundaries are real (`Check2HGIModule.py:1193-1195`), but the shipped loss has **five** terms, adding masked-place category reconstruction at 0.3 and the anchor at 0.1 (§3). The sentence itself does not claim completeness; A5 does |
| A5 | 605-609 | "Its objective is the fixed-weight sum $\mathcal{L} = 0.4\mathcal{L}_{c2p} + 0.3\mathcal{L}_{p2r} + 0.3\mathcal{L}_{r2c}$" | **OVERSTATED** ("its objective **is**") | The three weights are correct (`build_design_k_delaunay.py:363-365`; `Check2HGIModule.py:51-53`), but the shipped objective of the representation the later chapter uses is the five-term sum of §3. The chapter's own comment at `:648-652` flagged exactly this with a `[VERIFY]`; that VERIFY is now answered |
| A6 | 610-616 | "Each term uses a bilinear discriminator, $\mathcal{D}=\sigma(\mathbf{e}_1^{\top}\mathbf{W}\mathbf{e}_2)$ ... The discriminator is linear in either embedding when the other is held fixed, and its output lies between 0 and 1." | **SUPPORTED** | `discriminate` and `discriminate_global` are used by all three boundary terms with their own learned matrices `weight_c2p`, `weight_p2r`, `weight_r2c` (`Check2HGIModule.py:1156-1190`). The logistic function bounds the output |
| A7 | 617-622 | The per-boundary loss "favors a high score for a true pair and a low score for a false pair", with the two-log form | **SUPPORTED** | `loss_c2p = -torch.log(pos_c2p + EPS).mean() - torch.log(1 - neg_c2p + EPS).mean()`, `Check2HGIModule.py:1159`, and the same shape at `:1184` and `:1189` |
| A8 | 623-625 | "$\mathbf{e}^{+}$ belongs to a true pair, such as a check-in and the place where it occurred, whereas $\mathbf{e}^{-}$ is substituted from another example in the batch." | **SUPPORTED** | Positive `pos_poi_expanded = pos_poi_emb_pure[data.checkin_to_poi]` at `:828`; negative is a uniformly sampled different place from the same positive matrix, `:840-845`. Full-batch training, so "the batch" is the dataset (`build_design_k_delaunay.py:298-312`) |
| A9 | 625-626 | "No prediction target appears in these equations, which is why the representation is described as trained without task labels." | **first clause SUPPORTED, inference OVERSTATED** | True of the three displayed equations (§4.1). The inference fails because the two terms not displayed include the category-reconstruction term, and because the category is an input feature. This is the sentence that carries A3's error into a justification |
| A10 | 662-664 | "Where a place embedding answers ``what is this place,'' a check-in-level representation answers ``what is this visit''" | **SUPPORTED** | Two visits to one place can differ: the exported table is per check-in, and a check-in vector depends on the visit's own category and time features and on its temporal neighborhood (`variants.py:481-496` over `preprocess.py:172-199`) |
| A11 | 664-666 | Forward pointers to Chapter 5 and to Table `tab:fund:lineage` | **SUPPORTED**, out of scope for this audit | pointer text only, no factual claim about the representation |

---

## 7 · Drafts (proposals only, nothing was edited)

Register checked against WRITING_LAW: American English, no em-dash, no contractions, no process
narration, no repo codenames, canonical GLOSSARY names only. Terms used and already registered:
*check-in*, *place / POI*, *region*, *check-in-level representation (Check2HGI)*, *place embedding
(HGI)*, *next category*, *next region*, *the 7-category taxonomy*, *transductive*, *leakage audit*.
Two ordinary words are used that GLOSSARY does not carry as rows and that the chapter's live prose
already uses: *node* (`:100`, `:222`) and *one-hot* (`:8`, `:201`). **Registry check owed to the
author, not self-authorized:** "graph node", "node feature", and "edge weight" are ordinary graph
vocabulary rather than names this project coined, and if §1's fail-closed rule is read strictly they
need rows before the drafts below land.

### D1 · Replaces `2_fundamentals.tex:383`

> The representations used in this work are trained without any prediction target. No objective reads
> the category or the region of a future visit, and none reads the category of a place as a label to
> be classified. What a visit contributes is its own description: the category of the place visited is
> an input feature of its node, together with the hour and the day of the week.

### D2 · Replaces `2_fundamentals.tex:602-603` (assertion A3)

> It adds a fourth level below the place and learns one vector per visit from the visits themselves,
> with no next-category or next-region target in its objective. Each check-in node carries the
> category of the place visited and the time of the visit, so a category is an input, not a label.

### D3 · Replaces `2_fundamentals.tex:625-626` (assertion A9)

> No next-step target appears in these equations. Two auxiliary terms complete the objective the final
> study uses: a reconstruction term at weight 0.3, which recovers a masked place's own distribution
> over the seven categories from its neighbors, and a term at weight 0.1, which keeps the trainable
> place table near its pretrained values.

### D4 · Corrects A5, `2_fundamentals.tex:605-609`

Keep the equation and change the lead-in from "Its objective is the fixed-weight sum" to:

> Its three hierarchical boundaries contribute the fixed-weight sum

### D5 · One clause naming the POI2Vec-style anchor (AUT-21), for use where the spatial branch is
introduced

> The spatial branch starts from a table of place vectors pretrained by skip-gram over random walks on
> the graph of places, taken at the level of the fine class rather than the individual place, and that
> pretrained table is also the value the branch is kept near during training.

### D6 · If the author wants the graph channel named in the Fundamentals rather than only in Chapter 5

> Because a visit's node is linked to the visit that follows it and the category is a node feature, a
> visit vector can carry information about the next category; Chapter~\ref{ch:mobiwac} reports the
> screening audit that bounds this channel and states its three limits.

---

## 8 · Spec versus code

The spec and the code agree on every point this report turns on. Three notes where the spec is more
careful than the chapter, and one wording point:

1. Spec `:50` already states the correct scope: *"The representation builder never receives the
   supervised next-category or next-region targets. A visit's own category is nevertheless an input
   feature, and aggregated current-visit category features are used by the masked reconstruction
   auxiliary."* The chapter's absence claim is weaker than the spec it descends from.
2. Spec `:78` states *"The node has no learnable user-ID, POI-ID, latitude, or longitude feature on
   the active check-in path"*, which the eleven-column accounting in §0 confirms.
3. Spec `:343` calls the anchor coefficient `0.1`, agreeing with the code, and nowhere attributes a
   category term to it. The `1e-8` correction in §3.1 is a correction to the **prior audit's**
   phrasing, not to the spec.
4. One wording divergence, not a factual one: spec `:105` reports the Alabama cache as having
   *"219,976 directed sequence edges"*; the shipped cache's `edge_index` is `(2, 219976)`, so the
   count matches exactly.

---

## 9 · [VERIFY] flags

- **[VERIFY: per-dataset generality of the eleven-column accounting.]** The feature-width and exact
  reconstruction test in §0, and the 96,326-window adjacency test in §4.2, were run on the **Alabama**
  cache only (`output/check2hgi/alabama/temp/checkin_graph.pt`). The construction code is
  dataset-independent and the seven-class taxonomy is shared, so the same eleven columns are expected
  everywhere, but I opened one cache, not six. The other five were not tested and inherit no verdict
  from this one.
- **[VERIFY: which `le_lambda` value produced the shipped POI2Vec tables.]** The default is `1e-8` and
  the runner does not override it (`run_poi2vec.py:38-46`), so `1e-8` is what a rerun would use. I did
  not find a provenance record inside `output/hgi/<state>/` stating the value used for the tables now
  on disk, so the claim rests on the code path rather than on a recorded run.
- **[VERIFY: no per-state override of the five loss weights at build time.]** The weights in §3 are the
  builder's defaults, and the spec's reproduction command at `:606-628` passes them explicitly with
  the same values. I did not locate a per-dataset launch log for the six shipped builds, so I cannot
  state from a run record that no dataset was built with a different weight.
- **[VERIFY: whether "graph node", "node feature", and "edge weight" need GLOSSARY rows.]** Author's
  call, per the fail-closed rule. The drafts in §7 use them.
- **[NOT ATTEMPTED, and flagged rather than guessed.]** Whether the shipped v14 build for each dataset
  was produced by `scripts/probe/build_design_k_delaunay.py` rather than by another script with
  different defaults. `output/check2hgi_design_k_resln_mae_l0_1/<state>/` carries the three parquet
  tables but no provenance JSON that I could find, and the archaeology budget was reached.

## 10 · What a second pass should re-check first

The claim in §4.2 is the one that justifies changing the document, so it is the one to attack. Two
specific attacks: rerun the window-adjacency test on a second dataset, and confirm from a launch
record that the exported tables were produced with `--num-layers 2`, since a one-layer encoder would
still reach the target visit in one hop and a three-layer one would reach further.
