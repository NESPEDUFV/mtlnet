# HGI (Hierarchical Graph Infomax) Embedding Module

This module implements the complete HGI pipeline for generating POI and region embeddings from spatial check-in data.

> **Looking for the agent-facing summary?** See `CLAUDE.md` in this directory.

---

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Flow](#pipeline-flow)
3. [Intermediate Files](#intermediate-files)
4. [Model Architectures](#model-architectures)
5. [Theory & Key Insights](#theory--key-insights)
6. [Usage](#usage)
7. [Configuration Reference](#configuration-reference)
8. [Migration & Validation](#migration--validation)
9. [Critical Fixes Made During Migration](#critical-fixes-made-during-migration)
10. [Performance Notes](#performance-notes)
11. [Test Suite](#test-suite)
12. [File Structure](#file-structure)
13. [⚠️ Smoke Testing Hazard](#️-smoke-testing-hazard)

---

## ⚠️ Smoke Testing Hazard

> **Read this BEFORE running `pipelines/embedding/hgi.pipe.py` for any reason that is not a full production regeneration.**

`pipelines/embedding/hgi.pipe.py` has `force_preprocess=True` baked into `HGI_CONFIG` and writes its outputs **unconditionally** into `output/hgi/<state>/` (and the downstream `input/category.parquet` + `input/next.parquet`). The pipeline does **not** read the existing artifacts before overwriting them — there is no "skip if up to date" check.

**This means a 3-epoch smoke run will silently overwrite a 2000-epoch production-quality artifact**, and the only recovery is restoring from a backup. This was hit during the torch 2.11 upgrade (PR #9, Gate 6b) — the worktree's `output/` was a symlink into the main repo, so a 3-epoch smoke clobbered the real Alabama HGI embeddings. Recovery required `rsync` from a sibling worktree that happened to have an intact non-symlinked copy.

### Before running ANY HGI smoke test, do ONE of these

1. **Snapshot the existing output** (cheapest, always safe):
   ```bash
   cp -a output/hgi/<state> output/hgi/<state>.backup-$(date +%Y%m%d_%H%M%S)
   ```
   Restore with `rsync -a --delete <backup>/ output/hgi/<state>/` after the smoke.

2. **Override the output root** so artifacts land somewhere disposable:
   ```bash
   DATA_ROOT=/tmp/hgi_smoke_$(date +%s) python pipelines/embedding/hgi.pipe.py
   ```
   This works because `src/configs/paths.py` respects `$DATA_ROOT`. The smoke writes into `/tmp/hgi_smoke_*/hgi/<state>/` and never touches the real `output/`.

3. **Edit `STATES` in `hgi.pipe.py` to a state that does not exist on disk yet** (e.g. a state you have never regenerated). The pipeline still writes, but to a fresh path with no preexisting artifact to clobber.

### What is "smoke testing" in this context?

Any of the following count as a smoke test that needs the precaution above:

- Running `python pipelines/embedding/hgi.pipe.py` with shortened epoch counts (`HGI_CONFIG.epoch=3`, `poi2vec_epochs=3`) just to verify the code path works — e.g. after a torch upgrade.
- Verifying that `Node2Vec.random_walk` (`torch_cluster`) works after a dependency bump.
- Validating that GCNConv / SetTransformer numerics behave on a new device or driver.
- Anything where you `Ctrl+C` after one epoch.

**Full production regeneration** (the only time it's safe to run with the default 2000-epoch config and the real `output/` path) is when you actually want to replace the current artifacts with a fresh, fully-trained set — and even then, take a snapshot first so you can roll back if metrics regress.

### Why isn't `force_preprocess=False` the default?

It currently has to be `True` because the pipeline depends on intermediate files (`temp/edges.csv`, `temp/pois.csv`, `temp/gowalla.pt`) being regenerated when the upstream POI source changes. Adding a hash-based "skip if unchanged" check is a real refactor (intermediate file content depends on `boroughs_area.csv` + the POI parquet + the shapefile, all of which would need fingerprinting). Until that refactor lands, the snapshot/`DATA_ROOT` discipline above is the only safety net.

---

## Overview

### What is HGI?

**Hierarchical Graph Infomax (HGI)** is a self-supervised learning method that generates embeddings at multiple spatial granularities:

- **POI Level**: Individual points of interest (restaurants, shops, etc.)
- **Region Level**: Census tracts or administrative areas
- **City Level**: Global summary of the entire area

### What Problem Does It Solve?

HGI learns spatial representations that capture:
- **Local patterns**: Which POIs are spatially close and functionally similar
- **Regional patterns**: What characterizes each census tract
- **Global patterns**: City-wide functional organization

These embeddings are used as input features for downstream tasks like:
- Next-POI prediction
- POI category classification
- Region similarity analysis

### Three-Level Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                        CITY LEVEL                           │
│     Area-weighted aggregation of all region embeddings      │
│                    city_emb = sigmoid(sum(region * area))   │
└─────────────────────────────────────────────────────────────┘
                              ^
┌─────────────────────────────────────────────────────────────┐
│                       REGION LEVEL                          │
│      Attention-pooled POIs + Region GCN refinement          │
│            region_emb = PMA(POIs) + GCN(regions)            │
└─────────────────────────────────────────────────────────────┘
                              ^
┌─────────────────────────────────────────────────────────────┐
│                        POI LEVEL                            │
│         GCN encoding over Delaunay spatial graph            │
│              poi_emb = GCN(features, edges)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Pipeline Flow

The HGI pipeline consists of 5 phases that run sequentially:

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3a: Spatial Graph Construction                       │
│  preprocess_hgi(poi_emb_path=None)                          │
│  ├── Load POI data + census tract shapefile                 │
│  ├── Delaunay triangulation (connect nearby POIs)           │
│  ├── Compute edge weights (spatial x regional)              │
│  └── Output: edges.csv, pois.csv, encodings.json            │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3b-3d: POI2Vec Pre-training                          │
│  train_poi2vec()                                            │
│  ├── 3b: Generate random walks on POI graph                 │
│  ├── 3c: Train FCLASS embeddings (skip-gram + hierarchy)    │
│  ├── 3d: Reconstruct POI embeddings from fclass lookup      │
│  └── Output: poi_embeddings.pt                              │
│                                                             │
│  *** CRITICAL INSIGHT ***                                   │
│  POI2Vec learns at FCLASS level, NOT POI level!             │
│  Multiple POIs with same fclass share identical embeddings  │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: Graph Enrichment                                  │
│  preprocess_hgi(poi_emb_path=poi_embeddings.pt)             │
│  ├── Reload graph structure                                 │
│  ├── Load POI2Vec embeddings as node features               │
│  ├── Compute region features (area, adjacency, similarity)  │
│  └── Output: graph_data.pkl                                 │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  PHASE 5: HGI Training                                      │
│  train_hgi()                                                │
│  ├── Initialize POIEncoder, POI2Region, region2city         │
│  ├── Train with mutual information maximization loss        │
│  ├── Track best embeddings (lowest loss)                    │
│  └── Output: embeddings.parquet, region_embeddings.parquet  │
└─────────────────────────────────────────────────────────────┘
```

---

## Intermediate Files

### Temporary Files (`output/hgi/{state}/temp/`)

| File | Columns/Keys | Shape | Purpose |
|------|--------------|-------|---------|
| `edges.csv` | source, target, weight | [N_edges, 3] | Delaunay graph for Node2Vec walks |
| `pois.csv` | placeid, category, fclass | [N_pois, 3] | POI metadata for fclass lookup |
| `encodings.json` | category: {name->code}, fclass: {name->code} | dict | Reverse mapping for decoding |
| `graph_data.pkl` | node_features, edge_index, edge_weight, region_id, region_area, coarse_region_similarity, region_adjacency, y, place_id, category_classes, fclass_classes | dict | Complete graph state for HGI training |

### Output Files (`output/hgi/{state}/`)

| File | Columns | Shape | Purpose |
|------|---------|-------|---------|
| `embeddings.parquet` | placeid, 0, 1, ..., dim-1, category | [N_pois, dim+2] | **Final POI embeddings** |
| `region_embeddings.parquet` | region_id, reg_0, ..., reg_(dim-1) | [N_regions, dim+1] | **Final region embeddings** |
| `poi_embeddings.pt` | in_embed.weight, placeids | tensor + list | POI2Vec output (fclass->POI mapped) |

### Key File: `graph_data.pkl`

This pickle contains the complete graph representation:

```python
{
    'node_features': np.ndarray,           # [N_pois, feature_dim] - POI2Vec embeddings
    'edge_index': np.ndarray,              # [2, N_edges] - COO sparse format
    'edge_weight': np.ndarray,             # [N_edges] - normalized to [0,1]
    'region_id': np.ndarray,               # [N_pois] - maps POI -> region index
    'region_area': np.ndarray,             # [N_regions] - area in km^2
    'region_adjacency': np.ndarray,        # [2, N_adj] - which regions touch
    'coarse_region_similarity': np.ndarray,# [N_regions, N_regions] - cosine similarity
    'y': np.ndarray,                       # [N_pois] - category labels (encoded)
    'place_id': np.ndarray,                # [N_pois] - original placeid values
    'category_classes': list,              # Category names for decoding
    'fclass_classes': list,                # Fclass names for decoding
    'number_pois': int,
    'number_regions': int,
}
```

---

## Model Architectures

### 1. POI2Vec (`poi2vec.py`)

**Purpose**: Pre-train POI embeddings using spatial random walks.

#### Critical Insight: fclass-Level Learning

**POI2Vec learns embeddings at the fclass (functional class) level, NOT at the POI level.** This is the most important concept to understand:

```
┌─────────────────────────────────────────────────────────────┐
│                    POI2Vec OUTPUT                           │
│                                                             │
│   What you might expect:                                    │
│   POI_1 -> embedding_1                                      │
│   POI_2 -> embedding_2                                      │
│   POI_3 -> embedding_3                                      │
│                                                             │
│   What actually happens:                                    │
│   fclass "Coffee Shop" -> embedding_A                       │
│   fclass "Restaurant"  -> embedding_B                       │
│   fclass "Gym"         -> embedding_C                       │
│                                                             │
│   Then reconstruction:                                      │
│   POI_1 (fclass="Coffee Shop") -> embedding_A               │
│   POI_2 (fclass="Coffee Shop") -> embedding_A  (SAME!)      │
│   POI_3 (fclass="Restaurant")  -> embedding_B               │
└─────────────────────────────────────────────────────────────┘
```

**Why fclass-level?**
- **Stability**: More training data per fclass (many POIs per fclass)
- **Generalization**: Prevents overfitting to individual POI quirks
- **Semantic structure**: Hierarchy loss enforces category-fclass relationships

#### POI2Vec Phases

```
PHASE 3b: Random Walk Generation
┌─────────────────────────────────────────────────────────────┐
│  Delaunay Graph --> Node2Vec Walks --> fclass Sequences     │
│                                                             │
│  POI walk:    [POI_1, POI_3, POI_7, POI_2, ...]            │
│                   |       |       |       |                 │
│                   v       v       v       v                 │
│  fclass walk: [cafe, restaurant, bar, cafe, ...]           │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
PHASE 3c: fclass Embedding Training
┌─────────────────────────────────────────────────────────────┐
│  EmbeddingModel:                                            │
│    in_embed:  [vocab_size, embed_dim]  # vocab = num fclass │
│    out_embed: [vocab_size, embed_dim]                       │
│                                                             │
│  Loss = Skip-gram + lambda * Hierarchy                      │
│                                                             │
│  Skip-gram:  maximize P(context | center)                   │
│              -log sigma(center . context)                   │
│              -log sigma(-center . negative)                 │
│                                                             │
│  Hierarchy:  L2(category_emb - fclass_emb)                  │
│              Forces related fclasses to cluster by category │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
PHASE 3d: POI-Level Reconstruction
┌─────────────────────────────────────────────────────────────┐
│  For each POI i:                                            │
│      poi_embedding[i] = fclass_embeddings[poi.fclass[i]]    │
│                                                             │
│  This is a LOOKUP TABLE operation!                          │
│  NO learning happens here - just index mapping.             │
│                                                             │
│  Result: POIs with same fclass share IDENTICAL embeddings   │
└─────────────────────────────────────────────────────────────┘
```

#### Hard Negative Sampling

Instead of random negatives, POI2Vec samples fclasses that **never** co-occur with the center fclass in any walk:

```python
# For center fclass "Coffee Shop":
positive_context = {"Restaurant", "Bar", "Gym"}  # Seen together in walks
negative_candidates = ALL_FCLASSES - positive_context - {"Coffee Shop"}
# These are fclasses that NEVER appeared near Coffee Shop
# Learning to distinguish them is harder but more meaningful
```

---

### 2. POIEncoder (`model/POIEncoder.py`)

**Purpose**: Encode POIs using graph convolution over the Delaunay spatial graph.

**Architecture**:
```
Input: x [N_pois, in_channels], edge_index [2, E], edge_weight [E]
                              |
                              v
                    GCNConv(in -> hidden)
                              |
                              v
                         PReLU activation
                              |
                              v
Output: [N_pois, hidden_channels]
```

**Why GCN?**
- Respects spatial structure (nearby POIs influence each other)
- Edge weights encode both distance and region boundaries
- Single layer captures 1-hop neighborhood information

**Code**:
```python
class POIEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels):
        self.conv = GCNConv(in_channels, hidden_channels)
        self.prelu = nn.PReLU()

    def forward(self, x, edge_index, edge_weight):
        x = self.conv(x, edge_index, edge_weight)
        x = self.prelu(x)
        return x
```

---

### 3. POI2Region (`model/RegionEncoder.py`)

**Purpose**: Aggregate POI embeddings into region embeddings using attention, then refine with region-level GCN.

**Two-Stage Architecture**:

```
Stage 1: POI-to-Region Aggregation (PMA)
┌─────────────────────────────────────────────────────────────┐
│  For each region r:                                         │
│    1. Extract POIs: pois_r = x[region_id == r]              │
│    2. Learnable seed query: S [1, dim]                      │
│    3. Multihead Attention: region_r = Attention(S, pois_r)  │
│                                                             │
│  PMA learns WHICH POIs matter for summarizing each region   │
│                                                             │
│  Attention formula:                                         │
│    score = softmax(Q . K^T / sqrt(d))                       │
│    region_emb = score . V                                   │
│                                                             │
│  Segmented softmax: normalizes WITHIN each region           │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
Stage 2: Region-Level GCN
┌─────────────────────────────────────────────────────────────┐
│  Input: region_emb [N_regions, dim]                         │
│         region_adjacency [2, N_adj]                         │
│                                                             │
│  GCNConv + PReLU                                            │
│                                                             │
│  Region GCN captures WHICH REGIONS are similar              │
│  Adjacent regions influence each other's embeddings         │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
Output: [N_regions, hidden_channels]
```

**Why Two Stages?**
- **PMA**: Learns attention weights to identify important POIs per region
- **Region GCN**: Incorporates regional context (adjacent regions influence each other)

---

### 4. HGI Module (`model/HGIModule.py`)

**Purpose**: Learn embeddings by maximizing mutual information across the three-level hierarchy.

**Forward Pass**:
```
Input: Graph data with POI features, edges, region assignments
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  1. POI Encoding                                            │
│     pos_poi = POIEncoder(x, edges)        # Real features   │
│     neg_poi = POIEncoder(corrupt(x), edges) # Shuffled      │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  2. Region Aggregation                                      │
│     region_emb = POI2Region(pos_poi)                        │
│     neg_region = POI2Region(neg_poi)                        │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  3. City Encoding                                           │
│     city_emb = sigmoid(sum(region_emb * region_area))       │
└─────────────────────────────────────────────────────────────┘
                              |
                              v
┌─────────────────────────────────────────────────────────────┐
│  4. Hard Negative Sampling for Loss                         │
│     25%: regions with similarity 0.6-0.8 (hard negatives)   │
│     75%: random regions (easy negatives)                    │
└─────────────────────────────────────────────────────────────┘
```

**Loss Function** (Mutual Information Maximization):
```
L_poi2region = -log sigma(poi @ W @ same_region)      # Positive
             - log(1 - sigma(poi @ W @ other_region)) # Negative

L_region2city = -log sigma(region @ W @ city)         # Positive
              - log(1 - sigma(neg_region @ W @ city)) # Negative

Total Loss = alpha * L_poi2region + (1-alpha) * L_region2city
```

**Corruption Function**: Random permutation of POI features breaks the correspondence between features and graph structure, creating negative samples.

```python
def corruption(x):
    """Shuffle rows to break feature-structure correspondence"""
    return x[torch.randperm(x.size(0))]
```

---

## Theory & Key Insights

### 1. Why fclass-Level Embeddings?

POI2Vec learns at the **fclass** (functional class) level rather than individual POIs:

| Approach | Pros | Cons |
|----------|------|------|
| POI-level | Unique per POI | Sparse data, overfitting |
| fclass-level | More data, generalizes | POIs with same fclass are identical |

The fclass approach is chosen because:
- **Data efficiency**: Each fclass has many POI examples
- **Semantic coherence**: fclasses are meaningful functional categories
- **Hierarchy enforcement**: Category-fclass L2 loss creates semantic structure

```
fclass embeddings cluster by category:

     "Food" category
     ┌─────────────────┐
     │  o Coffee Shop  │
     │  o Restaurant   │
     │     o Bar       │
     └─────────────────┘

     "Retail" category
     ┌─────────────────┐
     │  o Grocery      │
     │    o Mall       │
     │  o Boutique     │
     └─────────────────┘
```

### 2. Graph Infomax Principle

The core idea is to **maximize mutual information** between local (POI/region) and global (region/city) representations:

```
I(local; global) = H(local) - H(local | global)
```

By maximizing this, we ensure:
- Local embeddings contain information predictive of global context
- Global embeddings summarize local patterns effectively

### 3. Contrastive Learning Framework

HGI uses contrastive learning with positive and negative pairs:

| Pair Type | Example | Goal |
|-----------|---------|------|
| Positive | (POI, its region) | High score |
| Negative | (POI, random region) | Low score |
| Positive | (Region, city) | High score |
| Negative | (Corrupted region, city) | Low score |

The model learns to score positive pairs high and negative pairs low using bilinear discriminators:
```
score = sigmoid(z1^T @ W @ z2)
```

### 4. Hard Negative Mining

Easy negatives (random regions) provide weak learning signal. HGI uses **hard negatives**:

```
Region similarity matrix:
      R0    R1    R2    R3
R0   1.0   0.3   0.7   0.1
R1   0.3   1.0   0.2   0.8
R2   0.7   0.2   1.0   0.4
R3   0.1   0.8   0.4   1.0

For R0:
  Easy negatives: R3 (sim=0.1) - obviously different
  Hard negatives: R2 (sim=0.7) - confusingly similar!

Hard negatives force the model to learn subtle distinctions.
```

### 5. Edge Weight Formula

Delaunay edges are weighted by both spatial distance and regional boundaries
(Eq. 2 of Huang et al., ISPRS 2023):

```
w_spatial = log((1 + D^1.5) / (1 + dist^1.5))

    D = bounding box diagonal (normalizer)
    dist = haversine distance in meters

w_regional = 1.0                   if same census tract
           = cross_region_weight   otherwise       # `w_r` in the paper

final_weight = normalize(w_spatial * w_regional)  -> [0, 1]
```

The cross-region weight `w_r` controls how strongly the GCN prefers within-region
connections over cross-region ones. It is a **dataset-specific hyperparameter**
that the paper sets to `0.4` for Xiamen/Shenzhen, while the third-party
reproduction uses `0.5`. On our US-state datasets `0.4` is a **local pessimum**.

**Alabama `w_r` sweep** (5 folds × 50 epochs, fixes #3 + #4 always applied):

| w_r | Cat F1              | Cat Acc             | Next F1             |
|-----|---------------------|---------------------|---------------------|
| 0.4 | 0.7388 ± 0.0205     | 0.7833 ± 0.0137     | 0.2837 ± 0.0110     |
| 0.5 | 0.7678 ± 0.0211     | 0.8000 ± 0.0153     | 0.2750 ± 0.0176     |
| 0.6 | 0.7944 ± 0.0186     | 0.8237 ± 0.0110     | 0.2767 ± 0.0174     |
| **0.7** | **0.8186 ± 0.0123** | **0.8366 ± 0.0125** | **0.2837 ± 0.0108** |

Cat F1 rises ~2.6 pp per 0.1 step with no sign of flattening at 0.7 — the true
optimum may be at `0.8` or even `1.0`. Next F1 is effectively flat across the
sweep.

**Why the optimum differs from the paper**: the paper trains on Xiamen
(~45k POIs in 1.7k km²) and Shenzhen (~300k POIs in 2k km²) — dense urban
fabrics. Alabama has ~11.7k POIs over ~130k km², so an average census tract is
much larger relative to POI spacing. Penalising cross-region edges by 60%
(`w_r=0.4`) starves the POI encoder of useful long-range signal on a sparse
dataset; a milder penalty (`w_r=0.7`) preserves the geographic structure and
the category head rewards it with +8 pp F1.

**Default and per-state override.** `cross_region_weight` defaults to `0.7` in
`HGIPreprocess`, `preprocess_hgi()`, `HGI_CONFIG` (in `pipelines/embedding/hgi.pipe.py`)
and the `hgi.py` argparse CLI. Override per state via the
`CROSS_REGION_WEIGHT_PER_STATE` dict at the top of `pipelines/embedding/hgi.pipe.py`.

**Current per-state defaults.** The values below are best-effort starting
points extrapolated from POI density vs. the paper's anchors (Xiamen 26 POI/km²
→ 0.4; Alabama 0.089 POI/km² → 0.7). Only Alabama is empirically swept.

| State | POIs | Area (km²) | Density (POI/km²) | `w_r` | Source |
|---|---:|---:|---:|:---:|---|
| Arizona | 20,440 | 294,207 | 0.0695 | 0.7 | interpolated |
| Alabama | 11,706 | 131,171 | 0.0892 | **0.7** | **swept** |
| Texas | 155,208 | 676,587 | 0.2294 | 0.7 | interpolated |
| California | 165,881 | 403,932 | 0.4107 | 0.6 | interpolated |
| Florida | 74,862 | 139,671 | 0.5360 | 0.6 | interpolated |

(Paper anchors for comparison: Xiamen ~45k POIs / 1.7k km² / 26 POI/km² / `w_r=0.4`;
Shenzhen ~303k POIs / 2k km² / 150 POI/km² / `w_r=0.4`.)

**Recommendation when onboarding a new state**: run a 3-point sweep
(`{0.4, 0.7, 1.0}`) to bracket the optimum before committing to a full training
run. Each sweep point costs ~25 min on CPU (8 min HGI regen + 16 min MTLnet
5 folds × 50 epochs) on the Alabama-sized dataset.

---

## Usage

### Running the Full Pipeline

```python
from embeddings.hgi.hgi import create_embedding
from argparse import Namespace

args = Namespace(
    dim=64,
    epoch=2000,
    poi2vec_epochs=100,
    alpha=0.5,
    attention_head=4,
    lr=0.006,            # paper value; requires the 40-epoch warmup below
    warmup_period=40,
    gamma=1.0,
    max_norm=0.9,
    device='cpu',
    shapefile='/path/to/census_tracts.shp',
    force_preprocess=True,
    cross_region_weight=0.7,  # Eq. 2 w_r — sweep per state, see §5 for Alabama
)

create_embedding(state="Texas", args=args)
```

### Using the Pipeline Script

```bash
cd /path/to/ingred
python pipelines/embedding/hgi.pipe.py
```

Configure states in the script:
```python
STATES = {
    'Texas': Resources.TL_TX,
    'California': Resources.TL_CA,
}
```

### Loading Generated Embeddings

```python
import pandas as pd

# POI embeddings
poi_emb = pd.read_parquet("output/hgi/Texas/embeddings.parquet")
# Columns: placeid, 0, 1, ..., 63, category

# Region embeddings
region_emb = pd.read_parquet("output/hgi/Texas/region_embeddings.parquet")
# Columns: region_id, reg_0, reg_1, ..., reg_63
```

---

## Configuration Reference

### HGI Training Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `dim` | 64 | Embedding dimension for POI and region embeddings |
| `epoch` | 2000 | Number of HGI training epochs |
| `alpha` | 0.5 | Loss balance: alpha * L_poi2region + (1-alpha) * L_region2city |
| `attention_head` | 4 | Number of attention heads in PMA |
| `lr` | 0.001 | Adam learning rate |
| `gamma` | 1.0 | StepLR decay factor (1.0 = no decay) |
| `max_norm` | 0.9 | Gradient clipping max norm |
| `device` | 'cpu' | Training device ('cpu' or 'cuda') |

### POI2Vec Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `poi2vec_epochs` | 100 | fclass embedding training epochs |
| `walk_length` | 10 | Steps per random walk |
| `walks_per_node` | 5 | Walks generated per POI |
| `context_size` | 5 | Skip-gram context window |
| `p`, `q` | 0.5 | Node2Vec return/in-out parameters |
| `k` | 5 | Negative samples per positive |
| `batch_size` | 2048 | Training batch size |
| `lr` | 0.05 | Adam learning rate |

### Preprocessing Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `force_preprocess` | `True` | Regenerate graph even if pickle exists |
| `shapefile` | — | Path to TIGER/Line census tract shapefile |
| `cta_file` | `None` | Optional: pre-computed boroughs CSV |
| `cross_region_weight` | `0.7` | `w_r` in Eq. 2 — dataset-specific; see [Edge Weight Formula](#5-edge-weight-formula) for the Alabama sweep. Override per state in `pipelines/embedding/hgi.pipe.py:CROSS_REGION_WEIGHT_PER_STATE`. |

---

## Migration & Validation

This implementation is a **migration of the original HGI baseline** from
[`region-embedding-benchmark`](https://github.com/RightBank/region-embedding-benchmark/tree/main/region-embedding/baselines/HGI),
adapted to fit the project's data layout, configuration system, and Python
package structure. The migration is verified to be **bit-for-bit equivalent**
to the original source on the loss path.

### What changed vs. the original

| Aspect | Original `region-embedding-benchmark` | This migration |
|---|---|---|
| Node features for HGI | Pre-trained SIREN/location-encoder embeddings (loaded from `poi_embeddings_*.pt` files generated externally) | **POI2Vec** trained in-pipeline (same fclass-level skip-gram + hierarchy loss as the notebook's `poi-encoder/` baseline) |
| Preprocessing | Two separate scripts + `poi_index.csv` for ordering | Single `preprocess_hgi()` function called twice; ordering is implicit |
| Region adjacency cache | Recomputed every step inside `forward()` | Computed once and cached on `data._hgi_neg_cache` |
| Discriminator math | Bilinear `poi @ W @ region` via per-pair Python loop | Vectorized: `(poi @ W) * region).sum(-1)` — same bilinear form, equivalent gradients |
| Hard-negative selection | Per-region Python loop with `random.random()` / `random.choice()` | Same Python loop preserved (RNG order matches) — but candidate sets are precomputed and cached |
| `RegionEncoder.POI2Region` | Per-region loop calling `PMA(...)` | Vectorized (manual MAB decomposition with segmented softmax via `pyg_softmax` + `scatter`) — see [Critical Fixes](#critical-fixes-made-during-migration) below |
| Logging & paths | Hardcoded Colab paths | Uses `IoPaths` / `Resources` from `src/configs/` |

### Equivalence proof

`tests/test_embeddings/test_hgi_reference_equivalence.py` imports the **actual
unmodified `hgi.py` and `set_transformer.py`** from
`region-embedding-benchmark/baselines/HGI/model/` via a small shim
(`tests/test_embeddings/_hgi_reference_shim.py`) and runs both implementations
side-by-side on identical inputs with synchronized RNG state. The tests assert:

1. **Loss values match within 1e-5** across multiple shapes (N=24..100, R=3..10, dim=16..64)
2. **Gradients match within 1e-5** for every shared parameter

These tests are skipped if `temp/tarik-new/region-embedding-benchmark-main/`
isn't on disk (so they don't break CI), but they pass on the dev machine.

### Quality validation against the original Alabama output

The original codebase produced an Alabama embedding CSV which was added at
`output/hgi/alabama/hgi.csv`. `tests/test_embeddings/test_hgi_alabama_csv_equivalence.py`
compares the migrated `embeddings.parquet` against that CSV on the intersection
of placeids (10,269 POIs, 100% coverage) and asserts:

| Metric | Threshold | Observed |
|---|---|---|
| Placeid coverage | 100% of original | ✅ |
| Category labels match on shared POIs | 100% | ✅ |
| L2 norm ratio | < 2× | ~1.04× |
| Procrustes-aligned cosine (mean) | ≥ 0.5 | 0.70 |
| ≥ 0.5 fraction | ≥ 85% | 95% |
| Pairwise distance Spearman ρ | ≥ 0.20 | 0.29 |
| k=10 NN overlap (vs random baseline) | ≥ 20× | ~30× |

The two embedding spaces are **structurally equivalent** but not byte-equal
(the contrastive loss has rotation/scale freedom and different random seeds
produce different walks/init), which is the expected ceiling for any
non-deterministic re-training of a contrastive model.

### Downstream MTL F1 comparison (Alabama)

Side-by-side MTL training (5-fold CV, 50 epochs, identical hyperparameters)
on the **migrated embeddings** vs the **original CSV embeddings**:

| | Cat F1 | Cat Acc | Next F1 | Next Acc |
|---|---|---|---|---|
| **Migration** | 78.25 ± 2.30 | 81.88 | 27.92 ± 1.54 | 36.97 |
| Original CSV | 65.21 ± 3.03 | 71.74 | 26.68 ± 1.15 | 36.27 |
| Δ | **+13.04 pp** | **+10.14 pp** | +1.24 pp | +0.70 pp |

The migration is **at least as good as the original on every metric** and
substantially better on category prediction. The improvement is partly
because the migration retains 1,437 more POIs that the original CSV had
filtered out, and partly because the bug fixes in `RegionEncoder` and the
loss formulation give cleaner gradients during HGI training.

---

## Critical Fixes Made During Migration

Two real bugs were found by reading the original source side-by-side and
fixed during migration. Both are pinned by the test suite so they cannot
silently regress.

### 1. RegionEncoder vectorized PMA — multi-head split was wrong

**Symptom (before fix):** `model/RegionEncoder.py` rewrote the original
per-region `for r in range(R): self.PMA(x[zone == r])` Python loop into a
fully vectorized form using segmented softmax. The vectorized version did:

```python
K_split = torch.cat(K_pois.split(dim_split, 1), 0).view(-1, num_heads, dim_split)
```

After `torch.cat(..., 0)`, the data layout is `[H*N, dim_split]` with the
first N rows belonging to head 0, the next N to head 1, etc. The subsequent
`.view(-1, H, d)` interprets this as `[N, H, d]` in C-order, which scrambles
the head/POI assignment. For any N > num_heads, attention scores were being
computed against the wrong slice of features.

**Fix:** Replace `cat + view` with a direct `view`:

```python
K_split = K_pois.view(N, num_heads, dim_split)
V_split = V_pois.view(N, num_heads, dim_split)
Q_split = Q_seed.view(1, num_heads, dim_split)
```

This is both correct (each POI's `[h*d:(h+1)*d]` slice maps to head `h`)
and simpler. The reference equivalence test now passes — proof that the
vectorized PMA matches the original loop bit-for-bit.

### 2. Loss negative-pair construction was semantically swapped

**Symptom (before fix):** `model/HGIModule.py`'s `loss()` constructed the
negative POI-region pairs differently from the reference. The reference
asks "do POIs from a foreign region R' fit region R's embedding?" — i.e. it
swaps the POIs. The migration was asking "do region R's POIs fit a foreign
region R\_neg's embedding?" — i.e. it swapped the regions instead. Both are
valid contrastive formulations but they produce **different gradients** and
therefore non-equivalent embeddings.

We measured the divergence on synthetic data with identical weights:
- Loss values differed by ~0.05 on the first step
- Gradient cosine similarity on `region_emb`: **0.7355** (i.e. 25% different direction)

**Fix:** Restructured `forward()` to return `(pos_poi_idx, pos_target_region,
neg_poi_idx, neg_target_region, ...)` and rewrote `loss()` to gather POI/region
pairs from those indices. The negative path now scores `(POIs of R')` against
`region_emb[R]`, matching the reference exactly.

After the fix:
- Loss values match the reference to **0.00** (bit-equal)
- Gradient cosine similarity: **1.000000** (max abs diff `1.86e-08` — fp32 noise)

Both fixes are committed in `604b4d7 feat(time2vec): add migration equivalence
suite + MTLnet A/B comparison` and pinned by the test suite forever.

---

## Performance Notes

The HGI training pipeline went from ~120 s to **~76 s** end-to-end on Alabama
(1.6× faster) through three independent commits, while preserving downstream
F1 (slightly improved across the board). All optimizations are
**equivalence-preserving** — the test suite's bit-for-bit reference checks
still pass.

### Pipeline phase breakdown (Alabama, 200 HGI epochs, 6 POI2Vec epochs)

| Phase | Pre-perf | Post-perf | Speedup |
|---|---|---|---|
| 1. preprocess (Delaunay) | ~5 s | 5 s | — |
| 2. **POI2Vec** | **~93 s** | **53 s** | **1.8×** |
| 3. preprocess + pickle | ~4 s | 4 s | — |
| 4. **HGI training** | **~22 s** | **8 s** | **2.8×** |
| 5. generate inputs | ~5 s | 6 s | — |
| **TOTAL** | **~120 s** | **76 s** | **1.6×** |

### Device choice: CPU, not MPS

`HGI_CONFIG.device` and the `train_poi2vec(device=...)` call are both
**hardcoded to CPU** in `pipelines/embedding/hgi.pipe.py`, even on Apple
Silicon machines where MPS is available. Reason: empirically measured on
Alabama (50 HGI training epochs):

| Device | ms / epoch | Burn-in | Per-step forward |
|---|---|---|---|
| **CPU** (`threads=6`) | **47.7** | 0.13 s | 6 ms |
| **MPS** | **8398** | 10.3 s | 8200 ms |

**CPU is ~176× faster than MPS for HGI training.** The HGI inner loop has
many small ops (1108 regions × small GCN convs + a Python `random.choice`
hard-negative loop), and MPS dispatch overhead per op completely dominates
the actual compute. POI2Vec is also pinned to CPU because its DataLoader
/ `__getitem__` is the bottleneck and runs on CPU regardless of model device.

The pipeline log line was updated in commit `078ec0a` to print **both**
the HGI device and the global device so the choice is visible:

```
HGI Pipeline - 1 state(s) | hgi_device=cpu | global_device=mps | dim=64
```

### CPU thread count

`train_hgi()` wraps the epoch loop in a `_hgi_thread_context()` that pins
the CPU thread count to 6 for the duration of training and restores the
previous value on exit. Override via `HGI_NUM_THREADS=N` (set to 0 to skip
the override entirely).

Why 6? Sweep on Alabama (50 epochs each):

| `torch.set_num_threads(N)` | ms/epoch |
|---|---|
| 1 | 71 |
| 2 | 55 |
| 4 | 52 |
| **6** | **48** ← optimal |
| 8 (default) | 58 |
| 12 | 57 |

Above 6, contention with the macOS scheduler / efficiency cores starts
costing more than the parallelism gains.

### Vectorization wins

Two pure-Python loops over `num_regions=1108` were the dominant cost in
`HierarchicalGraphInfomax.forward()` (75% of forward time on Alabama). Both
were replaced with cached lookups + vectorized tensor ops in commit
`be2cc62`:

- **`hard_neg_loop`** — kept as a Python loop (RNG order must match the
  reference) but the per-iteration similarity matrix slicing and the
  "all-other-regions" candidate lists are now precomputed once and cached
  on `data._hgi_neg_cache`.
- **`neg_pair_build`** — used to do `(data.region_id == neg_r).nonzero(...)`
  inside a 1108-iteration Python loop. Replaced with a sort-by-region-id
  + offset-table approach using `repeat_interleave` + `arange` + index
  arithmetic. O(N×R) → O(N + neg_total).

POI2Vec optimizations in commit `38d19a4`:

- **`POISet.__init__`** now precomputes `_neg_candidates: list[list[int]]`
  indexed by center fclass. `__getitem__` no longer constructs sets on every
  call (~21 µs → ~14 µs per item, 351 K calls per epoch).
- **`EmbeddingModel.forward`** vectorized the per-batch hierarchy L2 loss:
  was `for pair in pairs: ...` (267 pairs × 172 batches × 6 epochs = 275 K
  small lookups), now a single gather + `(diff*diff).sum()`. Per-batch
  forward: 7.4 → 4.0 ms; backward: 13.3 → 8.5 ms.

### What's left on the table

POI2Vec **walk generation** (~15 s) is now the next-biggest single cost. It
runs `Node2Vec` from `torch_geometric` which is mostly C library code, so
the gain from rewriting it would be small. The HGI training itself is near
the floor — backward dominates and there's not much left to vectorize without
changing the algorithm.

---

## Test Suite

All HGI tests live under `tests/test_embeddings/` and are 100% green on
the canonical config:

| File | Tests | What it covers |
|---|---|---|
| `test_hgi.py` | 36 | Unit tests: corruption, discriminator math, hyperparameters, hard-negative constants, RegionEncoder vectorized PMA matches per-region loop, edge weight formula, haversine, SetTransformer parts |
| `test_hgi_reference_equivalence.py` | 6 | **Live import of the unmodified original `hgi.py`** from `region-embedding-benchmark` via a shim. Asserts loss values and gradients match bit-for-bit on multiple shapes/seeds. Auto-skipped if the reference repo isn't on disk. |
| `test_hgi_alabama_csv_equivalence.py` | 8 | Compares the migrated `embeddings.parquet` against the user's `output/hgi/alabama/hgi.csv` (original Alabama output) using Procrustes alignment, k-NN overlap, pairwise distance Spearman, category match, L2 norm sanity. Auto-skipped if either file is missing. |
| `test_hgi_perf_regression.py` | 2 | Pins the HGI epoch wall-clock under 50 ms on a synthetic graph and verifies the cached `data._hgi_neg_cache` is populated and reused — guards against accidentally reintroducing per-region Python loops. |
| **Total** | **52** | |

Run them all:

```bash
python -m pytest tests/test_embeddings/test_hgi.py \
                 tests/test_embeddings/test_hgi_reference_equivalence.py \
                 tests/test_embeddings/test_hgi_alabama_csv_equivalence.py \
                 tests/test_embeddings/test_hgi_perf_regression.py -v
```

### Profiling scripts (in `scripts/`)

| Script | Purpose |
|---|---|
| `scripts/profile_hgi_alabama.py` | Phase-by-phase wall-clock for the full HGI pipeline + per-step breakdown of `train_hgi`. Used to compare device choices and validate every speedup commit. |
| `scripts/profile_poi2vec_alabama.py` | Walk generation, dataset construction, per-`__getitem__` timing, loader iteration, and per-batch model breakdown for POI2Vec. |

---

## File Structure

```
research/embeddings/hgi/
├── README.md                 # This documentation (human-facing)
├── CLAUDE.md                 # Agent-facing summary (paths, defaults, gotchas)
├── __init__.py               # Module exports
├── hgi.py                    # Pipeline orchestrator (create_embedding, train_hgi,
│                             #   _hgi_thread_context for CPU thread pinning)
├── poi2vec.py                # POI2Vec pre-training (POI2Vec, EmbeddingModel, POISet)
├── preprocess.py             # Graph construction (HGIPreprocess, preprocess_hgi)
├── utils.py                  # Spatial utilities (haversine, bbox diagonal)
└── model/
    ├── __init__.py           # Model exports
    ├── HGIModule.py          # Core HGI model (HierarchicalGraphInfomax, corruption)
    │                         #   — vectorized neg-pair build with cached lookup
    ├── POIEncoder.py         # GCN-based POI encoding
    ├── RegionEncoder.py      # Attention pooling + region GCN (POI2Region)
    │                         #   — vectorized PMA, fixed multi-head view bug
    └── SetTransformer.py     # Attention components (MAB, SAB, PMA)
```

---

## Summary: What Each Component Does

| Component | Input | Output | Key Operation |
|-----------|-------|--------|---------------|
| `preprocess.py` | POI data + shapefile | edges.csv, pois.csv | Delaunay triangulation |
| `poi2vec.py` | edges.csv, pois.csv | poi_embeddings.pt | fclass-level skip-gram |
| `POIEncoder` | POI features + graph | POI embeddings | 1-layer GCN |
| `POI2Region` | POI embeddings | Region embeddings | PMA + Region GCN |
| `HGIModule` | All of above | Final embeddings | Mutual info maximization |

---

## References

- **Deep Graph Infomax**: Velickovic et al., 2019 - The foundational graph representation learning method
- **Node2Vec**: Grover & Leskovec, 2016 - Random walk-based graph embedding
- **Set Transformer**: Lee et al., 2019 - Attention-based set functions (PMA, SAB)
- **Region Embedding Benchmark**: Original implementation this module follows
