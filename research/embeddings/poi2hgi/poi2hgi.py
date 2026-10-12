"""POI2HGI (POI Hierarchical Graph Infomax) embedding pipeline with temporal features."""

import argparse
import math
import pickle as pkl

import pandas as pd
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

from configs.paths import IoPaths, EmbeddingEngine, Resources
from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
from embeddings.hgi.model.POIEncoder import POIEncoder
from embeddings.hgi.model.RegionEncoder import POI2Region
from embeddings.poi2hgi.preprocess import preprocess_poi2hgi


def train_epoch(data, model, optimizer, scheduler, args):
    """Train POI2HGI model for one epoch."""
    model.train()
    optimizer.zero_grad()

    pos_poi, pos_reg, neg_reg, all_reg, all_reg_neg, city = model(data)
    loss = model.loss(pos_poi, pos_reg, neg_reg, all_reg, all_reg_neg, city)

    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
    optimizer.step()
    scheduler.step()

    return loss.item()


def train_poi2hgi(city, args):
    """Train POI2HGI model and generate embeddings."""
    output_folder = IoPaths.POI2HGI.get_state_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Load preprocessed data
    data_path = IoPaths.POI2HGI.get_graph_data_file(city)
    print(f"Loading data: {data_path}")

    with open(data_path, 'rb') as handle:
        city_dict = pkl.load(handle)

    in_channels = city_dict['node_features'].shape[1]  # 36 (temporal features)
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

    # Initialize model (reusing HGI components)
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
    ).to(args.device)

    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    # Training loop
    t = trange(1, args.epoch + 1, desc=f"Training POI2HGI")
    lowest_loss = math.inf
    best_region_emb, best_poi_emb = None, None

    for epoch in t:
        loss = train_epoch(data, model, optimizer, scheduler, args)
        if loss < lowest_loss:
            best_region_emb, best_poi_emb = model.get_region_emb()
            lowest_loss = loss
        t.set_postfix(loss=f'{loss:.4f}', best=f'{lowest_loss:.4f}')

    # Save POI embeddings
    output_path = IoPaths.get_embedd(city, EmbeddingEngine.POI2HGI)
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
    """Run full POI2HGI pipeline: Preprocess -> Train."""
    city = state
    shapefile_path = args.shapefile
    graph_data_file = IoPaths.POI2HGI.get_graph_data_file(city)

    if graph_data_file.exists() and not args.force_preprocess:
        print(f"Using existing graph data: {graph_data_file}")
    else:
        print("Preprocessing with temporal features...")
        preprocess_poi2hgi(
            city=city,
            city_shapefile=str(shapefile_path),
        )

    print("Training POI2HGI...")
    train_poi2hgi(city, args)


run_pipeline = create_embedding  # Backwards compatibility


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='POI2HGI Embedding Pipeline')

    # Data
    parser.add_argument('--city', type=str, default='Alabama')
    parser.add_argument('--shapefile', type=str, default=Resources.TL_AL)

    # Pipeline
    parser.add_argument('--force_preprocess', action='store_true')

    # Model
    parser.add_argument('--dim', type=int, default=64)
    parser.add_argument('--attention_head', type=int, default=4)
    parser.add_argument('--alpha', type=float, default=0.5)

    # Training
    parser.add_argument('--lr', type=float, default=0.001)
    parser.add_argument('--gamma', type=float, default=1.0)
    parser.add_argument('--max_norm', type=float, default=0.9)
    parser.add_argument('--epoch', type=int, default=2000)

    # Device
    parser.add_argument('--device', type=str,
                        default='cpu')

    args = parser.parse_args()

    print(f"POI2HGI Pipeline | City: {args.city} | Device: {args.device}")
    create_embedding(state=args.city, args=args)
    print("Done!")
