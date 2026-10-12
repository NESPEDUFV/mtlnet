"""HGI (Hierarchical Graph Infomax) embedding pipeline.

This module implements the complete HGI pipeline following the reference
implementation from region-embedding-benchmark.

Pipeline Phases (matching hgi_texas.py):
    Phase 3a: Build Delaunay spatial graph → edges.csv, pois.csv
    Phase 3b-3d: Train POI2Vec → fclass embeddings → POI-level embeddings
    Phase 4: Preprocess with embeddings → complete data_dict → save pickle
    Phase 5: Train HGI → generate POI and region embeddings

Key differences from reference:
    - Phases 3a and 4 are handled by preprocess_hgi() (called twice)
    - Embedding loading is internal to preprocess_hgi() (Phase 4a merged into 4)
    - No poi_index.csv needed (ordering implicit in preprocess_hgi)

Reference: /notebooks/hgi_texas.py
"""

import argparse
import contextlib
import math
import os
import pickle as pkl

import pandas as pd
import pytorch_warmup as warmup
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

from configs.paths import IoPaths, EmbeddingEngine, Resources
from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
from embeddings.hgi.model.POIEncoder import POIEncoder
from embeddings.hgi.model.RegionEncoder import POI2Region
from embeddings.hgi.preprocess import preprocess_hgi
from embeddings.hgi.poi2vec import train_poi2vec


# Optimal CPU thread count for HGI training on Apple Silicon, measured
# empirically on Alabama: 6 threads is ~17% faster than the default 8
# (47.7 vs 57.5 ms/epoch). Override via the HGI_NUM_THREADS env var.
_DEFAULT_HGI_NUM_THREADS = 6


@contextlib.contextmanager
def _hgi_thread_context():
    """Set torch CPU thread count for HGI training, restore on exit.

    HGI training is dominated by small CPU GCN ops; using all available
    perf cores produces contention with the OS scheduler on macOS, slowing
    each epoch. Override via HGI_NUM_THREADS=N (set to 0 to skip the
    override and inherit the global setting).
    """
    override = os.environ.get("HGI_NUM_THREADS")
    if override is not None:
        try:
            target = int(override)
        except ValueError:
            target = _DEFAULT_HGI_NUM_THREADS
    else:
        target = _DEFAULT_HGI_NUM_THREADS

    if target <= 0:
        yield
        return

    previous = torch.get_num_threads()
    if previous == target:
        yield
        return

    try:
        torch.set_num_threads(target)
        yield
    finally:
        torch.set_num_threads(previous)


def train_epoch(data, model, optimizer, scheduler, warmup_scheduler, args):
    """Train HGI model for one epoch."""
    model.train()
    optimizer.zero_grad()

    outputs = model(data)
    loss = model.loss(*outputs)

    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
    optimizer.step()
    # Mirrors RightBank/HGI/train.py: warmup dampens StepLR for the first
    # `warmup_period` epochs (linear ramp from 0 to args.lr).
    with warmup_scheduler.dampening():
        scheduler.step()

    return loss.item()


def train_hgi(city, args):
    """Phase 5: Train HGI model and generate POI + region embeddings.

    Args:
        city: City/state name
        args: Namespace with hyperparameters (dim, alpha, attention_head, lr, etc.)

    Outputs:
        - POI embeddings: output/hgi/{city}/embeddings.parquet
        - Region embeddings: output/hgi/{city}/region_embeddings.parquet
    """
    output_folder = IoPaths.HGI.get_state_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Load preprocessed data
    data_path = IoPaths.HGI.get_graph_data_file(city)
    print(f"Loading data: {data_path}")

    with open(data_path, 'rb') as handle:
        city_dict = pkl.load(handle)

    in_channels = city_dict['node_features'].shape[1]
    num_pois = city_dict['number_pois']
    num_regions = city_dict['number_regions']

    print(f"POIs: {num_pois}, Regions: {num_regions}, Features: {in_channels}")

    # Create PyTorch Geometric Data object
    data = Data(
        x=torch.tensor(city_dict['node_features'], dtype=torch.float32),
        edge_index=torch.tensor(city_dict['edge_index'], dtype=torch.int64),
        edge_weight=torch.tensor(city_dict['edge_weight'], dtype=torch.float32),
        region_id=torch.tensor(city_dict['region_id'], dtype=torch.int64),
        region_area=torch.tensor(city_dict['region_area'], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(city_dict['coarse_region_similarity'], dtype=torch.float32),
        region_adjacency=torch.tensor(city_dict['region_adjacency'], dtype=torch.int64),
    ).to(args.device)

    place_ids = city_dict.get('place_id', [])
    categories_encoded = city_dict.get('y', [])
    category_classes = city_dict.get('category_classes', None)

    # Initialize model
    poi_encoder = POIEncoder(in_channels, args.dim)
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = HierarchicalGraphInfomax(
        hidden_channels=args.dim,
        poi_encoder=poi_encoder,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha=args.alpha,
        hard_neg_prob=getattr(args, "hard_neg_prob", 0.25),
    ).to(args.device)

    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)
    warmup_scheduler = warmup.LinearWarmup(optimizer, args.warmup_period)

    # Training loop — pin CPU thread count for the duration so each epoch
    # benefits from the optimal setting without polluting global state.
    t = trange(1, args.epoch + 1, desc=f"Training HGI")
    lowest_loss = math.inf
    best_region_emb, best_poi_emb = None, None

    with _hgi_thread_context():
        for epoch in t:
            loss = train_epoch(data, model, optimizer, scheduler, warmup_scheduler, args)
            if loss < lowest_loss:
                best_region_emb, best_poi_emb = model.get_region_emb()
                lowest_loss = loss
            t.set_postfix(loss=f'{loss:.4f}', best=f'{lowest_loss:.4f}')

    # Save POI embeddings
    output_path = IoPaths.get_embedd(city, EmbeddingEngine.HGI)
    embeddings_np = best_poi_emb.cpu().numpy()

    df = pd.DataFrame(embeddings_np, columns=[f'{i}' for i in range(embeddings_np.shape[1])])
    df.insert(0, 'placeid', place_ids)
    if category_classes is not None and len(categories_encoded) > 0:
        categories = [category_classes[c] for c in categories_encoded]
        df.insert(1, 'category', categories)
    df.to_parquet(output_path, index=False)
    print(f"POI embeddings: {output_path} {embeddings_np.shape}")

    # Save region embeddings
    region_output_path = output_folder / "region_embeddings.parquet"
    region_embeddings_np = best_region_emb.cpu().numpy()

    region_df = pd.DataFrame(region_embeddings_np, columns=[f'reg_{i}' for i in range(region_embeddings_np.shape[1])])
    region_df.insert(0, 'region_id', range(num_regions))
    region_df.to_parquet(region_output_path, index=False)
    print(f"Region embeddings: {region_output_path} {region_embeddings_np.shape}")


def create_embedding(state: str, args):
    """Run full HGI pipeline matching reference flow.

    Flow (matching hgi_texas.py):
        Phase 3a: Preprocess (graph only) → edges.csv, pois.csv
        Phase 3b-3d: POI2Vec → fclass embeddings → POI embeddings
        Phase 4: Preprocess (with embeddings) → data_dict → save pickle
        Phase 5: Train HGI → POI + region embeddings
    """
    city = state
    shapefile_path = args.shapefile
    graph_data_file = IoPaths.HGI.get_graph_data_file(city)

    if graph_data_file.exists() and not args.force_preprocess:
        print(f"Using existing graph data: {graph_data_file}")
    else:
        # Phase 3a: Build Delaunay graph (no embeddings yet)
        print("=" * 80)
        print(f"Phase 3a: Building spatial graph for {city}")
        print("=" * 80)
        preprocess_hgi(
            city=city,
            city_shapefile=str(shapefile_path),
            poi_emb_path=None,
            cross_region_weight=getattr(args, "cross_region_weight", 0.7),
        )

        # Phase 3b-3d: Train POI2Vec (always required)
        print("=" * 80)
        print(f"Phase 3b-3d: Training POI2Vec for {city}")
        print("=" * 80)
        poi_emb_path = train_poi2vec(
            city=city,
            epochs=args.poi2vec_epochs,
            embedding_dim=args.dim,
            device=args.device
        )

        # Phase 4: Preprocess with learned embeddings → build complete data_dict
        print("=" * 80)
        print(f"Phase 4: Building HGI graph with POI2Vec embeddings for {city}")
        print("=" * 80)
        data = preprocess_hgi(
            city=city,
            city_shapefile=str(shapefile_path),
            poi_emb_path=str(poi_emb_path),
            cross_region_weight=getattr(args, "cross_region_weight", 0.7),
        )

        # Save pickle for train_hgi
        graph_data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(graph_data_file, "wb") as f:
            pkl.dump(data, f)
        print(f"✓ Saved graph data: {graph_data_file}")
        print()

    # Phase 5: Train HGI
    print("=" * 80)
    print(f"Phase 5: Training HGI model for {city}")
    print("=" * 80)
    train_hgi(city, args)


run_pipeline = create_embedding  # Backwards compatibility

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='HGI Embedding Pipeline')

    # Data
    parser.add_argument('--city', type=str, default='Alabama')
    parser.add_argument('--shapefile', type=str, default=Resources.TL_AL)

    # Pipeline
    parser.add_argument('--force_preprocess', action='store_true', default=True,
                        help='Force reprocessing even if graph data exists')
    parser.add_argument('--poi2vec_epochs', type=int, default=100,
                        help='Number of epochs for POI2Vec training')

    # Model
    parser.add_argument('--dim', type=int, default=64)
    parser.add_argument('--attention_head', type=int, default=4)
    parser.add_argument('--alpha', type=float, default=0.5)

    # Training
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--gamma', type=float, default=1.0)
    parser.add_argument('--max_norm', type=float, default=0.9)
    parser.add_argument('--epoch', type=int, default=2000)

    # Preprocessing
    parser.add_argument('--cross_region_weight', type=float, default=0.7,
                        help='Cross-region edge weight w_r (Eq. 2). '
                             'Paper 0.4, repro 0.5, Alabama-best 0.7. Sweep per state.')

    # Device
    parser.add_argument('--device', type=str,
                        default='cpu')

    args = parser.parse_args()

    print(f"HGI Pipeline | City: {args.city} | Device: {args.device}")
    create_embedding(state=args.city, args=args)
    print("Done!")
