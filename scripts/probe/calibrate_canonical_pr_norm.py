"""Calibrate canonical c2hgi POI2Region PMA participation ratio.

Trains canonical c2hgi for 50 epochs on AL (or specified state), reading
the PMA softmax distribution at epoch 50 to compute per-region
participation ratio. Sets the kill rule for S3-b V1: c2r PMA PR_norm
must be < 2× this calibration's PR_norm at the same epoch budget.

Usage::

    python scripts/probe/calibrate_canonical_pr_norm.py --state alabama
"""
from __future__ import annotations

import argparse
import json
import math
import pickle
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from torch.nn.utils import clip_grad_norm_
from torch_geometric.data import Data
from tqdm import trange

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption  # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI  # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region  # noqa: E402

EPS = 1e-7


@torch.no_grad()
def measure_pma_pr(pma_module: POI2Region, x: torch.Tensor,
                   zone: torch.Tensor, num_regions: int) -> dict:
    """Recompute the PMA softmax weights and return PR / entropy stats.

    Replicates the internal computation in POI2Region.forward up to and
    including the softmax over zone, without running the full forward.
    """
    from torch_geometric.utils import softmax as pyg_softmax, scatter

    mab = pma_module.PMA.mab
    K = mab.fc_k(x)
    Q = mab.fc_q(pma_module.PMA.S).squeeze(0)
    H = pma_module.num_heads
    d = pma_module.hidden_channels // H
    N = x.size(0)
    K_split = K.view(N, H, d)
    Q_split = Q.view(1, H, d)
    scores = (K_split * Q_split).sum(dim=-1) / math.sqrt(pma_module.hidden_channels)
    alpha = pyg_softmax(scores, zone, num_nodes=num_regions)

    log_a = torch.log(alpha.clamp(min=EPS))
    entropy_terms = -(alpha * log_a)
    ent_per_region = scatter(entropy_terms, zone, dim=0,
                             dim_size=num_regions, reduce='add').mean(dim=1)
    pr_inv = scatter(alpha ** 2, zone, dim=0,
                     dim_size=num_regions, reduce='add')
    pr = 1.0 / pr_inv.clamp(min=EPS)
    ones = torch.ones_like(zone, dtype=torch.float32)
    sizes = scatter(ones, zone, dim=0, dim_size=num_regions, reduce='add')
    valid = sizes > 0
    pr_norm = (pr / sizes.unsqueeze(-1).clamp(min=1)).mean(dim=1)

    return {
        "entropy_mean": float(ent_per_region[valid].mean().item()),
        "participation_ratio_mean": float(pr_norm[valid].mean().item()),
        "n_regions_with_input": int(valid.sum().item()),
        "min_zone_size": int(sizes[valid].min().item()),
        "max_zone_size": int(sizes[valid].max().item()),
        "mean_zone_size": float(sizes[valid].mean().item()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=50)
    ap.add_argument("--device", type=str, default="mps")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    state_lc = args.state.lower()

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)
    in_channels = d["node_features"].shape[1]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(f"[{state_lc}] pois={num_pois} regions={num_regions} feat={in_channels}")

    device = torch.device(args.device)
    data = Data(
        x=torch.tensor(d["node_features"], dtype=torch.float32),
        edge_index=torch.tensor(d["edge_index"], dtype=torch.int64),
        edge_weight=torch.tensor(d["edge_weight"], dtype=torch.float32),
        checkin_to_poi=torch.tensor(d["checkin_to_poi"], dtype=torch.int64),
        poi_to_region=torch.tensor(d["poi_to_region"], dtype=torch.int64),
        region_adjacency=torch.tensor(d["region_adjacency"], dtype=torch.int64),
        region_area=torch.tensor(d["region_area"], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(
            d["coarse_region_similarity"], dtype=torch.float32),
        num_pois=num_pois, num_regions=num_regions,
    ).to(device)

    checkin_encoder = CheckinEncoder(in_channels, 64, num_layers=2)
    checkin2poi = Checkin2POI(64, 4)
    poi2region = POI2Region(64, 4)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI(
        hidden_channels=64,
        checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

    print(f"[{state_lc}] training canonical c2hgi for {args.epochs} epochs")
    log = []
    for epoch in trange(1, args.epochs + 1, desc=f"Calibrate[{state_lc}]"):
        model.train(); optimizer.zero_grad()
        outputs = model(data)
        loss = model.loss(*outputs)
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=0.9)
        optimizer.step()
        if epoch in (1, 25, 50):
            model.eval()
            stats = measure_pma_pr(
                poi2region, model.poi_embedding,
                data.poi_to_region, num_regions
            )
            log.append({"epoch": epoch, "loss": float(loss.item()), **stats})

    print()
    for entry in log:
        print(
            f"  ep{entry['epoch']:>3}: loss={entry['loss']:.4f}  "
            f"entropy={entry['entropy_mean']:.4f}  "
            f"PR_norm={entry['participation_ratio_mean']:.4f}  "
            f"zone_size [min/mean/max]="
            f"{entry['min_zone_size']}/{entry['mean_zone_size']:.1f}/{entry['max_zone_size']}"
        )

    out_dir = REPO / "logs" / "substrate_s1"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"canonical_pr_norm_{state_lc}.json"
    out_path.write_text(json.dumps(log, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Kill rule for S3-b V1: c2r PMA PR_norm at ep50 must be < 2× "
          f"{log[-1]['participation_ratio_mean']:.4f} = "
          f"{2 * log[-1]['participation_ratio_mean']:.4f}")


if __name__ == "__main__":
    main()
