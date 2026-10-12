# POI2HGI: POI Embeddings with Temporal Features

## Overview

POI2HGI generates POI embeddings using **temporal patterns** and **spatial hierarchy**, without using category information as input features. This is designed for downstream tasks where category is the prediction target.

## Key Difference from HGI

| Aspect | HGI | POI2HGI |
|--------|-----|---------|
| Node features | Category one-hot | Temporal patterns (36-dim) |
| POI2Vec step | Optional pre-training | Not needed |
| Region similarity | Category distribution | Temporal distribution |
| Use case | General POI embeddings | Category prediction task |

## Architecture

```
POI (temporal features) → POI Encoder (GCN) → POI2Region (Attention) → Region2City
      [N_pois, 36]           [N_pois, 64]        [N_regions, 64]          [64]
```

Reuses HGI's model components:
- `POIEncoder`: 2-layer GCN with PReLU
- `POI2Region`: Multi-head attention pooling + region GCN
- `HierarchicalGraphInfomax`: Mutual information maximization

## Temporal Features (36 dimensions per POI)

| Feature | Dimensions | Description |
|---------|------------|-------------|
| `hour_hist` | 24 | Normalized histogram of visit hours (0-23) |
| `dow_hist` | 7 | Normalized histogram of visit days (Mon-Sun) |
| `hour_mean_sin` | 1 | sin(2π × mean_hour / 24) |
| `hour_mean_cos` | 1 | cos(2π × mean_hour / 24) |
| `dow_mean_sin` | 1 | sin(2π × mean_dow / 7) |
| `dow_mean_cos` | 1 | cos(2π × mean_dow / 7) |
| `visit_count_log` | 1 | log(1 + num_checkins), normalized |

## Usage

### Command Line
```bash
cd /Users/vitor/Desktop/mestrado/ingred
PYTHONPATH=src python -m embeddings.poi2hgi.poi2hgi --city Alabama --device mps
```

### Pipeline
```bash
python pipelines/embedding/poi2hgi.pipe.py
```

### Programmatic
```python
from embeddings.poi2hgi import create_embedding
from argparse import Namespace

args = Namespace(
    shapefile='path/to/shapefile.shp',
    force_preprocess=False,
    dim=64,
    attention_head=4,
    alpha=0.5,
    lr=0.001,
    gamma=1.0,
    max_norm=0.9,
    epoch=2000,
    device='mps'
)
create_embedding(state='Alabama', args=args)
```

## Output

### POI Embeddings
`/output/poi2hgi/{state}/embeddings.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `placeid` | str/int | POI identifier |
| `category` | str | Original category (for reference only) |
| `0` - `63` | float32 | 64-dim embedding |

### Region Embeddings
`/output/poi2hgi/{state}/region_embeddings.parquet`

| Column | Type | Description |
|--------|------|-------------|
| `region_id` | int | Region index |
| `reg_0` - `reg_63` | float32 | 64-dim embedding |

## Files

- `__init__.py` - Module exports
- `preprocess.py` - Temporal feature extraction and graph construction
- `poi2hgi.py` - Training script
- `CLAUDE.md` - This documentation

## Dependencies

Reuses from HGI:
- `embeddings.hgi.model.HGIModule`
- `embeddings.hgi.model.POIEncoder`
- `embeddings.hgi.model.RegionEncoder`
- `embeddings.hgi.utils`
