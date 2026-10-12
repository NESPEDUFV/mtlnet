# CLAUDE.md - Technical Documentation for AI Agents

This document provides a comprehensive technical reference for AI agents working with the INGRED hierarchical location embedding system.

---

## Project Overview

**INGRED** implements hierarchical graph-based embedding methods for location data:
- **HGI**: 3-level hierarchy (POI → Region → City) for spatial embeddings
- **Check2HGI**: 4-level hierarchy (Check-in → POI → Region → City) for event embeddings

Both use **mutual information maximization** via contrastive learning with bilinear discrimination.

---

## Architecture Overview

### Check2HGI 4-Level Hierarchy

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CHECK2HGI ARCHITECTURE                            │
└──────────────────────────────────────────────────────────────────────────┘

INPUT
─────
Data(
    x=[N_checkins, F],           # Check-in features (category + temporal)
    edge_index=[2, E],           # User-sequence edges
    edge_weight=[E],             # Temporal decay weights
    checkin_to_poi=[N_checkins], # Check-in → POI mapping
    poi_to_region=[N_pois],      # POI → Region mapping
    region_adjacency=[2, R_adj], # Region neighbor edges
    region_area=[N_regions],     # Region areas for city aggregation
)

FORWARD PASS
────────────

Level 1: CHECK-IN ENCODING
┌─────────────────────────────────────────────────────────────────────────┐
│  CheckinEncoder (Multi-layer GCN)                                        │
│                                                                          │
│  x [N_checkins, F] ──► GCNConv ──► PReLU ──► GCNConv ──► checkin_emb    │
│                        (F→D)                  (D→D)      [N_checkins, D] │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
Level 2: POI ENCODING (Aggregation)
┌─────────────────────────────────────────────────────────────────────────┐
│  Checkin2POI (Multi-head Attention Pooling)                              │
│                                                                          │
│  For each POI p:                                                         │
│    checkins_at_p = checkin_emb[checkin_to_poi == p]                     │
│    poi_emb[p] = AttentionPool(checkins_at_p, seed_vector)               │
│                                                                          │
│  Output: poi_emb [N_pois, D]                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
Level 3: REGION ENCODING (Aggregation + GCN)
┌─────────────────────────────────────────────────────────────────────────┐
│  POI2Region (Attention Pooling + Region GCN) [Reused from HGI]          │
│                                                                          │
│  Step 1: Aggregate POIs per region (PMA attention)                      │
│  Step 2: Apply GCN on region_adjacency graph                            │
│                                                                          │
│  Output: region_emb [N_regions, D]                                      │
└─────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
Level 4: CITY ENCODING (Global Aggregation)
┌─────────────────────────────────────────────────────────────────────────┐
│  region2city (Area-weighted Sigmoid)                                     │
│                                                                          │
│  city_emb = sigmoid(Σ region_emb[i] * region_area[i])                   │
│                                                                          │
│  Output: city_emb [D]                                                   │
└─────────────────────────────────────────────────────────────────────────┘

LOSS COMPUTATION
────────────────
┌─────────────────────────────────────────────────────────────────────────┐
│  3-Boundary Mutual Information Maximization                              │
│                                                                          │
│  Boundary 1: Check-in ↔ POI                                             │
│    pos = discriminate(checkin, poi[checkin_to_poi], W_c2p)              │
│    neg = discriminate(checkin, poi[random], W_c2p)                      │
│    L_c2p = -log(pos) - log(1-neg)                                       │
│                                                                          │
│  Boundary 2: POI ↔ Region                                               │
│    pos = discriminate(poi, region[poi_to_region], W_p2r)                │
│    neg = discriminate(poi, region[random], W_p2r)                       │
│    L_p2r = -log(pos) - log(1-neg)                                       │
│                                                                          │
│  Boundary 3: Region ↔ City                                              │
│    pos = discriminate_global(region, city, W_r2c)                       │
│    neg = discriminate_global(shuffled_region, city, W_r2c)              │
│    L_r2c = -log(pos) - log(1-neg)                                       │
│                                                                          │
│  Total: L = α_c2p*L_c2p + α_p2r*L_p2r + α_r2c*L_r2c                    │
│         (defaults: 0.4, 0.3, 0.3)                                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Module Reference

### Check2HGI Pipeline

| File | Purpose | Key Functions |
|------|---------|---------------|
| `src/embeddings/check2hgi/check2hgi.py` | Entry point, training loop | `create_embedding()`, `train_check2hgi()` |
| `src/embeddings/check2hgi/preprocess.py` | Graph construction | `preprocess_check2hgi()`, `Check2HGIPreprocess` |
| `src/embeddings/check2hgi/model/Check2HGIModule.py` | Core model + loss | `Check2HGI.forward()`, `Check2HGI.loss()` |
| `src/embeddings/check2hgi/model/CheckinEncoder.py` | Check-in GCN | `CheckinEncoder.forward()` |
| `src/embeddings/check2hgi/model/Checkin2POI.py` | Attention pooling | `Checkin2POI.forward()` |

### HGI Pipeline (Reference Implementation)

| File | Purpose | Key Functions |
|------|---------|---------------|
| `src/embeddings/hgi/hgi.py` | POI embedding entry point | `create_embedding()`, `train()` |
| `src/embeddings/hgi/preprocess.py` | Delaunay graph, region features | `preprocess()` |
| `src/embeddings/hgi/poi2vec.py` | Node2Vec pre-training | `train_poi2vec()` |
| `src/embeddings/hgi/model/HGIModule.py` | 3-level loss computation | `HGI.forward()`, `HGI.loss()` |
| `src/embeddings/hgi/model/POIEncoder.py` | POI-level GCN | `POIEncoder.forward()` |
| `src/embeddings/hgi/model/RegionEncoder.py` | POI2Region aggregation | `POI2Region.forward()` |

### Shared Components

`src/embeddings/hgi/model/RegionEncoder.py` is **imported by Check2HGI** for POI→Region aggregation.

---

## Key Function Signatures

### check2hgi.py

```python
def create_embedding(state: str, args: Namespace) -> None:
    """Run full Check2HGI pipeline: Preprocess -> Train.

    Args:
        state: State/city name (e.g., "Alabama")
        args: Namespace with hyperparameters (dim, epoch, lr, etc.)

    Side effects:
        - Creates output/check2hgi/{state}/embeddings.parquet (with category column)
        - Creates output/check2hgi/{state}/poi_embeddings.parquet
        - Creates output/check2hgi/{state}/region_embeddings.parquet
    """

def train_check2hgi(city: str, args: Namespace) -> None:
    """Train Check2HGI model and generate embeddings.

    Key optimizations:
        - Single encoder pass (embedding-level corruption)
        - Mixed precision training (CUDA only)
        - Best epoch tracking (saves model state, not embeddings)
    """
```

### preprocess.py

```python
def preprocess_check2hgi(
    city: str,
    city_shapefile: str,
    edge_type: str = 'user_sequence',  # 'user_sequence', 'same_poi', 'both'
    temporal_decay: float = 3600.0,    # seconds
) -> dict:
    """Preprocess check-in data into graph format.

    Returns dict with:
        node_features: np.array[N_checkins, F]
        edge_index: np.array[2, E]
        edge_weight: np.array[E]
        checkin_to_poi: np.array[N_checkins]
        poi_to_region: np.array[N_pois]
        region_adjacency: np.array[2, R_adj]
        region_area: np.array[N_regions]
        coarse_region_similarity: np.array[N_regions, N_regions]
        metadata: DataFrame[userid, placeid, datetime, category]
        num_checkins, num_pois, num_regions: int
    """
```

### Check2HGIModule.py

```python
class Check2HGI(nn.Module):
    def __init__(
        self,
        hidden_channels: int,
        checkin_encoder: CheckinEncoder,
        checkin2poi: Checkin2POI,
        poi2region: POI2Region,
        region2city: Callable,
        alpha_c2p: float = 0.4,
        alpha_p2r: float = 0.3,
        alpha_r2c: float = 0.3,
    ):
        """Initialize Check2HGI.

        Note: Corruption is done at embedding-level (not feature-level)
        for 2x encoder speedup.
        """

    def forward(self, data: Data) -> Tuple[
        Tensor,  # pos_checkin_emb [N_checkins, D]
        Tensor,  # pos_poi_expanded [N_checkins, D]
        Tensor,  # neg_poi_expanded [N_checkins, D]
        Tensor,  # pos_poi_emb [N_pois, D]
        Tensor,  # pos_region_expanded [N_pois, D]
        Tensor,  # neg_region_expanded [N_pois, D]
        Tensor,  # pos_region_emb [N_regions, D]
        Tensor,  # neg_region_emb [N_regions, D]
        Tensor,  # city_emb [D]
    ]:
        """Forward pass returning all tensors needed for loss computation."""

    def loss(
        self,
        pos_checkin, pos_poi_exp, neg_poi_exp,
        pos_poi, pos_region_exp, neg_region_exp,
        pos_region, neg_region, city
    ) -> Tensor:
        """Compute 3-boundary hierarchical MI loss."""

    def get_embeddings(self) -> Tuple[Tensor, Tensor, Tensor]:
        """Return (checkin_emb, poi_emb, region_emb) on CPU."""
```

---

## Tensor Shapes Reference

| Stage | Tensor | Shape | Description |
|-------|--------|-------|-------------|
| **Input** | `data.x` | `[N_checkins, F]` | Check-in features (F = num_categories + 4) |
| | `data.edge_index` | `[2, E]` | User-sequence edges |
| | `data.edge_weight` | `[E]` | Temporal decay weights |
| | `data.checkin_to_poi` | `[N_checkins]` | POI index for each check-in |
| | `data.poi_to_region` | `[N_pois]` | Region index for each POI |
| | `data.region_adjacency` | `[2, R_adj]` | Region neighbor edges |
| | `data.region_area` | `[N_regions]` | Geographic area per region |
| **Level 1** | `checkin_emb` | `[N_checkins, D]` | Check-in embeddings |
| **Level 2** | `poi_emb` | `[N_pois, D]` | POI embeddings |
| **Level 3** | `region_emb` | `[N_regions, D]` | Region embeddings |
| **Level 4** | `city_emb` | `[D]` | City embedding |
| **Loss** | `W_c2p, W_p2r, W_r2c` | `[D, D]` | Bilinear discrimination weights |

**Typical values:**
- `D` = 64 (hidden dimension)
- `F` = num_categories + 4 (temporal sin/cos)
- `N_checkins` = 100K - 5M per state
- `N_pois` = 10K - 500K per state
- `N_regions` = 1K - 10K per state

---

## Implementation Decisions

### Why Embedding-Level Corruption

**Original approach** (HGI):
```python
# Two encoder passes
pos_emb = encoder(x, edge_index)
neg_emb = encoder(corruption(x), edge_index)  # Shuffle features
```

**Optimized approach** (Check2HGI):
```python
# Single encoder pass
pos_emb = encoder(x, edge_index)
neg_emb = pos_emb[torch.randperm(pos_emb.size(0))]  # Shuffle embeddings
```

**Rationale:**
- 2x speedup on encoder (most expensive operation)
- Mathematically equivalent for contrastive learning
- Slightly different negative distribution, but empirically works well

**Code location:** `Check2HGIModule.py:141`

### Why No Hard Negatives

**Original HGI:**
```python
# 25% hard negatives (similar but wrong regions)
if random() < 0.25:
    neg_idx = sample_from_similar_regions(similarity_matrix)
else:
    neg_idx = random_region()
```

**Check2HGI simplified:**
```python
# Pure random negatives
neg_idx = torch.randint(0, num_targets - 1, (batch_size,))
neg_idx = torch.where(neg_idx >= pos_idx, neg_idx + 1, neg_idx)
```

**Rationale:**
- O(1) vs O(R) complexity per sample
- Hard negative selection required Python loop
- Random negatives sufficient for convergence
- Better scalability to large datasets

**Code location:** `Check2HGIModule.py:189-202`

### Why Per-Boundary Loss Weights

**Original HGI:** Single `alpha` for POI-Region vs Region-City

**Check2HGI:** Three alphas: `alpha_c2p=0.4, alpha_p2r=0.3, alpha_r2c=0.3`

**Rationale:**
- New Check-in↔POI boundary needs tuning
- Different boundaries may need different emphasis
- Defaults work well across states

**Code location:** `Check2HGIModule.py:49-51`

---

## Data Flow: Preprocessing

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        PREPROCESSING PIPELINE                            │
└─────────────────────────────────────────────────────────────────────────┘

Step 1: LOAD DATA
─────────────────
data/checkins/{City}.parquet
    ├── userid: int
    ├── placeid: int
    ├── datetime: timestamp
    ├── category: str
    ├── latitude: float
    └── longitude: float

    ↓ Sort by (userid, datetime)
    ↓ Encode categories with LabelEncoder

Step 2: SPATIAL JOIN
────────────────────
Shapefile (census tracts)
    ├── GEOID: str
    └── geometry: Polygon

    ↓ Create POI dataframe (unique placeids)
    ↓ Spatial join: POI coordinates → census tract
    ↓ Drop POIs outside any region
    ↓ Create mappings: placeid → poi_idx, poi_idx → region_idx

Step 3: BUILD EDGES
───────────────────
Option A: User Sequence (default)
    For each user's check-in sequence:
        edge(checkin_i, checkin_i+1)
        weight = exp(-time_gap / temporal_decay)

Option B: Same-POI
    For each POI:
        Connect all check-ins at that POI
        weight = 1.0 (sampled to max 50 edges)

Option C: Both
    Concatenate A + B

Step 4: BUILD NODE FEATURES
───────────────────────────
Per check-in:
    ├── category_onehot: [num_categories]
    ├── hour_sin: sin(2π × hour / 24)
    ├── hour_cos: cos(2π × hour / 24)
    ├── dow_sin: sin(2π × day_of_week / 7)
    └── dow_cos: cos(2π × day_of_week / 7)

Feature dim: num_categories + 4

Step 5: BUILD REGION FEATURES
─────────────────────────────
    ├── region_area: From shapefile geometry
    ├── region_adjacency: Regions that touch (spatial join)
    └── coarse_region_similarity: Cosine similarity of POI category distributions

Step 6: SAVE
────────────
output/check2hgi/{city}/temp/checkin_graph.pt (pickle)
```

---

## Extension Guide

### Adding a New Encoder

1. Create `src/embeddings/check2hgi/model/NewEncoder.py`:
```python
class NewEncoder(nn.Module):
    def __init__(self, in_channels, hidden_channels, **kwargs):
        super().__init__()
        # Your architecture

    def forward(self, x, edge_index, edge_weight=None):
        # Return [N, hidden_channels]
        return output
```

2. Import in `check2hgi.py:24-26`
3. Replace `checkin_encoder` initialization at line 163

### Adding a New Loss Term

1. Add new weight parameter in `Check2HGIModule.__init__()`:
```python
self.alpha_new = alpha_new
self.weight_new = nn.Parameter(torch.Tensor(hidden_channels, hidden_channels))
```

2. Add to `loss()` method:
```python
loss_new = self.compute_new_loss(...)
total_loss += self.alpha_new * loss_new
```

3. Add CLI argument in `check2hgi.py:334`

### Adding a New Aggregation Method

1. Create `src/embeddings/check2hgi/model/NewAggregation.py`:
```python
class NewAggregation(nn.Module):
    def __init__(self, hidden_channels, **kwargs):
        super().__init__()

    def forward(self, embeddings, assignment, num_targets):
        # embeddings: [N_source, D]
        # assignment: [N_source] indices into targets
        # num_targets: int
        # Return: [num_targets, D]
        pass
```

2. Replace `checkin2poi` or `poi2region` in model initialization

---

## Common Development Tasks

### Modify Preprocessing

**Add new edge type:**
1. Edit `preprocess.py`, find `_build_edges()` method
2. Add new branch in edge type switch
3. Add CLI option in both `preprocess.py` and `check2hgi.py`

**Add new node feature:**
1. Edit `_build_features()` in `preprocess.py`
2. Append to feature vector (update expected dimensions)

### Debug Training Issues

**NaN loss:**
- Check for zero-count aggregations (POIs with no check-ins)
- Disable AMP: `--no_amp`
- Add gradient clipping: `--max_norm 0.5`

**Memory issues:**
- Reduce batch size: `--batch_size 512`
- Enable mini-batch: `--mini_batch_threshold 100000`
- Reduce neighbors: `--num_neighbors 5`

**Slow convergence:**
- Increase learning rate: `--lr 0.01`
- Adjust loss weights toward struggling boundary
- Check edge type (user_sequence usually better)

### Add Downstream Evaluation

1. Create `src/evaluation/next_poi.py`
2. Load embeddings from parquet
3. Implement train/test split
4. Use embeddings as features for classifier/ranker
5. Report metrics (Hit@K, MRR, NDCG)

---

## File Locations Quick Reference

```
src/embeddings/check2hgi/
├── check2hgi.py           # Line 119: train_check2hgi()
├── preprocess.py          # Line 50: preprocess_check2hgi()
└── model/
    ├── Check2HGIModule.py # Line 29: class Check2HGI
    ├── CheckinEncoder.py  # Line 8: class CheckinEncoder
    └── Checkin2POI.py     # Line 10: class Checkin2POI

src/embeddings/hgi/
├── hgi.py                 # Reference 3-level implementation
├── preprocess.py          # Delaunay triangulation
└── model/
    ├── HGIModule.py       # Original loss computation
    ├── POIEncoder.py      # POI-level GCN
    ├── RegionEncoder.py   # POI2Region (imported by Check2HGI)
    └── SetTransformer.py  # PMA, MAB, SAB

pipelines/embedding/
└── check2hgi.pipe.py      # Multi-state batch processing

configs/
├── paths.py               # IoPaths.CHECK2HGI, EmbeddingEngine
└── globals.py             # Global configuration
```

---

## Known Limitations

1. **MPS Float16 Disabled** - Apple Silicon has NaN issues with scatter/softmax in float16
2. **torch.compile Incompatible** - PyG dynamic scatter breaks compilation
3. **No Validation Split** - Uses training loss for model selection (acceptable for unsupervised)
4. **Single GPU Only** - No DDP wrapper implemented yet

---

## Future Work Opportunities

1. **Hard Negative Sampling Option** - Add `--use_hard_negatives` flag
2. **Checkin2Vec Pre-training** - Similar to POI2Vec but for sequences
3. **Distributed Training** - DDP wrapper for multi-GPU
4. **Adaptive Loss Weights** - Learn alphas during training
5. **Temporal Attention** - Time-aware edge weighting in encoder
