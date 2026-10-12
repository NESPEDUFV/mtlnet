"""Design H — Check2HGI with a *learnable* POI embedding table at POI-pool.

The user's intuition: instead of injecting frozen POI2Vec at the POI-pool
boundary (Design B), let the model learn its own per-POI embeddings inside
the c2hgi structure. The POI table is initialised from POI2Vec (warm start
on fclass-discriminative geometry), then co-trained via L_p2r and L_r2c.

Architecturally this is identical to Design B except the POI residual is a
learnable ``nn.Embedding(num_pois, D)`` rather than a frozen
``Linear(POI2Vec)``. Both update only via the reg-side losses; both leave
the cat path byte-identical to canonical c2hgi via ``.detach()`` on the
canonical pool output.

Hypothesis: a co-trained POI table can carve a representation that better
fits the contrastive loss on this graph than the frozen POI2Vec residual.
If H beats B on reg without hurting cat, the learning is doing useful work.

Usage::

    python scripts/probe/build_design_h_learnable_poi.py --state alabama --epochs 500
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


POI2VEC_DIM = 64


class Check2HGI_DesignH(Check2HGI):
    """Learnable per-POI embedding table at the POI-pool boundary.

    Parameters
    ----------
    poi2vec_init: optional [num_pois, D] tensor. If provided, the learnable
        POI table is initialised with these values. Otherwise uses Xavier.
    gamma_init: initial scalar weight on the learnable POI residual.
    """

    def __init__(self, *args, num_pois: int, poi2vec_init: torch.Tensor | None = None,
                 gamma_init: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.poi_table = nn.Embedding(num_pois, self.hidden_channels)
        if poi2vec_init is not None:
            # POI2Vec dim may differ from hidden_channels — project.
            if poi2vec_init.shape[1] != self.hidden_channels:
                # Same dim by default (64), but support generic init.
                proj = nn.Linear(poi2vec_init.shape[1], self.hidden_channels, bias=False)
                with torch.no_grad():
                    self.poi_table.weight.copy_(proj(poi2vec_init.float()))
            else:
                with torch.no_grad():
                    self.poi_table.weight.copy_(poi2vec_init.float())
        self.gamma = nn.Parameter(torch.tensor(float(gamma_init)))

    def forward(self, data):
        num_pois = data.num_pois
        num_regions = data.num_regions

        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)

        pos_poi_emb_canonical = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)
        neg_poi_emb_canonical = self.checkin2poi(neg_checkin_emb, data.checkin_to_poi, num_pois)

        # Learnable POI table — gradients reach it via L_p2r/L_r2c only.
        # speed: nn.Embedding(N).weight is identical to embedding(arange(N))
        poi_residual = self.poi_table.weight  # [N_pois, D]

        pos_poi_emb_for_reg = pos_poi_emb_canonical.detach() + self.gamma * poi_residual
        neg_poi_emb_for_reg = neg_poi_emb_canonical.detach() + self.gamma * poi_residual

        pos_region_emb = self.poi2region(pos_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        city_emb = self.region2city(pos_region_emb, data.region_area)

        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb_for_reg
        self.region_embedding = pos_region_emb

        # L_c2p: canonical c2hgi (same as Design B)
        pos_poi_expanded = pos_poi_emb_canonical[data.checkin_to_poi]
        neg_poi_indices = self._sample_negative_indices(
            data.checkin_to_poi, num_pois, data.x.device
        )
        neg_poi_expanded = pos_poi_emb_canonical[neg_poi_indices]

        pos_region_expanded = pos_region_emb[data.poi_to_region]
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions,
            data.coarse_region_similarity, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]

        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb_for_reg, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb,
        )


def load_poi2vec_init(state: str, num_pois: int, placeid_to_idx: dict) -> torch.Tensor:
    state_lc = state.lower()
    state_cap = state.capitalize()
    csv = REPO / f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state_cap}.csv"
    df = pd.read_csv(csv)
    emb_cols = [str(i) for i in range(POI2VEC_DIM)]
    arr = np.zeros((num_pois, POI2VEC_DIM), dtype=np.float32)
    seen = np.zeros(num_pois, dtype=bool)
    for placeid, vec in zip(df["placeid"].astype(int).tolist(), df[emb_cols].to_numpy(np.float32)):
        idx = placeid_to_idx.get(placeid)
        if idx is None:
            continue
        arr[idx] = vec
        seen[idx] = True
    return torch.from_numpy(arr)


def train_design_h(state: str, args: argparse.Namespace) -> None:
    state_lc = state.lower()
    suffix = getattr(args, "out_suffix", "") or ""
    out_dir = REPO / "output" / f"check2hgi_design_h{suffix}" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(f"[{state_lc}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
          f"feature_dim={in_channels} (canonical 11-dim)")

    device = torch.device(args.device)
    poi2vec_init = load_poi2vec_init(state, num_pois, d["placeid_to_idx"]) if args.warm_start else None

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

    model = Check2HGI_DesignH(
        hidden_channels=args.dim,
        checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha_c2p=args.alpha_c2p,
        alpha_p2r=args.alpha_p2r,
        alpha_r2c=args.alpha_r2c,
        num_pois=num_pois,
        poi2vec_init=poi2vec_init,
        gamma_init=args.gamma_init,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,} (warm_start={args.warm_start})")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    t = trange(1, args.epochs + 1, desc=f"Train Design H [{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    POSTFIX_EVERY = 25
    for epoch in t:
        model.train()
        optimizer.zero_grad()
        outputs = model(data)
        loss = model.loss(*outputs)
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        l = loss.item()
        if l < lowest:
            lowest = l
            best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch % POSTFIX_EVERY == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", best_ep=best_epoch, refresh=False)
            t.refresh()

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f} gamma={model.gamma.item():.3f}")
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

    poi_np = poi_emb.numpy()
    poi_df = pd.DataFrame(poi_np, columns=[f"{i}" for i in range(poi_np.shape[1])])
    placeid_to_idx = d["placeid_to_idx"]
    idx_to_placeid = {v: k for k, v in placeid_to_idx.items()}
    poi_df.insert(0, "placeid", [idx_to_placeid.get(i, i) for i in range(len(poi_df))])
    poi_df.to_parquet(out_dir / "poi_embeddings.parquet", index=False)

    reg_np = region_emb.numpy()
    reg_df = pd.DataFrame(reg_np, columns=[f"reg_{i}" for i in range(reg_np.shape[1])])
    reg_df.insert(0, "region_id", range(num_regions))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote 3 parquets")

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
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0)
    ap.add_argument("--warm-start", dest="warm_start", action="store_true", default=True,
                    help="Initialise POI table from POI2Vec (default).")
    ap.add_argument("--no-warm-start", dest="warm_start", action="store_false",
                    help="Random-init POI table.")
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()
    train_design_h(args.state, args)


if __name__ == "__main__":
    main()
