# GeoTreeSkipGram — geographically-tree-regularized skip-gram, per-POI 64-d substrate

> ⚠ **This is NOT POI2Vec (Feng et al., AAAI 2017).** It was originally mislabeled
> "B2a POI2Vec"; the audit (`docs/studies/closing_data/BASELINES_IMPL_AUDIT.md`) found it
> diverges from POI2Vec on the defining mechanism, so it was relabeled (class
> `GeoPOI2Vec → GeoTreeSkipGram`). The **faithful AAAI'17 POI2Vec** lives in
> `scripts/baselines/poi2vec_lib/` + `build_poi2vec_substrate.py`. This module is kept as a
> separate, honestly-named baseline (a geo-regularized skip-gram is a legitimate method).

Class-(A) SC-substrate-column baseline. Emits a probe-engine substrate that plugs into the
FROZEN matched-head MTL board (cat=`next_gru`, reg=`next_stan_flow_dualtower` / H3-alt
`next_getnext_hard`) via `train.py --engine`, exactly like
`scripts/mtl_improvement/build_overlap_probe_engine.py`.

## What it is
word2vec/skip-gram over POI check-in sequences, with a soft **geographical regularizer**
injected through a binary tree over a recursive rectangular partition of the map
(hierarchical-softmax routing). POIs near a split line route to both children with a
heuristic influence weight phi. Output = a per-POI latent table (center embeddings) — the
standalone 64-d POI column this baseline emits. Implemented in
`geotree_skipgram_lib/model.py` (`build_geo_binary_tree`, `GeoTreeSkipGram`); the geo
path-loss is vectorized (flat packed edges + scatter-add).

## How it differs from AAAI'17 POI2Vec (why it is not POI2Vec)
1. **Objective**: skip-gram (single center→context pair) — the paper is **CBOW** (sum a
   context window, route the TARGET POI's tree path against it).
2. **phi**: ad-hoc boundary-fraction heuristic — the paper's phi is the normalized
   **overlap area** of a POI's theta-buffered box with each leaf rectangle.
3. **Tree**: data-dependent **median kd-tree** — the paper's is a **fixed recursive
   rectangular midpoint grid** to a theta cell size.
4. **No user latent** — the paper includes a user term in the objective.

## Not the in-repo `hgi/poi2vec.py`
`research/embeddings/hgi/poi2vec.py` is an **fclass-level Node2Vec teacher used inside HGI**
(POIs of the same fclass share a vector); it is itself mislabeled "POI2Vec" and is also not
the AAAI'17 model. Distinct from both this baseline and the faithful `poi2vec_lib/`.

## Leak-safety (HARD requirement — enforced)
Pretrained on the fold's **TRAIN portion only**. The split is reproduced bit-identically with
`StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed)` over
`load_next_data(state, CHECK2HGI)` — same algorithm/groups(userid)/y(next_category)/seed as
`FoldCreator._create_check2hgi_mtl_folds` and `compute_region_transition._build_per_fold`.
Skip-gram pairs come ONLY from train-users' check-ins; `assert val_users.isdisjoint(train_users)`
runs before training. One substrate is emitted PER (state, seed, fold); score it with
`train.py --only-fold k` against that engine dir (fully leak-clean). The reg ranking prior
`region_transition_log_seed{S}_fold{N}.pt` is per-fold/per-seed; rebuild it for the trainer's
n_splits before each scored run (the trainer hard-asserts n_splits consistency — a leak guard).

## Row-alignment
The matched heads consume a check-in-level `embeddings.parquet`
(`userid,placeid,category,datetime,0..63`) in the check2hgi row order. We LEFT-JOIN the per-POI
table onto the frozen check2hgi embeddings frame on `placeid`, then run the canonical
`generate_next_input_from_checkins` + `build_next_region_for`. Asserts:
`len(embeddings)==len(check2hgi embeddings)` and `len(next)==len(next_region)==len(sequences)`.

## Run
Smoke (AL, 1 fold, 2 epochs, scratch OUTPUT_DIR, frozen output/ untouched):
```bash
bash scripts/baselines/smoke_geotree_skipgram.sh           # DEV=cuda by default
```
Build one leak-safe per-fold substrate:
```bash
OUTPUT_DIR=/tmp/bl_geotree PYTHONPATH=src .venv/bin/python \
  scripts/baselines/build_geotree_skipgram_substrate.py <state> --seed <S> --fold <N> \
  --epochs 5 --max-pairs 0 --device cuda
```
Then run the champion recipe with `--engine <X> --only-fold <N>` pointed at that dir. For P3,
pass `--stride 1` to the builder (overlapping windows) and re-run n=20.

## Enum note (for the integrator)
Dev + smoke use the zero-enum-edit escape hatch (scratch `OUTPUT_DIR` + `--engine check2hgi`).
For the SCORED P3 run, append ONE `EmbeddingEngine` member at the END of the enum
(`BASELINE_GEOTREE_SKIPGRAM = "baseline_geotree_skipgram"`) and add it to `get_next_region`
`supported`, `folds._MTL_C2HGI_ALLOWED_ENGINES`, and `builders._CHECKIN_LEVEL_ENGINES`. Tag
the PR `[ENUM-MERGE]`; merge last.
