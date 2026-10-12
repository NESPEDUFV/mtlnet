"""Phase 11 S3-a — Direct Checkin2Region pooler (additive regulariser on J).

Tests the user's "Check-in↔Region methodology" reframe in its safest form:
add a parallel ``Checkin2Region`` PMA pooler that pools per-check-in
embeddings directly into regions, supervised via a fourth contrastive
boundary ``L_c2r``. The canonical 3-boundary path (c2p, p2r, r2c) and
J's POI-pool injection are preserved unchanged. Downstream
``region_embeddings.parquet`` stays POI-pooled — c2r is supervision-
only, not a region-emb replacement (S3-b would do the replacement).

Hypothesis: HGI's POI2Region was tuned for stable POI2Vec inputs;
c2hgi feeds it a mixture of contextual check-in pools. A direct
check-in→region pathway, supervised by its own contrastive boundary,
should provide a cleaner gradient signal back through the check-in
encoder than the indirect path through Checkin2POI → POI2Region.

Bit-equivalence at ``alpha_c2r=0.0`` is the scaffold sanity check:
the new code is gated on ``alpha_c2r > 0`` and preserves the J
forward + loss byte-for-byte when off.

Output dir: ``output/check2hgi_substrate_s3a/<state>/``.

Usage::

    python scripts/probe/build_substrate_s3a.py --state alabama \
        --alpha-c2r 0.2 --epochs 500 --device mps
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

# Reuse J's exact build pattern for the POI-pool boundary.
sys.path.insert(0, str(REPO / "scripts" / "probe"))
from build_design_j_anchor import (  # noqa: E402
    Check2HGI_DesignJ,
    load_poi2vec,
    POI2VEC_DIM,
)


EPS = 1e-7


class Check2HGI_S3a(Check2HGI_DesignJ):
    """J + parallel Checkin2Region pooler with L_c2r contrastive boundary.

    When ``alpha_c2r=0.0`` the forward pass is bit-equivalent to J: no
    extra modules instantiated, no extra RNG draws, no extra tensors in
    the return tuple. When ``alpha_c2r > 0`` an additional pooler runs
    on ``pos_checkin_emb`` with ``zone = poi_to_region[checkin_to_poi]``
    (each check-in is assigned to its POI's region) and a contrastive
    L_c2r is added to the loss.
    """

    def __init__(
        self,
        *args,
        alpha_c2r: float = 0.0,
        c2r_attention_head: int = 4,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.alpha_c2r = float(alpha_c2r)

        if self.alpha_c2r > 0.0:
            # Reuse POI2Region — index-agnostic in its `zone` argument.
            self.c2r_pooler = POI2Region(self.hidden_channels, c2r_attention_head)
            self.weight_c2r = nn.Parameter(
                torch.Tensor(self.hidden_channels, self.hidden_channels)
            )
            uniform(self.hidden_channels, self.weight_c2r)
        else:
            self.c2r_pooler = None
            self.weight_c2r = None

        # Buffer for entropy probe (set during forward when c2r is active).
        self._c2r_last_alpha = None

    def forward(self, data):
        out = super().forward(data)  # J's 9-tuple (preserves RNG order)

        if self.alpha_c2r == 0.0:
            # Byte-identical to J. No extras.
            return out

        # Build check-in→region zone vector.
        checkin_to_region = data.poi_to_region[data.checkin_to_poi]   # [N_checkins]
        num_regions = int(data.num_regions)

        # Positive: pool pos_checkin_emb (already in self.checkin_embedding).
        # The c2r_pooler is only used here — we reuse its output across both
        # pos and neg pairs by indexing different region rows.
        pos_region_emb_via_checkin = self.c2r_pooler(
            self.checkin_embedding, checkin_to_region, data.region_adjacency
        )

        # S3-a v2: foreign-region negatives. Each check-in's positive region
        # is its true region; the negative is a randomly sampled different
        # region's c2r-pool encoding. Mirrors p2r's contrast pattern (random
        # other region, exclude self) without similarity-mined hard negs —
        # the latter are a separate lever.
        N = checkin_to_region.size(0)
        device = data.x.device
        rand_neg = torch.randint(0, num_regions - 1, (N,), device=device)
        rand_neg = torch.where(rand_neg >= checkin_to_region, rand_neg + 1, rand_neg)

        pos_region_expanded_c = pos_region_emb_via_checkin[checkin_to_region]
        neg_region_expanded_c = pos_region_emb_via_checkin[rand_neg]

        return out + (
            pos_region_expanded_c,           # [N_checkins, D]
            neg_region_expanded_c,           # [N_checkins, D]
        )

    def loss(self, *args):
        if self.alpha_c2r == 0.0:
            # Identical to J's call: 9-tuple → super().loss(*9-tuple).
            return super().loss(*args)

        base_args = args[:9]
        pos_region_expanded_c, neg_region_expanded_c = args[9], args[10]

        base_loss = super().loss(*base_args)

        # L_c2r: discriminate (true checkin, true region encoding)
        # vs (true checkin, corrupted-feature region encoding).
        pos_checkin = base_args[0]                                   # pos_checkin_emb
        pos_score = self.discriminate(pos_checkin, pos_region_expanded_c, self.weight_c2r)
        neg_score = self.discriminate(pos_checkin, neg_region_expanded_c, self.weight_c2r)
        loss_c2r = (
            -torch.log(pos_score + EPS).mean()
            - torch.log(1 - neg_score + EPS).mean()
        )
        return base_loss + self.alpha_c2r * loss_c2r

    @torch.no_grad()
    def c2r_attention_entropy(self, data):
        """Compute mean per-region entropy of the c2r PMA softmax weights.

        Returns (entropy_mean, entropy_std, participation_ratio_mean).
        Participation ratio is 1/sum(alpha**2) per region, head-averaged,
        normalised by region size — values near 1 mean fully uniform,
        near 1/N mean concentrated on one item.
        """
        if self.c2r_pooler is None:
            return None
        from torch_geometric.utils import softmax as pyg_softmax

        pos_checkin_emb = self.checkin_encoder(
            data.x, data.edge_index, data.edge_weight
        )
        zone = data.poi_to_region[data.checkin_to_poi]
        num_regions = int(data.num_regions)

        mab = self.c2r_pooler.PMA.mab
        K = mab.fc_k(pos_checkin_emb)
        Q = mab.fc_q(self.c2r_pooler.PMA.S).squeeze(0)

        H = self.c2r_pooler.num_heads
        d = self.c2r_pooler.hidden_channels // H
        N = pos_checkin_emb.size(0)
        K_split = K.view(N, H, d)
        Q_split = Q.view(1, H, d)
        scores = (K_split * Q_split).sum(dim=-1) / math.sqrt(self.c2r_pooler.hidden_channels)
        alpha = pyg_softmax(scores, zone, num_nodes=num_regions)        # [N, H]

        # Entropy per region per head.
        # H_region_head = -sum_i alpha_ih log alpha_ih  (sum over check-ins in region)
        log_a = torch.log(alpha.clamp(min=EPS))
        entropy_terms = -(alpha * log_a)                                # [N, H]
        from torch_geometric.utils import scatter
        ent_per_region = scatter(entropy_terms, zone, dim=0,
                                 dim_size=num_regions, reduce='add')   # [R, H]
        # Participation ratio per region per head: 1/sum(alpha^2)
        pr_inv = scatter(alpha ** 2, zone, dim=0,
                         dim_size=num_regions, reduce='add')           # [R, H]
        pr = 1.0 / pr_inv.clamp(min=EPS)
        # Region sizes for normalisation.
        ones = torch.ones_like(zone, dtype=torch.float32)
        sizes = scatter(ones, zone, dim=0, dim_size=num_regions, reduce='add')
        valid = sizes > 0
        pr_norm = (pr / sizes.unsqueeze(-1).clamp(min=1)).mean(dim=1)   # [R]
        ent_mean_per_region = ent_per_region.mean(dim=1)                # [R]

        return {
            "entropy_mean": float(ent_mean_per_region[valid].mean().item()),
            "entropy_std": float(ent_mean_per_region[valid].std().item()),
            "participation_ratio_mean": float(pr_norm[valid].mean().item()),
            "n_regions_with_checkins": int(valid.sum().item()),
        }


def train(state: str, args):
    seed = getattr(args, "seed", None)
    if seed is not None:
        torch.manual_seed(int(seed))
        np.random.seed(int(seed))

    state_lc = state.lower()
    suffix = getattr(args, "out_suffix", "") or ""
    base = "check2hgi_substrate_s3a" + (f"_{suffix}" if suffix else "")
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
        f"λ={args.anchor_lambda} α_c2r={args.alpha_c2r}"
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
    poi2region = POI2Region(args.dim, args.attention_head)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = Check2HGI_S3a(
        hidden_channels=args.dim, checkin_encoder=checkin_encoder,
        checkin2poi=checkin2poi, poi2region=poi2region,
        region2city=region2city, corruption=corruption,
        alpha_c2p=args.alpha_c2p, alpha_p2r=args.alpha_p2r, alpha_r2c=args.alpha_r2c,
        num_pois=num_pois, poi2vec_anchor=poi2vec, gamma_init=args.gamma_init,
        alpha_c2r=args.alpha_c2r, c2r_attention_head=args.c2r_attention_head,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    entropy_log = []
    t = trange(1, args.epochs + 1, desc=f"Train S3a[{state_lc}]")
    lowest = math.inf
    best_epoch = 0
    best_state = None
    POSTFIX_EVERY = 25
    for epoch in t:
        model.train(); optimizer.zero_grad()
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
        if epoch in (1, 25, 50, args.epochs) and args.alpha_c2r > 0:
            stats = model.c2r_attention_entropy(data)
            if stats is not None:
                entropy_log.append({"epoch": epoch, **stats})
                t.write(
                    f"[{state_lc}] ep{epoch} c2r entropy={stats['entropy_mean']:.4f} "
                    f"pr_norm={stats['participation_ratio_mean']:.4f}"
                )
        if epoch % POSTFIX_EVERY == 0 or epoch == args.epochs:
            t.set_postfix(loss=f"{l:.4f}", best_ep=best_epoch, refresh=False)
            t.refresh()

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f}")
    model.load_state_dict(best_state); model.eval()
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

    if entropy_log:
        import json
        (out_dir / "c2r_entropy_log.json").write_text(
            json.dumps(entropy_log, indent=2)
        )
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
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.3)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--alpha-c2r", dest="alpha_c2r", type=float, default=0.0,
                    help="S3-a additive boundary weight. 0.0 = canonical-J equivalent.")
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
