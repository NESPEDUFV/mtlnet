"""Design D — train the heterogeneous c2hgi+POI encoder (5 contrastive boundaries).

Reads heterograph.pt produced by build_design_d_heterograph.py. Encoder is
PyG HeteroConv stack with **typed weights per edge type**. The structural
property: gradient from L_p2p only updates spatial-conv params, never the
sequence-conv params; gradient from L_c2c only updates seq-conv params.
This is what should escape the cat-vs-reg trade-off observed in Designs
A/E.

Architecture:
    Layer 1 HeteroConv:
        ('checkin','seq','checkin')   GCNConv(11→64)   <- with sin proj layer
        ('checkin','visits','poi')    SAGEConv((11,64)→64)
        ('poi','visited','checkin')   SAGEConv((64,11)→64)
        ('poi','spatial','poi')       GCNConv(64→64)

    Layer 2: same edge types, all dims 64→64.

Loss boundaries (defaults α_c2c=0.15, α_c2p=0.30, α_p2p=0.15, α_p2r=0.25, α_r2c=0.15):
    L_c2c   discriminate(checkin_h, checkin_h) over self vs random shuffle
    L_c2p   discriminate(checkin_h, poi_h[visits target]) vs negatives
    L_p2p   discriminate(poi_h, poi_h[Delaunay neighbour]) vs negatives
    L_p2r   discriminate(poi_h, region_h[poi_to_region]) — uses POI2Region as in c2hgi
    L_r2c   discriminate(region_h, city) — area-weighted

Outputs to ``output/check2hgi_design_d/<state>/``:
  - embeddings.parquet
  - poi_embeddings.parquet
  - region_embeddings.parquet

Usage::

    python scripts/probe/build_design_d_train.py --state alabama --epochs 500
"""

from __future__ import annotations

import argparse
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import HeteroData
from torch_geometric.nn import HeteroConv, GCNConv, SAGEConv
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))
from embeddings.hgi.model.RegionEncoder import POI2Region


EPS = 1e-7


class HeteroEncoder(nn.Module):
    """Two-layer HeteroConv stack with typed weights per edge."""

    def __init__(self, checkin_in: int, poi_in: int, hidden: int):
        super().__init__()
        self.proj_checkin = nn.Linear(checkin_in, hidden)
        self.proj_poi = nn.Linear(poi_in, hidden)
        # Layer 1
        self.conv1 = HeteroConv({
            ("checkin", "seq", "checkin"): GCNConv(hidden, hidden, add_self_loops=False),
            ("checkin", "visits", "poi"): SAGEConv((hidden, hidden), hidden),
            ("poi", "visited", "checkin"): SAGEConv((hidden, hidden), hidden),
            ("poi", "spatial", "poi"): GCNConv(hidden, hidden, add_self_loops=False),
        }, aggr="sum")
        # Layer 2
        self.conv2 = HeteroConv({
            ("checkin", "seq", "checkin"): GCNConv(hidden, hidden, add_self_loops=False),
            ("checkin", "visits", "poi"): SAGEConv((hidden, hidden), hidden),
            ("poi", "visited", "checkin"): SAGEConv((hidden, hidden), hidden),
            ("poi", "spatial", "poi"): GCNConv(hidden, hidden, add_self_loops=False),
        }, aggr="sum")
        self.act = nn.PReLU()

    def forward(self, h: HeteroData) -> dict:
        x = {
            "checkin": self.proj_checkin(h["checkin"].x),
            "poi": self.proj_poi(h["poi"].x),
        }
        edge_index_dict = {
            ("checkin", "seq", "checkin"): h["checkin", "seq", "checkin"].edge_index,
            ("checkin", "visits", "poi"): h["checkin", "visits", "poi"].edge_index,
            ("poi", "visited", "checkin"): h["poi", "visited", "checkin"].edge_index,
            ("poi", "spatial", "poi"): h["poi", "spatial", "poi"].edge_index,
        }
        # GCNConv accepts edge_weight via separate kwarg if we use SimpleConv... PyG
        # HeteroConv passes only edge_index and (optionally) edge_attr if defined.
        # For simplicity, omit edge weights here — uniform weight after the typed
        # GCN normalisation. (Future improvement: subclass to thread edge_weight.)
        x1 = self.conv1(x, edge_index_dict)
        x1 = {k: self.act(v) for k, v in x1.items()}
        x2 = self.conv2(x1, edge_index_dict)
        return x2


class DesignD(nn.Module):
    """Full Design D model: HeteroEncoder + POI2Region + 5 bilinear discriminators."""

    def __init__(self, checkin_in: int, poi_in: int, hidden: int, num_pois: int,
                 attention_head: int = 4):
        super().__init__()
        self.hidden = hidden
        self.num_pois = num_pois
        self.encoder = HeteroEncoder(checkin_in, poi_in, hidden)
        self.poi2region = POI2Region(hidden, attention_head)
        # Bilinear weights for each contrastive boundary
        self.W_c2c = nn.Parameter(torch.empty(hidden, hidden))
        self.W_c2p = nn.Parameter(torch.empty(hidden, hidden))
        self.W_p2p = nn.Parameter(torch.empty(hidden, hidden))
        self.W_p2r = nn.Parameter(torch.empty(hidden, hidden))
        self.W_r2c = nn.Parameter(torch.empty(hidden, hidden))
        for w in [self.W_c2c, self.W_c2p, self.W_p2p, self.W_p2r, self.W_r2c]:
            nn.init.uniform_(w, -1.0/math.sqrt(hidden), 1.0/math.sqrt(hidden))

    def discriminate(self, a, b, W):
        return torch.sigmoid((a @ W * b).sum(dim=-1))

    def discriminate_global(self, emb, summary, W):
        return torch.sigmoid(emb @ (W @ summary))

    def forward(self, h: HeteroData, extras: dict):
        x = self.encoder(h)
        checkin_h = x["checkin"]
        poi_h = x["poi"]

        # Region path (canonical c2hgi-style POI2Region)
        poi_to_region = extras["poi_to_region"]
        region_adj = extras["region_adjacency"]
        region_area = extras["region_area"]
        region_h = self.poi2region(poi_h, poi_to_region, region_adj)
        # City: area-weighted sum + sigmoid (from canonical c2hgi)
        city_h = torch.sigmoid((region_h.transpose(0, 1) * region_area).sum(dim=1))

        return checkin_h, poi_h, region_h, city_h

    def loss(self, h: HeteroData, extras: dict, alphas: dict):
        checkin_h, poi_h, region_h, city_h = self.forward(h, extras)
        device = checkin_h.device
        N_c = checkin_h.size(0)
        N_p = poi_h.size(0)
        N_r = region_h.size(0)

        # Negative samples by random permutation
        perm_c = torch.randperm(N_c, device=device)
        perm_p = torch.randperm(N_p, device=device)
        perm_r = torch.randperm(N_r, device=device)

        # L_c2c — checkin self-contrastive (positive: identity vs negative: shuffled)
        # Use seq edges as positive pairs (i, j) where j is sequence-neighbour
        seq_ei = h["checkin", "seq", "checkin"].edge_index
        if seq_ei.numel() > 0:
            i, j = seq_ei
            pos_c2c = self.discriminate(checkin_h[i], checkin_h[j], self.W_c2c)
            neg_c2c = self.discriminate(checkin_h[i], checkin_h[perm_c[j]], self.W_c2c)
            L_c2c = -torch.log(pos_c2c + EPS).mean() - torch.log(1 - neg_c2c + EPS).mean()
        else:
            L_c2c = torch.tensor(0.0, device=device)

        # L_c2p — visits edges (checkin → POI)
        v_ei = h["checkin", "visits", "poi"].edge_index
        i, j = v_ei  # i = checkin idx, j = poi idx
        pos_c2p = self.discriminate(checkin_h[i], poi_h[j], self.W_c2p)
        neg_j = perm_p[j]
        neg_c2p = self.discriminate(checkin_h[i], poi_h[neg_j], self.W_c2p)
        L_c2p = -torch.log(pos_c2p + EPS).mean() - torch.log(1 - neg_c2p + EPS).mean()

        # L_p2p — Delaunay POI-POI edges
        s_ei = h["poi", "spatial", "poi"].edge_index
        if s_ei.numel() > 0:
            i, j = s_ei
            pos_p2p = self.discriminate(poi_h[i], poi_h[j], self.W_p2p)
            neg_p2p = self.discriminate(poi_h[i], poi_h[perm_p[j]], self.W_p2p)
            L_p2p = -torch.log(pos_p2p + EPS).mean() - torch.log(1 - neg_p2p + EPS).mean()
        else:
            L_p2p = torch.tensor(0.0, device=device)

        # L_p2r — each POI vs its region (positive); shuffled region (negative)
        poi_region = extras["poi_to_region"]
        pos_regs = region_h[poi_region]
        neg_regs = region_h[perm_r[poi_region]]
        pos_p2r = self.discriminate(poi_h, pos_regs, self.W_p2r)
        neg_p2r = self.discriminate(poi_h, neg_regs, self.W_p2r)
        L_p2r = -torch.log(pos_p2r + EPS).mean() - torch.log(1 - neg_p2r + EPS).mean()

        # L_r2c
        pos_r2c = self.discriminate_global(region_h, city_h, self.W_r2c)
        neg_r2c = self.discriminate_global(region_h[perm_r], city_h, self.W_r2c)
        L_r2c = -torch.log(pos_r2c + EPS).mean() - torch.log(1 - neg_r2c + EPS).mean()

        total = (alphas["c2c"] * L_c2c + alphas["c2p"] * L_c2p + alphas["p2p"] * L_p2p
                 + alphas["p2r"] * L_p2r + alphas["r2c"] * L_r2c)
        return total, {"c2c": L_c2c.item(), "c2p": L_c2p.item(), "p2p": L_p2p.item(),
                       "p2r": L_p2r.item(), "r2c": L_r2c.item()}


def train_design_d(state: str, args: argparse.Namespace) -> None:
    state_lc = state.lower()
    out_dir = REPO / "output" / "check2hgi_design_d" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    payload_path = out_dir / "temp" / "heterograph.pt"
    with open(payload_path, "rb") as f:
        payload = pickle.load(f)
    h: HeteroData = payload["hetero"]
    extras_np = payload["extras"]

    device = torch.device(args.device)
    h = h.to(device)
    extras = {
        "poi_to_region": torch.tensor(extras_np["poi_to_region"], dtype=torch.int64, device=device),
        "region_adjacency": torch.tensor(extras_np["region_adjacency"], dtype=torch.int64, device=device),
        "region_area": torch.tensor(extras_np["region_area"], dtype=torch.float32, device=device),
        "coarse_region_similarity": torch.tensor(extras_np["coarse_region_similarity"],
                                                  dtype=torch.float32, device=device),
        "num_pois": int(extras_np["num_pois"]),
        "num_regions": int(extras_np["num_regions"]),
    }
    metadata = extras_np["metadata"]
    placeid_to_idx = extras_np["placeid_to_idx"]

    print(f"[{state_lc}] checkin={h['checkin'].x.shape}  poi={h['poi'].x.shape}")
    print(f"           seq_edges={h['checkin','seq','checkin'].edge_index.shape[1]}  "
          f"visits={h['checkin','visits','poi'].edge_index.shape[1]}  "
          f"spatial={h['poi','spatial','poi'].edge_index.shape[1]}")

    model = DesignD(
        checkin_in=h["checkin"].x.shape[1],
        poi_in=h["poi"].x.shape[1],
        hidden=args.dim,
        num_pois=h["poi"].x.shape[0],
        attention_head=args.attention_head,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma)

    alphas = {"c2c": args.alpha_c2c, "c2p": args.alpha_c2p, "p2p": args.alpha_p2p,
              "p2r": args.alpha_p2r, "r2c": args.alpha_r2c}

    t = trange(1, args.epochs + 1, desc=f"Train Design D [{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    for epoch in t:
        model.train()
        optimizer.zero_grad()
        total, parts = model.loss(h, extras, alphas)
        total.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        scheduler.step()
        l = total.item()
        if l < lowest:
            lowest = l
            best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        t.set_postfix(L=f"{l:.3f}", best=f"{lowest:.3f}", ep=best_epoch,
                      c2c=f"{parts['c2c']:.2f}", c2p=f"{parts['c2p']:.2f}",
                      p2p=f"{parts['p2p']:.2f}", p2r=f"{parts['p2r']:.2f}")

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        checkin_h, poi_h, region_h, city_h = model(h, extras)
        checkin_emb = checkin_h.cpu().numpy()
        poi_emb = poi_h.cpu().numpy()
        region_emb = region_h.cpu().numpy()

    df = pd.DataFrame(checkin_emb, columns=[f"{i}" for i in range(checkin_emb.shape[1])])
    df.insert(0, "datetime", metadata["datetime"].values)
    df.insert(0, "category", metadata["category"].values)
    df.insert(0, "placeid", metadata["placeid"].values)
    df.insert(0, "userid", metadata["userid"].values)
    df.to_parquet(out_dir / "embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote embeddings.parquet shape={checkin_emb.shape}")

    poi_df = pd.DataFrame(poi_emb, columns=[f"{i}" for i in range(poi_emb.shape[1])])
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, "placeid", [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(out_dir / "poi_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote poi_embeddings.parquet shape={poi_emb.shape}")

    reg_df = pd.DataFrame(region_emb, columns=[f"reg_{i}" for i in range(region_emb.shape[1])])
    reg_df.insert(0, "region_id", range(region_emb.shape[0]))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote region_embeddings.parquet shape={region_emb.shape}")

    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        import shutil
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--alpha-c2c", dest="alpha_c2c", type=float, default=0.15)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.30)
    ap.add_argument("--alpha-p2p", dest="alpha_p2p", type=float, default=0.15)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.25)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.15)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()
    train_design_d(args.state, args)


if __name__ == "__main__":
    main()
