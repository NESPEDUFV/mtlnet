"""
Sphere2Vec (sphereM): contrastive spherical-RBF location embeddings.

This module trains a `SphereLocationContrastiveModel` on per-checkin
coordinates, then forward-passes all checkins and aggregates per `placeid`
(mean over the model's embeddings) to produce POI-level embeddings.

The training distribution is per-checkin (not deduplicated), to faithfully
match the source notebook. Because the model is a pure function of `(lat, lon)`
the per-POI mean is mathematically equal to the per-coord embedding (modulo
a deterministic forward pass), so the output for a given POI is identical to
what you would get from a deduplicated forward pass.
"""

import argparse
import os
import random
import sys

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from configs.globals import DEVICE
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths
from embeddings.sphere2vec.model.Sphere2VecModule import (
    SphereLocationContrastiveModel,
    contrastive_bce,
)
from embeddings.sphere2vec.model.dataset import (
    ContrastiveSpatialDataset,
    FastContrastiveSpatialDataset,
)


def seed_everything(seed: int) -> None:
    """Seed Python, NumPy and PyTorch RNGs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _worker_init_fn(worker_id: int) -> None:
    """
    Per-worker RNG seeding for `DataLoader` workers.

    The dataset uses the global `np.random` (verbatim port from the notebook).
    Without this hook, child workers inherit a copy of the parent state at
    fork time, then never update it — so every worker draws from the same
    pre-fork sequence. Seeding from `torch.initial_seed()` (which DataLoader
    derives deterministically from `args.seed` via `torch.manual_seed`) gives
    each worker a unique but reproducible stream.
    """
    worker_seed = (torch.initial_seed() + worker_id) % (2 ** 32)
    np.random.seed(worker_seed)
    random.seed(worker_seed)


def _to_torch_device(device) -> torch.device:
    if isinstance(device, torch.device):
        return device
    return torch.device(str(device))


def _identity_collate(batch):
    """Passthrough collator: returns whatever __getitems__ produced verbatim.

    Used with `FastContrastiveSpatialDataset.__getitems__`, which already
    emits a fully batched ``(coord_i, coord_j, label)`` tuple. The default
    `torch.utils.data.default_collate` would otherwise try to ``torch.stack``
    the three tensors and fail on the mismatched shapes.
    """
    return batch


def train_epoch(
    model: SphereLocationContrastiveModel,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    tau: float,
) -> float:
    """Train for one epoch and return the average loss."""
    model.train()
    total_loss = 0.0
    n_batches = 0

    for coord_i, coord_j, label in dataloader:
        ci = coord_i.float().to(device)
        cj = coord_j.float().to(device)

        z_i = model(ci)
        z_j = model(cj)

        loss = contrastive_bce(z_i, z_j, label, tau=tau)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1)


def create_embedding(state: str, args) -> None:
    """
    Train Sphere2Vec on a state's check-ins and write a POI-level
    `embeddings.parquet`.

    Args:
        state: State name (used for I/O routing via ``IoPaths.SPHERE2VEC``).
        args: ``argparse.Namespace``-like object with the model + training
            hyperparameters listed in the CLI section below.
    """
    # Resolve device early
    device = _to_torch_device(args.device)

    # Setup output directories
    output_folder = IoPaths.SPHERE2VEC.get_state_dir(state)
    output_folder.mkdir(parents=True, exist_ok=True)

    # Seed everything for reproducibility (notebook had no seeds — we add it)
    seed_everything(int(args.seed))

    # Load check-ins
    checkins_path = IoPaths.get_city(state)
    print(f"Loading check-ins from: {checkins_path}")
    checkins = pd.read_parquet(checkins_path)
    print(f"Loaded {len(checkins)} check-ins")

    # Validate required columns
    required_cols = ["latitude", "longitude", "category", "placeid"]
    for col in required_cols:
        if col not in checkins.columns:
            raise ValueError(f"Required column missing: {col}")

    # Faithful to notebook: train on per-checkin coords (no dedup)
    coords = (
        checkins[["latitude", "longitude"]].values.astype(np.float32)
    )
    placeids = checkins["placeid"].astype(str).values
    categories = checkins["category"].astype(str).values
    print(f"Coordinates shape: {coords.shape}")

    # Build dataset + dataloader.
    #
    # `legacy_dataset=False` (default) uses the vectorized
    # FastContrastiveSpatialDataset which implements __getitems__ for
    # batched fetch — ~5–10× faster epoch times at large batch sizes.
    # Statistically equivalent to the per-item version (same Bernoulli
    # positive ratio, same Gaussian noise scale, same uniform negative
    # sampling) but produces a different per-batch sample sequence.
    #
    # Set `legacy_dataset=True` for bit-exact equivalence with the source
    # notebook's per-item __getitem__ (used by the equivalence test in
    # tests/test_embeddings/test_sphere2vec.py).
    use_legacy_dataset = bool(getattr(args, "legacy_dataset", False))
    if use_legacy_dataset:
        dataset = ContrastiveSpatialDataset(coords, pos_radius=args.pos_radius)
        # Default collate_fn handles the per-item path (3 scalar tensors → 3 stacked tensors)
        collate_fn = None
    else:
        dataset = FastContrastiveSpatialDataset(coords, pos_radius=args.pos_radius)
        # FastContrastiveSpatialDataset.__getitems__ already returns a fully
        # batched (coord_i, coord_j, label) tuple, so the DataLoader needs a
        # passthrough collator — the default collator would otherwise try to
        # `torch.stack` the 3 tensors against each other and fail on the
        # mismatched shapes ([B,2] vs [B,2] vs [B]).
        collate_fn = _identity_collate

    num_workers = int(getattr(args, "num_workers", 2))
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=num_workers,
        drop_last=True,
        worker_init_fn=_worker_init_fn if num_workers > 0 else None,
        # `persistent_workers` keeps the worker processes alive across
        # epochs (avoids re-fork on every epoch). At small batch sizes
        # this is the difference between 33s warmup and 5s warmup.
        persistent_workers=(num_workers > 0),
        collate_fn=collate_fn,
    )
    print(f"Total batches per epoch: {len(dataloader)}")

    # Initialize model
    encoder_variant = str(getattr(args, "encoder_variant", "rbf")).lower()
    if encoder_variant not in {"rbf", "paper"}:
        raise ValueError(
            f"--encoder-variant must be 'rbf' or 'paper', got {encoder_variant!r}"
        )
    model = SphereLocationContrastiveModel(
        embed_dim=args.dim,
        spa_embed_dim=args.spa_embed_dim,
        num_scales=args.num_scales,
        min_scale=args.min_scale,
        max_scale=args.max_scale,
        num_centroids=args.num_centroids,
        ffn_hidden_dim=args.ffn_hidden_dim,
        ffn_num_hidden_layers=args.ffn_num_hidden_layers,
        ffn_dropout_rate=args.ffn_dropout_rate,
        ffn_act=args.ffn_act,
        ffn_use_layernormalize=args.ffn_use_layernormalize,
        ffn_skip_connection=args.ffn_skip_connection,
        device=str(device),
        encoder_variant=encoder_variant,
        min_radius=getattr(args, "min_radius", None),
        max_radius=getattr(args, "max_radius", None),
    ).to(device)
    print(f"Encoder variant: {encoder_variant}")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Training loop
    print(f"Training for {args.epoch} epochs on {device}...")
    bar = tqdm(range(1, args.epoch + 1), desc="Training")
    for _ in bar:
        avg_loss = train_epoch(
            model, dataloader, optimizer, device, tau=args.tau
        )
        bar.set_postfix(loss=f"{avg_loss:.4f}")

    # Save trained model state_dict
    model_path = IoPaths.SPHERE2VEC.get_model_file(state)
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to: {model_path}")

    # Generate embeddings for all check-ins.
    #
    # FAITHFUL TO NOTEBOOK: the source notebook (cell 12) calls
    #     loc_embeds = model(torch.Tensor(coords))
    # without `model.eval()` and without `torch.no_grad()`. This means the
    # FFN's two `nn.Dropout(p=0.5)` layers are ACTIVE during inference, so
    # each forward pass on the same coordinate yields a different embedding.
    # The downstream `groupby+mean` step partially averages out this noise.
    #
    # We deliberately preserve this behavior (rather than calling
    # `model.eval()`) so that the migrated package's output matches the
    # source. To get deterministic embeddings instead, set
    # `args.eval_inference = True`. Defaults to False to match the notebook.
    eval_inference = bool(getattr(args, "eval_inference", False))
    if eval_inference:
        print("Generating embeddings (eval mode, dropout disabled)...")
        model.eval()
        no_grad_ctx = torch.no_grad()
    else:
        print("Generating embeddings (train mode, dropout active — matches notebook)...")
        # Stay in whatever mode the training loop left us in (train mode).
        # No `no_grad` context: notebook builds the autograd graph here too.
        from contextlib import nullcontext
        no_grad_ctx = nullcontext()

    eval_batch_size = int(getattr(args, "eval_batch_size", 10000))
    all_embeddings = []
    with no_grad_ctx:
        for start in tqdm(range(0, len(coords), eval_batch_size), desc="Embedding"):
            end = min(start + eval_batch_size, len(coords))
            batch = torch.from_numpy(coords[start:end]).float().to(device)
            # `.detach()` is required because the notebook's call path keeps
            # autograd alive (no `no_grad`); `.numpy()` would error otherwise.
            embeddings = model(batch).detach().cpu().numpy()
            all_embeddings.append(embeddings)
    embeddings = np.vstack(all_embeddings)

    # Build per-checkin DataFrame, then collapse to per-POI via groupby+mean
    embed_dim = embeddings.shape[1]
    embed_cols = [f"{i}" for i in range(embed_dim)]
    df_checkin = pd.DataFrame(embeddings, columns=embed_cols)
    df_checkin.insert(0, "placeid", placeids)
    df_checkin["category"] = categories

    # Mean of per-checkin embeddings per POI.
    # NOTE: `sort=True` (pandas default) matches notebook cell 14 — rows are
    # ordered by `placeid` ascending. We make this explicit for clarity.
    df_mean_embeds = (
        df_checkin
        .groupby("placeid", sort=True)[embed_cols]
        .mean()
        .reset_index()
    )

    # Mode of per-checkin categories per POI (matches notebook cell 14).
    df_mode_cat = (
        df_checkin
        .groupby("placeid", sort=True)["category"]
        .agg(lambda s: s.mode().iat[0] if not s.mode().empty else s.iloc[0])
        .reset_index()
    )

    df_final = df_mean_embeds.merge(df_mode_cat, on="placeid")

    # DEVIATION FROM NOTEBOOK (intentional): the notebook ends with column
    # order [placeid, "0", ..., "63", category]. We reorder to
    # [placeid, category, "0", ..., "63"] to match the project convention
    # established by space2vec / hgi / poi2hgi (downstream consumers are
    # column-order agnostic, but human readers and other engines expect
    # `category` immediately after `placeid`).
    df_final = df_final[["placeid", "category", *embed_cols]]

    output_path = IoPaths.get_embedd(state, EmbeddingEngine.SPHERE2VEC)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_parquet(output_path, index=False)

    print(f"Embeddings saved to: {output_path}")
    print(f"Per-checkin embeddings: {df_checkin.shape}")
    print(f"Per-POI embeddings:     {df_final.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Sphere2Vec embeddings for POI data"
    )
    parser.add_argument("--state", type=str, default="Alabama")
    parser.add_argument(
        "--dim", type=int, default=InputsConfig.EMBEDDING_DIM,
        help="Output embedding dimensionality (final projector output)",
    )
    parser.add_argument("--spa_embed_dim", type=int, default=128)
    parser.add_argument("--num_scales", type=int, default=32)
    parser.add_argument("--min_scale", type=float, default=10)
    parser.add_argument("--max_scale", type=float, default=1e7)
    parser.add_argument("--num_centroids", type=int, default=256)
    parser.add_argument("--ffn_hidden_dim", type=int, default=512)
    parser.add_argument("--ffn_num_hidden_layers", type=int, default=1)
    parser.add_argument("--ffn_dropout_rate", type=float, default=0.5)
    parser.add_argument("--ffn_act", type=str, default="relu")
    parser.add_argument("--ffn_use_layernormalize", action="store_true", default=True)
    parser.add_argument("--ffn_skip_connection", action="store_true", default=True)
    parser.add_argument("--epoch", type=int, default=50)
    parser.add_argument(
        "--batch_size",
        type=int,
        default=4096,
        help="Default 4096 (~9× faster than notebook's 64 on MPS, no quality loss). "
             "Use --batch_size 64 with --legacy_dataset for canonical notebook reproduction.",
    )
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--tau", type=float, default=0.15)
    parser.add_argument("--pos_radius", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--num_workers", type=int, default=2)
    parser.add_argument("--eval_batch_size", type=int, default=10000)
    parser.add_argument("--device", type=str, default=str(DEVICE))
    parser.add_argument(
        "--legacy_dataset",
        action="store_true",
        help="Use the per-item ContrastiveSpatialDataset (notebook-faithful, slower). "
             "Default is the vectorized FastContrastiveSpatialDataset.",
    )
    parser.add_argument(
        "--eval_inference",
        action="store_true",
        help="Run final embedding pass with model.eval() + torch.no_grad() for "
             "deterministic outputs. Default is notebook-faithful (dropout active).",
    )
    parser.add_argument(
        "--encoder_variant",
        type=str,
        default="rbf",
        choices=["rbf", "paper"],
        help="Position encoder variant. 'rbf' (default, backward-compat) is the "
             "notebook's custom random-RBF-on-sphere encoder. 'paper' is the "
             "closed-form Eq.8 sphereM encoder from Mai et al. 2023 (the official "
             "SphereMixScaleSpatialRelationEncoder).",
    )
    parser.add_argument(
        "--min_radius",
        type=float,
        default=None,
        help="Paper-variant min_radius (upstream default: 10). Defaults to --min_scale if omitted.",
    )
    parser.add_argument(
        "--max_radius",
        type=float,
        default=None,
        help="Paper-variant max_radius (upstream default: 10000). Defaults to --max_scale if omitted.",
    )

    args = parser.parse_args()
    create_embedding(state=args.state, args=args)
