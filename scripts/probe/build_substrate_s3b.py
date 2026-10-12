"""Phase 11 S3-b V1 — Replace POI2Region with Checkin2Region (primary path).

User's original hypothesis: c2hgi's POI2Region was tuned for HGI's
POI2Vec-stable inputs; c2hgi feeds it the mean of contextually-encoded
check-ins per POI — a mixture distribution. S3-b replaces POI2Region
with a structurally-analogous Checkin2Region pooler that operates
directly on per-check-in embeddings, with `zone = poi_to_region[
checkin_to_poi]`. The L_p2r contrastive boundary is replaced with a
structurally-equivalent L_c2r boundary using HGI's foreign-region
negative sampling pattern.

Cat path: c2hgi POI level (Checkin2POI output) is preserved as the
input to L_c2p. There is no parallel POI→region canonical path to
`.detach()`, so cat-side gradient flow through Checkin2POI now
co-trains with the region-side path. Cat-preservation gate (≥38.76 AL
F1 vs canonical 40.76) is the highest-variance risk.

V1 reuses POI2Region(D, num_heads) verbatim as the Checkin2Region
module (zero new design). Mirrors `HGIModule.forward` + `HGIModule.loss`
pattern — see `research/embeddings/hgi/model/HGIModule.py`.

Output dir: ``output/check2hgi_substrate_s3b/<state>/``.

Usage::

    python scripts/probe/build_substrate_s3b.py --state alabama \
        --epochs 500 --device mps
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

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption  # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI  # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region  # noqa: E402
from torch_geometric.nn.inits import uniform  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "probe"))
from build_design_j_anchor import (  # noqa: E402
    Check2HGI_DesignJ,
    load_poi2vec,
    POI2VEC_DIM,
)


EPS = 1e-7


class Check2HGI_S3b(Check2HGI_DesignJ):
    """Replace POI→Region pathway with Check-in→Region. Primary boundary.

    Loss = α_c2p · L_c2p + α_c2r · L_c2r + α_r2c · L_r2c + λ · L_anchor

    where L_c2r mirrors HGI's L_p2r:
      pos = discriminate(checkin_i, region_emb[region(i)])
      neg = discriminate(checkin_j, region_emb[region(i)])
            for j sampled from a foreign region (random other region)

    Notes
    -----
    - We *override* `forward` and `loss` entirely rather than reusing
      Check2HGI's 9-tuple, because the structural meaning of the slots
      changes (POI emb → check-in emb at the discriminator inputs).
    - J's POI table + anchor loss are preserved — but the POI table
      is now only used for the anchor regulariser; it does not
      participate in the region pathway. We keep it because removing
      it would conflate "S3-b methodology" with "drop J's prior".
      A clean ablation of "S3-b without J's POI table" can be done
      separately if V1 is directional.
    """

    def __init__(
        self,
        *args,
        c2r_attention_head: int = 4,
        alpha_c2r: float = 0.3,   # replaces alpha_p2r as the primary p2r-equivalent weight
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.c2r_pooler = POI2Region(self.hidden_channels, c2r_attention_head)
        self.weight_c2r = nn.Parameter(
            torch.Tensor(self.hidden_channels, self.hidden_channels)
        )
        uniform(self.hidden_channels, self.weight_c2r)
        # alpha_p2r becomes meaningless (no p2r boundary); rename for clarity.
        self.alpha_c2r = float(alpha_c2r)

    def forward(self, data):
        """Returns a 9-tuple matching HGIModule's reference semantics:

            (pos_checkin_idx, pos_target_region_for_checkin,
             neg_checkin_idx, neg_target_region_for_checkin,
             pos_checkin_emb, region_emb, neg_region_emb, city_emb,
             pos_poi_emb_for_c2p)

        The first 8 slots mirror HGI's structure for the L_c2r boundary
        (with check-ins replacing POIs); the 9th carries the POI-level
        embedding needed for L_c2p (c2hgi's c2p boundary, preserved).
        """
        num_pois = int(data.num_pois)
        num_regions = int(data.num_regions)
        device = data.x.device

        # Encoder: per-check-in embeddings (positive + corrupted-feature negative).
        pos_checkin_emb = self.checkin_encoder(data.x, data.edge_index, data.edge_weight)
        cor_x = self.corruption(data.x)
        neg_checkin_emb = self.checkin_encoder(cor_x, data.edge_index, data.edge_weight)

        # POI level: kept for L_c2p only. NO involvement in region pathway.
        pos_poi_emb_canonical = self.checkin2poi(pos_checkin_emb, data.checkin_to_poi, num_pois)

        # J's POI table is preserved as anchor target only; does NOT
        # contribute to region-side embeddings.
        # (We do not add `+ self.gamma * self.poi_table.weight` to the
        # region path here — that would re-introduce the J merge mechanism
        # at the POI→region boundary that no longer exists.)

        # Check-in → Region (primary pathway). Each check-in is assigned
        # to its POI's region.
        checkin_to_region = data.poi_to_region[data.checkin_to_poi]      # [N_checkins]

        region_emb = self.c2r_pooler(
            pos_checkin_emb, checkin_to_region, data.region_adjacency
        )
        neg_region_emb = self.c2r_pooler(
            neg_checkin_emb, checkin_to_region, data.region_adjacency
        )
        city_emb = self.region2city(region_emb, data.region_area)

        # Store for embedding extraction.
        self.checkin_embedding = pos_checkin_emb
        self.poi_embedding = pos_poi_emb_canonical
        self.region_embedding = region_emb

        # ─── Foreign-region negative sampling (mirrors HGIModule.forward) ───
        # For each region R, pick a random foreign region R'. Then:
        #   pos pairs = (every check-in in R, R)
        #   neg pairs = (every check-in in R', R)
        # Pairing: positive check-in i contributes (i, region(i)); negatives
        # are constructed by gathering all check-ins from the foreign region.

        N = pos_checkin_emb.size(0)
        pos_checkin_idx = torch.arange(N, device=device)
        pos_target_region = checkin_to_region                            # [N]

        # Build per-region check-in buckets (cached).
        cache = getattr(data, "_s3b_neg_cache", None)
        if cache is None or cache.get("R") != num_regions:
            cir_cpu = checkin_to_region.detach().cpu()
            sort_idx = torch.argsort(cir_cpu, stable=True)
            sizes = torch.bincount(cir_cpu, minlength=num_regions)
            offsets = torch.zeros(num_regions + 1, dtype=torch.long)
            offsets[1:] = sizes.cumsum(0)
            data._s3b_neg_cache = {
                "R": num_regions,
                "sort_idx": sort_idx.to(device),
                "sizes": sizes.to(device),
                "offsets": offsets.to(device),
            }
            cache = data._s3b_neg_cache

        sort_idx = cache["sort_idx"]
        sizes = cache["sizes"]
        offsets = cache["offsets"]

        # Pick negative region per region (uniform random ≠ self).
        neg_region_indices = torch.randint(0, num_regions - 1, (num_regions,), device=device)
        arange_R = torch.arange(num_regions, device=device)
        neg_region_indices = torch.where(
            neg_region_indices >= arange_R, neg_region_indices + 1, neg_region_indices)

        neg_sizes = sizes[neg_region_indices]
        neg_total = int(neg_sizes.sum().item())

        if neg_total == 0:
            neg_checkin_idx = torch.empty(0, dtype=torch.long, device=device)
            neg_target_region_for_checkin = torch.empty(0, dtype=torch.long, device=device)
        else:
            neg_target_region_for_checkin = torch.repeat_interleave(arange_R, neg_sizes)
            out_starts = torch.zeros(num_regions, dtype=torch.long, device=device)
            out_starts[1:] = neg_sizes[:-1].cumsum(0)
            within = (
                torch.arange(neg_total, device=device)
                - out_starts[neg_target_region_for_checkin]
            )
            src_starts = offsets[neg_region_indices]
            src_pos = src_starts[neg_target_region_for_checkin] + within
            neg_checkin_idx = sort_idx[src_pos]

        return (
            pos_checkin_idx, pos_target_region,
            neg_checkin_idx, neg_target_region_for_checkin,
            pos_checkin_emb, region_emb, neg_region_emb, city_emb,
            pos_poi_emb_canonical,
        )

    def loss(self, *args):
        (pos_checkin_idx, pos_target_region,
         neg_checkin_idx, neg_target_region,
         pos_checkin_emb, region_emb, neg_region_emb, city_emb,
         pos_poi_emb_canonical) = args

        # ─── L_c2r (replaces L_p2r as primary, HGI-style) ───
        pos_chk = pos_checkin_emb[pos_checkin_idx]
        pos_reg = region_emb[pos_target_region]
        pos_score = self.discriminate(pos_chk, pos_reg, self.weight_c2r, sigmoid=True)
        loss_pos_c2r = -torch.log(pos_score + EPS).mean()

        if neg_checkin_idx.numel() > 0:
            neg_chk = pos_checkin_emb[neg_checkin_idx]
            neg_reg = region_emb[neg_target_region]
            neg_score = self.discriminate(neg_chk, neg_reg, self.weight_c2r, sigmoid=True)
            loss_neg_c2r = -torch.log(1 - neg_score + EPS).mean()
        else:
            loss_neg_c2r = torch.zeros((), device=pos_checkin_emb.device)

        loss_c2r = loss_pos_c2r + loss_neg_c2r

        # ─── L_c2p (preserved from canonical c2hgi) ───
        # The c2p positive/negative pairs need `data.checkin_to_poi` which
        # is not in the loss-tuple. forward() stashes a data ref via
        # `attach_data_ref`; the helper below reconstructs the c2p formulation.
        loss_c2p = self._c2p_loss_cached(pos_checkin_emb, pos_poi_emb_canonical)

        # ─── L_r2c (preserved from canonical c2hgi) ───
        pos_r2c = self.discriminate_global(region_emb, city_emb, self.weight_r2c)
        neg_r2c = self.discriminate_global(neg_region_emb, city_emb, self.weight_r2c)
        loss_r2c = (
            -torch.log(pos_r2c + EPS).mean()
            - torch.log(1 - neg_r2c + EPS).mean()
        )

        # alpha_c2p, alpha_r2c keep canonical defaults; alpha_p2r is replaced
        # by alpha_c2r as the primary p2r-equivalent term.
        return (
            self.alpha_c2p * loss_c2p
            + self.alpha_c2r * loss_c2r
            + self.alpha_r2c * loss_r2c
        )

    def _c2p_loss_cached(self, pos_checkin_emb, pos_poi_emb_canonical):
        """Compute L_c2p using the data ref stashed in forward.

        Mirrors Check2HGIModule's c2p formulation: each check-in vs
        its POI (positive) and vs a random other POI (negative).
        """
        if not hasattr(self, "_data_for_loss"):
            raise RuntimeError("forward() did not stash data for loss; call forward first.")
        data = self._data_for_loss
        device = pos_checkin_emb.device

        pos_poi_expanded = pos_poi_emb_canonical[data.checkin_to_poi]
        # Random different POI per check-in.
        num_pois = pos_poi_emb_canonical.size(0)
        neg_idx = torch.randint(0, num_pois - 1, (data.checkin_to_poi.size(0),), device=device)
        neg_idx = torch.where(neg_idx >= data.checkin_to_poi, neg_idx + 1, neg_idx)
        neg_poi_expanded = pos_poi_emb_canonical[neg_idx]

        pos_score = self.discriminate(pos_checkin_emb, pos_poi_expanded, self.weight_c2p)
        neg_score = self.discriminate(pos_checkin_emb, neg_poi_expanded, self.weight_c2p)
        return (
            -torch.log(pos_score + EPS).mean()
            - torch.log(1 - neg_score + EPS).mean()
        )

    def attach_data_ref(self, data):
        """Caller hook: stash data for c2p loss after forward."""
        self._data_for_loss = data


def train(state: str, args):
    seed = getattr(args, "seed", None)
    if seed is not None:
        torch.manual_seed(int(seed))
        np.random.seed(int(seed))

    state_lc = state.lower()
    suffix = getattr(args, "out_suffix", "") or ""
    base = "check2hgi_substrate_s3b" + (f"_{suffix}" if suffix else "")
    out_dir = REPO / "output" / base / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(
        f"[{state_lc}] pois={num_pois} regions={num_regions} feat={in_channels} "
        f"λ_anchor={args.anchor_lambda} α_c2r={args.alpha_c2r}"
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

    # Log per-region check-in count distribution (sparse-region risk).
    cir = data.poi_to_region[data.checkin_to_poi]
    sizes = torch.bincount(cir.cpu(), minlength=num_regions)
    print(
        f"[{state_lc}] per-region check-in count: "
        f"min={int(sizes.min())} mean={float(sizes.float().mean()):.1f} "
        f"median={int(sizes.median())} max={int(sizes.max())} "
        f"#regions_with_zero={int((sizes == 0).sum())}"
    )

    checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
    checkin2poi = Checkin2POI(args.dim, args.attention_head)
    poi2region = POI2Region(args.dim, args.attention_head)  # base; never used for region

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI_S3b(
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
    t = trange(1, args.epochs + 1, desc=f"S3b[{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    POSTFIX_EVERY = 25
    for epoch in t:
        model.train(); optimizer.zero_grad()
        model.attach_data_ref(data)
        outputs = model(data)
        loss_main = model.loss(*outputs)
        loss_anchor = model.anchor_loss()
        loss = loss_main + args.anchor_lambda * loss_anchor
        loss.backward()
        clip_grad_norm_(model.parameters(), max_norm=args.max_norm)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        l = loss.item()
        if l < lowest:
            lowest = l; best_epoch = epoch
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
        if epoch in (1, 25, 50, args.epochs):
            t.write(f"[{state_lc}] ep{epoch} loss={l:.4f}")
            smoke_log.append({"epoch": epoch, "loss": float(l)})
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
        (out_dir / "s3b_smoke_log.json").write_text(json.dumps(smoke_log, indent=2))
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
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.0,
                    help="Unused in S3-b (no p2r boundary). Kept for parent class API.")
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--alpha-c2r", dest="alpha_c2r", type=float, default=0.3,
                    help="S3-b primary boundary weight; replaces alpha_p2r.")
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0)
    ap.add_argument("--anchor-lambda", dest="anchor_lambda", type=float, default=0.1)
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
