"""Phase 4 (preprocess→pickle) for FL HGI + 5-epoch timing probe to project Phase 5 cost.
Does NOT run the full HGI train. Writes gowalla.pt pickle, then times 5 epochs and prints projection.
"""
import sys, time, pickle as pkl, math
from pathlib import Path
from argparse import Namespace
from copy import copy

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import torch
from configs.paths import IoPaths, EmbeddingEngine, Resources
from configs.model import InputsConfig
from embeddings.hgi.preprocess import preprocess_hgi

CITY = "Florida"
CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM, alpha=0.5, attention_head=4, lr=0.006,
    gamma=1.0, max_norm=0.9, epoch=2000, warmup_period=40, poi2vec_epochs=100,
    force_preprocess=True, cross_region_weight=0.7, device='cpu', shapefile=str(Resources.TL_FL),
)

def main():
    graph_data_file = IoPaths.HGI.get_graph_data_file(CITY)
    poi_emb_path = IoPaths.HGI.get_poi_emb_file(CITY)
    cta_file = str(IoPaths.HGI.get_boroughs_file(CITY))
    print(f"[phase4] graph_data_file={graph_data_file}")
    print(f"[phase4] poi_emb_path={poi_emb_path} exists={Path(poi_emb_path).exists()}")
    print(f"[phase4] cta_file={cta_file} exists={Path(cta_file).exists()}")
    print(f"[phase4] shapefile={CONFIG.shapefile} exists={Path(CONFIG.shapefile).exists()}")

    if graph_data_file.exists():
        print(f"[phase4] pickle already exists, loading")
        with open(graph_data_file, "rb") as f:
            data = pkl.load(f)
    else:
        t0 = time.time()
        data = preprocess_hgi(
            city=CITY, city_shapefile=CONFIG.shapefile, poi_emb_path=str(poi_emb_path),
            cta_file=cta_file, cross_region_weight=CONFIG.cross_region_weight,
        )
        graph_data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(graph_data_file, "wb") as f:
            pkl.dump(data, f)
        print(f"[phase4] preprocess+save took {time.time()-t0:.1f}s -> {graph_data_file}")

    print(f"[phase4] num_pois={data['number_pois']} num_regions={data['number_regions']} "
          f"in_channels={data['node_features'].shape[1]} edges={data['edge_index'].shape}")

    # --- 5-epoch timing probe ---
    import pytorch_warmup as warmup
    from torch.nn.utils import clip_grad_norm_
    from torch.optim.lr_scheduler import StepLR
    from torch_geometric.data import Data
    from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
    from embeddings.hgi.model.POIEncoder import POIEncoder
    from embeddings.hgi.model.RegionEncoder import POI2Region

    args = CONFIG
    d = Data(
        x=torch.tensor(data['node_features'], dtype=torch.float32),
        edge_index=torch.tensor(data['edge_index'], dtype=torch.int64),
        edge_weight=torch.tensor(data['edge_weight'], dtype=torch.float32),
        region_id=torch.tensor(data['region_id'], dtype=torch.int64),
        region_area=torch.tensor(data['region_area'], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(data['coarse_region_similarity'], dtype=torch.float32),
        region_adjacency=torch.tensor(data['region_adjacency'], dtype=torch.int64),
    ).to(args.device)
    poi_encoder = POIEncoder(data['node_features'].shape[1], args.dim)
    poi2region = POI2Region(args.dim, args.attention_head)
    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))
    model = HierarchicalGraphInfomax(
        hidden_channels=args.dim, poi_encoder=poi_encoder, poi2region=poi2region,
        region2city=region2city, corruption=corruption, alpha=args.alpha,
        hard_neg_prob=getattr(args, "hard_neg_prob", 0.25),
    ).to(args.device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    sch = StepLR(opt, step_size=1, gamma=args.gamma)
    wu = warmup.LinearWarmup(opt, args.warmup_period)
    print(f"[probe] params={sum(p.numel() for p in model.parameters()):,}")
    torch.set_num_threads(6)
    NPROBE = 5
    t0 = time.time()
    for e in range(NPROBE):
        model.train(); opt.zero_grad()
        out = model(d); loss = model.loss(*out)
        loss.backward(); clip_grad_norm_(model.parameters(), max_norm=args.max_norm); opt.step()
        with wu.dampening(): sch.step()
    dt = (time.time()-t0)/NPROBE
    proj_h = dt * 2000 / 3600
    print(f"[probe] {dt:.2f} s/epoch  ->  2000 epochs PROJECTION = {proj_h:.2f} GPU-h (CPU-h here)")
    print(f"[probe] DECISION: {'PROCEED (<=2h)' if proj_h<=2 else ('CAUTION (2-4h)' if proj_h<=4 else 'STOP (>4h)')}")

if __name__ == "__main__":
    main()
