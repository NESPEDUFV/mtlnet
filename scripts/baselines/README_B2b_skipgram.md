# Baseline B2b — Skip-gram (word2vec / SGNS) over check-in sequences

**Class (A) SC-SUBSTRATE-COLUMN** baseline for the matched-head MTL board.
Emits a 64-d check-in-level embedding probe-engine that plugs into the FROZEN
champion pipeline (`cat=next_gru`, `reg=next_stan_flow_dualtower`,
`model=mtlnet_crossattn_dualtower`) via `scripts/train.py --engine`. Only the
substrate axis changes; folds / seeds / labels / metric / heads / selector are
identical to the champion.

## Files (NEW — no edits to `src/` or `scripts/train.py`)
- `scripts/baselines/skipgram_lib.py` — pure SGNS library (Mikolov et al.,
  NeurIPS 2013): center/context tables, unigram^0.75 negative sampling,
  dynamic window, Adam. No side effects on import.
- `scripts/baselines/build_b2b_skipgram_substrate.py` — per-(state,seed,fold)
  leak-safe builder: derives the train-user set, trains skip-gram on
  train-portion POI sequences ONLY, emits a row-aligned check-in-level
  `embeddings.parquet`, then builds `next.parquet` + `sequences_next.parquet`
  + `next_region.parquet` and symlinks `region_embeddings.parquet`.

## Method
Treat each user's chronologically ordered `placeid` trajectory as a "sentence";
run SGNS to learn a 64-d vector per POI; look the vector up per check-in (same
POI => same vector). Standard POI-seq treatment (cf. DeepCity arXiv:1610.03676,
CAPE, SG-CWARP). The emitted `embeddings.parquet` keeps check2hgi's exact row
order (sorted `['userid','datetime']`) so `generate_next_input_from_checkins`
produces row-aligned matched-head inputs.

## Leak-safety (HARD requirement — enforced)
1. `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)` over the
   frozen check2hgi `next.parquet` (`groups=userid`, `y=next_category`). Verified
   **bit-identical** to `FoldCreator._create_check2hgi_mtl_folds` /
   `compute_region_transition._build_per_fold` (same train_idx arrays AND user
   sets).
2. `train_userids = set(userids[train_idx])`; `assert train.isdisjoint(val)`.
3. Skip-gram trains ONLY on POI sequences whose `userid in train_userids`.
4. POIs unseen in train users -> deterministic ZERO vector (cold-start
   placeholder, index 0; never trained on val users => no leak). Smoke cold rate
   AL fold0 = 2.1%.
5. The reg ranking prior (seeded per-fold `log_T`) is the champion's own
   `region_transition_log_seed{S}_fold{N}.pt`, passed via
   `--per-fold-transition-dir output/check2hgi/<state>` — substrate-independent.
   Run the STALE-log_T mtime preflight before any scored run.

## Deviations (documented)
- The in-repo `research/embeddings/hgi/poi2vec.py` is the FCLASS-level HGI
  teacher (categories), NOT this baseline. B2b is a standalone POI-level
  skip-gram column.
- Cold-start POIs get a zero vector (above).
- The region label space is the shared check2hgi TIGER-tract partition (the
  geographic partition is substrate-independent; `region_embeddings.parquet`
  is symlinked from check2hgi).
- WINDOWING: this builder defaults to the CURRENT stride-9 (non-overlapping)
  windows for the smoke / code path. The board's paper-grade n=20 runs are
  stride-1 (P3, post-freeze) — pass `--stride 1`.

## Smoke (tiny — AL, 1 seed, 5 folds @ 1 epoch; do NOT run full n=20)
Build a self-contained scratch overlay (frozen check2hgi read-only) and train:
```bash
SCRATCH=/tmp/bl_b2b/output; rm -rf $SCRATCH && mkdir -p $SCRATCH
OUTPUT_DIR=$SCRATCH DATA_ROOT=$PWD/data PYTHONPATH=src .venv/bin/python \
  scripts/baselines/build_b2b_skipgram_substrate.py \
  --state alabama --seed 0 --fold 0 --epochs 2 --window 3 \
  --engine-value check2hgi --read-output-dir $PWD/output

OUTPUT_DIR=$SCRATCH DATA_ROOT=$PWD/data RESULTS_ROOT=/tmp/bl_b2b/results \
PYTHONPATH=src .venv/bin/python scripts/train.py \
  --task mtl --task-set check2hgi_next_region --engine check2hgi \
  --state alabama --seed 0 --folds 5 --epochs 1 --batch-size 2048 --no-checkpoints \
  --model mtlnet_crossattn_dualtower --cat-head next_gru --reg-head next_stan_flow_dualtower \
  --task-a-input-type checkin --task-b-input-type region --log-t-kd-weight 0.0 \
  --per-fold-transition-dir $PWD/output/check2hgi/alabama
```
SMOKE PASS criteria: leak-disjoint assert holds; skip-gram converges; substrate
row-aligns (`next==region==seq`); all 5 folds run; per-fold JSONs carry the
scored keys (`diagnostic_best_epochs.next_category.f1`, `...next_region`).
(Numbers at ep1 are near floor — smoke proves PLUMBING, not quality.)

Known: at ep1 with an untrained substrate the reg metrics are degenerate, which
trips a PRE-EXISTING quirk in frozen `src/tracking/storage.py:157`
(`statistics.stdev` over identical fold values) during the AGGREGATE summary —
AFTER all per-fold scored JSONs are written. Not a B2b bug; absent at the
paper-grade 50-epoch run. Do not patch frozen `src/`.

## P3 scored run (post-freeze) — ENUM-MERGE note
For the scored n=20 paper run, emit per-fold engine dirs and run train.py per
fold with `--folds 1` against the matching `--per-fold-transition-dir`. This
needs ONE shared-file edit (sequential `[ENUM-MERGE]`, integrator merges last):
append `B2B_SKIPGRAM = "b2b_skipgram"` to `EmbeddingEngine` (END of enum, no
reorder) and add it to the three allow-lists:
`paths.get_next_region.supported`, `folds._MTL_C2HGI_ALLOWED_ENGINES`,
`builders._CHECKIN_LEVEL_ENGINES`. The builder already monkeypatches these at
RUNTIME (process-local) so dev/smoke needs ZERO enum edits.
