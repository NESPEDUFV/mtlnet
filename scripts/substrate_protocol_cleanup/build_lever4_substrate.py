"""Lever 4 — POI2Vec at p2r boundary, additive substrate variant.

Mechanism (from `docs/studies/merge_design/LEVER_4_POI2VEC_P2R.md`):
    region_prior[r] = mean({ POI2Vec[i] for i in pois_of_region[r] })
    L_substrate = L_canonical + alpha * (1 - cos(region_emb[r], W * region_prior[r]))

The region_prior is computed once at build time from the POI2Vec table and
poi_to_region map; the W is a learnable Linear projection (POI2VEC_DIM ->
hidden_channels). The cosine term is added to the substrate's `loss()` at
every training step.

This variant builds on the SAME architecture as the base substrate (either
canonical c2hgi or a winner from Wave 1 — controlled by `--base`).

Output layout matches Design B exactly:
    output/check2hgi_lever4_<base>/<state>/
        embeddings.parquet, poi_embeddings.parquet, region_embeddings.parquet,
        temp/{checkin_graph.pt, sequences_next.parquet}

Usage:
    python scripts/substrate_protocol_cleanup/build_lever4_substrate.py \
        --state alabama --base canonical --epochs 500 --alpha 0.1 --device cuda
"""

from __future__ import annotations

import argparse
import math
import pickle
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption  # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI  # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region  # noqa: E402

POI2VEC_DIM = 64


def load_poi2vec_table(state, num_pois, placeid_to_idx):
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
    n_unmapped = int((~seen).sum())
    if n_unmapped > 0:
        print(f"  WARN {n_unmapped} POIs missing from POI2Vec — left zero")
    return torch.from_numpy(arr)


def compute_region_prior(poi2vec: torch.Tensor, poi_to_region: np.ndarray, num_regions: int):
    """Mean-pool POI2Vec by region."""
    prior = torch.zeros(num_regions, POI2VEC_DIM)
    counts = torch.zeros(num_regions)
    p2r_t = torch.from_numpy(np.asarray(poi_to_region, dtype=np.int64))
    prior.index_add_(0, p2r_t, poi2vec)
    counts.index_add_(0, p2r_t, torch.ones(poi2vec.shape[0]))
    counts = counts.clamp_min(1)
    prior = prior / counts.unsqueeze(1)
    return prior


class Check2HGI_Lever4(Check2HGI):
    """Canonical c2hgi + Lever 4 region-prior term on L_p2r.

    The forward pass is the **canonical** c2hgi (no POI2Vec at the POI-pool
    boundary — that is Design B's mechanism). Lever 4 is layered on top by
    the loss extension only. This makes it a clean "control on canonical"
    when --base=canonical.

    When --base=design_b, the forward is Design B's (POI2Vec at POI-pool),
    and Lever 4 adds the region-prior term on top (B + Lever 4).
    """

    def __init__(self, *args, region_prior: torch.Tensor, alpha_prior: float = 0.1,
                 design_b_mode: bool = False, poi2vec_table: torch.Tensor = None,
                 gamma_init: float = 1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.alpha_prior = float(alpha_prior)
        self.region_prior_proj = nn.Linear(POI2VEC_DIM, self.hidden_channels, bias=True)
        self.register_buffer("region_prior", region_prior.float())
        self.design_b_mode = design_b_mode
        if design_b_mode:
            assert poi2vec_table is not None
            self.poi2vec_proj = nn.Linear(POI2VEC_DIM, self.hidden_channels, bias=True)
            self.gamma = nn.Parameter(torch.tensor(float(gamma_init)))
            self.register_buffer("poi2vec_table", poi2vec_table.float())

    def forward(self, data):
        if not self.design_b_mode:
            # Canonical c2hgi forward
            return super().forward(data)
        # Design B forward (copied verbatim from build_design_b_poi_pool.py)
        num_pois = data.num_pois
        num_regions = data.num_regions
        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)
        pos_poi_emb_canonical = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)
        neg_poi_emb_canonical = self.checkin2poi(neg_checkin_emb, data.checkin_to_poi, num_pois)
        poi2vec_residual = self.poi2vec_proj(self.poi2vec_table)
        pos_poi_emb_for_reg = pos_poi_emb_canonical.detach() + self.gamma * poi2vec_residual
        neg_poi_emb_for_reg = neg_poi_emb_canonical.detach() + self.gamma * poi2vec_residual
        pos_region_emb = self.poi2region(pos_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        neg_region_emb = self.poi2region(neg_poi_emb_for_reg, data.poi_to_region, data.region_adjacency)
        city_emb = self.region2city(pos_region_emb, data.region_area)
        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb_for_reg
        self.region_embedding = pos_region_emb
        pos_poi_expanded = pos_poi_emb_canonical[data.checkin_to_poi]
        neg_poi_indices = self._sample_negative_indices(data.checkin_to_poi, num_pois, data.x.device)
        neg_poi_expanded = pos_poi_emb_canonical[neg_poi_indices]
        pos_region_expanded = pos_region_emb[data.poi_to_region]
        neg_region_indices = self._sample_negative_indices_with_similarity(
            data.poi_to_region, num_regions, data.coarse_region_similarity, data.x.device
        )
        neg_region_expanded = pos_region_emb[neg_region_indices]
        return (
            pos_checkin_emb, pos_poi_expanded, neg_poi_expanded,
            pos_poi_emb_for_reg, pos_region_expanded, neg_region_expanded,
            pos_region_emb, neg_region_emb, city_emb,
        )

    def lever4_term(self):
        """1 - cos(region_emb, W * region_prior) — to be ADDED to L_p2r."""
        target = self.region_prior_proj(self.region_prior)  # [N_reg, D]
        # self.region_embedding is set during forward()
        return (1.0 - F.cosine_similarity(self.region_embedding, target, dim=-1)).mean()


def train_lever4(state: str, args):
    state_lc = state.lower()
    base = "canonical" if args.base == "canonical" else args.base
    out_root = f"check2hgi_lever4_{base}"
    out_dir = REPO / "output" / out_root / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)
    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(f"[{state_lc}/{base}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
          f"feature_dim={in_channels} alpha_prior={args.alpha}")

    device = torch.device(args.device)
    poi2vec_table = load_poi2vec_table(state, num_pois, d["placeid_to_idx"])
    region_prior = compute_region_prior(poi2vec_table, d["poi_to_region"], num_regions)

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

    model = Check2HGI_Lever4(
        hidden_channels=args.dim,
        checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha_c2p=args.alpha_c2p,
        alpha_p2r=args.alpha_p2r,
        alpha_r2c=args.alpha_r2c,
        region_prior=region_prior,
        alpha_prior=args.alpha,
        design_b_mode=(args.base == "design_b"),
        poi2vec_table=poi2vec_table if args.base == "design_b" else None,
        gamma_init=args.gamma_init,
    ).to(device)
    print(f"[{state_lc}/{base}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    t = trange(1, args.epochs + 1, desc=f"Train Lever4/{base}[{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    for epoch in t:
        model.train()
        optimizer.zero_grad()
        outputs = model(data)
        loss_main = model.loss(*outputs)
        loss_prior = model.lever4_term()
        loss = loss_main + model.alpha_prior * loss_prior
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
        if epoch % 25 == 0 or epoch == args.epochs:
            t.set_postfix(
                loss=f"{l:.4f}", prior=f"{loss_prior.item():.4f}", best_ep=best_epoch,
                refresh=False,
            )
            t.refresh()

    print(f"[{state_lc}/{base}] best_epoch={best_epoch} loss={lowest:.4f}")
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
    print(f"[{state_lc}/{base}] wrote embeddings.parquet shape={emb_np.shape}")

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

    (out_dir / "temp").mkdir(exist_ok=True)
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--base", choices=["canonical", "design_b"], default="canonical")
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--num-layers", dest="num_layers", type=int, default=2)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.4)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.3)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--alpha", type=float, default=0.1, help="region-prior term weight (Lever 4)")
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()
    train_lever4(args.state, args)


if __name__ == "__main__":
    main()
