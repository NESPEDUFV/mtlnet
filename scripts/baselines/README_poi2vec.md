# FAITHFUL POI2Vec (AAAI 2017) — class-(A) SC-substrate-column baseline

**Reference**: Feng, Cong, Chen, Yeo, "POI2Vec: Geographical Latent Representation
for Predicting Future Visitors", AAAI 2017. Reference impl:
`github.com/yongqyu/POI2Vec`.

This builder (`build_poi2vec_substrate.py` + `poi2vec_lib/`) is the **faithful**
AAAI'17 POI2Vec, built as a substrate-column baseline for the board: it pretrains a
per-POI 64-d table and plugs it **under the matched champion heads** (cat=`next_gru`,
reg=`next_stan_flow_dualtower`) via `train.py --engine`, leak-safe per
`(state, seed, fold)`. It is the integration-template twin of
`build_geotree_skipgram_substrate.py` / `build_b2c_onehot64_substrate.py`.

> **Why a new file, not a fix to `geotree_skipgram`?** The existing
> `geotree_skipgram` baseline gets **all four** of POI2Vec's defining mechanisms wrong
> (skip-gram not CBOW; ad-hoc boundary-fraction phi not overlap-area; data-dependent
> median kd-tree not a fixed midpoint grid; no user term). It is kept as its own
> honest geo-regularized-skip-gram baseline; this is the faithful POI2Vec.

## The four things that make it POI2Vec (done RIGHT here)

1. **FIXED recursive rectangular MIDPOINT tree** (`build_midpoint_tree`,
   `poi2vec_lib/model.py`). Split each node's rectangle at its geometric midpoint,
   **alternating the split axis by depth parity** (lon at even depth, lat at odd),
   recursing until **both** side lengths ≤ `--theta` degrees. **Breadth-first node
   numbering.** This geometry is **data-independent** (depends only on bbox + theta),
   so it is built once per state and is fold-independent → leak-safe to compute over
   all POI coords (coordinates are not labels).

2. **OVERLAP-AREA phi** (`build_poi_routes`). Each POI gets a `theta`-sided
   axis-aligned box around its (lon,lat); we intersect it with every leaf rectangle it
   overlaps and set `phi_leaf = intersection_area / sum_of_intersection_areas`
   (so `sum(phi)=1`). Capped to the top `--route-count` (default 4) leaves
   (renormalized). A POI fully inside one leaf gets `phi=[1.0]`. Verified by
   `poi2vec_lib/test_phi.py` on a hand-built 2×2 grid.

3. **CBOW forward + hierarchical softmax + USER term** (`POI2VecAAAI.forward_nll`).
   Per example: take a context window of POIs, **SUM** their input embeddings **+ the
   user vector**, and route the **target** POI's tree path(s) against that summed
   vector. Per-leaf path prob = `prod_edge sigmoid(dir · ⟨ctx_sum, node_vec⟩)`; because
   the target routes to multiple leaves, per-leaf probs are combined weighted by phi.
   The **user softmax is negative-sampled** (binary log-sigmoid on the true user + k
   sampled users) — NOT a full O(n_poi) softmax (the A40 OOMs on big states).

4. **Tables**: `poi_embed[n_poi,64]` (input/context embeddings — **THIS is the exported
   substrate**), `user_embed[n_user,64]` (`n_user` from a `userid→idx` map built over
   the raw userids `load_next_data` returns), `node_vec[n_internal,64]` routing
   vectors. **EXPORT ONLY `poi_embed`** (`POI2VecAAAI.export_table`).

## Loss form (the documented deviation)

The paper multiplies a user factor by the geographical path probability,
`pr = pr_user · pr_path`. We realize this as an additive log-loss with each factor
entering **exactly once**:

```
loss = -log(pr_path) - log(pr_user)        # == -log(pr_path · pr_user)
```

- **pr_path** (geographical, multi-leaf). Default = a numerically-**stable phi-weighted
  mixture** (`--loss-form mixture`): `pr_path = sum_leaf phi_leaf · pr_path_leaf`, with
  `pr_path_leaf = prod_edge sigmoid(dir · ⟨ctx_sum, node_vec⟩)`. The paper's exact
  **noisy-OR** `pr_path = 1 - prod_leaf(1 - pr_path_leaf)` is available via
  `--loss-form noisy_or` (verified NaN-free at 2 epochs on AL); it underflows to
  `log(0)` early on the 16k-leaf grid (zero-init node vectors → all sigmoids ≈ 0.5,
  products tiny), hence the stable mixture default.
- **pr_user** (user factor). `sigmoid(⟨ctx_sum, user_true⟩)`, the word2vec-NEG
  approximation of the paper's user softmax: a positive on the true user + k sampled
  negatives (avoids the O(n_poi) full softmax that OOMs big states on the A40).

Because `pr_user` is per-SAMPLE (user-level), `-log(pr_path) - log(pr_user)` is exactly
the paper's multiplicative `pr = pr_user · pr_path` with the user factor entering ONCE.
**[MF1, fixed]** an earlier build double-counted `pr_user` — as a per-leaf path gate AND
the separate NEG term (= `pr_user²`); the path gate was removed so it now enters once.

This is the one **mechanism-level** deviation (mixture vs noisy-OR for the path
combination), and it is opt-out (`--loss-form noisy_or` reproduces the paper's form).

## Deviations from AAAI'17 (and which are intentional matched-protocol choices)

| # | Deviation | Intentional / why |
|---|-----------|-------------------|
| D1 | **DIM = 64**, not the paper's 200. | **Intentional matched-protocol.** The board's SC comparison varies only the *substrate* under fixed 64-d heads; 200-d would confound the substrate axis. Set by `--embed-dim 64`. |
| D2 | Default loss = **stable phi-weighted mixture** NLL, not the paper's noisy-OR. | Numerical stability (see §loss). Paper form available via `--loss-form noisy_or`. |
| D3 | User softmax = **negative sampling** (k=5), not full softmax. | **Intentional.** Full O(n_user) softmax is fine but the user *path-gate* and the paper's joint normalization over all POIs is what OOMs; NEG is the reference-impl approach and avoids the big-state A40 OOM. |
| D4 | Tree depth driven by `--theta` (cell size), with a `max_depth=40` safety cap. | Faithful — the paper's tree is "to a theta cell size"; the cap only guards pathological bboxes. |
| D5 | CBOW window is **forward/causal** (target at t, context = preceding up-to-W POIs), sourced from the champion's `sequences_next` windows. | Matches POI2Vec's "predict future visitor" framing and keeps row-alignment with the matched heads. The paper uses a symmetric context; forward is the causal-prediction specialization used here for parity with the next-POI task. |
| D6 | `user_embed` / `poi_embed` share a single dim (`--user-dim` is accepted but coerced to `--embed-dim`). | Simplicity; both are 64-d. A mismatched user-dim would need a projection the paper does not specify. |
| D7 | Coords are the **mean (lon,lat) per placeid** from `IoPaths.load_city`; bbox from finite coords. | Standard; POIs with missing/out-of-bbox coords fall back to the nearest leaf center with `phi=[1.0]` (degenerate, documented in `build_poi_routes`). |

## Leak-safety & row-alignment (VERBATIM from the geotree template)

- `reproduce_fold_train_idx` reproduces `FoldCreator._create_check2hgi_mtl_folds`
  (`folds.py:1162`) bit-identically: `StratifiedGroupKFold(userid, n_splits, shuffle,
  random_state=seed)` over `load_next_data(state, CHECK2HGI)`. We take `train_idx`,
  derive the train-user set, **assert val users are disjoint**, and build CBOW examples
  ONLY from train-user check-ins.
- The emit block reconstructs the check-in-level `embeddings.parquet` by LEFT-JOIN of
  the per-POI table onto the check2hgi embeddings frame on `placeid`, then runs the
  canonical `generate_next_input_from_checkins` + `build_next_region_for` so
  `next`/`next_region`/`sequences` are row-aligned (asserts mirror the champion's).
- **Required hardening**: `assert_not_clobbering_frozen` runs at the TOP of `main()`,
  before any write, and refuses to write into the frozen `output/check2hgi/<state>/`
  tree (embeddings + next + next_region) unless `OUTPUT_DIR` is a scratch dir.

## Usage

Smoke (leak-safe, 1 fold, 2 epochs, CPU, scratch dir):

```bash
bash scripts/baselines/smoke_poi2vec.sh           # AL, seed 0, fold 0, theta 0.05
```

Direct build into a scratch `OUTPUT_DIR`:

```bash
OUTPUT_DIR=/tmp/bl_poi2vec PYTHONPATH=src .venv/bin/python \
  scripts/baselines/build_poi2vec_substrate.py alabama --seed 0 --fold 0 \
  --epochs 30 --theta 0.05 --route-count 4 --context-window 9 \
  --user-dim 64 --device cuda
```

CLI: `--theta`, `--route-count 4`, `--user-dim 64`, `--epochs 30`,
`--context-window 9`, `--device`, `--loss-form {mixture,noisy_or}`, `--n-neg-user 5`,
`--seed`, `--fold`, `--n-splits 5`, `--batch-size`, `--lr`, `--max-examples`,
`--stride`, `--all-data` (leaky smoke only).

For a scored board run, register a dedicated `EmbeddingEngine` member and emit there
(deferred to the main agent's consolidated commit — this builder uses the
`PROBE_ENGINE=CHECK2HGI` + scratch-`OUTPUT_DIR` zero-enum escape hatch).
