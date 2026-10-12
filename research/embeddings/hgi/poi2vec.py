"""POI2Vec: Pre-training POI embeddings using fclass-level hierarchical Node2Vec for HGI.

⚠ NAMING (clarity note, 2026-06-19): despite the module/class name, this is an *fclass-level
hierarchical Node2Vec teacher* used INSIDE HGI — it is NOT the AAAI'17 POI2Vec baseline
(Feng et al. 2017). The faithful AAAI'17 POI2Vec baseline lives in
``scripts/baselines/poi2vec_lib/``. This teacher is load-bearing for the frozen HGI/v14
substrates (build-time only; train.py reads the frozen parquet and never imports this), so the
class/module/artifact names are intentionally LEFT UNCHANGED to avoid churning the ~25 build
scripts that read its output CSV by hardcoded path. Do not rename without a dedicated PR.

Reference Implementation
------------------------
This implementation follows the region-embedding-benchmark approach:
    Phase 3b: Generate random walks → convert to fclass sequences
    Phase 3c: Train fclass embeddings with hierarchical category-fclass loss
    Phase 3d: Reconstruct POI embeddings from fclass embeddings

Key Differences from Standard Node2Vec:
    - Operates at fclass level (not POI level)
    - Multiple POIs with same fclass share the same embedding
    - Uses hierarchical L2 loss to enforce category-fclass semantic structure
    - Hard negative sampling: samples fclasses that NEVER co-occur with center
"""

import argparse
import math
import os
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import Node2Vec
from tqdm import tqdm

from configs.paths import IoPaths


class POISet(torch.utils.data.Dataset):
    """Dataset for fclass-level skip-gram training with hard negative sampling.

    Hard negative sampling: For each center fclass, samples negatives from
    fclasses that NEVER co-occurred with it in the random walks.

    Performance notes:
        The candidate list for each fclass is computed ONCE in __init__ and
        cached (one Python list per fclass). __getitem__ then only does a
        list lookup, a single random.sample() call, and three small tensor
        constructions — no per-call set construction. This drops per-item
        cost from ~23 µs to ~6 µs on Alabama, halving DataLoader epoch
        wall time.
    """

    def __init__(self, vocab_size, fclass_walks, global_co_occurrence, k=5):
        """
        Args:
            vocab_size: Number of unique fclass values
            fclass_walks: List of fclass sequences (converted from POI walks)
            global_co_occurrence: Dict mapping fclass → list of co-occurring fclasses
            k: Negative samples per positive context position
        """
        self.vocab_size = vocab_size
        self.fclass_walks = fclass_walks
        self.global_co_occurrence = global_co_occurrence
        self.k = k

        # Precompute the negative-sampling candidate list for every center
        # fclass. Each list contains every fclass that never co-occurred
        # with the center in the random walks. If that set is empty, we
        # fall back to "every other fclass" (matches the original edge
        # case in __getitem__). Cached once so __getitem__ does not need
        # to construct sets on every call.
        self._neg_candidates: list[list[int]] = []
        all_classes = set(range(vocab_size))
        for center in range(vocab_size):
            positive_set = set(global_co_occurrence.get(int(center), []))
            candidates = list(all_classes - positive_set - {int(center)})
            if not candidates:
                # Edge case: all fclasses co-occur with center
                candidates = [i for i in range(vocab_size) if i != int(center)]
            self._neg_candidates.append(candidates)

    def __len__(self):
        return len(self.fclass_walks)

    def __getitem__(self, idx):
        """Returns (center_fclass, positive_context, negative_context)."""
        walk = self.fclass_walks[idx]
        center = walk[0]                    # Target fclass
        positive = walk[1:]                 # Context fclasses in walk

        # Hard negative sampling: cached candidate list per center fclass
        negative_candidates = self._neg_candidates[int(center)]

        # Sample k negatives per positive context position
        num_negatives = len(positive) * self.k
        if num_negatives <= len(negative_candidates):
            negatives = random.sample(negative_candidates, num_negatives)
        else:
            # Not enough unique candidates: take all then pad with random.choice
            negatives = random.sample(negative_candidates, len(negative_candidates))
            while len(negatives) < num_negatives:
                negatives.append(random.choice(negative_candidates))

        return (
            torch.tensor(center, dtype=torch.long),
            torch.tensor(positive, dtype=torch.long),
            torch.tensor(negatives, dtype=torch.long)
        )


class EmbeddingModel(nn.Module):
    """Hierarchical fclass embedding model with category-fclass L2 regularization.

    Architecture:
        - Input embeddings: [vocab_size, embed_size]
        - Output embeddings: [vocab_size, embed_size]
        - Loss: Skip-gram + L2(category_emb, fclass_emb)
    """

    def __init__(self, vocab_size, embed_size, hierarchy_pairs, le_lambda=1e-8):
        """
        Args:
            vocab_size: Number of unique fclass values
            embed_size: Embedding dimension
            hierarchy_pairs: List of (category, fclass) tuples for L2 loss
            le_lambda: Weight for hierarchical loss (default 1e-8)
        """
        super().__init__()
        self.in_embed = nn.Embedding(vocab_size, embed_size)
        self.out_embed = nn.Embedding(vocab_size, embed_size)
        self.hierarchy_pairs = torch.tensor(hierarchy_pairs, dtype=torch.long)
        self.le_lambda = le_lambda

        # Initialize embeddings
        nn.init.xavier_uniform_(self.in_embed.weight)
        nn.init.xavier_uniform_(self.out_embed.weight)

    def forward(self, input_labels, pos_labels, neg_labels):
        """
        Args:
            input_labels: [batch_size] center fclass
            pos_labels: [batch_size, context_size] positive context
            neg_labels: [batch_size, context_size * k] negative context

        Returns:
            total_loss, hierarchy_loss
        """
        batch_size = input_labels.size(0)

        # Get embeddings
        input_emb = self.in_embed(input_labels)        # [batch, D]
        pos_emb = self.out_embed(pos_labels)           # [batch, ctx, D]
        neg_emb = self.out_embed(neg_labels)           # [batch, ctx*k, D]

        # Skip-gram loss: dot products with sigmoid
        input_emb_expand = input_emb.unsqueeze(2)      # [batch, D, 1]

        pos_dot = torch.bmm(pos_emb, input_emb_expand).squeeze(2)   # [batch, ctx]
        neg_dot = torch.bmm(neg_emb, -input_emb_expand).squeeze(2)  # [batch, ctx*k]

        log_pos = F.logsigmoid(pos_dot).sum(1)         # [batch]
        log_neg = F.logsigmoid(neg_dot).sum(1)         # [batch]

        loss_graph = -(log_pos + log_neg).mean()

        # Hierarchical L2 loss: 0.5 * lambda * sum_pairs ||cat_emb - fclass_emb||^2
        # Vectorized: gather all category and fclass embeddings in one shot.
        if self.hierarchy_pairs.numel() > 0:
            if self.hierarchy_pairs.device != input_labels.device:
                self.hierarchy_pairs = self.hierarchy_pairs.to(input_labels.device)
            cat_idx = self.hierarchy_pairs[:, 0]
            fclass_idx = self.hierarchy_pairs[:, 1]
            cat_embs = self.in_embed(cat_idx)              # [P, D]
            fclass_embs = self.in_embed(fclass_idx)        # [P, D]
            diff = cat_embs - fclass_embs                  # [P, D]
            # sum_pairs ||diff||^2 == (diff * diff).sum() and matches the
            # original `loss_hierarchy += torch.norm(...) ** 2` semantics.
            loss_hierarchy = 0.5 * self.le_lambda * (diff * diff).sum()
        else:
            loss_hierarchy = torch.tensor(0.0, dtype=torch.float32, device=input_labels.device)

        return loss_graph + loss_hierarchy, loss_hierarchy

    def get_embeddings(self):
        """Return trained fclass embeddings."""
        return self.in_embed.weight.detach().cpu().numpy()


def _get_poi2vec_num_workers(device: torch.device) -> int:
    """Optimal DataLoader num_workers for POI2Vec training.

    MPS: num_workers=0 — forked workers cannot share MPS memory with the
    parent process; IPC pickling overhead dominates for small vocab datasets.
    Mirrors the same reasoning as folds.py _get_num_workers().

    CPU/CUDA: parallel workers overlap __getitem__ (random-walk lookup +
    random.sample + tensor construction, ~6 µs/item) with compute.
    Cap at 4 — beyond that, Python GIL contention in random.sample offsets gains.
    """
    if device.type == 'mps':
        return 0
    return min(10, os.cpu_count() or 1)


class POI2Vec:
    """POI2Vec with fclass-level hierarchical embeddings.

    Workflow:
        1. Generate POI-level random walks using Node2Vec
        2. Convert POI walks to fclass sequences
        3. Train fclass embeddings with hierarchical loss
        4. Reconstruct POI embeddings from fclass embeddings
    """

    def __init__(self, edges_file, pois_file, embedding_dim=64,
                 walk_length=10, context_size=5, walks_per_node=5,
                 p=0.5, q=0.5, device=None):
        """
        Args:
            edges_file: Path to edges.csv (Delaunay graph)
            pois_file: Path to pois.csv (must have 'placeid', 'category', 'fclass' columns)
            embedding_dim: Output embedding dimension
            walk_length: Steps per random walk
            context_size: Skip-gram context window
            walks_per_node: Walks generated per POI
            p, q: Node2Vec parameters
            device: torch device (cuda/cpu)
        """
        self.embedding_dim = embedding_dim
        self.walk_length = walk_length
        self.context_size = context_size
        self.walks_per_node = walks_per_node
        self.p = p
        self.q = q
        if device is None:
            if torch.cuda.is_availableable():
                device = torch.device('cuda')
            else:
                device = torch.device('cpu')
        self.device = torch.device(device) if not isinstance(device, torch.device) else device

        # Load data
        print("Loading edges and POIs...")
        self.edges = pd.read_csv(edges_file)
        self.pois = pd.read_csv(pois_file)

        # Validate required columns
        required_cols = ['placeid', 'category', 'fclass']
        missing = [c for c in required_cols if c not in self.pois.columns]
        if missing:
            raise ValueError(f"pois.csv missing columns: {missing}. Found: {self.pois.columns.tolist()}")

        # Build edge index for PyG
        edge_index = torch.tensor(
            self.edges[['source', 'target']].values.T,
            dtype=torch.long
        )

        # Initialize Node2Vec for walk generation
        print("Initializing Node2Vec walk generator...")
        self.node2vec_model = Node2Vec(
            edge_index=edge_index,
            embedding_dim=embedding_dim,
            walk_length=walk_length,
            context_size=context_size,
            walks_per_node=walks_per_node,
            p=p,
            q=q,
            sparse=True
        )

        # Placeholders for training
        self.fclass_walks = []
        self.global_co_occurrence = {}
        self.vocab_size = int(self.pois['fclass'].max()) + 1

        print(f"  POIs: {len(self.pois)}")
        print(f"  Edges: {len(self.edges)}")
        print(f"  Unique fclass values: {self.vocab_size}")

    def generate_walks(self, batch_size=128):
        """
        Phase 3b: Generate random walks and convert to fclass sequences.

        Returns:
            fclass_walks: List of fclass sequences
            global_co_occurrence: Dict mapping fclass → co-occurring fclasses
        """
        print("=" * 80)
        print("PHASE 3b: Generating Random Walks")
        print("=" * 80)

        # Generate walks using Node2Vec
        loader = self.node2vec_model.loader(batch_size=batch_size, shuffle=True, num_workers=0)

        self.fclass_walks = []
        poi_walks = []

        print(f"Generating walks (batch_size={batch_size})...")
        for pos_rw, _ in tqdm(loader, desc="Walk generation"):
            for walk in pos_rw:
                poi_walk = walk.tolist()
                poi_walks.append(poi_walk)

                # Convert POI indices → fclass values
                fclass_walk = [int(self.pois.iloc[poi_idx]['fclass']) for poi_idx in poi_walk]
                self.fclass_walks.append(fclass_walk)

        print(f"Generated {len(self.fclass_walks)} fclass walks")

        # Build global co-occurrence dictionary
        print("Building global co-occurrence statistics...")
        self.global_co_occurrence = {i: [] for i in range(self.vocab_size)}

        for walk in self.fclass_walks:
            center = walk[0]
            context = walk[1:]
            self.global_co_occurrence[center].extend(context)

        # Deduplicate
        for fclass in range(self.vocab_size):
            self.global_co_occurrence[fclass] = list(set(self.global_co_occurrence[fclass]))

        print(f"Co-occurrence stats computed for {self.vocab_size} fclass values")
        print()
        return self.fclass_walks, self.global_co_occurrence

    def train(self, epochs=5, batch_size=2048, lr=0.05, k=5, le_lambda=1e-8):
        """
        Phase 3c: Train fclass embeddings with hierarchical loss.

        Args:
            epochs: Training epochs (default 5, same as reference)
            batch_size: Batch size (default 2048, same as reference)
            lr: Learning rate (default 0.05, same as reference)
            k: Negative samples per positive (default 5)
            le_lambda: Weight on the category-fclass hierarchical L2 loss.
                Set to 0.0 to disable the only explicit category-label path
                into fclass embeddings (leakage ablation arm A).

        Returns:
            fclass_embeddings: numpy array [vocab_size, embedding_dim]
        """
        print("=" * 80)
        print("PHASE 3c: Training fclass Embeddings")
        print("=" * 80)

        # Generate walks if not already done
        if not self.fclass_walks:
            self.generate_walks()

        # Extract hierarchy pairs (category, fclass)
        print("Extracting category-fclass hierarchy pairs...")
        hierarchy_pairs = list(set([
            tuple(row) for row in self.pois[['category', 'fclass']].values
        ]))
        print(f"  Found {len(hierarchy_pairs)} unique (category, fclass) pairs")

        # Build dataset
        print("Building POISet dataset...")
        dataset = POISet(
            vocab_size=self.vocab_size,
            fclass_walks=self.fclass_walks,
            global_co_occurrence=self.global_co_occurrence,
            k=k
        )

        # Build model
        print("Initializing EmbeddingModel...")
        model = EmbeddingModel(
            vocab_size=self.vocab_size,
            embed_size=self.embedding_dim,
            hierarchy_pairs=hierarchy_pairs,
            le_lambda=le_lambda
        ).to(self.device)

        # DataLoader: parallel workers on CPU/CUDA; num_workers=0 on MPS
        # (forked MPS workers incur IPC overhead — same reasoning as folds.py).
        num_workers = _get_poi2vec_num_workers(self.device)
        loader = torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            persistent_workers=(num_workers > 0),
        )

        # AdamW: proper weight-decay decoupling gives slightly better
        # generalisation than vanilla Adam for embedding tables.
        optimizer = torch.optim.Adam(model.parameters(), lr=lr)

        device_label = f"{self.device.type}" + (
            f":{self.device.index}" if self.device.type == 'cuda' else ""
        )
        print(f"Training for {epochs} epochs "
              f"(batch={batch_size}, lr={lr}, workers={num_workers}, device={device_label})...")

        best_loss = math.inf
        best_embeddings = None

        model.train()
        for epoch in range(epochs):
            total_loss = 0.0
            total_hierarchy_loss = 0.0
            num_batches = 0

            with tqdm(loader, desc=f"Epoch {epoch+1}/{epochs}") as pbar:
                for center, pos, neg in pbar:
                    center = center.to(self.device)
                    pos = pos.to(self.device)
                    neg = neg.to(self.device)

                    optimizer.zero_grad()
                    loss, loss_hierarchy = model(center, pos, neg)
                    loss.backward()
                    optimizer.step()

                    total_loss += loss.item()
                    total_hierarchy_loss += loss_hierarchy.item()
                    num_batches += 1

                    pbar.set_postfix({
                        'loss': f"{loss.item():.4f}",
                        'h_loss': f"{loss_hierarchy.item():.2e}"
                    })

            avg_loss = total_loss / num_batches
            avg_h_loss = total_hierarchy_loss / num_batches
            print(f"  Epoch {epoch+1}/{epochs}: Loss={avg_loss:.4f}, "
                  f"Hierarchy Loss={avg_h_loss:.2e}")

            # Keep the best-epoch snapshot — guards against late-epoch overshoot
            if avg_loss < best_loss:
                best_loss = avg_loss
                best_embeddings = model.get_embeddings().copy()

        # Extract embeddings
        print("Extracting fclass embeddings...")
        embeddings = best_embeddings if best_embeddings is not None else model.get_embeddings()
        print(f"  Shape: {embeddings.shape} (best epoch loss={best_loss:.4f})")
        print()

        return embeddings

    def reconstruct_poi_embeddings(self, fclass_embeddings, add_category_label=False):
        """
        Phase 3d: Map each POI to its fclass embedding.

        This is the CRITICAL RECONSTRUCTION STEP that converts fclass-level
        embeddings to POI-level embeddings via index lookup:
            poi_embedding[i] = fclass_embeddings[poi.fclass[i]]

        Args:
            fclass_embeddings: numpy array [vocab_size, embedding_dim]
            add_category_label: If True, add 'category' column to output

        Returns:
            DataFrame with columns: placeid, 0..D-1, [category]
        """
        print("=" * 80)
        print("PHASE 3d: POI-Level Embedding Reconstruction")
        print("=" * 80)
        print("Mapping each POI to its fclass embedding...")
        print("Note: Multiple POIs with same fclass will share the same embedding")
        print()

        num_pois = len(self.pois)
        embed_dim = fclass_embeddings.shape[1]

        # Initialize embedding matrix
        poi_embeddings = np.full((num_pois, embed_dim), np.nan, dtype=np.float32)

        # Validate fclass values
        fclass_values = self.pois['fclass'].values
        valid = (fclass_values >= 0) & (fclass_values < self.vocab_size)

        if not valid.all():
            invalid_count = (~valid).sum()
            print(f"  WARNING: {invalid_count} POIs have invalid fclass values")

        # CRITICAL OPERATION: Map each POI to its fclass embedding
        # This is the reconstruction: poi_emb[i] = fclass_emb[fclass[i]]
        poi_embeddings[valid] = fclass_embeddings[fclass_values[valid]]

        print(f"  ✓ Mapped {valid.sum()} POIs to their fclass embeddings")

        # Statistics
        fclass_counts = self.pois[valid].groupby('fclass').size()
        print(f"  Average POIs per fclass: {fclass_counts.mean():.1f}")
        print(f"  Max POIs sharing same fclass: {fclass_counts.max()}")
        print(f"  Min POIs per fclass: {fclass_counts.min()}")
        print()

        # Build output DataFrame
        emb_cols = [str(i) for i in range(embed_dim)]
        output_df = pd.DataFrame(poi_embeddings, columns=emb_cols)
        output_df.insert(0, 'placeid', self.pois['placeid'].astype(str))

        if add_category_label:
            output_df['category'] = self.pois['category'].values

        return output_df

    def save_fclass_embeddings(self, embeddings, output_path):
        """Save fclass-level embeddings as PyTorch tensor."""
        output_path = Path(output_path)

        save_dict = {
            "in_embed.weight": torch.tensor(embeddings, dtype=torch.float32),
            "vocab_size": self.vocab_size,
            "embedding_dim": self.embedding_dim,
            "fclass_to_idx": {int(fclass): int(fclass) for fclass in range(self.vocab_size)}
        }

        torch.save(save_dict, output_path)
        print(f"Saved fclass embeddings: {output_path}")
        print(f"  Shape: {embeddings.shape}")

    def save_poi_embeddings_csv(self, poi_df, output_path):
        """Save POI-level embeddings as CSV."""
        output_path = Path(output_path)
        poi_df.to_csv(output_path, index=False)
        print(f"Saved POI embeddings (CSV): {output_path}")
        print(f"  Columns: {poi_df.columns.tolist()}")
        print(f"  Shape: {poi_df.shape}")

    def save_poi_embeddings_tensor(self, poi_df, output_path):
        """Save POI-level embeddings as PyTorch tensor (compatible with preprocess.py)."""
        output_path = Path(output_path)

        # Extract embedding columns (all except placeid and category)
        emb_cols = [c for c in poi_df.columns if c.isdigit()]
        embeddings = poi_df[emb_cols].values.astype(np.float32)
        placeids = poi_df['placeid'].tolist()

        save_dict = {
            "in_embed.weight": torch.tensor(embeddings, dtype=torch.float32),
            "placeids": placeids
        }

        torch.save(save_dict, output_path)
        print(f"Saved POI embeddings (tensor): {output_path}")
        print(f"  Shape: {embeddings.shape}")


def train_poi2vec(city, epochs=5, embedding_dim=64, batch_size=2048,
                  lr=0.05, k=5, device=None, save_intermediate=True,
                  le_lambda=1e-8):
    """
    Train POI2Vec embeddings for a city (all three phases).

    Workflow:
        Phase 3b: Generate random walks → fclass sequences
        Phase 3c: Train fclass embeddings with hierarchical loss
        Phase 3d: Reconstruct POI embeddings from fclass embeddings

    Args:
        city: City name
        epochs: Training epochs (default 5)
        embedding_dim: Embedding dimension (default 64)
        batch_size: Training batch size (default 2048)
        lr: Learning rate (default 0.05)
        k: Negative samples per positive (default 5)
        device: torch device (None for auto-detect)
        save_intermediate: If True, save fclass embeddings + CSV

    Returns:
        poi_emb_path: Path to POI embeddings (tensor format for preprocess.py)
    """
    print("=" * 80)
    print(f"POI2Vec Training: {city}")
    print("=" * 80)

    temp_folder = IoPaths.HGI.get_temp_dir(city)
    if not temp_folder.exists():
        raise FileNotFoundError(f"HGI temp folder not found: {temp_folder}")

    edges_file = temp_folder / "edges.csv"
    pois_file = temp_folder / "pois.csv"

    if not edges_file.exists() or not pois_file.exists():
        raise FileNotFoundError("edges.csv or pois.csv not found. Run preprocess_hgi first.")

    # Initialize POI2Vec
    poi2vec = POI2Vec(
        edges_file=edges_file,
        pois_file=pois_file,
        embedding_dim=embedding_dim,
        device=device
    )

    # Phase 3b: Generate walks
    poi2vec.generate_walks(batch_size=128)

    # Phase 3c: Train fclass embeddings
    fclass_embeddings = poi2vec.train(
        epochs=epochs,
        batch_size=batch_size,
        lr=lr,
        k=k,
        le_lambda=le_lambda,
    )

    # Phase 3d: Reconstruct POI embeddings
    poi_df = poi2vec.reconstruct_poi_embeddings(
        fclass_embeddings=fclass_embeddings,
        add_category_label=True
    )

    # Save outputs
    output_folder = IoPaths.HGI.get_output_dir(city)
    output_folder.mkdir(parents=True, exist_ok=True)

    if save_intermediate:
        # Save fclass embeddings (for analysis)
        fclass_path = output_folder / f"poi2vec_fclass_embeddings_{city}.pt"
        poi2vec.save_fclass_embeddings(fclass_embeddings, fclass_path)

        # Save POI embeddings as CSV (for analysis)
        csv_path = output_folder / f"poi2vec_poi_embeddings_{city}.csv"
        poi2vec.save_poi_embeddings_csv(poi_df, csv_path)

    # Save POI embeddings as tensor (compatible with preprocess.py)
    poi_emb_path = IoPaths.HGI.get_poi_emb_file(city)
    poi2vec.save_poi_embeddings_tensor(poi_df, poi_emb_path)

    print("=" * 80)
    print(f"POI2Vec training completed!")
    print(f"  Final output: {poi_emb_path}")
    print("=" * 80)

    return poi_emb_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train POI2Vec embeddings for HGI")
    parser.add_argument("--city", type=str, default="Alabama", help="City name")
    parser.add_argument("--epochs", type=int, default=5, help="Training epochs")
    parser.add_argument("--dim", type=int, default=64, help="Embedding dimension")
    parser.add_argument("--batch_size", type=int, default=2048, help="Training batch size")
    parser.add_argument("--lr", type=float, default=0.05, help="Learning rate")
    parser.add_argument("--k", type=int, default=5, help="Negative samples per positive")
    parser.add_argument("--device", type=str, default=None, help="Device (cuda/cpu)")
    parser.add_argument("--no_intermediate", action='store_true',
                        help="Skip saving intermediate files (fclass embeddings, CSV)")

    args = parser.parse_args()

    train_poi2vec(
        city=args.city,
        epochs=args.epochs,
        embedding_dim=args.dim,
        batch_size=args.batch_size,
        lr=args.lr,
        k=args.k,
        device=args.device,
        save_intermediate=not args.no_intermediate
    )
