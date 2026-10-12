"""Phase 11 S3-b V2-c — S3-b + per-check-in POI2Vec anchor.

Same architecture as S3-b V1 (Checkin2Region replaces POI2Region as
the primary region pathway, no POI2Vec residual on the region path)
plus a new anchor loss that pulls every check-in encoding toward its
POI's POI2Vec fclass embedding:

    L_anchor_chk = mean_i ‖ pos_checkin_emb[i] − POI2Vec[poi(checkin_i)] ‖²

The encoder itself is now pulled toward fclass-aware geometry; the
Checkin2Region pooler then operates on fclass-aware contextual
check-in vectors.

Pre-registered expected outcome (advisor): AL Acc@10 ∈ [55, 62] %,
mean Δ vs J ∈ [−1, 0] pp. Surprise threshold (would change writeup):
AL ≥ 62.5 % AND AZ ≥ 52.5 %.

Output dir: ``output/check2hgi_substrate_s3b_v2c/<state>/``.

Usage::

    python scripts/probe/build_substrate_s3b_v2c.py --state alabama \
        --epochs 500 --device mps --lambda-chk-anchor 0.1
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

from embeddings.check2hgi.model.Check2HGIModule import corruption  # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI  # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "probe"))
from build_substrate_s3b import Check2HGI_S3b  # noqa: E402
from build_design_j_anchor import load_poi2vec, POI2VEC_DIM  # noqa: E402


class Check2HGI_S3b_V2c(Check2HGI_S3b):
    """S3-b V1 + per-check-in POI2Vec anchor on the encoder output."""

    def checkin_anchor_loss(self):
        """L2 distance from per-check-in encoding to its POI's POI2Vec.

        Requires `attach_data_ref(data)` to have been called in this
        forward pass (S3-b's loss path uses the same hook).
        """
        if self.checkin_embedding is None or not torch.is_tensor(self.checkin_embedding):
            raise RuntimeError("checkin_embedding not set; call forward first.")
        if not hasattr(self, "_data_for_loss"):
            raise RuntimeError("data ref not attached; call attach_data_ref(data).")
        data = self._data_for_loss
        # POI2Vec target per check-in: poi2vec_anchor[poi(checkin)].
        target = self.poi2vec_anchor[data.checkin_to_poi]    # [N_checkins, D]
        return ((self.checkin_embedding - target) ** 2).mean()


def train(state: str, args):
    seed = getattr(args, "seed", None)
    if seed is not None:
        torch.manual_seed(int(seed))
        np.random.seed(int(seed))

    state_lc = state.lower()
    suffix = getattr(args, "out_suffix", "") or ""
    base = "check2hgi_substrate_s3b_v2c" + (f"_{suffix}" if suffix else "")
    out_dir = REPO / "output" / base / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(
        f"[{state_lc}] V2-c  pois={num_pois} regions={num_regions} feat={in_channels} "
        f"λ_anchor={args.anchor_lambda} α_c2r={args.alpha_c2r} "
        f"λ_chk_anchor={args.lambda_chk_anchor}"
    )

    device = torch.device(args.device)
    poi2vec = load_poi2vec(state, num_pois, d["placeid_to_idx"])

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
    metadata = d["metadata"]

    checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
    checkin2poi = Checkin2POI(args.dim, args.attention_head)
    poi2region = POI2Region(args.dim, args.attention_head)  # unused (S3-b path)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI_S3b_V2c(
        hidden_channels=args.dim, checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi, poi2region=poi2region,
        region2city=region2city, corruption=corruption,
        alpha_c2p=args.alpha_c2p, alpha_p2r=args.alpha_p2r, alpha_r2c=args.alpha_r2c,
        num_pois=num_pois, poi2vec_anchor=poi2vec, gamma_init=args.gamma_init,
        c2r_attention_head=args.c2r_attention_head, alpha_c2r=args.alpha_c2r,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    smoke_log = []
    t = trange(1, args.epochs + 1, desc=f"S3b-V2c[{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    POSTFIX_EVERY = 25
    for epoch in t:
        model.train(); optimizer.zero_grad()
        model.attach_data_ref(data)
        outputs = model(data)
        loss_main = model.loss(*outputs)
        loss_poi_anchor = model.anchor_loss()           # J's POI-table anchor (preserved)
        loss_chk_anchor = model.checkin_anchor_loss()    # V2-c new term
        loss = (
            loss_main
            + args.anchor_lambda * loss_poi_anchor
            + args.lambda_chk_anchor * loss_chk_anchor
        )
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        l = loss.item()
        if l < lowest:
            lowest = l; best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch in (1, 25, 50, 100, 250, args.epochs):
            t.write(
                f"[{state_lc}] ep{epoch} total={l:.4f} main={loss_main.item():.4f} "
                f"poi_anchor={loss_poi_anchor.item():.4f} "
                f"chk_anchor={loss_chk_anchor.item():.4f}"
            )
            smoke_log.append({
                "epoch": epoch,
                "loss_total": float(l),
                "loss_main": float(loss_main.item()),
                "loss_poi_anchor": float(loss_poi_anchor.item()),
                "loss_chk_anchor": float(loss_chk_anchor.item()),
            })
        if epoch % POSTFIX_EVERY == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", best_ep=best_epoch, refresh=False)
            t.refresh()

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state); model.eval()
    model.attach_data_ref(data)
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

    (out_dir / "temp").mkdir(exist_ok=True)
    import shutil
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")

    if smoke_log:
        import json
        (out_dir / "v2c_loss_log.json").write_text(json.dumps(smoke_log, indent=2))
    print(f"[{state_lc}] wrote {out_dir}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--num-layers", dest="num_layers", type=int, default=2)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--c2r-attention-head", dest="c2r_attention_head",
                    type=int, default=4)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.4)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.0)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--alpha-c2r", dest="alpha_c2r", type=float, default=0.3)
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0)
    ap.add_argument("--anchor-lambda", dest="anchor_lambda", type=float, default=0.1,
                    help="J's POI-table anchor weight (preserved from S3-b V1).")
    ap.add_argument("--lambda-chk-anchor", dest="lambda_chk_anchor",
                    type=float, default=0.1,
                    help="V2-c per-check-in POI2Vec anchor weight.")
    ap.add_argument("--out-suffix", dest="out_suffix", type=str, default="")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    args = ap.parse_args()
    train(args.state, args)


if __name__ == "__main__":
    main()
