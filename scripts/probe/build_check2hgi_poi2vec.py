"""Build a Check2HGI variant that augments check-in features with POI2Vec.

Hypothesis (post diagnostic): the C2HGI→HGI reg gap is in the *training signal* —
HGI's POI-level features (POI2Vec from fclass-level Node2Vec) carry richer POI
identity than C2HGI's per-check-in features (category one-hot + temporal sin/cos).
Mean-pool diagnostic falsified the per-visit-noise hypothesis at the region level
(both AL + AZ regressed under post-hoc pooling). This script tests whether
appending POI2Vec to each check-in's input feature vector lifts reg toward HGI
without hurting cat.

Pipeline
--------
1. Load canonical ``output/check2hgi/<state>/temp/checkin_graph.pt`` (preserves
   geo-spatial preprocessing — no need to re-run shapefile join).
2. Load HGI's POI2Vec table: ``output/hgi/<state>/poi2vec_poi_embeddings_<State>.csv``
   (64-dim per placeid, deterministic — already built for the HGI baseline).
3. Per check-in: lookup the POI's POI2Vec(64) via placeid → poi_idx →
   poi2vec_arr[poi_idx]. Append to canonical 11-dim features → 75-dim.
4. Save augmented graph to ``output/check2hgi_poi2vec/<state>/temp/checkin_graph.pt``.
5. Train Check2HGI on augmented features. ``CheckinEncoder`` reads
   ``in_channels = node_features.shape[1]`` so it auto-adapts.
6. Write ``embeddings.parquet``, ``poi_embeddings.parquet``,
   ``region_embeddings.parquet`` to ``output/check2hgi_poi2vec/<state>/``.

The output directory layout mirrors canonical Check2HGI exactly so the existing
``--region-emb-source check2hgi_poi2vec`` switch in ``p1_region_head_ablation.py``
finds region embeddings without further plumbing.

Usage::

    python scripts/probe/build_check2hgi_poi2vec.py --state alabama --epochs 500
    python scripts/probe/build_check2hgi_poi2vec.py --state arizona --epochs 500
"""

from __future__ import annotations

import argparse
import math
import pickle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.nn.utils import clip_grad_norm_
from torch.optim.lr_scheduler import StepLR
from torch_geometric.data import Data
from tqdm import trange

import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.hgi.model.RegionEncoder import POI2Region

POI2VEC_DIM = 64
CANONICAL_FEATURE_DIM = None  # detected from canonical graph


def build_augmented_graph(state: str) -> Path:
    """Augment canonical Check2HGI features with POI2Vec, save to new dir."""
    state_lc = state.lower()
    state_cap = state.capitalize()

    canon_graph = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    poi2vec_csv = REPO / "output" / "hgi" / state_lc / f"poi2vec_poi_embeddings_{state_cap}.csv"
    out_graph_dir = REPO / "output" / "check2hgi_poi2vec" / state_lc / "temp"
    out_graph_dir.mkdir(parents=True, exist_ok=True)
    out_graph = out_graph_dir / "checkin_graph.pt"

    if not canon_graph.exists():
        raise FileNotFoundError(f"Canonical graph missing: {canon_graph}")
    if not poi2vec_csv.exists():
        raise FileNotFoundError(f"POI2Vec CSV missing: {poi2vec_csv}")

    with open(canon_graph, "rb") as f:
        g = pickle.load(f)

    placeid_to_idx: dict = g["placeid_to_idx"]
    num_pois = int(g["num_pois"])
    canonical_feats = np.asarray(g["node_features"], dtype=np.float32)  # [N_checkins, F]
    checkin_to_poi = np.asarray(g["checkin_to_poi"], dtype=np.int64)

    p2v_df = pd.read_csv(poi2vec_csv)
    emb_cols = [str(i) for i in range(POI2VEC_DIM)]
    missing_cols = [c for c in emb_cols if c not in p2v_df.columns]
    if missing_cols:
        raise RuntimeError(f"POI2Vec CSV missing columns {missing_cols[:5]}...")

    poi2vec_arr = np.zeros((num_pois, POI2VEC_DIM), dtype=np.float32)
    seen = np.zeros(num_pois, dtype=bool)
    for placeid, vec in zip(p2v_df["placeid"].values, p2v_df[emb_cols].to_numpy(dtype=np.float32)):
        idx = placeid_to_idx.get(int(placeid))
        if idx is None:
            continue
        poi2vec_arr[idx] = vec
        seen[idx] = True

    n_unseen = int((~seen).sum())
    if n_unseen > 0:
        # Should never happen — HGI's POI2Vec covers exactly the c2hgi POI universe
        # (both built from the same checkin parquet).
        print(f"[WARN] {n_unseen} POIs missing from POI2Vec table — those rows kept as zero")

    augmented = np.concatenate(
        [canonical_feats, poi2vec_arr[checkin_to_poi]], axis=1
    )  # [N_checkins, F + 64]

    g_aug = dict(g)
    g_aug["node_features"] = augmented
    g_aug["_poi2vec_dim"] = POI2VEC_DIM
    g_aug["_canonical_feature_dim"] = canonical_feats.shape[1]

    with open(out_graph, "wb") as f:
        pickle.dump(g_aug, f)

    print(
        f"[{state_lc}] canonical_feat_dim={canonical_feats.shape[1]} "
        f"+ poi2vec_dim={POI2VEC_DIM} = {augmented.shape[1]} "
        f"({augmented.shape[0]} checkins, {num_pois} pois) -> {out_graph}"
    )
    return out_graph


def train_with_augmented(state: str, args: argparse.Namespace, graph_path: Path) -> None:
    """Train Check2HGI on augmented features. Mirrors train_check2hgi but
    points all output paths at output/check2hgi_poi2vec/<state>/.
    """
    state_lc = state.lower()
    out_dir = REPO / "output" / "check2hgi_poi2vec" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(
        f"[{state_lc}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
        f"feature_dim={in_channels} (canonical={d.get('_canonical_feature_dim','?')}+poi2vec={POI2VEC_DIM})"
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
    )

    metadata = d["metadata"]

    checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
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

    data = data.to(device)

    t = trange(1, args.epochs + 1, desc=f"Train check2hgi+POI2Vec [{state_lc}]")
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

    # Region embeddings (canonical reg_* schema)
    reg_np = region_emb.numpy()
    reg_df = pd.DataFrame(reg_np, columns=[f"reg_{i}" for i in range(reg_np.shape[1])])
    reg_df.insert(0, "region_id", range(num_regions))
    reg_df.to_parquet(out_dir / "region_embeddings.parquet", index=False)
    print(f"[{state_lc}] wrote region_embeddings.parquet shape={reg_np.shape}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True, help="alabama | arizona | ...")
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
    ap.add_argument("--device", type=str, default="cpu",
                    help="cpu | mps | cuda — full-batch is small; cpu is usually fine")
    args = ap.parse_args()

    g = build_augmented_graph(args.state)
    train_with_augmented(args.state, args, g)


if __name__ == "__main__":
    main()
