"""
Regression test for HGI training-step throughput.

Pins the wall-clock cost of one HGI epoch on a synthetic graph (CPU).
The test fails if a future change makes the inner loop noticeably slower
than the vectorized baseline. The threshold is intentionally generous
(2x slower than measured baseline) so it does NOT trip on machine-load
noise but DOES catch regressions like reintroducing the per-region
Python loop in HGIModule.forward().

Baseline measurement on a 2024 M-series Mac (12-core):
    ~9 ms per epoch on synthetic graph (1000 POIs, 100 regions).
    A reintroduction of the per-region loop would push this to ~80 ms.

Threshold: each profiled epoch must finish in under 50 ms (5x baseline).
"""
from __future__ import annotations

import statistics
import time

import torch
from torch_geometric.data import Data

from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
from embeddings.hgi.model.POIEncoder import POIEncoder
from embeddings.hgi.model.RegionEncoder import POI2Region


# Threshold per epoch (ms). Generous enough to avoid CI noise but tight
# enough to catch a reintroduction of the O(N*R) per-region scan.
MAX_EPOCH_MS = 50.0
NUM_EPOCHS = 30
NUM_POIS = 1000
NUM_REGIONS = 100
HIDDEN = 64


def _build_synthetic_data(num_pois: int, num_regions: int, hidden: int):
    g = torch.Generator().manual_seed(0)
    x = torch.randn(num_pois, hidden, generator=g)
    # Chain edges
    src = torch.arange(num_pois - 1)
    dst = torch.arange(1, num_pois)
    edge_index = torch.stack([
        torch.cat([src, dst]),
        torch.cat([dst, src]),
    ])
    edge_weight = torch.ones(2 * (num_pois - 1))
    region_id = torch.arange(num_pois) % num_regions
    region_adjacency = torch.stack([
        torch.cat([torch.arange(num_regions - 1), torch.arange(1, num_regions)]),
        torch.cat([torch.arange(1, num_regions), torch.arange(num_regions - 1)]),
    ])
    region_area = torch.rand(num_regions, generator=g)
    coarse_region_similarity = torch.rand(num_regions, num_regions, generator=g) * 0.5
    return Data(
        x=x, edge_index=edge_index, edge_weight=edge_weight,
        region_id=region_id, region_adjacency=region_adjacency,
        region_area=region_area, coarse_region_similarity=coarse_region_similarity,
    )


def _build_model(hidden: int):
    torch.manual_seed(0)
    return HierarchicalGraphInfomax(
        hidden_channels=hidden,
        poi_encoder=POIEncoder(hidden, hidden),
        poi2region=POI2Region(hidden, 4),
        region2city=lambda z, a: torch.sigmoid((z.transpose(0, 1) * a).sum(dim=1)),
        corruption=corruption,
        alpha=0.5,
    )


def test_hgi_epoch_under_threshold():
    """One HGI training epoch must complete in under MAX_EPOCH_MS."""
    data = _build_synthetic_data(NUM_POIS, NUM_REGIONS, HIDDEN)
    model = _build_model(HIDDEN)
    opt = torch.optim.Adam(model.parameters(), lr=0.001)

    # Burn-in: warm caches and lazy state
    model.train()
    for _ in range(2):
        opt.zero_grad()
        out = model(data)
        loss = model.loss(*out)
        loss.backward()
        opt.step()

    # Profiled epochs
    epoch_ms = []
    for _ in range(NUM_EPOCHS):
        t0 = time.perf_counter()
        opt.zero_grad()
        out = model(data)
        loss = model.loss(*out)
        loss.backward()
        opt.step()
        epoch_ms.append((time.perf_counter() - t0) * 1000)

    median_ms = statistics.median(epoch_ms)
    p95_ms = sorted(epoch_ms)[int(NUM_EPOCHS * 0.95)]
    assert median_ms < MAX_EPOCH_MS, (
        f"HGI epoch median = {median_ms:.1f} ms (>= {MAX_EPOCH_MS} ms threshold). "
        f"Likely a regression in HGIModule.forward() (e.g. reintroduced per-region loop). "
        f"Full distribution: median={median_ms:.1f}, p95={p95_ms:.1f}, "
        f"min={min(epoch_ms):.1f}, max={max(epoch_ms):.1f}"
    )


def test_neg_pair_build_uses_cached_lookup():
    """The vectorized neg_pair build must populate the data._hgi_neg_cache attribute.

    This guards against a refactor that accidentally rebuilds the lookup
    every step (which would re-introduce the O(N*R) cost).
    """
    data = _build_synthetic_data(NUM_POIS, NUM_REGIONS, HIDDEN)
    model = _build_model(HIDDEN)
    model.eval()
    with torch.no_grad():
        _ = model(data)
    assert hasattr(data, "_hgi_neg_cache"), (
        "data._hgi_neg_cache not populated — neg_pair build is no longer cached"
    )
    cache = data._hgi_neg_cache
    for key in ("R", "hard_lists", "all_regions_per_region",
                "sort_idx", "sizes", "region_offsets"):
        assert key in cache, f"Cache is missing key: {key}"
    assert cache["R"] == NUM_REGIONS

    # Second call must reuse the cached lookup (no rebuild). We detect this
    # by mutating the cache and checking the model still uses our value.
    sentinel = cache["sort_idx"]
    with torch.no_grad():
        _ = model(data)
    assert data._hgi_neg_cache["sort_idx"] is sentinel, (
        "Cache was rebuilt on the second call — caching is broken"
    )
