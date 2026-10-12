"""
Space2Vec: Spatial contrastive learning for location embeddings.

This module trains a Space2Vec model using contrastive learning on
spatial proximity pairs and generates location embeddings for POIs.
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from configs.globals import DEVICE
from configs.model import InputsConfig
from configs.paths import IoPaths, EmbeddingEngine
from embeddings.space2vec.model.SpaceEncoder import SpaceContrastiveModel
from embeddings.space2vec.model.dataset import (
    PairsMemmapDataset,
    build_pairs_memmap,
    to_xy_km,
)

# Check if AMP is available (CUDA only, not MPS)
AMP_AVAILABLE = torch.cuda.is_available()

# Check if torch.compile is available (PyTorch 2.0+)
COMPILE_AVAILABLE = hasattr(torch, "compile") and sys.version_info >= (3, 8)


def worker_init_fn(worker_id: int):
    """Initialize each worker with a unique seed."""
    worker_seed = torch.initial_seed() % 2**32 + worker_id
    np.random.seed(worker_seed)


def train_epoch(
    model: SpaceContrastiveModel,
    dataloader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    tau: float,
    precomputed_xy: bool = True,
    max_grad_norm: float = 1.0,
    loss_type: str = "bce",
    use_amp: bool = False,
    scaler: torch.cuda.amp.GradScaler = None,
) -> float:
    """
    Train for one epoch.

    Args:
        model: SpaceContrastiveModel instance
        dataloader: Training data loader
        optimizer: Optimizer instance
        device: Device for training
        tau: Temperature for contrastive loss
        precomputed_xy: If True, coordinates are already in XY km format
        max_grad_norm: Maximum gradient norm for clipping
        loss_type: Loss function type - "bce" or "infonce"
        use_amp: Whether to use Automatic Mixed Precision (CUDA only)
        scaler: GradScaler for AMP (required if use_amp=True)

    Returns:
        Average loss for the epoch
    """
    model.train()
    total_loss = 0.0
    n_batches = 0

    # Use autocast context manager only for CUDA with AMP
    amp_context = torch.cuda.amp.autocast() if use_amp else torch.autocast(device_type="cpu", enabled=False)

    for coord_i, coord_j, label in dataloader:
        if precomputed_xy:
            # Coordinates are already in XY km format
            XY_i = coord_i.float()
            XY_j = coord_j.float()
        else:
            # Convert to numpy for coordinate transformation
            ci = coord_i.numpy()
            cj = coord_j.numpy()

            # Convert lat/lon to XY in kilometers
            XY_i = torch.from_numpy(to_xy_km(ci)).float()
            XY_j = torch.from_numpy(to_xy_km(cj)).float()

        # Compute deltas and add noise for augmentation
        deltas_km = (XY_j - XY_i).to(device)
        noise = torch.randn_like(deltas_km) * 0.01

        optimizer.zero_grad()

        # Forward pass with AMP if enabled
        with amp_context:
            z_i = model(deltas_km + noise)
            z_j = model(deltas_km - noise)
            loss = model.contrastive_loss(z_i, z_j, label.to(device), tau=tau, loss_type=loss_type)

        if use_amp and scaler is not None:
            # AMP backward pass
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
            scaler.step(optimizer)
            scaler.update()
        else:
            # Standard backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=max_grad_norm)
            optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / max(n_batches, 1)


def create_embedding(state: str, args):
    """
    Train Space2Vec model and generate embeddings for a state.

    Args:
        state: State name
        args: Command line arguments with training parameters
    """
    # Setup output directories
    output_folder = IoPaths.SPACE2VEC.get_state_dir(state)
    output_folder.mkdir(parents=True, exist_ok=True)

    pairs_dir = IoPaths.SPACE2VEC.get_pairs_dir(state)
    pairs_dir.mkdir(parents=True, exist_ok=True)

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

    # Extract coordinates and metadata (with optional deduplication)
    if args.deduplicate:
        # Deduplicate to unique places - dramatically reduces memory for large datasets
        original_count = len(checkins)
        checkins_unique = checkins.drop_duplicates(subset=["placeid"])
        coords = checkins_unique[["latitude", "longitude"]].values.astype(np.float32)
        categories = checkins_unique["category"].astype(str).values
        placeids = checkins_unique["placeid"].astype(str).values
        print(f"Deduplicated: {original_count:,} checkins -> {len(coords):,} unique places")
    else:
        # Original behavior: use all checkins
        coords = checkins[["latitude", "longitude"]].values.astype(np.float32)
        categories = checkins["category"].astype(str).values
        placeids = checkins["placeid"].astype(str).values

    print(f"Coordinates shape: {coords.shape}")

    # Generate spatial proximity pairs
    pairs_count_file = pairs_dir / "pairs_count.npy"
    if pairs_count_file.exists() and not args.force_pairs:
        print(f"Loading existing pairs from: {pairs_dir}")
        n_pairs = int(np.load(pairs_count_file)[0])
    else:
        print("Generating spatial proximity pairs...")
        n_pairs = build_pairs_memmap(
            coords_deg=coords,
            out_dir=pairs_dir,
            max_pairs=args.max_pairs,
            r_pos_km=args.r_pos_km,
            r_neg_km=args.r_neg_km,
            k_pos_per_i=args.k_pos_per_i,
            k_neg_per_i=args.k_neg_per_i,
            block=args.block_size,
            seed=args.seed,
            hard_neg_ratio=args.hard_neg_ratio,
        )

    print(f"Total pairs: {n_pairs}")

    # Create dataset and dataloader with precomputed XY coordinates
    dataset = PairsMemmapDataset(coords, pairs_dir, precompute_xy=True)
    num_workers = min(8, os.cpu_count() or 1)
    dataloader = DataLoader(
        dataset,
        batch_size=args.batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=num_workers,
        persistent_workers=True if num_workers > 0 else False,
        prefetch_factor=4 if num_workers > 0 else None,
        worker_init_fn=worker_init_fn,
    )

    # Initialize model
    encoder_type = "PyTorch" if args.use_torch_encoder else "numpy"
    print(
        f"Initializing model: embed_dim={args.dim}, spa_embed_dim={args.spa_embed_dim}, "
        f"freq_num={args.freq_num}, encoder={encoder_type}, loss={args.loss_type}"
    )

    model = SpaceContrastiveModel(
        embed_dim=args.dim,
        spa_embed_dim=args.spa_embed_dim,
        coord_dim=2,
        frequency_num=args.freq_num,
        max_radius=args.max_radius,
        min_radius=args.min_radius,
        ffn_act="leakyrelu",
        freq_init="geometric",
        ffn_num_hidden_layers=1,
        ffn_dropout_rate=0.5,
        ffn_use_layernormalize=True,
        ffn_skip_connection=True,
        ffn_hidden_dim=512,
        device=str(args.device),
        use_torch_encoder=args.use_torch_encoder,
    ).to(args.device)

    # Optional: Compile model for faster execution (PyTorch 2.0+)
    if args.compile and COMPILE_AVAILABLE:
        print("Compiling model with torch.compile()...")
        model = torch.compile(model)
    elif args.compile and not COMPILE_AVAILABLE:
        print("Warning: torch.compile() not available, skipping compilation")

    optimizer = torch.optim.Adam(model.parameters(), lr=args.lr)

    # Learning rate scheduler: cosine annealing for better convergence
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=args.epoch, eta_min=1e-6
    )

    # Setup AMP (Automatic Mixed Precision) - CUDA only
    use_amp = args.amp and AMP_AVAILABLE and args.device.type == "cuda"
    scaler = torch.cuda.amp.GradScaler() if use_amp else None
    if args.amp and not use_amp:
        print("Warning: AMP requested but not available (requires CUDA). Training in FP32.")
    elif use_amp:
        print("Using Automatic Mixed Precision (AMP) for faster training")

    # Training loop
    print(f"Training for {args.epoch} epochs on {args.device}...")
    bar = tqdm(range(1, args.epoch + 1), desc="Training")

    for epoch in bar:
        avg_loss = train_epoch(
            model,
            dataloader,
            optimizer,
            args.device,
            args.tau,
            precomputed_xy=True,
            max_grad_norm=args.max_grad_norm,
            loss_type=args.loss_type,
            use_amp=use_amp,
            scaler=scaler,
        )
        scheduler.step()
        current_lr = scheduler.get_last_lr()[0]
        bar.set_postfix(loss=f"{avg_loss:.4f}", lr=f"{current_lr:.2e}")

    # Save trained model
    model_path = IoPaths.SPACE2VEC.get_model_file(state)
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to: {model_path}")

    # Generate embeddings for all coordinates
    # NOTE: The notebook uses raw lat/lon coordinates for embedding generation,
    # even though training uses XY deltas. We match this for compatibility.
    print("Generating embeddings...")
    model.eval()

    # Process in batches for memory efficiency
    batch_size = 10000
    all_embeddings = []

    with torch.no_grad():
        for start in tqdm(range(0, len(coords), batch_size), desc="Embedding"):
            end = min(start + batch_size, len(coords))
            batch_coords = coords[start:end]

            # Use raw lat/lon coordinates (same as notebook cell 14)
            batch_tensor = torch.from_numpy(batch_coords).float().to(args.device)

            embeddings = model.encode(batch_tensor).cpu().numpy()
            all_embeddings.append(embeddings)

    embeddings = np.vstack(all_embeddings)

    # Save embeddings
    output_path = IoPaths.get_embedd(state, EmbeddingEngine.SPACE2VEC)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(embeddings, columns=[f"{i}" for i in range(embeddings.shape[1])])
    df.insert(0, "placeid", placeids)
    df.insert(1, "category", categories)
    df.to_parquet(output_path, index=False)

    print(f"Embeddings saved to: {output_path}")
    print(f"Embedding dimensions: {embeddings.shape}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create Space2Vec embeddings for POI data"
    )
    parser.add_argument(
        "--state", type=str, default="Texas", help="State name for processing"
    )
    parser.add_argument(
        "--dim",
        type=int,
        default=InputsConfig.EMBEDDING_DIM,
        help="Dimension of output embedding",
    )
    parser.add_argument(
        "--spa_embed_dim",
        type=int,
        default=128,
        help="Spatial encoder hidden dimension",
    )
    parser.add_argument(
        "--freq_num", type=int, default=16, help="Number of frequency bands"
    )
    parser.add_argument(
        "--max_radius",
        type=float,
        default=50,
        help="Max radius for position encoding",
    )
    parser.add_argument(
        "--min_radius",
        type=float,
        default=0.02,
        help="Min radius for position encoding",
    )
    parser.add_argument(
        "--epoch", type=int, default=40, help="Number of training epochs"
    )
    parser.add_argument("--batch_size", type=int, default=256, help="Batch size")
    parser.add_argument("--lr", type=float, default=3e-4, help="Learning rate")
    parser.add_argument(
        "--r_pos_km",
        type=float,
        default=10.0,
        help="Positive pair radius in kilometers",
    )
    parser.add_argument(
        "--r_neg_km",
        type=float,
        default=70.0,
        help="Negative pair minimum distance in kilometers",
    )
    parser.add_argument(
        "--k_pos_per_i", type=int, default=8, help="Max positive pairs per anchor"
    )
    parser.add_argument(
        "--k_neg_per_i", type=int, default=16, help="Max negative pairs per anchor"
    )
    parser.add_argument(
        "--hard_neg_ratio",
        type=float,
        default=0.0,
        help="Fraction of negatives from 'hard' zone (r_neg to 2*r_neg). Default 0.0 (disabled)",
    )
    parser.add_argument(
        "--max_pairs", type=int, default=None, help="Maximum pairs to generate"
    )
    parser.add_argument(
        "--tau", type=float, default=0.15, help="Temperature for contrastive loss"
    )
    parser.add_argument(
        "--max_grad_norm",
        type=float,
        default=1.0,
        help="Maximum gradient norm for clipping",
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--device",
        type=str,
        default=str(DEVICE),
        help="Device to use for training (cpu, cuda, mps)",
    )
    parser.add_argument(
        "--force_pairs",
        action="store_true",
        help="Force regeneration of pairs even if they exist",
    )
    parser.add_argument(
        "--use_torch_encoder",
        action="store_true",
        default=True,
        help="Use pure PyTorch encoder (faster, default). Use --no_torch_encoder for numpy version.",
    )
    parser.add_argument(
        "--no_torch_encoder",
        action="store_true",
        help="Use numpy-based encoder (slower but notebook compatible)",
    )
    parser.add_argument(
        "--loss_type",
        type=str,
        default="bce",
        choices=["bce", "infonce"],
        help="Loss function: 'bce' (original) or 'infonce' (standard contrastive)",
    )
    parser.add_argument(
        "--block_size",
        type=int,
        default=5000,
        help="Block size for bulk BallTree queries during pair generation (default: 5000)",
    )
    parser.add_argument(
        "--amp",
        action="store_true",
        help="Enable Automatic Mixed Precision (AMP) for faster CUDA training. "
             "Ignored on CPU/MPS devices.",
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Enable torch.compile() for faster execution (PyTorch 2.0+ required)",
    )
    parser.add_argument(
        "--deduplicate",
        action="store_true",
        default=True,
        help="Deduplicate to unique places before processing. "
             "Dramatically reduces memory and time for large datasets (e.g., 4M -> 155K for Texas).",
    )

    args = parser.parse_args()

    # Handle torch encoder flag
    if args.no_torch_encoder:
        args.use_torch_encoder = False

    # Convert device string to torch device
    args.device = torch.device(args.device)

    create_embedding(state=args.state, args=args)
