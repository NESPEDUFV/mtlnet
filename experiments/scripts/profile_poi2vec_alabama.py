"""
Profile POI2Vec training for Alabama: walks, dataset construction,
and per-epoch breakdown of loss components.

Run with:
  python scripts/profile_poi2vec_alabama.py
"""
from __future__ import annotations

import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import torch

from configs.paths import IoPaths


def main():
    from embeddings.hgi.poi2vec import POI2Vec, POISet, EmbeddingModel

    edges_file = IoPaths.HGI.get_edges_file("Alabama")
    pois_file = IoPaths.HGI.get_pois_processed_file("Alabama")
    if not edges_file.exists() or not pois_file.exists():
        print(f"ERROR: Run preprocess_a first to create {edges_file} / {pois_file}")
        sys.exit(1)

    device = torch.device("cpu")
    print(f"Device: {device}")
    print(f"Threads: {torch.get_num_threads()}")
    print()

    # ----- Phase 3a-style construction -----
    t0 = time.perf_counter()
    poi2vec = POI2Vec(str(edges_file), str(pois_file), embedding_dim=64, device=device)
    print(f"POI2Vec construction: {time.perf_counter() - t0:.2f}s")
    print(f"  POIs: {len(poi2vec.pois)}")
    print(f"  Vocab (fclass): {poi2vec.vocab_size}")
    print()

    # ----- Walk generation -----
    t0 = time.perf_counter()
    poi2vec.generate_walks()
    walks_wall = time.perf_counter() - t0
    print(f"\nWalk generation total: {walks_wall:.2f}s")
    print(f"  walks: {len(poi2vec.fclass_walks)}")
    print()

    # ----- Dataset construction -----
    t0 = time.perf_counter()
    dataset = POISet(
        vocab_size=poi2vec.vocab_size,
        fclass_walks=poi2vec.fclass_walks,
        global_co_occurrence=poi2vec.global_co_occurrence,
        k=5,
    )
    print(f"POISet construction: {time.perf_counter() - t0:.2f}s")

    # ----- Per-getitem timing -----
    print("\nProfiling POISet.__getitem__ (1000 calls)...")
    t0 = time.perf_counter()
    for i in range(1000):
        _ = dataset[i % len(dataset)]
    getitem_wall = time.perf_counter() - t0
    print(f"  1000 __getitem__ calls: {getitem_wall*1000:.1f}ms ({getitem_wall:.4f}ms/call)")
    print(f"  Estimated for full dataset ({len(dataset)} walks): "
          f"{getitem_wall * len(dataset) / 1000:.1f}s per epoch via __getitem__")

    # ----- Loader iteration timing -----
    print("\nProfiling DataLoader iteration (1 epoch, batch_size=2048)...")
    loader = torch.utils.data.DataLoader(dataset, batch_size=2048, shuffle=True, num_workers=0)
    t0 = time.perf_counter()
    n_batches = 0
    for _ in loader:
        n_batches += 1
    loader_wall = time.perf_counter() - t0
    print(f"  Full epoch loader iter: {loader_wall:.2f}s ({n_batches} batches, "
          f"{loader_wall*1000/n_batches:.1f}ms/batch)")

    # ----- Model build -----
    hierarchy_pairs = list(set([
        tuple(row) for row in poi2vec.pois[['category', 'fclass']].values
    ]))
    print(f"\nHierarchy pairs: {len(hierarchy_pairs)}")

    model = EmbeddingModel(
        vocab_size=poi2vec.vocab_size,
        embed_size=64,
        hierarchy_pairs=hierarchy_pairs,
        le_lambda=1e-8,
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.05)

    # ----- Per-batch breakdown -----
    print("\nProfiling per-batch forward+backward (50 batches)...")
    phase_times = {"forward": [], "backward": [], "optim": []}

    @contextmanager
    def timed(name):
        t0 = time.perf_counter()
        yield
        phase_times[name].append(time.perf_counter() - t0)

    # Burn-in
    for batch in loader:
        center, pos, neg = batch
        center, pos, neg = center.to(device), pos.to(device), neg.to(device)
        optimizer.zero_grad()
        loss, _ = model(center, pos, neg)
        loss.backward()
        optimizer.step()
        break

    model.train()
    n = 0
    for batch in loader:
        if n >= 50:
            break
        center, pos, neg = batch
        center, pos, neg = center.to(device), pos.to(device), neg.to(device)
        optimizer.zero_grad()
        with timed("forward"):
            loss, _ = model(center, pos, neg)
        with timed("backward"):
            loss.backward()
        with timed("optim"):
            optimizer.step()
        n += 1

    print(f"\n{'phase':12s}  {'mean(ms)':>10s}  {'median(ms)':>10s}  {'sum(s)':>10s}")
    for name, times in phase_times.items():
        ms = [t * 1000 for t in times]
        print(f"{name:12s}  {statistics.mean(ms):10.2f}  {statistics.median(ms):10.2f}  "
              f"{sum(ms)/1000:10.3f}")

    # Estimate per-epoch wall
    per_batch_ms = sum(statistics.mean(v) for v in phase_times.values())
    per_epoch_train_s = per_batch_ms * n_batches / 1000
    per_epoch_loader_s = loader_wall  # iteration cost
    print(f"\nEstimated per-epoch: train={per_epoch_train_s:.1f}s + "
          f"loader_overhead≈{per_epoch_loader_s:.1f}s")
    print(f"Estimated for 6 epochs: {6 * (per_epoch_train_s + per_epoch_loader_s):.1f}s")


if __name__ == "__main__":
    main()
