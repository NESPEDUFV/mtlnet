"""
Dataset classes and pair generation utilities for Space2Vec.

Contains functions for generating spatial proximity pairs using BallTree
and dataset classes for in-memory and memory-mapped pair storage.
"""

import time
from pathlib import Path
from typing import Tuple, Union

import numpy as np
from sklearn.neighbors import BallTree
from torch.utils.data import Dataset
from tqdm import tqdm

# Earth radius in kilometers
EARTH_RADIUS_KM = 6371.0


def latlon_to_radians(coords: np.ndarray) -> np.ndarray:
    """Convert latitude/longitude from degrees to radians."""
    return np.radians(coords.astype(np.float32))


def to_xy_km(latlon_deg: np.ndarray) -> np.ndarray:
    """
    Convert lat/lon degrees to approximate XY coordinates in kilometers.

    Uses a simple cylindrical projection suitable for local areas.

    Args:
        latlon_deg: Array of shape (B, 2) in degrees [lat, lon]

    Returns:
        Array of shape (B, 2) in kilometers [x, y]
    """
    lat = np.radians(latlon_deg[:, 0])
    lon = np.radians(latlon_deg[:, 1])
    x = EARTH_RADIUS_KM * lon * np.cos(np.mean(lat))
    y = EARTH_RADIUS_KM * lat
    return np.stack([x, y], axis=1)


def spatial_proximity_pairs_kdtree_fast(
    coords: np.ndarray,
    r_pos_km: float = 1.0,
    r_neg_km: float = 5.0,
    max_pairs: int = 50_000,
    k_neg_per_i: int = 5,
    max_pos_per_i: int = 5,
    seed: int = 42,
    leaf_size: int = 40,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate spatial proximity pairs using BallTree for efficient spatial queries.

    Positive pairs: locations within r_pos_km of each other
    Negative pairs: locations beyond r_neg_km from each other

    Args:
        coords: Lat/lon coordinates of shape (N, 2)
        r_pos_km: Positive pair radius in kilometers
        r_neg_km: Negative pair minimum distance in kilometers
        max_pairs: Maximum number of pairs to generate
        k_neg_per_i: Number of negative pairs per anchor
        max_pos_per_i: Maximum positive pairs per anchor
        seed: Random seed
        leaf_size: BallTree leaf size

    Returns:
        Tuple of (i_indices, j_indices, labels) as numpy arrays
    """
    rng = np.random.default_rng(seed)
    coords = np.asarray(coords, dtype=np.float32)
    N = coords.shape[0]
    coords_rad = latlon_to_radians(coords)

    r_pos_rad = r_pos_km / EARTH_RADIUS_KM
    r_neg_rad = r_neg_km / EARTH_RADIUS_KM

    tree = BallTree(coords_rad, metric="haversine", leaf_size=leaf_size)

    # Pre-allocate arrays
    i_arr = np.empty(max_pairs, dtype=np.int32)
    j_arr = np.empty(max_pairs, dtype=np.int32)
    y_arr = np.empty(max_pairs, dtype=np.uint8)

    pos_lists = tree.query_radius(coords_rad, r=r_pos_rad, return_distance=False)
    close_lists = tree.query_radius(coords_rad, r=r_neg_rad, return_distance=False)

    write = 0
    for i in range(N):
        if write >= max_pairs:
            break

        # Positive pairs
        pos_i = pos_lists[i]
        pos_i = pos_i[pos_i != i]
        if pos_i.size > 0:
            if pos_i.size > max_pos_per_i:
                pos_i = rng.choice(pos_i, size=max_pos_per_i, replace=False)
            m = min(pos_i.size, max_pairs - write)
            i_arr[write : write + m] = i
            j_arr[write : write + m] = pos_i[:m].astype(np.int32)
            y_arr[write : write + m] = 1
            write += m
            if write >= max_pairs:
                break

        # Negative pairs - vectorized sampling
        close_neighbors = close_lists[i]
        exclude_indices = np.append(close_neighbors, i)

        if write < max_pairs:
            valid_neg = np.setdiff1d(
                np.arange(N, dtype=np.int32), exclude_indices, assume_unique=False
            )

            if valid_neg.size > 0:
                n_neg = min(k_neg_per_i, valid_neg.size, max_pairs - write)
                neg_samples = rng.choice(valid_neg, size=n_neg, replace=False)
                i_arr[write : write + n_neg] = i
                j_arr[write : write + n_neg] = neg_samples
                y_arr[write : write + n_neg] = 0
                write += n_neg

    return i_arr[:write], j_arr[:write], y_arr[:write]


def build_pairs_memmap(
    coords_deg: np.ndarray,
    out_dir: Union[str, Path],
    max_pairs: int = None,
    r_pos_km: float = 1.0,
    r_neg_km: float = 20.0,
    k_pos_per_i: int = 5,
    k_neg_per_i: int = 5,
    block: int = 5_000,
    seed: int = 42,
    leaf_size: int = 40,
    verbose: bool = True,
    hard_neg_ratio: float = 0.0,
    streaming: bool = False,
) -> int:
    """
    Build spatial proximity pairs and store in memory-mapped files.

    Uses streaming single-point BallTree queries by default to minimize memory usage.
    For smaller datasets, set streaming=False for faster bulk queries.

    Args:
        coords_deg: Lat/lon coordinates in degrees, shape (N, 2)
        out_dir: Output directory for memmap files
        max_pairs: Maximum number of pairs to generate
        r_pos_km: Positive pair radius in kilometers
        r_neg_km: Negative pair minimum distance in kilometers
        k_pos_per_i: Maximum positive pairs per anchor
        k_neg_per_i: Maximum negative pairs per anchor
        block: Block size for progress updates (streaming) or bulk queries (non-streaming)
        seed: Random seed
        leaf_size: BallTree leaf size
        verbose: Whether to print progress
        hard_neg_ratio: Fraction of negatives to sample from "hard" zone
            (r_neg_km to 2*r_neg_km). Default 0.0 (disabled).
        streaming: If True, use memory-efficient streaming queries (default).
            If False, use faster bulk queries (higher memory usage).

    Returns:
        Number of pairs generated
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rng = np.random.default_rng(seed)
    coords_deg = np.asarray(coords_deg, dtype=np.float32)
    N = coords_deg.shape[0]
    coords_rad = np.radians(coords_deg)

    if max_pairs is None:
        max_pairs = N * (k_pos_per_i + k_neg_per_i)

    # Create memory-mapped files for pairs
    i_mm = np.memmap(
        out_dir / "pairs_i.int32", dtype=np.int32, mode="w+", shape=(max_pairs,)
    )
    j_mm = np.memmap(
        out_dir / "pairs_j.int32", dtype=np.int32, mode="w+", shape=(max_pairs,)
    )
    y_mm = np.memmap(
        out_dir / "pairs_y.uint8", dtype=np.uint8, mode="w+", shape=(max_pairs,)
    )
    wptr = 0

    # Create memory-mapped XY coordinates (avoids recomputing during training)
    xy_coords = to_xy_km(coords_deg)
    xy_mm = np.memmap(
        out_dir / "coords_xy.float32", dtype=np.float32, mode="w+", shape=(N, 2)
    )
    xy_mm[:] = xy_coords
    xy_mm.flush()
    del xy_coords  # Free memory

    r_pos = r_pos_km / EARTH_RADIUS_KM
    r_neg = r_neg_km / EARTH_RADIUS_KM
    r_hard_max = 2 * r_neg  # Hard negatives are in [r_neg, 2*r_neg]

    # Calculate how many hard vs random negatives per anchor
    use_hard_neg = hard_neg_ratio > 0
    k_hard_per_i = int(k_neg_per_i * hard_neg_ratio) if use_hard_neg else 0
    k_rand_per_i = k_neg_per_i - k_hard_per_i

    if verbose:
        print(f"Building BallTree for {N:,} points...")
        if use_hard_neg:
            print(f"Hard negative mining: {k_hard_per_i} hard + {k_rand_per_i} random per anchor")
        print(f"Mode: {'streaming (low memory)' if streaming else 'bulk (fast)'}")

    tree = BallTree(coords_rad, metric="haversine", leaf_size=leaf_size)

    # Progress bar for total points
    pbar = tqdm(total=N, desc="Generating pairs", disable=not verbose)

    # Create permutation for random access order to prevent spatial bias
    # when max_pairs is reached before iterating all points.
    order = np.arange(N)
    rng.shuffle(order)

    if streaming:
        # STREAMING MODE: Process one point at a time (low memory)
        for k in range(N):
            if wptr >= max_pairs:
                break
            
            i = order[k]

            # Query for this single point
            coord_i = coords_rad[i : i + 1]
            pos_neighbors = tree.query_radius(coord_i, r=r_pos, return_distance=False)[0]
            pos_neighbors = pos_neighbors[pos_neighbors != i]

            # Positive pairs
            if pos_neighbors.size > 0:
                if pos_neighbors.size > k_pos_per_i:
                    pos_neighbors = rng.choice(pos_neighbors, size=k_pos_per_i, replace=False)
                n = min(pos_neighbors.size, max_pairs - wptr)
                i_mm[wptr : wptr + n] = i
                j_mm[wptr : wptr + n] = pos_neighbors[:n]
                y_mm[wptr : wptr + n] = 1
                wptr += n

            if wptr >= max_pairs:
                break

            # Negative pairs using rejection sampling (O(1) memory per point)
            if wptr < max_pairs and k_rand_per_i > 0:
                # Query close neighbors only when needed
                close_neighbors = tree.query_radius(coord_i, r=r_neg, return_distance=False)[0]
                close_set = set(close_neighbors.tolist())
                close_set.add(i)

                # Hard negatives from [r_neg, 2*r_neg] zone
                if use_hard_neg and k_hard_per_i > 0:
                    hard_zone = tree.query_radius(coord_i, r=r_hard_max, return_distance=False)[0]
                    hard_candidates = [j for j in hard_zone if j not in close_set and j != i]
                    if hard_candidates:
                        n_hard = min(k_hard_per_i, len(hard_candidates), max_pairs - wptr)
                        hard_samples = rng.choice(hard_candidates, size=n_hard, replace=False)
                        i_mm[wptr : wptr + n_hard] = i
                        j_mm[wptr : wptr + n_hard] = hard_samples
                        y_mm[wptr : wptr + n_hard] = 0
                        wptr += n_hard

                # Random negatives using rejection sampling
                if wptr < max_pairs and k_rand_per_i > 0:
                    neg_count = 0
                    max_trials = k_rand_per_i * 50
                    trials = 0
                    while neg_count < k_rand_per_i and trials < max_trials and wptr < max_pairs:
                        j = rng.integers(0, N)
                        trials += 1
                        if j not in close_set:
                            i_mm[wptr] = i
                            j_mm[wptr] = j
                            y_mm[wptr] = 0
                            wptr += 1
                            neg_count += 1

            # Update progress
            if (k + 1) % block == 0 or k == N - 1:
                pbar.update(block if (k + 1) % block == 0 else (k + 1) % block)
                pbar.set_postfix(pairs=wptr)

    else:
        # BULK MODE: Process blocks of SHUFFLED indices
        for start in range(0, N, block):
            if wptr >= max_pairs:
                break

            end = min(start + block, N)
            # Get the actual indices for this block from the shuffled order
            block_indices = order[start:end]
            block_coords = coords_rad[block_indices]
            block_size = len(block_indices)

            # Bulk query for entire block
            pos_lists = tree.query_radius(block_coords, r=r_pos, return_distance=False)
            close_lists = tree.query_radius(block_coords, r=r_neg, return_distance=False)

            # Query for hard negatives zone if enabled
            if use_hard_neg:
                hard_zone_lists = tree.query_radius(
                    block_coords, r=r_hard_max, return_distance=False
                )

            # Process each point in the block
            for local_i in range(block_size):
                if wptr >= max_pairs:
                    break

                global_i = block_indices[local_i]

                # Positive pairs
                pos_neighbors = pos_lists[local_i]
                pos_neighbors = pos_neighbors[pos_neighbors != global_i]

                if pos_neighbors.size > 0:
                    if pos_neighbors.size > k_pos_per_i:
                        pos_neighbors = rng.choice(
                            pos_neighbors, size=k_pos_per_i, replace=False
                        )
                    n = min(pos_neighbors.size, max_pairs - wptr)
                    i_mm[wptr : wptr + n] = global_i
                    j_mm[wptr : wptr + n] = pos_neighbors[:n]
                    y_mm[wptr : wptr + n] = 1
                    wptr += n

                if wptr >= max_pairs:
                    break

                # Negative pairs using rejection sampling
                close_neighbors = close_lists[local_i]
                close_set = set(close_neighbors.tolist())
                close_set.add(global_i)

                if wptr < max_pairs:
                    # Hard negatives
                    if use_hard_neg and k_hard_per_i > 0:
                        hard_zone = hard_zone_lists[local_i]
                        hard_candidates = [j for j in hard_zone if j not in close_set]
                        if hard_candidates:
                            n_hard = min(k_hard_per_i, len(hard_candidates), max_pairs - wptr)
                            hard_samples = rng.choice(hard_candidates, size=n_hard, replace=False)
                            i_mm[wptr : wptr + n_hard] = global_i
                            j_mm[wptr : wptr + n_hard] = hard_samples
                            y_mm[wptr : wptr + n_hard] = 0
                            wptr += n_hard

                    # Random negatives using rejection sampling
                    if wptr < max_pairs and k_rand_per_i > 0:
                        neg_count = 0
                        max_trials = k_rand_per_i * 50
                        trials = 0
                        while neg_count < k_rand_per_i and trials < max_trials and wptr < max_pairs:
                            j = rng.integers(0, N)
                            trials += 1
                            if j not in close_set:
                                i_mm[wptr] = global_i
                                j_mm[wptr] = j
                                y_mm[wptr] = 0
                                wptr += 1
                                neg_count += 1

            # Update progress bar
            pbar.update(block_size)
            pbar.set_postfix(pairs=wptr)

    pbar.close()

    # Flush and save count
    i_mm.flush()
    j_mm.flush()
    y_mm.flush()
    np.save(out_dir / "pairs_count.npy", np.array([wptr], dtype=np.int64))

    if verbose:
        print(f"Generated {wptr:,} pairs, saved to {out_dir}")

    return wptr


class SpatialContrastiveDataset(Dataset):
    """
    In-memory dataset for spatial contrastive learning.

    Generates pairs on initialization and stores them in memory.
    Suitable for smaller datasets.
    """

    def __init__(
        self,
        coords: np.ndarray,
        r_pos_km: float = 1.0,
        r_neg_km: float = 5.0,
        max_pairs: int = 2_000_000,
        k_neg_per_i: int = 10,
        max_pos_per_i: int = 5,
        seed: int = 42,
    ):
        """
        Args:
            coords: Lat/lon coordinates of shape (N, 2)
            r_pos_km: Positive pair radius in kilometers
            r_neg_km: Negative pair minimum distance in kilometers
            max_pairs: Maximum number of pairs
            k_neg_per_i: Number of negative pairs per anchor
            max_pos_per_i: Maximum positive pairs per anchor
            seed: Random seed
        """
        self.coords = np.asarray(coords, dtype=np.float32)
        self.i_arr, self.j_arr, self.y_arr = spatial_proximity_pairs_kdtree_fast(
            self.coords,
            r_pos_km=r_pos_km,
            r_neg_km=r_neg_km,
            max_pairs=max_pairs,
            k_neg_per_i=k_neg_per_i,
            max_pos_per_i=max_pos_per_i,
            seed=seed,
        )

    def __len__(self) -> int:
        return len(self.i_arr)

    def __getitem__(self, idx: int) -> Tuple[np.ndarray, np.ndarray, int]:
        i = int(self.i_arr[idx])
        j = int(self.j_arr[idx])
        y = int(self.y_arr[idx])
        return self.coords[i], self.coords[j], y


class PairsMemmapDataset(Dataset):
    """
    Memory-mapped dataset for spatial contrastive learning.

    Loads pre-computed pairs from memory-mapped files for efficient
    handling of large datasets. Uses memory-mapped XY coordinates
    when available to minimize RAM usage.
    """

    def __init__(
        self,
        coords_deg: np.ndarray,
        out_dir: Union[str, Path],
        precompute_xy: bool = True,
    ):
        """
        Args:
            coords_deg: Lat/lon coordinates in degrees, shape (N, 2)
            out_dir: Directory containing memmap pair files
            precompute_xy: If True, use XY km coordinates for faster training
        """
        out_dir = Path(out_dir)
        self.coords = np.asarray(coords_deg, dtype=np.float32)
        self.i = np.memmap(out_dir / "pairs_i.int32", dtype=np.int32, mode="r")
        self.j = np.memmap(out_dir / "pairs_j.int32", dtype=np.int32, mode="r")
        self.y = np.memmap(out_dir / "pairs_y.uint8", dtype=np.uint8, mode="r")
        self.count = int(np.load(out_dir / "pairs_count.npy")[0])

        # Use XY coordinates - prefer memory-mapped file, fallback to in-memory
        self.precompute_xy = precompute_xy
        self.coords_xy = None

        if precompute_xy:
            xy_file = out_dir / "coords_xy.float32"
            if xy_file.exists():
                # Use memory-mapped XY coordinates (saves RAM for large datasets)
                N = len(self.coords)
                self.coords_xy = np.memmap(xy_file, dtype=np.float32, mode="r", shape=(N, 2))
            else:
                # Fallback: compute in memory (for backward compatibility)
                self.coords_xy = to_xy_km(self.coords)

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, idx: int) -> Tuple[np.ndarray, np.ndarray, int]:
        i = int(self.i[idx])
        j = int(self.j[idx])
        y = int(self.y[idx])

        if self.precompute_xy and self.coords_xy is not None:
            return self.coords_xy[i].copy(), self.coords_xy[j].copy(), y
        return self.coords[i], self.coords[j], y
