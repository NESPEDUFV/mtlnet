"""Train one Check2HGI variant on Alabama and evaluate via a sequence-aware
linear probe on next-category prediction.

Designed to be cheap (~5 min/run on a single GPU) so we can compare 5+ variants
across 3 seeds and still finish in under an hour.

The linear probe is the proxy for downstream MTLnet category quality:
- For each (current_checkin, next_checkin_same_user), predict next.category
  from current.embedding.
- Multinomial logistic regression with L2.
- 5-fold cross-validation, stratified by userid (user-disjoint folds).
- Reports macro-F1 + accuracy.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F

from torch_geometric.data import Data
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# project imports
_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from embeddings.check2hgi.model.Check2HGIModule import Check2HGI, corruption  # noqa: E402
from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder  # noqa: E402
from embeddings.check2hgi.model.Checkin2POI import Checkin2POI  # noqa: E402
from embeddings.hgi.model.RegionEncoder import POI2Region  # noqa: E402
from embeddings.check2hgi.model.variants import (  # noqa: E402
    GATTimeEncoder,
    ResidualLNEncoder,
    Check2HGI_InfoNCE,
    Check2HGI_Uncertainty,
    Check2HGI_Combined,
)


VARIANTS = [
    "baseline",       # V0: original Check2HGI
    "infonce",        # V1: InfoNCE multi-negative at C2P
    "gat_time",       # V2: GATv2 time-aware encoder
    "skip_ln",        # V3: residual + LayerNorm encoder
    "uncertainty",    # V4: learnable Kendall-style alphas
    "combined",       # V5: skip+LN encoder + InfoNCE + uncertainty
    "combined_gat",   # V6: GAT encoder + InfoNCE + uncertainty
    "infonce_tuned",  # V1+: InfoNCE with K=256, T=0.1 (SOTA-tuned)
    "gat_infonce",    # V7: GAT encoder + InfoNCE (no uncertainty)
]


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_data(state: str, device: str) -> tuple[Data, dict]:
    p = _root / "output" / "check2hgi" / state.lower() / "temp" / "checkin_graph.pt"
    with open(p, "rb") as f:
        cd = pickle.load(f)
    data = Data(
        x=torch.tensor(cd["node_features"], dtype=torch.float32),
        edge_index=torch.tensor(cd["edge_index"], dtype=torch.int64),
        edge_weight=torch.tensor(cd["edge_weight"], dtype=torch.float32),
        checkin_to_poi=torch.tensor(cd["checkin_to_poi"], dtype=torch.int64),
        poi_to_region=torch.tensor(cd["poi_to_region"], dtype=torch.int64),
        region_adjacency=torch.tensor(cd["region_adjacency"], dtype=torch.int64),
        region_area=torch.tensor(cd["region_area"], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(
            cd["coarse_region_similarity"], dtype=torch.float32
        ),
        num_pois=cd["num_pois"],
        num_regions=cd["num_regions"],
    ).to(device)
    return data, cd


def build_model(variant: str, in_channels: int, dim: int, heads: int, num_layers: int,
                alpha=(0.4, 0.3, 0.3), num_negatives=32, temperature=0.2,
                infonce_chunk_size: int | None = None):
    """Build a Check2HGI variant. Returns (model, encoder_kind)."""
    if variant in ("gat_time", "combined_gat", "gat_infonce"):
        ce = GATTimeEncoder(in_channels, dim, num_layers=num_layers, heads=heads)
    elif variant in ("skip_ln",):
        ce = ResidualLNEncoder(in_channels, dim, num_layers=max(num_layers, 3))
    elif variant == "combined":
        # V5 uses skip+LN encoder by default
        ce = ResidualLNEncoder(in_channels, dim, num_layers=3)
    else:
        ce = CheckinEncoder(in_channels, dim, num_layers=num_layers)

    c2p = Checkin2POI(dim, heads)
    p2r = POI2Region(dim, heads)

    def r2c(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    a_c2p, a_p2r, a_r2c = alpha

    if variant in ("infonce", "infonce_tuned", "gat_infonce"):
        # SOTA-tuned: K=256, T=0.1 for infonce_tuned; K=num_negatives, T=temperature otherwise
        if variant == "infonce_tuned":
            K, T = 256, 0.1
        else:
            K, T = num_negatives, temperature
        m = Check2HGI_InfoNCE(
            hidden_channels=dim, checkin_encoder=ce, checkin2poi=c2p, poi2region=p2r,
            region2city=r2c, corruption=corruption,
            alpha_c2p=a_c2p, alpha_p2r=a_p2r, alpha_r2c=a_r2c,
            num_negatives=K, temperature=T, chunk_size=infonce_chunk_size,
        )
    elif variant == "uncertainty":
        m = Check2HGI_Uncertainty(
            hidden_channels=dim, checkin_encoder=ce, checkin2poi=c2p, poi2region=p2r,
            region2city=r2c, corruption=corruption,
            alpha_c2p=a_c2p, alpha_p2r=a_p2r, alpha_r2c=a_r2c,
        )
    elif variant in ("combined", "combined_gat"):
        m = Check2HGI_Combined(
            hidden_channels=dim, checkin_encoder=ce, checkin2poi=c2p, poi2region=p2r,
            region2city=r2c, corruption=corruption,
            alpha_c2p=a_c2p, alpha_p2r=a_p2r, alpha_r2c=a_r2c,
            num_negatives=num_negatives, temperature=temperature,
        )
    else:
        m = Check2HGI(
            hidden_channels=dim, checkin_encoder=ce, checkin2poi=c2p, poi2region=p2r,
            region2city=r2c, corruption=corruption,
            alpha_c2p=a_c2p, alpha_p2r=a_p2r, alpha_r2c=a_r2c,
        )
    return m


def train_embedding(model, data, epochs, lr, max_norm, device, log_every=50, amp_dtype=None):
    optim = torch.optim.Adam(model.parameters(), lr=lr)
    losses = []
    best = (math.inf, 0, None)
    use_amp = amp_dtype is not None and device == "cuda"
    if use_amp:
        print(f"  [amp] using torch.autocast(cuda, dtype={amp_dtype})")
    for ep in range(1, epochs + 1):
        model.train()
        optim.zero_grad()
        if use_amp:
            with torch.autocast(device_type="cuda", dtype=amp_dtype):
                out = model(data)
                loss = model.loss(*out)
        else:
            out = model(data)
            loss = model.loss(*out)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_norm)
        optim.step()
        v = float(loss.item())
        losses.append(v)
        if not math.isfinite(v):
            raise RuntimeError(f"NaN/Inf loss at epoch {ep}")
        if v < best[0]:
            best = (v, ep, {k: t.detach().clone() for k, t in model.state_dict().items()})
        if ep % log_every == 0 or ep == 1 or ep == epochs:
            print(f"  ep {ep:4d}/{epochs}  loss={v:.4f}  best={best[0]:.4f}@{best[1]}")
    model.load_state_dict(best[2])
    return losses, best[1], best[0]


@torch.no_grad()
def extract_embeddings(model, data) -> np.ndarray:
    model.eval()
    _ = model(data)
    chk, _, _ = model.get_embeddings()
    return chk.cpu().numpy()


@torch.no_grad()
def extract_all_embeddings(model, data):
    """Return (checkin, poi, region) numpy arrays.

    Used by UP3 to dump region/POI embeddings as parquet alongside the
    check-in embeddings, so the variant's region embeddings can stand in
    for the baseline check2hgi region_embeddings.parquet in the F21c
    next-region apparatus.
    """
    model.eval()
    _ = model(data)
    chk, poi, reg = model.get_embeddings()
    return chk.cpu().numpy(), poi.cpu().numpy(), reg.cpu().numpy()


def build_eval_pairs(metadata: pd.DataFrame, embeddings: np.ndarray, cat_to_id: dict | None = None):
    """For each user, build (current_emb, next_category) pairs."""
    df = metadata.copy().reset_index(drop=True)
    df["emb_idx"] = np.arange(len(df))
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    df["next_category"] = df.groupby("userid")["category"].shift(-1)
    df = df.dropna(subset=["next_category"]).reset_index(drop=True)

    if cat_to_id is None:
        cats = sorted(df["category"].unique())
        cat_to_id = {c: i for i, c in enumerate(cats)}
    df["next_cat_id"] = df["next_category"].map(cat_to_id)

    X = embeddings[df["emb_idx"].values]
    y = df["next_cat_id"].values.astype(np.int64)
    groups = df["userid"].values
    return X, y, groups, cat_to_id


def linear_probe_cv(X: np.ndarray, y: np.ndarray, groups: np.ndarray, k: int = 5, seed: int = 42):
    """User-disjoint K-fold logistic regression. Returns per-fold + mean metrics."""
    folds = list(GroupKFold(n_splits=k).split(X, y, groups=groups))
    f1s, accs = [], []
    for fold_i, (tr, te) in enumerate(folds):
        clf = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(
                max_iter=200, C=1.0, n_jobs=1, solver="lbfgs",
                random_state=seed,
            )),
        ])
        clf.fit(X[tr], y[tr])
        pred = clf.predict(X[te])
        f1 = f1_score(y[te], pred, average="macro")
        acc = accuracy_score(y[te], pred)
        f1s.append(float(f1)); accs.append(float(acc))
    return {
        "f1_per_fold": f1s,
        "acc_per_fold": accs,
        "f1_mean": float(np.mean(f1s)),
        "f1_std": float(np.std(f1s)),
        "acc_mean": float(np.mean(accs)),
        "acc_std": float(np.std(accs)),
    }


def run_one(variant: str, seed: int, state: str, epochs: int, dim: int, heads: int,
            lr: float, max_norm: float, num_negatives: int, temperature: float,
            out_dir: Path, device: str = "cuda", log_every: int = 50,
            infonce_chunk_size: int | None = None, amp_dtype=None):
    set_seed(seed)
    data, cd = load_data(state, device)
    in_channels = data.x.size(1)
    metadata = cd["metadata"]

    print(f"\n[{variant} seed={seed}] start  ({state}, "
          f"checkins={cd['num_checkins']}, pois={cd['num_pois']}, regions={cd['num_regions']})")
    t0 = time.time()
    model = build_model(
        variant, in_channels, dim, heads, num_layers=2,
        alpha=(0.4, 0.3, 0.3), num_negatives=num_negatives, temperature=temperature,
        infonce_chunk_size=infonce_chunk_size,
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())

    losses, best_ep, best_loss = train_embedding(
        model, data, epochs=epochs, lr=lr, max_norm=max_norm, device=device, log_every=log_every,
        amp_dtype=amp_dtype,
    )
    embeddings, poi_embeddings, region_embeddings = extract_all_embeddings(model, data)
    train_time = time.time() - t0
    print(f"[{variant} seed={seed}] trained in {train_time:.1f}s, best_ep={best_ep}, best_loss={best_loss:.4f}")
    print(f"[{variant} seed={seed}] embeddings: chk={embeddings.shape}, "
          f"poi={poi_embeddings.shape}, region={region_embeddings.shape}")

    # Eval
    X, y, groups, _ = build_eval_pairs(metadata, embeddings)
    probe = linear_probe_cv(X, y, groups, k=5, seed=seed)
    print(f"[{variant} seed={seed}] probe: f1_macro={probe['f1_mean']:.4f}±{probe['f1_std']:.4f}  "
          f"acc={probe['acc_mean']:.4f}±{probe['acc_std']:.4f}")

    # Persist
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "variant": variant,
        "seed": seed,
        "state": state,
        "epochs": epochs,
        "dim": dim,
        "heads": heads,
        "lr": lr,
        "max_norm": max_norm,
        "n_params": n_params,
        "best_epoch": best_ep,
        "best_loss": best_loss,
        "train_time_s": train_time,
        "linear_probe": probe,
        "loss_curve": losses,
    }
    if variant in ("infonce", "combined"):
        result["num_negatives"] = num_negatives
        result["temperature"] = temperature

    fname = f"{state.lower()}_{variant}_seed{seed}_ep{epochs}.json"
    with open(out_dir / fname, "w") as f:
        json.dump(result, f, indent=2)

    # Also save the embeddings parquet (small) so we can reuse without retraining
    emb_path = out_dir / f"{state.lower()}_{variant}_seed{seed}_ep{epochs}_emb.parquet"
    df = pd.DataFrame(embeddings, columns=[str(i) for i in range(embeddings.shape[1])])
    df.insert(0, "datetime", metadata["datetime"].values)
    df.insert(0, "category", metadata["category"].values)
    df.insert(0, "placeid", metadata["placeid"].values)
    df.insert(0, "userid", metadata["userid"].values)
    df.to_parquet(emb_path, index=False)

    # UP3: dump region and POI embeddings in the schema p1_region_head_ablation
    # expects so they can swap in for output/check2hgi/{state}/region_embeddings.parquet
    # (cols: region_id, reg_0..reg_{D-1}; sorted by region_id).
    region_path = out_dir / f"{state.lower()}_{variant}_seed{seed}_ep{epochs}_region_emb.parquet"
    region_df = pd.DataFrame(
        region_embeddings,
        columns=[f"reg_{i}" for i in range(region_embeddings.shape[1])],
    )
    region_df.insert(0, "region_id", np.arange(region_embeddings.shape[0], dtype=np.int64))
    region_df.to_parquet(region_path, index=False)

    poi_path = out_dir / f"{state.lower()}_{variant}_seed{seed}_ep{epochs}_poi_emb.parquet"
    poi_df = pd.DataFrame(
        poi_embeddings,
        columns=[f"poi_{i}" for i in range(poi_embeddings.shape[1])],
    )
    poi_df.insert(0, "poi_idx", np.arange(poi_embeddings.shape[0], dtype=np.int64))
    poi_df.to_parquet(poi_path, index=False)

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=VARIANTS)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--state", default="Alabama")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--heads", type=int, default=4)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--max_norm", type=float, default=0.9)
    ap.add_argument("--num_negatives", type=int, default=32)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--out_dir", default="docs/results/UP1")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--log_every", type=int, default=50)
    ap.add_argument("--infonce_chunk_size", type=int, default=None,
                    help="Chunk size for InfoNCE neg sampling. None = no chunking. "
                         "Set to e.g. 262144 for FL on a 6 GB GPU.")
    ap.add_argument("--amp", choices=["bf16", "fp16", "none"], default="none",
                    help="Mixed-precision dtype for forward/loss. bf16 is the "
                         "safe choice on Ampere+ GPUs (RTX 30/40); fp16 needs "
                         "loss scaling not implemented here.")
    args = ap.parse_args()
    amp_dtype_map = {"bf16": torch.bfloat16, "fp16": torch.float16, "none": None}
    amp_dtype = amp_dtype_map[args.amp]

    out_dir = Path(args.out_dir)
    run_one(
        variant=args.variant, seed=args.seed, state=args.state, epochs=args.epochs,
        dim=args.dim, heads=args.heads, lr=args.lr, max_norm=args.max_norm,
        num_negatives=args.num_negatives, temperature=args.temperature,
        out_dir=out_dir, device=args.device, log_every=args.log_every,
        infonce_chunk_size=args.infonce_chunk_size, amp_dtype=amp_dtype,
    )


if __name__ == "__main__":
    main()
