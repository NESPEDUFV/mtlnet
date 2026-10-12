"""Design E — POI2Vec-augmented Check2HGI with stop-gradient at encoder→pool.

Per the advisor's recommendation: take the failed POI2Vec-input probe, add a
``.detach()`` on the encoder output before it reaches Checkin2POI. The c2p
boundary still updates the encoder (encoder learns cat-aligned check-in
features), but the p2r and r2c boundaries no longer pull the encoder toward
POI-mean discriminative features. Tests whether the cat-vs-reg trade-off is
fixable by **gradient isolation** alone, without graph surgery.

Input feature dim: canonical 11-dim + POI2Vec 64-dim = 75-dim per check-in
(reuses the augmented graph from build_check2hgi_poi2vec.py).

Architecture:
    checkin_emb       = CheckinEncoder(augmented_features)        # active grad
    checkin_emb_stop  = checkin_emb.detach()                       # stop here
    poi_emb           = Checkin2POI(checkin_emb_stop, ...)         # pool only
    region_emb        = POI2Region(poi_emb, ...)                   # standard
    city_emb          = region2city(region_emb)

Loss boundaries (unchanged):
    L_c2p uses (checkin_emb [active], poi_emb [from stopped input])
    L_p2r uses (poi_emb, region_emb_expanded)
    L_r2c uses (region_emb, city_emb)

Outputs to output/check2hgi_design_e/<state>/ with canonical schema.

Usage::

    python scripts/probe/build_design_e_stopgrad.py --state alabama --epochs 500
    python scripts/probe/build_design_e_stopgrad.py --state arizona --epochs 500
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
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.hgi.model.RegionEncoder import POI2Region


class Check2HGI_StopGrad(Check2HGI):
    """Check2HGI variant where encoder receives gradient only from L_c2p.

    Forward differs from base in exactly one place: ``checkin_emb`` is
    detached before being fed to ``checkin2poi``. The c2p discriminator
    still scores the *active* checkin_emb against the (stopped-pool) poi_emb,
    so encoder gradient flows from ``-log(σ(W·active·stopped))`` back to
    encoder params. The p2r and r2c boundaries operate purely on the
    stopped POI tower.
    """

    def forward(self, data):
        num_pois = data.num_pois
        num_regions = data.num_regions

        # Active encoder pass
        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)

        # Stop gradient before POI tower
        pos_checkin_stop = pos_checkin_emb.detach()
        neg_checkin_stop = neg_checkin_emb.detach()

        pos_poi_emb = self.checkin2poi(pos_checkin_stop, data.checkin_to_poi, num_pois)
        neg_poi_emb = self.checkin2poi(neg_checkin_stop, data.checkin_to_poi, num_pois)

        pos_region_emb = self.poi2region(pos_poi_emb, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb, data.poi_to_region, data.region_adjacency)

        city_emb = self.region2city(pos_region_emb, data.region_area)

        self.checkin_embedding = pos_checkin_emb  # active for downstream extraction
        self.poi_embedding = pos_poi_emb
        self.region_embedding = pos_region_emb

        pos_poi_expanded = pos_poi_emb[data.checkin_to_poi]
        neg_poi_indices = self._sample_negative_indices(
            data.checkin_to_poi, num_pois, data.x.device
        )
        neg_poi_expanded = pos_poi_emb[neg_poi_indices]

        pos_region_expanded = pos_region_emb[data.poi_to_region]
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions,
            data.coarse_region_similarity, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb,
        )


def train_design_e(state: str, args: argparse.Namespace) -> None:
    state_lc = state.lower()
    out_dir = REPO / "output" / "check2hgi_design_e" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    # Reuse the augmented graph from POI2Vec probe (same input features)
    graph_path = REPO / "output" / "check2hgi_poi2vec" / state_lc / "temp" / "checkin_graph.pt"
    if not graph_path.exists():
        raise FileNotFoundError(
            f"Augmented graph missing: {graph_path}. "
            f"Run scripts/probe/build_check2hgi_poi2vec.py --state {state} first."
        )
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(
        f"[{state_lc}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
        f"feature_dim={in_channels} (canonical+POI2Vec)"
    )

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

    checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
    checkin2poi = Checkin2POI(args.dim, args.attention_head)
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI_StopGrad(
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

    t = trange(1, args.epochs + 1, desc=f"Train Design E [{state_lc}]")
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
        t.set_postfix(loss=f"{l:.4f}", best=f"{lowest:.4f}", best_ep=best_epoch)

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state)
    model.eval()
    with torch.no_grad():
        _ = model(data)
        checkin_emb, poi_emb, region_emb = model.get_embeddings()

    # check-in embeddings
    emb_np = checkin_emb.numpy()
    df = pd.DataFrame(emb_np, columns=[f"{i}" for i in range(emb_np.shape[1])])
    df.insert(0, "datetime", metadata["datetime"].values)
    df.insert(0, "category", metadata["category"].values)
    df.insert(0, "placeid", metadata["placeid"].values)
    df.insert(0, "userid", metadata["userid"].values)
    df.to_parquet(out_dir / "embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote embeddings.parquet shape={emb_np.shape}")

    # POI embeddings
    poi_np = poi_emb.numpy()
    poi_df = pd.DataFrame(poi_np, columns=[f"{i}" for i in range(poi_np.shape[1])])
    placeid_to_idx = d["placeid_to_idx"]
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, "placeid", [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(out_dir / "poi_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote poi_embeddings.parquet shape={poi_np.shape}")

    # Region embeddings
    reg_np = region_emb.numpy()
    reg_df = pd.DataFrame(reg_np, columns=[f"reg_{i}" for i in range(reg_np.shape[1])])
    reg_df.insert(0, "region_id", range(num_regions))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote region_embeddings.parquet shape={reg_np.shape}")

    # Mirror temp dir for downstream lookup
    (out_dir / "temp").mkdir(exist_ok=True)
    import shutil
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")


def main():
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
    args = ap.parse_args()
    train_design_e(args.state, args)


if __name__ == "__main__":
    main()
