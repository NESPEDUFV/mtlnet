"""F50 T1.2 — Build a 2-level region hierarchy via k-means on region embeddings.

For each state, clusters the n_regions × 64 region embeddings into n_clusters
groups using k-means (sklearn, deterministic with seed=42). Saves the resulting
hierarchy as `output/check2hgi/<state>/region_hierarchy.pt`:

    {
      "state": str,
      "n_regions": int,
      "n_clusters": int,
      "region_to_cluster": LongTensor[n_regions],   # cluster id for each region
      "cluster_to_regions": list[list[int]],        # children of each cluster
      "n_features_per_region": int,
      "kmeans_inertia": float,
      "seed": int,
    }

n_clusters defaults heuristically:
    AL  (1109) -> 33    (≈ sqrt(1109))
    AZ  (1547) -> 39
    FL  (4702) -> 67    (≈ Florida county count; matches sqrt(4702))
    CA  (TBD)  -> sqrt
    TX  (TBD)  -> sqrt

This is data-driven (no shapefile parsing) — clusters by embedding similarity
rather than geographic adjacency. Sufficient for testing the F50 T1.2
hypothesis ("does hierarchical structure on the reg head reduce the FL
architectural cost?") because the hypothesis is about *architectural inductive
bias*, not geographic semantics.

Usage:
    python scripts/build_region_hierarchy.py --state florida
    python scripts/build_region_hierarchy.py --state alabama --n-clusters 33
    python scripts/build_region_hierarchy.py --state arizona

Output:
    $OUTPUT_DIR/check2hgi/<state>/region_hierarchy.pt
"""
from __future__ import annotations

import argparse
import math
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import pandas as pd
import torch
from sklearn.cluster import KMeans

OUTPUT_DIR = Path(os.environ.get("OUTPUT_DIR", _root / "output")).resolve()


def _embedding_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if c.startswith("reg_") or c.startswith("emb_")]


def build_hierarchy(state: str, engine: str = "check2hgi", n_clusters: int | None = None,
                    seed: int = 42) -> dict:
    """Cluster the state's region embeddings into n_clusters groups via k-means."""
    emb_path = OUTPUT_DIR / engine / state / "region_embeddings.parquet"
    if not emb_path.exists():
        raise FileNotFoundError(f"Region embeddings not found at {emb_path}. Run the upstream pipeline first.")

    df = pd.read_parquet(emb_path).sort_values("region_id").reset_index(drop=True)
    feat_cols = _embedding_columns(df)
    if not feat_cols:
        raise ValueError(f"No embedding columns (reg_*/emb_*) found in {emb_path}; cols = {df.columns.tolist()}")

    X = df[feat_cols].to_numpy(dtype=np.float32)
    region_ids = df["region_id"].to_numpy(dtype=np.int64)
    n_regions = X.shape[0]

    if n_clusters is None:
        n_clusters = max(8, int(round(math.sqrt(n_regions))))

    if n_clusters >= n_regions:
        raise ValueError(f"n_clusters ({n_clusters}) must be < n_regions ({n_regions})")

    km = KMeans(n_clusters=n_clusters, random_state=seed, n_init=10)
    labels = km.fit_predict(X)

    region_to_cluster = torch.zeros(n_regions, dtype=torch.long)
    # IMPORTANT: region embeddings are sorted by region_id (0..n_regions-1).
    # We assume region_id == row index (verified for FL: 4703 regions, 0..4702).
    if not np.array_equal(region_ids, np.arange(n_regions)):
        raise ValueError(
            f"region_ids are not 0..{n_regions-1} contiguous; "
            f"first 10 = {region_ids[:10]}, last 10 = {region_ids[-10:]}. "
            "Build script assumes contiguous region_id == row index."
        )
    region_to_cluster[:] = torch.from_numpy(labels.astype(np.int64))

    # Build cluster_to_regions
    cluster_to_regions: list[list[int]] = [[] for _ in range(n_clusters)]
    for r, c in enumerate(labels):
        cluster_to_regions[int(c)].append(int(r))

    # Stats
    cluster_sizes = [len(v) for v in cluster_to_regions]
    return {
        "state": state,
        "engine": engine,
        "n_regions": int(n_regions),
        "n_clusters": int(n_clusters),
        "region_to_cluster": region_to_cluster,
        "cluster_to_regions": cluster_to_regions,
        "n_features_per_region": len(feat_cols),
        "feat_cols": feat_cols,
        "kmeans_inertia": float(km.inertia_),
        "kmeans_n_iter": int(km.n_iter_),
        "cluster_sizes_min": int(min(cluster_sizes)),
        "cluster_sizes_max": int(max(cluster_sizes)),
        "cluster_sizes_mean": float(np.mean(cluster_sizes)),
        "cluster_sizes_std": float(np.std(cluster_sizes)),
        "seed": seed,
    }


def save_hierarchy(hierarchy: dict, out_path: Path | None = None) -> Path:
    state = hierarchy["state"]
    engine = hierarchy.get("engine", "check2hgi")
    if out_path is None:
        out_path = OUTPUT_DIR / engine / state / "region_hierarchy.pt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(hierarchy, out_path)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True)
    parser.add_argument("--engine", default="check2hgi")
    parser.add_argument("--n-clusters", type=int, default=None,
                        help="Override default sqrt(n_regions). FL default = 67.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print(f"[F50 T1.2] Building region hierarchy: state={args.state} engine={args.engine}")
    h = build_hierarchy(args.state, engine=args.engine, n_clusters=args.n_clusters, seed=args.seed)

    print(f"  n_regions:     {h['n_regions']}")
    print(f"  n_clusters:    {h['n_clusters']}")
    print(f"  features/region: {h['n_features_per_region']}")
    print(f"  k-means inertia: {h['kmeans_inertia']:.2f}  (n_iter = {h['kmeans_n_iter']})")
    print(f"  cluster sizes: min={h['cluster_sizes_min']} mean={h['cluster_sizes_mean']:.1f}±{h['cluster_sizes_std']:.1f} max={h['cluster_sizes_max']}")

    out = save_hierarchy(h)
    print(f"\n✓ wrote {out}")


if __name__ == "__main__":
    main()
