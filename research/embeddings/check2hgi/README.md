# Check2HGI - Check-in Hierarchical Graph Infomax

> **Check2HGI generates hierarchical embeddings for check-in events by extending HGI's mutual information maximization from 3 to 4 levels, capturing user mobility patterns, temporal context, and spatial relationships.**

---

## What is Check2HGI?

Check2HGI extends HGI to learn **embeddings for individual check-in events**, not just POIs. It uses a **4-level hierarchy**:

```
                        ┌─────────────┐
                        │    CITY     │  ← Entire geographic area
                        └──────┬──────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
          ┌─────┴─────┐  ┌─────┴─────┐  ┌─────┴─────┐
          │  REGION   │  │  REGION   │  │  REGION   │  ← Census tracts
          └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
                │              │              │
             ┌──┴──┐        ┌──┴──┐        ┌──┴──┐
             │POI│POI│      │POI│POI│      │POI│POI│     ← Unique locations
             └──┬────┘      └──┬────┘      └──┬────┘
                │              │              │
           ┌────┼────┐    ┌────┼────┐    ┌────┼────┐
           ●    ●    ●    ●    ●    ●    ●    ●    ●     ← Check-in events
```

**Key Difference from HGI:**
- **HGI**: POI → Region → City (3 levels, one embedding per POI)
- **Check2HGI**: Check-in → POI → Region → City (4 levels, one embedding per check-in)

**Purpose:** Generate embeddings that capture:
- **User mobility patterns** - Sequential check-ins by same user are connected
- **Temporal context** - Time of day, day of week encoded in features
- **Spatial relationships** - Inherited from POI and Region aggregation
- **Individual event context** - Each check-in gets its own unique embedding

### Method Comparison

| Method | Hierarchy | Input | Output | Best For |
|--------|-----------|-------|--------|----------|
| **HGI** | POI → Region → City | POI coordinates + categories | 1 embedding per POI | Spatial analysis |
| **Check2HGI** | Check-in → POI → Region → City | Check-in events with timestamps | 1 embedding per event | Trajectory analysis |

### Key Components

| Component | Check2HGI | HGI |
|-----------|-----------|-----|
| **Encoder** | Multi-layer GCN on user sequences | Single GCN on Delaunay graph |
| **POI Aggregation** | Checkin2POI attention pooling | - |
| **Region Aggregation** | POI2Region attention + GCN | Same (reused) |
| **City Aggregation** | Area-weighted sigmoid | Same (reused) |
| **Features** | Category + temporal encoding | Category one-hot |

---

## Quick Start

```bash
cd /Users/vitor/Desktop/mestrado/ingred

# Run full pipeline
PYTHONPATH=src python -m embeddings.check2hgi.check2hgi \
    --city Alabama \
    --shapefile data/miscellaneous/tl_2022_01_tract_AL/tl_2022_01_tract.shp \
    --dim 64 \
    --epoch 500

# With different edge type
PYTHONPATH=src python -m embeddings.check2hgi.check2hgi \
    --city Alabama \
    --edge_type same_poi
```

**Output:**
- `output/check2hgi/alabama/embeddings.parquet` - Check-in embeddings
- `output/check2hgi/alabama/poi_embeddings.parquet` - POI embeddings
- `output/check2hgi/alabama/region_embeddings.parquet` - Region embeddings

---

## Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHECK2HGI PIPELINE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

  INPUT                         STEP 1                      STEP 2
  ─────                         ──────                      ──────

┌──────────────┐          ┌──────────────┐           ┌──────────────┐
│ Check-in     │          │ User-Sequence│           │ Check2HGI    │
│ Data         │─────────▶│ Graph        │──────────▶│ Training     │
│ (parquet)    │          │              │           │              │
└──────────────┘          └──────────────┘           └──────────────┘
                                │                           │
┌──────────────┐                │                           │
│ Shapefile    │────────────────┤                           │
│ (regions)    │                │                           │
└──────────────┘                ▼                           ▼
                         ┌──────────────┐           ┌──────────────┐
                         │ Graph Data   │           │ Check-in     │
                         │ (pickle)     │           │ Embeddings   │
                         │              │           │              │
                         │ • Node feats │           │ POI Emb      │
                         │ • Edges      │           │ Region Emb   │
                         │ • Mappings   │           └──────────────┘
                         └──────────────┘
```

---

## Step-by-Step Explanation

### Step 1: Preprocessing (`preprocess.py`)

**Purpose:** Build check-in graph with user-sequence edges.

**Input:**
- Check-in data (parquet) with: `userid`, `placeid`, `datetime`, `category`, `latitude`, `longitude`
- Shapefile with region boundaries (census tracts)

**What happens:**

```
1. LOAD CHECK-IN DATA
   ├── Read parquet file
   ├── Sort by (userid, datetime) for sequential edges
   └── Encode categories

2. SPATIAL JOIN
   ├── Create POI dataframe (unique placeids)
   ├── Assign each POI to a region (GEOID)
   └── Filter check-ins with valid POIs

3. BUILD CHECK-IN GRAPH
   │
   ├── OPTION A: User Sequence Edges (default)
   │   ├── Connect consecutive check-ins by same user
   │   ├── Edge: (checkin_i, checkin_j) if user(i) == user(j) and j follows i
   │   └── Weight: exp(-time_gap / tau) (temporal decay)
   │
   ├── OPTION B: Same-POI Edges
   │   ├── Connect check-ins at the same POI
   │   └── Weight: 1.0
   │
   └── OPTION C: Both
       └── Combine user sequence + same-POI edges

4. BUILD NODE FEATURES
   ├── Category one-hot encoding [num_categories dims]
   └── Temporal encoding [4 dims]:
       ├── hour_sin = sin(2π × hour / 24)
       ├── hour_cos = cos(2π × hour / 24)
       ├── dow_sin = sin(2π × day_of_week / 7)
       └── dow_cos = cos(2π × day_of_week / 7)

5. BUILD HIERARCHICAL MAPPINGS
   ├── checkin_to_poi: [num_checkins] → which POI each check-in belongs to
   ├── poi_to_region: [num_pois] → which region each POI belongs to
   ├── region_adjacency: [2, num_adj] → which regions are neighbors
   └── region_area: [num_regions] → area of each region

6. SAVE
   └── Pickle file with all graph data
```

**Output:** `output/check2hgi/{city}/temp/checkin_graph.pt`

```python
{
    'node_features': array[N_checkins, dim],      # Check-in features
    'edge_index': array[2, N_edges],              # Graph edges
    'edge_weight': array[N_edges],                # Edge weights
    'checkin_to_poi': array[N_checkins],          # Check-in → POI mapping
    'poi_to_region': array[N_pois],               # POI → Region mapping
    'region_adjacency': array[2, N_adj],          # Region adjacency
    'region_area': array[N_regions],              # Region areas
    'coarse_region_similarity': array[N_regions, N_regions],
    'metadata': DataFrame[userid, placeid, datetime],
}
```

---

### Step 2: Training (`check2hgi.py`)

**Purpose:** Learn 4-level hierarchical embeddings through mutual information maximization.

**What happens:**

```
1. LOAD DATA
   ├── Load preprocessed graph data
   └── Create PyTorch Geometric Data object

2. BUILD MODEL (4 components)
   │
   ├── CHECK-IN ENCODER (Multi-layer GCN)
   │   ├── Input: Check-in features + graph structure
   │   ├── 2 GCN layers with PReLU activation
   │   └── Output: Check-in embeddings [N_checkins, dim]
   │
   ├── CHECKIN2POI (Attention Pooling)
   │   ├── Input: Check-in embeddings grouped by POI
   │   ├── Multi-head attention aggregation
   │   └── Output: POI embeddings [N_pois, dim]
   │
   ├── POI2REGION (Attention Pooling + GCN) [Reused from HGI]
   │   ├── Input: POI embeddings grouped by region
   │   ├── PMA attention + Region GCN
   │   └── Output: Region embeddings [N_regions, dim]
   │
   └── REGION2CITY (Area-weighted Aggregation)
       ├── Input: Region embeddings + areas
       └── Output: City embedding [dim]

3. TRAIN WITH 3-BOUNDARY MUTUAL INFORMATION LOSS
   │
   ├── BOUNDARY 1: Check-in ↔ POI
   │   ├── Positive: Check-in with its POI (should agree)
   │   └── Negative: Check-in with random POI (should disagree)
   │
   ├── BOUNDARY 2: POI ↔ Region
   │   ├── Positive: POI with its region
   │   └── Negative: POI with random wrong region
   │
   └── BOUNDARY 3: Region ↔ City
       ├── Positive: Region with city summary
       └── Negative: Corrupted region with city
   │
   └── TOTAL LOSS
       L = α₁×L_c2p + α₂×L_p2r + α₃×L_r2c
       (default: α₁=0.4, α₂=0.3, α₃=0.3)

4. SAVE EMBEDDINGS
   ├── Check-in embeddings → embeddings.parquet
   ├── POI embeddings → poi_embeddings.parquet
   └── Region embeddings → region_embeddings.parquet
```

---

## Graph Construction

### User Sequence Edges (Default)

Connects consecutive check-ins by the same user:

```
User A's check-ins over time:
────────────────────────────────────────▶ time
   ●──────●────●───────────●
   C1     C2   C3          C4

Edges created:
   C1 ↔ C2  (weight: exp(-Δt₁₂/τ))
   C2 ↔ C3  (weight: exp(-Δt₂₃/τ))
   C3 ↔ C4  (weight: exp(-Δt₃₄/τ))
```

**Edge Weight Formula:**
```
weight = exp(-time_gap / τ)

where:
  time_gap = seconds between check-ins
  τ = temporal_decay parameter (default: 3600 = 1 hour)

Example:
  10 min gap (600s):  exp(-600/3600)  = 0.846
  1 hour gap (3600s): exp(-3600/3600) = 0.368
  6 hour gap:         exp(-21600/3600) = 0.002
```

### Same-POI Edges (Alternative)

Connects check-ins at the same location:

```
POI "Coffee Shop":
   User A ──●
           │
   User B ──●──●
           │
   User C ──●

All check-ins at same POI are connected (within sampling limit)
```

---

## Model Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CHECK2HGI MODEL                                    │
└─────────────────────────────────────────────────────────────────────────────┘

INPUT: x [N_checkins, features], edge_index, edge_weight

        ┌─────────────────────────────────────────────────────────┐
        │                 CHECK-IN ENCODER                         │
        │  GCNConv(features → dim) + PReLU                        │
        │  GCNConv(dim → dim) + PReLU                             │
        └─────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                          checkin_emb [N_checkins, dim]
                                      │
        ┌─────────────────────────────┴───────────────────────────┐
        │                   CHECKIN2POI                            │
        │                                                          │
        │  For each POI p:                                         │
        │    checkins_at_p = checkin_emb[checkin_to_poi == p]     │
        │    poi_emb[p] = AttentionPool(checkins_at_p)            │
        └─────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                            poi_emb [N_pois, dim]
                                      │
        ┌─────────────────────────────┴───────────────────────────┐
        │                   POI2REGION  [from HGI]                 │
        │                                                          │
        │  For each region r:                                      │
        │    pois_in_r = poi_emb[poi_to_region == r]              │
        │    region_emb[r] = PMA(pois_in_r)                       │
        │                                                          │
        │  Then: region GCN on adjacency graph                    │
        └─────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                          region_emb [N_regions, dim]
                                      │
        ┌─────────────────────────────┴───────────────────────────┐
        │                   REGION2CITY                            │
        │                                                          │
        │  city = sigmoid(Σ region_emb × area)                    │
        └─────────────────────────────┬───────────────────────────┘
                                      │
                                      ▼
                            city_emb [dim]

OUTPUT: checkin_emb, poi_emb, region_emb, city_emb
```

---

## Loss Function (3-Boundary MI Maximization)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MUTUAL INFORMATION MAXIMIZATION                           │
└─────────────────────────────────────────────────────────────────────────────┘

BOUNDARY 1: Check-in ↔ POI
──────────────────────────
Positive: checkin_i belongs to POI_j → should agree
Negative: checkin_i with random POI_k → should disagree

L_c2p = -log(σ(checkin·poi_correct)) - log(1 - σ(checkin·poi_wrong))


BOUNDARY 2: POI ↔ Region
────────────────────────
Positive: POI_i belongs to Region_j → should agree
Negative: POI_i with random wrong Region_k → should disagree

L_p2r = -log(σ(poi·region_correct)) - log(1 - σ(poi·region_wrong))


BOUNDARY 3: Region ↔ City
─────────────────────────
Positive: Real region with city summary → should agree
Negative: Corrupted region with city → should disagree

L_r2c = -log(σ(region·city)) - log(1 - σ(corrupted_region·city))


TOTAL LOSS
──────────
L = α₁ × L_c2p + α₂ × L_p2r + α₃ × L_r2c

Default weights: α₁=0.4, α₂=0.3, α₃=0.3
```

---

## File Reference

```
src/embeddings/check2hgi/
├── check2hgi.py           # Main pipeline orchestrator
├── preprocess.py          # Graph construction from check-in data
├── __init__.py            # Module exports
└── model/
    ├── Check2HGIModule.py # Main Check2HGI model + loss function
    ├── CheckinEncoder.py  # Multi-layer GCN for check-in encoding
    ├── Checkin2POI.py     # Attention pooling (check-ins → POIs)
    └── __init__.py        # Model exports

# Reused from HGI:
src/embeddings/hgi/model/
├── RegionEncoder.py       # POI2Region attention + GCN (imported)
└── SetTransformer.py      # PMA, MAB components (imported)
```

---

## Parameters

### Preprocessing (`preprocess.py`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--city` | Alabama | City/state name |
| `--shapefile` | - | Path to census tract shapefile |
| `--edge_type` | user_sequence | Graph edge type: `user_sequence`, `same_poi`, `both` |
| `--temporal_decay` | 3600 | Temporal decay τ for edge weights (seconds) |

### Training (`check2hgi.py`)
| Parameter | Default | Description |
|-----------|---------|-------------|
| `--dim` | 64 | Embedding dimension |
| `--num_layers` | 2 | Number of GCN layers in check-in encoder |
| `--epoch` | 500 | Training epochs |
| `--lr` | 0.001 | Learning rate |
| `--alpha_c2p` | 0.4 | Weight for check-in↔POI loss |
| `--alpha_p2r` | 0.3 | Weight for POI↔region loss |
| `--alpha_r2c` | 0.3 | Weight for region↔city loss |
| `--attention_head` | 4 | Attention heads in pooling layers |
| `--mini_batch_threshold` | 100000 | Use mini-batch if check-ins > threshold |
| `--batch_size` | 1024 | Mini-batch size (if used) |

---

## Output Format

### Check-in Embeddings (`embeddings.parquet`)
```
| userid | placeid | category   | datetime            | 0     | 1     | ... | 63    |
|--------|---------|------------|---------------------|-------|-------|-----|-------|
| 4      | 12398   | Restaurant | 2009-05-02 18:43:58 | -0.27 | 0.15  | ... | -0.17 |
| 4      | 6491808 | Coffee     | 2011-04-12 20:11:56 | -0.14 | 0.10  | ... | 0.14  |
```

**Note:** The `category` column contains the original category string for each check-in. Two check-ins at the same POI can have different categories.

### POI Embeddings (`poi_embeddings.parquet`)
```
| placeid | 0     | 1     | 2     | ... | 63    |
|---------|-------|-------|-------|-----|-------|
| 12398   | 0.123 | -0.45 | 0.789 | ... | 0.234 |
```

### Region Embeddings (`region_embeddings.parquet`)
```
| region_id | reg_0 | reg_1 | reg_2 | ... | reg_63 |
|-----------|-------|-------|-------|-----|--------|
| 0         | 0.234 | 0.567 | -0.12 | ... | 0.345  |
```

---

## Understanding Check2HGI Embeddings

### What Do Check2HGI Embeddings Capture?

Check2HGI creates **event-level embeddings** that combine:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              WHAT CHECK2HGI LEARNS FROM                                      │
└─────────────────────────────────────────────────────────────────────────────┘

1. 👤 USER MOBILITY PATTERNS (Primary Signal for Check-ins)
   ├── Sequential check-ins by same user are connected
   ├── Temporal decay: Recent transitions weighted higher
   └── Result: Similar trajectories → similar check-in embeddings

2. ⏰ TEMPORAL CONTEXT
   ├── Hour of day (sin/cos encoded)
   ├── Day of week (sin/cos encoded)
   └── Result: Morning coffee vs evening bar → different embeddings

3. 🏷️ CATEGORICAL INFORMATION
   ├── POI category (Restaurant, Shop, etc.)
   └── Result: Check-ins at similar categories share features

4. 🗺️ SPATIAL STRUCTURE (Inherited from POI/Region levels)
   ├── POI geographic context
   ├── Regional characteristics
   └── Result: Downtown vs suburban check-ins differ
```

### Key Insight: Event-Level, Not Location-Level

**Check2HGI is fundamentally an event embedding method.**

```python
# The same POI can have different check-in embeddings:

Check-in A: User visits Starbucks at 8am Monday
  → Embedding reflects: morning routine, weekday commute pattern

Check-in B: User visits Starbucks at 10pm Saturday
  → Embedding reflects: evening social activity, weekend leisure

Check-in C: Different user visits same Starbucks at 8am Monday
  → Embedding reflects: DIFFERENT user's patterns, even same time/place
```

### Comparison: HGI vs Check2HGI

```
                    HGI                         Check2HGI
                    ───                         ─────────
Unit of analysis:   POI (location)              Check-in (event)
Graph edges:        Spatial (Delaunay)          Temporal (user sequences)
Node features:      Category                    Category + time encoding
Output:             1 embedding per POI         1 embedding per check-in
Best for:           Spatial analysis            Trajectory/behavior analysis
```

---

## Use Cases

### Use Case 1: Similar Check-in Discovery

```python
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Load check-in embeddings
df = pd.read_parquet('output/check2hgi/alabama/embeddings.parquet')

# Find check-ins similar to a target
target_idx = 0
target_emb = df.iloc[target_idx, 3:].values  # Skip userid, placeid, datetime
all_embs = df.iloc[:, 3:].values

similarities = cosine_similarity([target_emb], all_embs)[0]
df['similarity'] = similarities

# Similar check-ins (same user patterns, temporal context)
similar = df.nlargest(10, 'similarity')[['userid', 'placeid', 'datetime', 'similarity']]
print(similar)
```

### Use Case 2: User Trajectory Embedding

```python
# Aggregate check-in embeddings per user
user_embeddings = df.groupby('userid').apply(
    lambda x: x.iloc[:, 3:].mean()
).reset_index()

# Now each user has a trajectory embedding
# Compare users based on their mobility patterns
```

### Use Case 3: Temporal Pattern Analysis

```python
# Group check-ins by hour of day
df['hour'] = pd.to_datetime(df['datetime']).dt.hour
hourly_patterns = df.groupby('hour').apply(
    lambda x: x.iloc[:, 3:].mean()
)

# Visualize: How do check-in embeddings vary by time?
```

### Use Case 4: Next Check-in Prediction

```python
# Use check-in embeddings as features for sequence models
# Check-ins with similar embeddings → likely next destinations
```

---

## When to Use Check2HGI vs HGI

```
Use Check2HGI when:
├── ✅ You need embeddings for individual check-in events
├── ✅ You care about user mobility patterns
├── ✅ Temporal context matters (time of day, day of week)
├── ✅ You have check-in data with (user, place, time)
└── ✅ Examples: Trajectory analysis, next-POI prediction, user profiling

Use HGI when:
├── ✅ You need embeddings for POIs (locations)
├── ✅ You care about spatial context only
├── ✅ Temporal information is not relevant
├── ✅ You don't have user/time data
└── ✅ Examples: POI similarity, spatial clustering, region analysis

Use Both when:
├── ✅ Combine POI embeddings (spatial) with check-in embeddings (temporal)
├── ✅ Multi-modal representation learning
└── ✅ Hybrid recommendation systems
```

---

## Scalability

Check2HGI handles large datasets (millions of check-ins) with:

1. **Vectorized Negative Sampling** - O(1) instead of O(N) per sample
2. **Full-batch Training** - For datasets < 500K check-ins
3. **Mini-batch Training** - For larger datasets using NeighborLoader

```python
# Example: Texas with 4M check-ins
# --mini_batch_threshold 100000 enables mini-batch training
```

---

## Multi-State Pipeline

Process multiple states in sequence:

```bash
PYTHONPATH=src python pipelines/embedding/check2hgi.pipe.py
```

This runs Check2HGI for all configured states (Alabama, Arizona, Georgia, Florida, California, Texas) with predefined shapefile paths.

---

## Project Structure

```
ingred/
├── src/embeddings/
│   ├── hgi/                    # POI-level embeddings (reference)
│   │   ├── hgi.py              # Training pipeline
│   │   ├── preprocess.py       # Delaunay graph construction
│   │   ├── poi2vec.py          # Optional pre-training
│   │   └── model/              # HGI model components
│   │       └── RegionEncoder.py # POI2Region (reused by Check2HGI)
│   │
│   └── check2hgi/              # Event-level embeddings
│       ├── check2hgi.py        # Training pipeline
│       ├── preprocess.py       # User-sequence graph
│       ├── README.md           # This file
│       ├── CLAUDE.md           # Technical docs for AI agents
│       └── model/              # Check2HGI model components
│
├── pipelines/embedding/        # Multi-state batch processing
│   └── check2hgi.pipe.py
│
├── data/checkins/              # Input: State parquet files
│
└── output/check2hgi/{city}/    # Output: Embeddings
    ├── embeddings.parquet      # Check-in embeddings
    ├── poi_embeddings.parquet  # POI embeddings
    └── region_embeddings.parquet
```

---

## Implementation Notes

### Optimizations from Original HGI

| Optimization | Original HGI | Check2HGI | Benefit |
|--------------|--------------|-----------|---------|
| Corruption | Feature-level (2 encoder passes) | Embedding-level (1 pass) | 2x encoder speedup |
| Negative Sampling | Hard negatives (25% similar) | Random negatives | O(1) vs O(R) complexity |
| Loss Weights | Single alpha | 3 alphas (c2p, p2r, r2c) | Per-boundary control |

### Known Limitations

1. **MPS Float16 Disabled** - Apple Silicon has NaN issues with scatter/softmax in float16
2. **torch.compile Incompatible** - PyG dynamic scatter operations break compilation
3. **No Validation Split** - Uses best training loss epoch (acceptable for unsupervised)
4. **Single GPU Only** - No DDP wrapper implemented

### Future Improvements

**High Priority:**
- [ ] Hard negative sampling option (`--use_hard_negatives`)
- [ ] Checkin2Vec pre-training (like POI2Vec for sequences)
- [ ] Downstream evaluation (next-POI prediction, clustering metrics)

**Medium Priority:**
- [ ] Gradient checkpointing for >10M check-ins
- [ ] Distributed training (DDP) for multi-GPU

**Low Priority:**
- [ ] Adaptive loss weighting (learn alphas during training)
- [ ] Temporal attention in CheckinEncoder

---

## References

- [Hierarchical Graph Infomax (Zhang et al., 2020)](https://dl.acm.org/doi/10.1145/3397536.3422213)
- [Deep Graph Infomax (Velickovic et al., 2019)](https://arxiv.org/abs/1809.10341)
- [Graph Convolutional Networks (Kipf & Welling, 2017)](https://arxiv.org/abs/1609.02907)
- [Set Transformer (Lee et al., 2019)](https://arxiv.org/abs/1810.00825)
- [Node2Vec (Grover & Leskovec, 2016)](https://arxiv.org/abs/1607.00653)
