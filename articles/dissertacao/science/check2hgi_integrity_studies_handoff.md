# Check2HGI representation integrity: evidence, limits, and study handoff

> **Purpose.** This document records the evidence behind the dissertation paragraphs
> *Whole-dataset training* and *Links between consecutive visits*. It also defines a replacement
> study that can settle both questions more directly. It is an internal scientific handoff, so it
> uses repository paths and operational model names that should not appear in dissertation prose.
>
> **Working directory for every relative path and command:**
> `/Users/vitor/Desktop/mestrado/ingred`.
>
> **No new experiment was run for this document.** Every result below comes from an existing JSON,
> CSV, script, or study record. The proposed study is a design for the next agent to implement and
> run.

---

## 1. The two questions in one page

The two integrity questions concern different paths through the representation.

1. **Whole-dataset training:** Check2HGI is trained once on the complete graph before the
   downstream user-disjoint folds are trained. Therefore, its parameters and exported vectors were
   shaped by visits from users who later belong to a validation fold. The question is whether this
   changes validation performance relative to a Check2HGI model trained with training users only.

2. **Links between consecutive visits:** the check-in graph connects consecutive visits in both
   directions, and the observed category of every visit is a node feature. The target visit is
   therefore a graph neighbor of the last observed visit. The question is whether the target
   category can pass through this edge into the last observed visit vector.

These paths must not be merged.

```text
Whole-dataset path
validation users' visits
        -> representation training
        -> learned parameters and vectors
        -> validation prediction

Consecutive-link path
target visit's observed category
        -> target node feature
        -> backward temporal graph edge
        -> last observed visit vector
        -> next-category prediction
```

The existing studies reduce concern about both paths, but neither settles the final reported
representation:

- The whole-dataset study found changes close to zero at three datasets. Its category arm used
  place-level vectors on only the validation windows whose places occurred in training. It did not
  measure the visit-level category input used by the reported model.
- The consecutive-link screen detected a graph-attention encoder that made the next category much
  easier to recover from one visit vector. However, the screen was run at Florida on development
  encoders, not on the final Check2HGI representation. Its linear classifier is also known to miss
  at least one nonlinear leak.

The strongest new study should solve both gaps together. It should train Check2HGI without
validation users, save the trained check-in encoder, and use that encoder to create validation-user
visit vectors from causal history edges. This provides the missing visit-level out-of-sample
representation and prevents the target visit from sending its category to the observed history.

---

## 2. Which Check2HGI is used in the reported system

The version map is defined in
`articles/dissertacao/science/check2hgi_v17_complete_picture.md`.

| Layer | Scientific identity | Operational identity |
|---|---|---|
| representation | Check2HGI v14, Design K | `check2hgi_design_k_resln_mae_l0_1` |
| windowed files | the same fixed v14 vectors under stride-1 windows | `check2hgi_dk_ovl` |
| downstream predictor | MTL v17 | `mtlnet_crossattn_dualtower` |

`check2hgi_dk_ovl` does not train another representation. It links to the v14 embedding tables and
creates nine-visit input windows. The final category stream receives a tensor of shape `[9, 64]`,
one contextual Check2HGI vector for each observed visit. The region stream receives nine
64-dimensional region vectors.

### 2.1 Inputs to one check-in node

The active check-in node input has 11 values:

```text
7-category one-hot
+ sin and cos of hour
+ sin and cos of day of week
```

The active check-in input does not contain user ID, place ID, coordinates, or a downstream
next-category target. The implementation is
`research/embeddings/check2hgi/preprocess.py:_build_node_features`.

### 2.2 Why a visit vector is contextual

The standard v14 check-in encoder is a two-layer residual GCN. It combines the node's 11 input
values with information from connected visits and exports one 64-dimensional vector for each
check-in. Consecutive visits of one user are connected in both directions by
`research/embeddings/check2hgi/preprocess.py:_build_user_sequence_edges`.

The vector of visit `t` is therefore not limited to the category and time of visit `t`. It can
contain information from adjacent visits. Since the target visit `t+1` is present in the complete
graph, a backward edge from `t+1` to `t` creates the consecutive-link path.

### 2.3 Training objective

The representation builder never receives the supervised next-category or next-region targets.
The complete active objective is:

```text
0.4 * check-in-to-place loss
+ 0.3 * place-to-region loss
+ 0.3 * region-to-city loss
+ 0.3 * masked-place category reconstruction
+ 0.1 * POI2Vec anchor
```

This distinction is important. The graph does not contain a column named `next_category`, but it
does contain the observed category of the node that later becomes the target of a supervised
window. A future category can therefore enter a history vector through graph message passing even
though it is absent from the self-supervised loss.

### 2.4 Durable exports and a limitation for new studies

The final builder exports:

- `embeddings.parquet`: one 64-dimensional row per check-in;
- `poi_embeddings.parquet`: one 64-dimensional row per place;
- `region_embeddings.parquet`: one 64-dimensional row per region.

The builder does not persist the selected `state_dict`. A new causal intervention cannot recompute
vectors with the exact fixed weights from the Parquet files alone. The replacement study must save
the selected checkpoint in a new study directory. It must not overwrite the fixed v14 artifacts.

---

## 3. Existing study A: whole-dataset training

### 3.1 Question and estimand

The study named A4 asks whether using the complete check-in graph changes downstream validation
performance. For each fold, it builds a Check2HGI representation using training users only and
compares it with the complete-corpus representation.

The recorded difference is:

```text
inflation = complete-corpus score - training-users-only score
```

A positive value favors the complete-corpus representation. A value near zero indicates that the
measured validation score did not depend strongly on including validation users during
representation training.

Primary record:

`docs/studies/pre_freeze_gates/A4_RESULTS.md`

Primary implementation:

- `scripts/pre_freeze_gates/a4_build.py`
- `scripts/pre_freeze_gates/a4_eval.py`
- `scripts/pre_freeze_gates/a4_cat_eval.py`

Raw committed results:

`docs/results/pre_freeze_gates/a4/`

### 3.2 Fold and build procedure

For each `(dataset, seed, fold)`, `a4_build.py` performs these operations:

1. Recreates the `StratifiedGroupKFold` split grouped by user.
2. Removes every validation user from the raw check-in table.
3. Builds a new check-in graph from the remaining users.
4. Trains the Design-K Check2HGI configuration for that fold.
5. Keeps the complete-data HGI Delaunay and POI2Vec spatial scaffolding fixed.
6. Saves training-only place and region vectors.
7. Maps training-only regions back to the complete region index space. Regions absent from training
   receive zero vectors.

The fixed HGI scaffolding means that A4 isolates the check-in-user transductive channel. It is not a
fully training-only reconstruction of every spatial input used by Design K.

### 3.3 Region arm

`a4_eval.py` builds the same nine-step region input with either the complete-corpus region vectors
or the training-only region vectors. It trains `next_stan_flow` and reports validation Acc@10.

The two arms use:

- the same train and validation indices;
- the same downstream training code;
- the same per-fold training-only region-transition matrix;
- the same device within one comparison.

The committed seed-0 results are:

| Dataset | Folds | Complete Acc@10 (0-100) | Training-only Acc@10 (0-100) | Difference (points) |
|---|---:|---:|---:|---:|
| Alabama | 5 | 61.89 | 62.22 | -0.33 points |
| Arizona | 5 | 53.08 | 53.06 | +0.01 points |
| Florida | 5 | 69.97 | 70.08 | -0.12 points |

Number sources:

- `docs/results/pre_freeze_gates/a4/a4_result_alabama_s0.json`
- `docs/results/pre_freeze_gates/a4/a4_result_arizona_s0.json`
- `docs/results/pre_freeze_gates/a4/a4_result_florida_s0.json`

The complete-corpus arm also reproduced the earlier v14 region result closely at Alabama and
Florida. This check found a column-selection defect during development and was the positive control
that showed the evaluation path could detect a broken representation.

### 3.4 Category arm

A training-only graph has no check-in nodes for validation users. The original A4 code could not
produce the visit-level validation vectors used by the category model. It therefore used a
place-level proxy:

1. Replace each visit vector with the trained vector of its place.
2. Keep only validation windows in which every observed place exists in the training-only graph.
3. Train the same `next_gru` procedure with complete-corpus or training-only place vectors.
4. Report macro-F1 on exactly the same covered validation rows in both arms.

The committed seed-0 results are:

| Dataset | Folds used | Complete macro-F1 (0-100) | Training-only macro-F1 (0-100) | Difference (points) | Covered validation rows |
|---|---:|---:|---:|---:|---:|
| Alabama | 5 | 29.07 | 28.78 | +0.29 points | 66.8% |
| Arizona | 5 | 31.09 | 30.83 | +0.27 points | 71.9% |
| Florida | 4 | 36.20 | 36.19 | +0.00 points | 86.9% |

Number sources:

- `docs/results/pre_freeze_gates/a4/a4_cat_result_alabama_s0.json`
- `docs/results/pre_freeze_gates/a4/a4_cat_result_arizona_s0.json`
- `docs/results/pre_freeze_gates/a4/a4_cat_result_florida_s0.json`

Florida has four category folds because fold 0 did not have the saved training-only place vectors
needed by this later proxy evaluation.

### 3.5 What A4 establishes

A4 found no meaningful advantage for the complete-corpus representation within the parts it
measured. The sign of the difference varies, and every mean difference is below one point. The
result appears at three datasets with different sizes and place coverage.

This is useful evidence against a large whole-dataset advantage. It is not evidence that the
reported representation is inductive.

### 3.6 What A4 does not establish

The following limits are material:

1. **The category arm is not the reported input.** It uses one vector per place. The reported model
   uses one contextual vector per check-in.
2. **The category arm excludes cold places.** Coverage is 66.8% to 86.9%, depending on the dataset.
3. **The region arm has low sensitivity to the representation.** Its downstream head includes a
   strong per-fold region-transition matrix. A4 recorded that a broken zero-dimensional embedding
   path still obtained substantial performance from this prior alone.
4. **Only seed 0 is committed.** The five folds are parts of one user partition, not five independent
   repetitions.
5. **Representation builds vary between runs.** `A4_RESULTS.md` records a later Alabama category
   draw of +0.88 points instead of the committed +0.29 points. The sign and small magnitude stayed
   consistent, but the decimal is not a deterministic constant.
6. **The spatial scaffolding remains complete-corpus.** The study holds HGI Delaunay and POI2Vec
   artifacts fixed on purpose.
7. **A4 does not solve out-of-sample check-in encoding.** It avoids this problem with the place-level
   proxy.

The missing item is an exact validation-user check-in vector created by an encoder trained without
that user.

### 3.7 Existing reproduction commands

The current scripts can reproduce the original design. The following example covers one Alabama
fold and the two evaluations after every fold has been built:

```bash
PYTHONPATH=src:research .venv/bin/python \
  scripts/pre_freeze_gates/a4_build.py \
  --state alabama --seed 0 --fold 0 --folds 5 --epochs 500

INGRED_DEVICE=cpu PYTHONPATH=src:scripts .venv/bin/python \
  scripts/pre_freeze_gates/a4_eval.py \
  --state alabama --seed 0 --folds 5 --epochs 30

INGRED_DEVICE=cpu PYTHONPATH=src:scripts .venv/bin/python \
  scripts/pre_freeze_gates/a4_cat_eval.py \
  --state alabama --seed 0 --folds 5 --epochs 30
```

`a4_build.py` must be run once for every fold before the evaluation commands. A rerun must use a new
output root or an explicit manifest because the script skips a fold when its output file already
exists.

---

## 4. Existing study B: links between consecutive visits

### 4.1 Exact path under study

For a supervised example, visits 1 through 9 are the observed history and visit 10 is the target.
The target visit is not part of the `[9, 64]` downstream input window. It is nevertheless present as
a node in the complete Check2HGI graph.

The graph creates this path:

```text
category one-hot of visit 10
        -> check-in encoder message passing
        -> 64-dimensional vector of visit 9
        -> category predictor
```

This is possible because:

- the category of every check-in is an input feature;
- consecutive visits are connected in both directions;
- the exported check-in vector is produced after graph message passing.

The standard final v14 encoder uses residual graph convolution at this level. The development
alternative called `check2hgi_gat` replaces this lower check-in encoder with
`GATTimeEncoder`. This is different from the attention pooling that Check2HGI uses between
check-ins and places, and it is different from the cross-attention in the downstream joint model.

### 4.2 Linear per-step screen

Primary implementation:

`scripts/embedding_eval/leak_sniff.py`

Primary results:

- `docs/results/embedding_eval/rescreen_cat/leak_sniff_fl.csv`
- `docs/results/embedding_eval/rescreen_cat/leak_sniff_resln_fl.csv`
- `docs/results/embedding_eval/rescreen_cat/RESCREEN.md`

For each encoder, the script loads the nine-visit category input as a flat matrix, infers the
per-visit width as `number_of_numeric_columns / 9`, and selects only the final 64 columns:

```python
last = X[:, -D:]
```

Each probe example therefore contains one 64-dimensional vector, the vector of the most recent
observed visit. The probe does not receive the other eight vectors, the joint model, or either task
head.

For each user-grouped fold, the script:

1. Computes the mean and standard deviation of each embedding dimension on training rows.
2. Standardizes training and validation rows with those training statistics.
3. Trains a new `torch.nn.Linear(64, 7)` classifier for 200 full-batch steps.
4. Reports macro-F1 on the validation users.

`GroupKFold(5)` is grouped by user. The splitter has no shuffle or seed. The linear layer itself is
not seeded in the script, so the stored result is one classifier-initialization draw per encoder.

The historical script also repeats the probe with raw vectors. The dissertation now reports only
the standardized comparison, but both values remain useful in this internal record.

### 4.3 Stored Florida results

| Encoder | Standardized last vector | Raw last vector | Difference from GCN reference, standardized | Stored verdict |
|---|---:|---:|---:|---|
| `check2hgi_gcn_ctrl` | 0.4090 | 0.4074 | 0.0000 | clean reference |
| `check2hgi_v3c_wd05` | 0.4087 | 0.4075 | -0.0003 | clean |
| `check2hgi_t24_dropedge` | 0.4090 | 0.4075 | +0.0000 | clean |
| `check2hgi_t43_sidefeat` | 0.4088 | 0.4066 | -0.0002 | clean |
| `check2hgi_t61_p2p` | 0.4073 | 0.4058 | -0.0017 | clean |
| `check2hgi_gat` | 0.4976 | 0.4863 | +0.0886 | leak |
| `check2hgi_rgcn` | 0.3328 | 0.4142 | -0.0762 | clean in this probe |

The graph-attention value is not critical because it is close to an absolute value of 0.50. It is
critical because the same probe and split give approximately 0.41 for the GCN reference and all
other non-attention candidates. The graph-attention encoder is an outlier by about 8.9 macro-F1
points under standardization.

The metric is macro-F1 over seven categories. A value of 0.4976 is not 49.76% classification
accuracy.

### 4.4 Why the reference score is nonzero

The reference embedding contains information about the current visit's category and time. Current
and next categories are correlated in mobility histories. A separate label-only benchmark confirms
that the history itself predicts the next category.

`docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.csv` reports for Florida:

| Input | Macro-F1 | Notes |
|---|---:|---|
| majority-class floor | 0.0566 | same class predicted for every row |
| best tested category-history predictor | 0.3617 | best of persistence, last category, counts, and nine-position category indicators |
| GCN reference, one contextual embedding | 0.4090 | linear probe on the last 64-dimensional vector |

The file calls 0.3617 a ceiling, but it is not a mathematical upper bound. It is the best result
among four implemented label-only predictors. The earlier `RESCREEN.md` phrase that describes an
approximate 0.45 label-history ceiling must not replace the later direct measurement of 0.3617.

A nonzero reference result is therefore expected. It does not prove a leak. It also does not prove
the absence of a leak because the reference vector is contextual and is built on the same
bidirectional graph.

### 4.5 Why the graph-attention result is a serious warning

`GATTimeEncoder` uses graph attention over the bidirectional user-sequence edges and can condition
attention on the temporal edge weight. The implementation note in
`research/embeddings/check2hgi/model/variants.py` records that this combination learned to copy a
recent connected category into the output.

The linear result has supporting downstream evidence. In the Florida development comparison:

| Encoder | Full next-category sequence model, macro-F1 |
|---|---:|
| GCN control | 0.6461 |
| graph attention | 0.9598 |
| R-GCN | 0.7539 |

Source: `docs/results/embedding_eval/rescreen_cat/RESCREEN.md`, complete Florida next-category
table.

The graph-attention result near 0.96 under the full sequence model is not consistent with ordinary
next-category predictability. It supports the forward-neighbor explanation found by the per-step
screen.

### 4.6 What the consecutive-link study establishes

The screen has three useful properties:

1. It uses one last-visit embedding, so a high score cannot be attributed to the downstream joint
   model or its nine-step sequence processing.
2. The GCN reference and graph-attention alternative use the same user groups and classifier
   design.
3. The graph-attention positive case shows that the screen can detect at least one encoder that
   makes future category information easier to recover.

The supported conclusion is relative: the graph-attention encoder exposes much more
next-category information to a linear classifier than the same-protocol GCN reference.

### 4.7 What the consecutive-link study does not establish

1. **It did not test the final v14 representation.** The final representation is
   `check2hgi_design_k_resln_mae_l0_1`; this name does not occur in the screening result directory.
2. **It covers Florida only.** Every row in the two leak-screen CSVs names Florida.
3. **It has no repeated probe seed.** The linear layer initialization is not seeded or repeated.
4. **It is a relative screen.** A channel shared by the GCN reference and every candidate could be
   present in all arms and remain hidden.
5. **A linear probe can miss a real leak.** The stored R-GCN row passes the per-step gate, while the
   full sequence model reaches 0.7539 against 0.6461 for the control. The study record explicitly
   states that the linear probe misses this nonlinear or multi-step case.
6. **It does not intervene on the target category.** It observes prediction scores but does not
   recompute the same history vector after masking or changing the target node feature.
7. **It does not compare causal and bidirectional graphs with the same trained weights.** Such a
   comparison would isolate the edge path directly.

### 4.8 Existing reproduction commands

The stored standardized and raw screen can be regenerated after the named embedding engines and
their `input/next.parquet` files exist:

```bash
PYTHONPATH=src .venv/bin/python \
  scripts/embedding_eval/leak_sniff.py \
  --state florida \
  --control check2hgi_gcn_ctrl \
  --engines check2hgi_gcn_ctrl check2hgi_v3c_wd05 \
            check2hgi_t24_dropedge check2hgi_t43_sidefeat \
            check2hgi_t61_p2p check2hgi_gat check2hgi_rgcn \
  --out docs/results/embedding_eval/rescreen_cat/leak_sniff_fl_rerun.csv
```

The label-only comparison is produced by:

```bash
PYTHONPATH=src .venv/bin/python \
  scripts/embedding_eval/autocorrelation_ceiling.py
```

Do not overwrite the committed source CSVs during a rerun. The linear probe is currently unseeded,
so a new file is expected to differ slightly.

---

## 5. The study that would settle both questions

### 5.1 Required scientific claims

The replacement study should estimate three separate effects:

1. **Whole-dataset effect:** the change caused by training the Check2HGI parameters with validation
   users included.
2. **Forward-edge effect:** the change caused by allowing a target visit to send messages to an
   observed history visit.
3. **Combined effect:** the difference between the reported full-graph representation and a
   training-users-only representation evaluated with causal history edges.

No result should use the word `leak-free`. A null score difference cannot prove the absence of all
future information. The strongest supported wording will depend on the controls below.

### 5.2 Key implementation change: save and reuse the check-in encoder

The final Design-K builder already tracks the state with the lowest training loss in memory. Add a
study-only option that writes this selected state to a new directory, for example:

```text
results/check2hgi_integrity_v2/
  <dataset>/
    split_seed_<s>/fold_<f>/representation_seed_<r>/
      complete/checkpoint.pt
      training_only/checkpoint.pt
```

Do not alter or overwrite `output/check2hgi_design_k_resln_mae_l0_1/`.

The checkpoint must include:

- the selected model `state_dict`;
- all constructor arguments;
- category vocabulary and order;
- representation width and layer count;
- graph feature schema;
- representation seed, split seed, fold, device, and software revision;
- hashes of every source data and spatial artifact used by the build.

The study needs the lower `ResidualLNEncoder` weights to create new check-in vectors. The upper
place and region modules are still needed during representation training because their objectives
shape the encoder.

### 5.3 Out-of-sample validation-user check-in vectors

After training a Check2HGI model with training users only:

1. Freeze the selected model weights.
2. Build check-in nodes for validation users from category and time features.
3. Build a directed history graph for these users. An edge may carry information from an earlier
   visit to a later visit, but not from a later visit to an earlier visit.
4. Run only the frozen check-in encoder to obtain one 64-dimensional vector per validation
   check-in.
5. Assemble the usual nine-visit windows from these vectors.

This operation does not require a validation place to occur in the training graph because the
active check-in encoder input has category and time features but no place-ID lookup. This closes the
place-level proxy and cold-place gaps in A4's category arm.

The edge direction must be verified against PyTorch Geometric's source-to-target convention. Do not
trust the names `forward`, `backward`, or `causal` without an intervention test.

### 5.4 Mandatory dependency test for the causal graph

For a fixed validation history and fixed encoder weights:

1. Compute the vector of the last observed visit.
2. Change only the one-hot category of the target visit.
3. Compute the last observed visit vector again.

Required controls:

- **Causal graph negative control:** the last observed vector must remain equal within a declared
  numerical tolerance.
- **Bidirectional graph positive control:** the same intervention must change at least one tested
  last-observed vector for an encoder known to use the backward edge.
- **Graph-attention positive control:** the probe or intervention must reproduce the known
  graph-attention warning. If it does not, the new instrument is not validated.

This test is stronger than a prediction score because it asks whether the target feature is a cause
of the history vector while all other inputs and weights remain fixed.

### 5.5 Experimental arms

Use the same data split, model initialization, downstream initialization, and evaluation rows
within each paired comparison.

| Arm | Representation training users | Validation inference edges | Purpose |
|---|---|---|---|
| R0 | complete dataset | original complete bidirectional graph export | reported-reference behavior |
| R1 | complete dataset | causal validation-user history graph | isolates the forward-edge path while keeping complete-data training |
| R2 | training users only | causal validation-user history graph | removes both validation-user training and the forward-edge path |
| P1 | same protocol as its control | bidirectional graph-attention encoder | required positive control |

Primary paired contrasts:

- `R0 - R1`: forward-edge contribution relative to the reported export;
- `R1 - R2`: whole-dataset parameter-training contribution under the same causal inference rule;
- `R0 - R2`: total change from the reported representation to the strict protocol.

R0 and R1 require a same-protocol complete-corpus rebuild if the exact v14 checkpoint is not
available. Compare their vectors and downstream scores with the fixed v14 export, but do not claim
byte equivalence. Seed pinning does not guarantee byte-identical graph training across devices.

### 5.6 Evaluation ladder

Run all arms through the following ladder. Each level answers a different question.

#### Level 0: direct vector dependency

- Change the target category and measure the last-vector change.
- Mask the target category and measure the last-vector change.
- Shuffle target categories between users as a second intervention.
- Report cosine change and L2 change, with the exact sample count.

The primary result is whether the causal arm is invariant while the positive control is not.

#### Level 1: single-vector probes

Use only the 64-dimensional vector of the last observed visit.

- linear classifier;
- small nonlinear MLP;
- standardized features using training-fold statistics only;
- repeated classifier seeds;
- GroupKFold or the exact stored user-disjoint fold indices.

The MLP is required because the existing linear screen misses the R-GCN case.

Report next-category macro-F1 beside:

- majority-class floor;
- last-category persistence;
- last-category balanced logistic classifier;
- complete nine-category-history benchmark;
- the graph-attention positive control.

Do not call the best implemented label-history model a mathematical ceiling.

#### Level 2: fixed single-task sequence models

Category:

- train `next_gru` on all nine check-in vectors;
- use identical train and validation rows across arms;
- report macro-F1 by fold and seed.

Region:

- evaluate a region model without the region-transition prior as the primary representation-sensitive
  result;
- evaluate the reported prior-equipped region head as a secondary compatibility result;
- report seen-region and unseen-region validation rows separately.

The no-prior region result is necessary because the existing A4 region head can obtain much of its
score without the embeddings.

#### Level 3: reported joint model

Run the reported joint model only after Levels 0 through 2 pass their controls. Use the same
training configuration, folds, seeds, selection metric, and evaluation convention as the reported
experiments. This level measures whether the strict representation changes the actual claim-bearing
system.

### 5.7 Seeds, folds, and pairing

The reported split seeds are `0`, `1`, `7`, and `100`. Each seed creates a different user partition
and model initialization. Fold numbers from different seeds are not the same partition.

For the replacement study:

- store the exact train and validation indices for every arm;
- assert that paired arms use identical indices;
- keep the representation seed identical within a pair;
- keep the downstream seed identical within a pair;
- record the device and precision;
- repeat the representation build because A4 shows non-negligible build-to-build variation.

The independent summary unit should be declared before analysis. A safe default is the mean across
five folds within each split seed, followed by inference across split seeds. Do not treat the five
folds of one partition as five independent datasets.

The number of representation repetitions and any practical-equivalence margin must be approved
before reading the new results. The existing 0.03 linear-screen margin is a development gate, not a
registered equivalence margin for the final representation.

### 5.8 Dataset order

Use a staged execution order:

1. **Alabama smoke and instrument validation.** It is the smallest U.S. graph and should detect
   construction errors quickly.
2. **Florida primary study.** It has the largest sample among the existing three-state integrity
   studies and contains the stored graph-attention positive case.
3. **Arizona replication.** It checks that a Florida conclusion is not isolated.
4. **California, Texas, and Istanbul coverage.** Run after the protocol and outputs are fixed.

The final claim must name the datasets actually completed. A three-dataset result cannot be written
as a six-dataset result.

### 5.9 Required output files

Use a new tracked result root, for example:

```text
docs/results/check2hgi_integrity_v2/
  PROTOCOL.md
  MANIFEST.json
  <dataset>/
    split_seed_<s>/
      fold_<f>/
        indices.npz
        build_complete.json
        build_training_only.json
        dependency_intervention.json
        linear_probe.json
        mlp_probe.json
        category_sequence.json
        region_no_prior.json
        region_reported_head.json
        joint_model.json
  summary.json
  summary.csv
```

Every result JSON must contain:

- dataset, split seed, representation seed, fold, and device;
- source and target arm names;
- row counts before and after every filter;
- metric name and selection convention;
- per-fold value, not only a mean;
- hashes of input vectors and fold indices;
- explicit skipped cells with reasons;
- software revision and command line.

The study must keep checkpoints and large vectors outside the tracked documentation tree if size
requires it, but `MANIFEST.json` must record their paths and hashes.

### 5.10 Decision table

| Observation | Supported interpretation | Action |
|---|---|---|
| Causal arm is invariant to target-category changes and positive control changes | edge-direction instrument works | continue to probes and downstream tests |
| Causal arm changes after a target-only intervention | causal graph is not causal or another path remains | stop and repair before training predictors |
| Positive control does not change | instrument cannot see the known problem | stop; do not interpret null results |
| R1 and R2 remain close across representation repetitions | whole-dataset parameter effect is small under causal inference | report a bounded effect with its interval and datasets |
| R0 differs from R1 while R1 and R2 are close | consecutive-link path is the main integrity issue | use causal representation or narrow the claims |
| R1 differs from R2 | validation-user representation training affects performance | reported transductive results require re-anchoring or stronger disclosure |
| Linear probe passes but MLP or sequence model fails | future information is nonlinear or distributed across steps | linear screen is insufficient; use the stronger result |
| Strict R2 changes the reported joint result materially | claim-bearing result depends on one or both channels | rerun the reported comparison with the strict representation |

No row in this table licenses the statement that no information from the future exists. The direct
intervention can establish that the tested target-category feature does not affect the tested
history vector under the tested causal construction.

---

## 6. Common mistakes to avoid

1. **Do not call `0.4976` accuracy.** It is macro-F1 over seven categories.
2. **Do not treat 0.50 or 0.60 as universal thresholds.** The warning is relative to matched controls
   and causal interventions.
3. **Do not say the linear classifier and graph attention are the same model.** The graph encoder
   produces embeddings. A separately trained linear classifier tests them.
4. **Do not say the probe receives one window.** It receives one vector from each example and is
   trained over many examples.
5. **Do not confuse lower graph attention with Checkin2POI attention pooling or downstream
   cross-attention.** They are different modules.
6. **Do not infer safety from the self-supervised objective.** The target category can enter through
   a node feature and an edge without appearing in the loss.
7. **Do not use validation statistics for standardization.** Fit all preprocessing on training rows
   within each fold.
8. **Do not compare different validation subsets.** Paired arms must use the same rows.
9. **Do not treat a missing place as a zero vector without reporting it.** Separate covered and
   uncovered rows.
10. **Do not keep the strong region-transition prior as the only region endpoint.** It reduces the
    sensitivity of the representation comparison.
11. **Do not report a new rerun as a reproduction of the exact committed decimal.** A4 records
    build-to-build variation.
12. **Do not overwrite fixed representation artifacts or committed result CSVs.** Use a new study
    root and a manifest.
13. **Do not count folds from one split as independent repetitions.** Aggregate according to the
    declared split-seed protocol.
14. **Do not interpret a null result until both positive and negative controls pass.**

---

## 7. Source map

### 7.1 Dissertation and scientific specifications

| Path | Use |
|---|---|
| `articles/dissertacao/src/chapters/5_mobiwac/05_setup.tex` | current dissertation explanation of both integrity questions |
| `articles/dissertacao/science/check2hgi_v17_complete_picture.md` | final Check2HGI identity, graph, features, objectives, export contract, and downstream use |
| `articles/dissertacao/science/fold_partition_and_seeds.md` | relation between split seeds, fold partitions, and reported statistical unit |
| `articles/dissertacao/WRITING_LAW.md` | dissertation language and claim rules |
| `articles/dissertacao/AGENT_GUARDRAILS.md` | number, claim, source, and verification rules |
| `articles/dissertacao/GLOSSARY.md` | canonical scientific terms |

### 7.2 Check2HGI implementation

| Path | Use |
|---|---|
| `research/embeddings/check2hgi/preprocess.py` | category and time node features; bidirectional user-sequence edges |
| `research/embeddings/check2hgi/model/variants.py` | residual GCN and graph-attention encoders |
| `research/embeddings/check2hgi/model/Check2HGIModule.py` | graph forward pass, losses, and stored embeddings |
| `research/embeddings/check2hgi/model/Checkin2POI.py` | check-in-to-place attention pooling |
| `scripts/probe/build_design_k_delaunay.py` | final v14 build, model selection, and embedding export |
| `scripts/mtl_improvement/build_overlap_probe_engine.py` | reuse of v14 vectors under the final nine-visit window protocol |

### 7.3 Whole-dataset study

| Path | Use |
|---|---|
| `docs/studies/pre_freeze_gates/A4_RESULTS.md` | main method, results, interpretation, and run-variance caveat |
| `scripts/pre_freeze_gates/a4_build.py` | training-users-only graph and representation build |
| `scripts/pre_freeze_gates/a4_eval.py` | region comparison |
| `scripts/pre_freeze_gates/a4_cat_eval.py` | in-coverage place-level category proxy |
| `docs/results/pre_freeze_gates/a4/a4_result_alabama_s0.json` | Alabama region values |
| `docs/results/pre_freeze_gates/a4/a4_result_arizona_s0.json` | Arizona region values |
| `docs/results/pre_freeze_gates/a4/a4_result_florida_s0.json` | Florida region values |
| `docs/results/pre_freeze_gates/a4/a4_cat_result_alabama_s0.json` | Alabama category values and coverage |
| `docs/results/pre_freeze_gates/a4/a4_cat_result_arizona_s0.json` | Arizona category values and coverage |
| `docs/results/pre_freeze_gates/a4/a4_cat_result_florida_s0.json` | Florida category values and coverage |

### 7.4 Consecutive-link study

| Path | Use |
|---|---|
| `scripts/embedding_eval/leak_sniff.py` | last-vector linear probe, standardization, grouping, and verdict rule |
| `docs/results/embedding_eval/rescreen_cat/leak_sniff_fl.csv` | GCN, graph-attention, R-GCN, and candidate results |
| `docs/results/embedding_eval/rescreen_cat/leak_sniff_resln_fl.csv` | residual-GCN candidate screen |
| `docs/results/embedding_eval/rescreen_cat/RESCREEN.md` | mechanism audit, full sequence results, and known linear false negative |
| `scripts/embedding_eval/autocorrelation_ceiling.py` | implemented label-history comparison |
| `docs/results/embedding_eval/rescreen_cat/autocorrelation_ceiling.csv` | label-history and majority-floor results |
| `articles/dissertacao/src_utils/_history/_round13/72_leak_screening_search.md` | audit of what the screen establishes and what remains untested |

---

## 8. Number ledger

| Value | Meaning | Source field or row |
|---:|---|---|
| 11 | active check-in node input width | `check2hgi_v17_complete_picture.md` section 3.2; `preprocess.py:_build_node_features` |
| 7 + 4 | seven category indicators plus four cyclic time values | same sources as the preceding row |
| 64 | check-in, place, and region representation width | `check2hgi_v17_complete_picture.md` sections 2 and 4 |
| 2 | residual GCN layers in the final check-in encoder | `check2hgi_v17_complete_picture.md` section 4.1 |
| 9 history visits, 10th target | supervised window contract | `check2hgi_v17_complete_picture.md` section 9 |
| 500 | Check2HGI training epochs in the final builder and A4 builds | `check2hgi_v17_complete_picture.md` section 7.1; `a4_build.py:--epochs` |
| 30 | downstream epochs in the stored A4 evaluation JSONs | `a4_result_*_s0.json:epochs`; evaluator defaults |
| 5 | user-grouped folds in A4 and the linear screen | A4 JSON `folds`; `leak_sniff.py:_probe` |
| 200 | full-batch optimization steps for each stored linear probe | `leak_sniff.py:_probe` |
| 0.03 | historical relative linear-screen margin | `leak_sniff.py:sniff` default; not a final-study equivalence margin |
| 0, 1, 7, 100 | reported downstream split seeds | `fold_partition_and_seeds.md` sections 3 and 5 |
| -0.3304 points | Alabama region complete minus training-only | `a4_result_alabama_s0.json:mean_inflation_pp` |
| +0.0114 points | Arizona region complete minus training-only | `a4_result_arizona_s0.json:mean_inflation_pp` |
| -0.1156 points | Florida region complete minus training-only | `a4_result_florida_s0.json:mean_inflation_pp` |
| +0.2936 points | Alabama category place-proxy difference | `a4_cat_result_alabama_s0.json:mean_inflation_pp` |
| +0.2665 points | Arizona category place-proxy difference | `a4_cat_result_arizona_s0.json:mean_inflation_pp` |
| +0.0031 points | Florida category place-proxy difference | `a4_cat_result_florida_s0.json:mean_inflation_pp` |
| 66.83% | Alabama category validation coverage | `a4_cat_result_alabama_s0.json:mean_incov_frac` |
| 71.87% | Arizona category validation coverage | `a4_cat_result_arizona_s0.json:mean_incov_frac` |
| 86.91% | Florida category validation coverage | `a4_cat_result_florida_s0.json:mean_incov_frac` |
| 0.4089797540 | standardized GCN-reference last-vector macro-F1 | `leak_sniff_fl.csv`, `check2hgi_gcn_ctrl:perstep` |
| 0.4976165004 | standardized graph-attention last-vector macro-F1 | `leak_sniff_fl.csv`, `check2hgi_gat:perstep` |
| 0.0886367464 | standardized graph-attention minus GCN reference | `leak_sniff_fl.csv`, `check2hgi_gat:delta_std` |
| 0.4074423291 | raw GCN-reference last-vector macro-F1 | `leak_sniff_fl.csv`, `check2hgi_gcn_ctrl:perstep_raw` |
| 0.4863103587 | raw graph-attention last-vector macro-F1 | `leak_sniff_fl.csv`, `check2hgi_gat:perstep_raw` |
| 0.3617 | Florida best implemented label-history macro-F1 | `autocorrelation_ceiling.csv`, Florida row |
| 0.0566 | Florida majority-class macro-F1 floor | `autocorrelation_ceiling.csv`, Florida row |
| 0.6461 | GCN-control full-sequence category macro-F1 | `RESCREEN.md`, complete Florida next-category table |
| 0.9598 | graph-attention full-sequence category macro-F1 | `RESCREEN.md`, complete Florida next-category table |
| 0.7539 | R-GCN full-sequence category macro-F1 | `RESCREEN.md`, complete Florida next-category table |
| +0.88 points | later Alabama A4 category rerun, used only to document build variation | `A4_RESULTS.md`, run-variance caveat |

Rounded dissertation values must continue to be derived from these source values rather than from
the rounded numbers in this handoff.

---

## 9. First actions for the next agent

1. Read this file and `check2hgi_v17_complete_picture.md` completely.
2. Confirm the final builder still does not save a checkpoint.
3. Create a study-only builder option that saves the selected model state without changing the
   fixed output directories.
4. Implement a minimal causal validation graph and the target-category perturbation test.
5. Validate edge direction with the graph-attention positive control before any full build.
6. Run one Alabama fold as an end-to-end smoke test.
7. Open every output file and count non-empty result cells before reporting that the run succeeded.
8. Freeze the protocol, margins, seeds, and output schema before the Florida study.
9. Run the complete paired arm matrix.
10. Only after the controls and primary results pass, revise the dissertation paragraphs.

The main priority is not another broad model comparison. It is a paired causal audit of the final
Check2HGI configuration with exact visit-level validation embeddings.
