"""tier_resln — ResLN-canonical substrate (ResidualLNEncoder, no POI2Vec).

Trains a plain Check2HGI (canonical 3-boundary contrastive objective, default
alphas 0.4/0.3/0.3) but swaps the check-in encoder from the canonical 2-layer
``CheckinEncoder`` (GCN) for ``ResidualLNEncoder`` (GCN + pre-LN + residual,
``num_layers=2`` pinned per canonical_improvement T3.2 recipe). Everything else
— graph, pooling heads, region path, region2city, loss — is byte-identical to
canonical c2hgi.

This mirrors the build path inside ``research/embeddings/check2hgi/check2hgi.py``
(encoder='resln' branch) but writes to a NEW engine dir
``output/check2hgi_resln/<state>/`` so the canonical substrate is untouched.

Outputs (same layout as canonical + design substrates so postbuild glue works):
  - embeddings.parquet        (per-check-in, cat-grade)
  - poi_embeddings.parquet    (per-POI)
  - region_embeddings.parquet (reg-grade)
  - temp/checkin_graph.pt      (copied verbatim from canonical)
  - temp/sequences_next.parquet (copied verbatim from canonical)

Usage::

    .venv/bin/python scripts/substrate_protocol_cleanup/build_resln_canonical.py \
        --state alabama --epochs 500 --device cuda --seed 42
"""

from __future__ import annotations

import argparse
import math
import pickle as pkl
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
from embeddings.check2hgi.model.variants import ResidualLNEncoder
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.hgi.model.RegionEncoder import POI2Region


def train(state: str, args: argparse.Namespace) -> None:
    state_lc = state.lower()
    # Seed for bit-reproducibility (mirrors check2hgi.train_check2hgi).
    seed = int(args.seed)
    import random as _py_random
    _py_random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    out_dir = REPO / "output" / "check2hgi_resln" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pkl.load(f)

    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(f"[{state_lc}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
          f"feature_dim={in_channels}")

    device = torch.device(args.device)

    data = Data(
        x=torch.tensor(d["node_features"], dtype=torch.float32),
        edge_index=torch.tensor(d["edge_index"], dtype=torch.int64),
        edge_weight=torch.tensor(d["edge_weight"], dtype=torch.float32),
        checkin_to_poi=torch.tensor(d["checkin_to_poi"], dtype=torch.int64),
        poi_to_region=torch.tensor(d["poi_to_region"], dtype=torch.int64),
        region_adjacency=torch.tensor(d["region_adjacency"], dtype=torch.int64),
        region_area=torch.tensor(d["region_area"], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(d["coarse_region_similarity"], dtype=torch.float32),
        num_pois=num_pois,
        num_regions=num_regions,
    ).to(device)

    metadata = d["metadata"]

    checkin_encoder = ResidualLNEncoder(in_channels, args.dim, num_layers=args.num_layers)
    print(f"[{state_lc}] encoder=ResidualLNEncoder num_layers={args.num_layers}")
    checkin2poi = Checkin2POI(args.dim, args.attention_head)
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI(
        hidden_channels=args.dim,
        checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha_c2p=args.alpha_c2p,
        alpha_p2r=args.alpha_p2r,
        alpha_r2c=args.alpha_r2c,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    t = trange(1, args.epochs + 1, desc=f"Train ResLN-canonical [{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    for epoch in t:
        model.train()
        optimizer.zero_grad()
        outputs = model(data)
        loss = model.loss(*outputs)
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        scheduler.step()
        l = loss.item()
        if l < lowest:
            lowest = l
            best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch % 25 == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", best_ep=best_epoch, refresh=False)
            t.refresh()

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        _ = model(data)
        checkin_emb, poi_emb, region_emb = model.get_embeddings()

    emb_np = checkin_emb.numpy()
    df = pd.DataFrame(emb_np, columns=[f"{i}" for i in range(emb_np.shape[1])])
    df.insert(0, "datetime", metadata["datetime"].values)
    df.insert(0, "category", metadata["category"].values)
    df.insert(0, "placeid", metadata["placeid"].values)
    df.insert(0, "userid", metadata["userid"].values)
    df.to_parquet(out_dir / "embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote embeddings.parquet shape={emb_np.shape}")

    poi_np = poi_emb.numpy()
    poi_df = pd.DataFrame(poi_np, columns=[f"{i}" for i in range(poi_np.shape[1])])
    placeid_to_idx = d["placeid_to_idx"]
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, "placeid", [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(out_dir / "poi_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote poi_embeddings.parquet shape={poi_np.shape}")

    reg_np = region_emb.numpy()
    reg_df = pd.DataFrame(reg_np, columns=[f"reg_{i}" for i in range(reg_np.shape[1])])
    reg_df.insert(0, "region_id", range(num_regions))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote region_embeddings.parquet shape={reg_np.shape}")

    (out_dir / "temp").mkdir(exist_ok=True)
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")
    print(f"[{state_lc}] copied checkin_graph.pt + sequences_next.parquet")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--num-layers", dest="num_layers", type=int, default=2)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.4)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.3)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    train(args.state, args)


if __name__ == "__main__":
    main()
