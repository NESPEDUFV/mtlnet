# Faithful STAN baseline

Self-contained reproduction of STAN (Luo, Liu, Liu. WWW 2021) adapted to the
next-region task on Gowalla state-level check-ins.

## What "faithful" means here

Unlike the in-house `next_stan` head in `src/models/next/next_stan/` — which
consumes Check2HGI / HGI region embeddings as input and uses a relative-
position-only pairwise bias — this baseline:

1. Learns its own POI embedding table from scratch (`nn.Embedding(n_pois, d_model)`).
2. Computes the pairwise attention bias from **raw Δt (minutes) and Δd
   (haversine km)** between every pair of check-ins in the 9-window, via
   STAN's interpolated 1-D interval-embedding tables.
3. Runs the bi-layer self-attention (trajectory aggregation + matching) on
   these inputs.
4. Projects the matching-layer output to `n_regions` for the classifier head.

The only adaptation vs the published architecture is the **target**: STAN's
paper predicts next-POI (~10 K candidates); we predict next-region (~1.1 K
on AL, ~1.5 K on AZ) so the result is comparable to our table. Everything
upstream of the classifier projection matches STAN's design.

## Components

- `etl.py` — slides 9+1 windows over `data/checkins/<State>.parquet`, joins
  in lat/lon/datetime per position, derives target_region via the existing
  Check2HGI graph (placeid_to_idx + poi_to_region), saves
  `output/baselines/stan/<state>/inputs.parquet`.
- `model.py` — `FaithfulSTAN` module: POI embedding + ΔT/ΔD pairwise-bias
  bi-layer self-attention + region classifier.
- `train.py` — StratifiedGroupKFold(5, seed=42), 50 epochs, AdamW + OneCycleLR,
  CrossEntropy. Writes JSON to `docs/results/baselines/`.

## CLI

```bash
PY=/Users/vitor/Desktop/mestrado/ingred/.venv/bin/python
PYTHONPATH=src DATA_ROOT=/path/to/data OUTPUT_DIR=/path/to/output \
  "$PY" -m research.baselines.stan.etl --state alabama
PYTHONPATH=src DATA_ROOT=/path/to/data OUTPUT_DIR=/path/to/output \
  "$PY" -m research.baselines.stan.train --state alabama --folds 5 --epochs 50 \
    --tag FAITHFUL_STAN_al_5f50ep
```
