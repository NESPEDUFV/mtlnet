"""Design B — Check2HGI with POI2Vec injected at the POI-pool boundary.

Canonical 11-dim input (NOT POI2Vec-augmented). Encoder is identical to
canonical c2hgi. POI2Vec enters AFTER ``Checkin2POI`` as a detached additive
residual that only the reg path sees.

Critical property: cat path is byte-identical in gradient-flow to canonical
c2hgi. The encoder receives gradient only from L_c2p (computed against the
non-detached canonical poi_emb). The L_p2r and L_r2c gradients flow through
the POI2Vec residual + POI2Region but stop at the detach() before reaching
encoder weights.

Design discriminator (vs Design E which failed): input features are NOT
augmented. The 75-dim mix is what killed Design E's cat — POI-static
features in input propagated through GCN regardless of gradient routing.

Architecture::

    checkin_emb        = CheckinEncoder(canonical_11_dim, ...)        # active grad
    poi_emb_canonical  = Checkin2POI(checkin_emb, ...)                # active grad
    poi_emb_for_reg    = poi_emb_canonical.detach() + γ·Linear(POI2Vec_for_poi)
    region_emb         = POI2Region(poi_emb_for_reg, ...)
    city_emb           = region2city(region_emb)

Loss boundaries::

    L_c2p uses (checkin_emb, poi_emb_canonical)   ← exactly canonical c2hgi
    L_p2r uses (poi_emb_for_reg, region_emb_exp)  ← reg path only
    L_r2c uses (region_emb, city_emb)             ← reg path only

POI2Vec is loaded frozen from HGI's pre-trained
``poi2vec_poi_embeddings_<State>.csv`` (64-dim per placeid).

Outputs to ``output/check2hgi_design_b/<state>/``:
  - embeddings.parquet       (per-check-in, from canonical encoder — cat-grade)
  - poi_embeddings.parquet   (per-POI from poi_emb_for_reg — fclass-aware)
  - region_embeddings.parquet (reg-grade)

Usage::

    python scripts/probe/build_design_b_poi_pool.py --state alabama --epochs 500
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
from embeddings.check2hgi.model.variants import ResidualLNEncoder
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI
from embeddings.hgi.model.RegionEncoder import POI2Region
# v13 mechanism now lives in the canonical module (reg_poi_mode='poi2vec_residual').
# The loader is shared with check2hgi.py via reg_poi_aug.
from embeddings.check2hgi.reg_poi_aug import load_poi2vec_table


POI2VEC_DIM = 64


def train_design_b(state: str, args: argparse.Namespace) -> None:
    state_lc = state.lower()
    # Reproducibility: this is an unsupervised build with random encoder init +
    # random negatives, so the run is seed-dependent. Pin it (paper-grade builds
    # must be reproducible). Without this two runs give rotated/independent
    # solutions (verified 2026-06-02).
    seed = int(getattr(args, "seed", 42))
    torch.manual_seed(seed)
    np.random.seed(seed)
    # tier_resln: --encoder resln + --out-engine check2hgi_resln_design_b stacks
    # the ResidualLNEncoder onto Design B's POI2Vec-at-pool injection. Default
    # out-engine preserves canonical Design B behaviour byte-for-byte.
    out_engine = getattr(args, "out_engine", None) or "check2hgi_design_b"
    out_dir = REPO / "output" / out_engine / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    # Use the CANONICAL c2hgi graph (11-dim features), NOT the POI2Vec-augmented one.
    graph_path = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(graph_path, "rb") as f:
        d = pickle.load(f)

    in_channels = d["node_features"].shape[1]
    num_checkins = d["num_checkins"]
    num_pois = d["num_pois"]
    num_regions = d["num_regions"]
    print(f"[{state_lc}] checkins={num_checkins} pois={num_pois} regions={num_regions} "
          f"feature_dim={in_channels} (canonical 11-dim — NOT augmented)")

    device = torch.device(args.device)

    poi2vec_table = load_poi2vec_table(state, num_pois, d["placeid_to_idx"])

    # v13+sidefeat: optionally load the T4.3 32-d POI side-feature tensor.
    side_features = None
    if getattr(args, "use_side_features", False):
        sf_path = REPO / "output" / "check2hgi" / state_lc / "poi_side_features.pt"
        if not sf_path.exists():
            print(f"[{state_lc}] computing POI side-features → {sf_path}")
            import subprocess
            r = subprocess.run(
                [sys.executable, str(REPO / "scripts/canonical_improvement/compute_poi_side_features.py"),
                 "--state", state],
                cwd=str(REPO), env={**__import__("os").environ, "PYTHONPATH": f"{REPO}/src:{REPO}/research"})
            if r.returncode != 0:
                raise RuntimeError(f"compute_poi_side_features.py failed rc={r.returncode}")
        sf = torch.load(sf_path)
        side_features = sf["features"] if isinstance(sf, dict) else sf
        if side_features.shape[0] != num_pois:
            raise ValueError(f"side_features rows {side_features.shape[0]} != num_pois {num_pois}")
        print(f"[{state_lc}] side_features attached shape={tuple(side_features.shape)}")

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
    # v13+sidefeat: attach side features so the canonical T4.3 post-pool path
    # (built when side_feature_dim > 0) operates on poi_emb_for_reg.
    if side_features is not None:
        data.side_features = side_features.float()
    data = data.to(device)

    metadata = d["metadata"]

    # tier_resln: encoder switch. Default 'gcn' = canonical CheckinEncoder
    # (byte-identical to prior Design B). 'resln' = ResidualLNEncoder, whose
    # forward(x, edge_index, edge_weight, **kwargs) signature matches
    # CheckinEncoder exactly (verified variants.py:482) so the call site
    # `self.checkin_encoder(data.x, data.edge_index, data.edge_weight)` in
    # Check2HGI_DesignB.forward needs no adaptation. num_layers pinned to the
    # CLI value (default 2) per the canonical_improvement T3.2 recipe pin.
    _encoder = getattr(args, "encoder", "gcn") or "gcn"
    if _encoder == "resln":
        checkin_encoder = ResidualLNEncoder(in_channels, args.dim, num_layers=args.num_layers)
        print(f"[{state_lc}] encoder=ResidualLNEncoder num_layers={args.num_layers}")
    else:
        checkin_encoder = CheckinEncoder(in_channels, args.dim, num_layers=args.num_layers)
        print(f"[{state_lc}] encoder=CheckinEncoder (canonical GCN) num_layers={args.num_layers}")
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
        # v13 — graduated reg-path POI2Vec residual (was Check2HGI_DesignB).
        reg_poi_mode="poi2vec_residual",
        gamma_init=args.gamma_init,
        poi2vec_table=poi2vec_table,
        side_feature_dim=(int(side_features.shape[1]) if side_features is not None else 0),
        side_feature_hidden=args.side_feature_hidden,
    ).to(device)
    print(f"[{state_lc}] params={sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)
    scheduler = StepLR(optimizer, step_size=1, gamma=args.gamma) if args.gamma != 1.0 else None

    t = trange(1, args.epochs + 1, desc=f"Train Design B [{state_lc}]")
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

    print(f"[{state_lc}] best_epoch={best_epoch} loss={lowest:.4f} gamma={model.reg_gamma.item():.3f}")
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
    import shutil
    shutil.copy(graph_path, out_dir / "temp" / "checkin_graph.pt")
    src_seq = REPO / f"output/check2hgi/{state_lc}/temp/sequences_next.parquet"
    if src_seq.exists():
        shutil.copy(src_seq, out_dir / "temp" / "sequences_next.parquet")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--seed", type=int, default=42,
                    help="Reproducibility seed (encoder init + negatives). Pinned by default.")
    ap.add_argument("--epochs", type=int, default=500)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--num-layers", dest="num_layers", type=int, default=2)
    ap.add_argument("--attention-head", dest="attention_head", type=int, default=4)
    ap.add_argument("--alpha-c2p", dest="alpha_c2p", type=float, default=0.4)
    ap.add_argument("--alpha-p2r", dest="alpha_p2r", type=float, default=0.3)
    ap.add_argument("--alpha-r2c", dest="alpha_r2c", type=float, default=0.3)
    ap.add_argument("--gamma-init", dest="gamma_init", type=float, default=1.0,
                    help="Initial value of γ (POI2Vec residual scale).")
    ap.add_argument("--lr", type=float, default=0.001)
    ap.add_argument("--gamma", type=float, default=1.0)
    ap.add_argument("--max-norm", dest="max_norm", type=float, default=0.9)
    ap.add_argument("--device", type=str, default="cpu")
    ap.add_argument("--encoder", type=str, default="gcn", choices=["gcn", "resln"],
                    help="Check-in encoder. 'gcn' (default) = canonical CheckinEncoder; "
                         "'resln' = ResidualLNEncoder (tier_resln stack).")
    ap.add_argument("--use-side-features", dest="use_side_features", action="store_true",
                    help="v13+sidefeat: stack T4.3 POI side-features (32d) onto the "
                         "POI2Vec reg-path residual. Loads/computes poi_side_features.pt.")
    ap.add_argument("--side-feature-hidden", dest="side_feature_hidden", type=int, default=16,
                    help="Hidden dim of the side-feature projection (matches T4.3).")
    ap.add_argument("--out-engine", dest="out_engine", type=str, default=None,
                    help="Output engine dir under output/ (default check2hgi_design_b). "
                         "tier_resln uses check2hgi_resln_design_b.")
    args = ap.parse_args()
    train_design_b(args.state, args)


if __name__ == "__main__":
    main()
