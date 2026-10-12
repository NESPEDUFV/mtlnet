"""
Profile the HGI training pipeline on Alabama to find where wall-clock goes.

Times each phase of pipelines/embedding/hgi.pipe.py:
  preprocess_a    — Phase 3a: Delaunay graph, edges.csv, pois.csv
  poi2vec         — Phase 3b-3d: walks + skipgram + reconstruction
  preprocess_b    — Phase 4: build full data_dict with POI2Vec embeddings
  hgi_train       — Phase 5: train_hgi epoch loop

For Phase 5 (the main loop), reports a per-epoch breakdown:
  forward         — model(data) — POIEncoder + POI2Region + region2city + hard-neg
  loss            — model.loss(*outputs)
  backward        — loss.backward() + clip_grad_norm
  optim           — optimizer.step() + scheduler.step()
  best_track      — best-loss bookkeeping (cpu transfer + clone)

Run with:
  python scripts/profile_hgi_alabama.py [--epochs 50] [--device mps|cpu] [--phase5_only]
"""
from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from contextlib import contextmanager
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=50,
                   help="Number of HGI epochs to run during Phase 5 profiling")
    p.add_argument("--poi2vec_epochs", type=int, default=6,
                   help="Number of POI2Vec epochs (matches default pipeline)")
    p.add_argument("--device", choices=["mps", "cpu"], default=None,
                   help="Override device (default: cpu, matching pipeline default)")
    p.add_argument("--phase5_only", action="store_true",
                   help="Skip preprocess + poi2vec, profile only train_hgi using existing pickle")
    args = p.parse_args()

    device_str = args.device or "cpu"

    import torch
    import math
    import pickle as pkl
    import numpy as np
    from torch.optim.lr_scheduler import StepLR
    from torch.nn.utils import clip_grad_norm_
    from torch_geometric.data import Data

    print(f"PyTorch:    {torch.__version__}")
    print(f"Device:     {device_str}")
    print(f"MPS avail:  {torch.backends.mps.is_available()}")
    print(f"Epochs:     {args.epochs}")
    print()

    from configs.paths import IoPaths, EmbeddingEngine, Resources
    from embeddings.hgi.preprocess import preprocess_hgi
    from embeddings.hgi.poi2vec import train_poi2vec
    from embeddings.hgi.model.HGIModule import HierarchicalGraphInfomax, corruption
    from embeddings.hgi.model.POIEncoder import POIEncoder
    from embeddings.hgi.model.RegionEncoder import POI2Region

    city = "Alabama"
    shapefile = str(Resources.TL_AL)
    graph_data_file = IoPaths.HGI.get_graph_data_file(city)

    phase_wall: dict[str, float] = {}

    # ----- PHASES 3a → 4: rebuild graph data, unless --phase5_only -----
    if not args.phase5_only:
        if graph_data_file.exists():
            graph_data_file.unlink()  # force regen so we measure cleanly

        t0 = time.perf_counter()
        preprocess_hgi(city=city, city_shapefile=shapefile, poi_emb_path=None)
        phase_wall["preprocess_a"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        poi_emb_path = train_poi2vec(
            city=city, epochs=args.poi2vec_epochs, embedding_dim=64, device=device_str
        )
        phase_wall["poi2vec"] = time.perf_counter() - t0

        t0 = time.perf_counter()
        data_dict = preprocess_hgi(
            city=city, city_shapefile=shapefile, poi_emb_path=str(poi_emb_path)
        )
        graph_data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(graph_data_file, "wb") as f:
            pkl.dump(data_dict, f)
        phase_wall["preprocess_b"] = time.perf_counter() - t0
    else:
        if not graph_data_file.exists():
            print(f"ERROR: --phase5_only requires existing {graph_data_file}")
            sys.exit(1)
        print(f"Reusing existing graph data: {graph_data_file}")

    # ----- PHASE 5: profile train_hgi -----
    print()
    print("=" * 80)
    print("Phase 5: train_hgi profiling")
    print("=" * 80)

    with open(graph_data_file, "rb") as f:
        city_dict = pkl.load(f)

    in_channels = city_dict["node_features"].shape[1]
    num_pois = city_dict["number_pois"]
    num_regions = city_dict["number_regions"]
    print(f"POIs={num_pois}, Regions={num_regions}, in_channels={in_channels}")

    device = torch.device(device_str)
    data = Data(
        x=torch.tensor(city_dict["node_features"], dtype=torch.float32),
        edge_index=torch.tensor(city_dict["edge_index"], dtype=torch.int64),
        edge_weight=torch.tensor(city_dict["edge_weight"], dtype=torch.float32),
        region_id=torch.tensor(city_dict["region_id"], dtype=torch.int64),
        region_area=torch.tensor(city_dict["region_area"], dtype=torch.float32),
        coarse_region_similarity=torch.tensor(
            city_dict["coarse_region_similarity"], dtype=torch.float32
        ),
        region_adjacency=torch.tensor(city_dict["region_adjacency"], dtype=torch.int64),
    ).to(device)

    poi_encoder = POIEncoder(in_channels, 64)
    poi2region = POI2Region(64, 4)

    def region2city(z, area):
        return torch.sigmoid((z.transpose(0, 1) * area).sum(dim=1))

    model = HierarchicalGraphInfomax(
        hidden_channels=64,
        poi_encoder=poi_encoder,
        poi2region=poi2region,
        region2city=region2city,
        corruption=corruption,
        alpha=0.5,
    ).to(device)

    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    scheduler = StepLR(optimizer, step_size=1, gamma=1.0)

    def sync():
        if device.type == "mps":
            torch.mps.synchronize()
        elif device.type == "cuda":
            torch.cuda.synchronize()

    phase_times: dict[str, list[float]] = {
        "forward": [], "loss": [], "backward": [],
        "optim": [], "best_track": [],
    }

    @contextmanager
    def timed(name):
        sync()
        t0 = time.perf_counter()
        yield
        sync()
        phase_times[name].append(time.perf_counter() - t0)

    # Burn-in epoch (untimed) — first call has lazy initialization overhead
    print("\nBurn-in: 1 epoch (untimed)")
    model.train()
    sync()
    bt = time.perf_counter()
    optimizer.zero_grad()
    out = model(data)
    loss = model.loss(*out)
    loss.backward()
    clip_grad_norm_(model.parameters(), max_norm=0.9)
    optimizer.step()
    scheduler.step()
    sync()
    print(f"  burn-in: {time.perf_counter() - bt:.2f}s")

    print(f"\nProfiled: {args.epochs} epochs")
    lowest_loss = math.inf
    epoch_walls = []

    sync()
    train_start = time.perf_counter()

    for epoch in range(args.epochs):
        model.train()
        ep_t0 = time.perf_counter()
        optimizer.zero_grad()

        with timed("forward"):
            outputs = model(data)
        with timed("loss"):
            loss = model.loss(*outputs)
        with timed("backward"):
            loss.backward()
            clip_grad_norm_(model.parameters(), max_norm=0.9)
        with timed("optim"):
            optimizer.step()
            scheduler.step()
        with timed("best_track"):
            cur = loss.item()
            if cur < lowest_loss:
                _ = model.get_region_emb()  # cpu transfer + clone
                lowest_loss = cur

        sync()
        epoch_walls.append(time.perf_counter() - ep_t0)

    sync()
    train_total = time.perf_counter() - train_start
    phase_wall["hgi_train"] = train_total

    print(f"\nTotal Phase 5 wall: {train_total:.2f}s ({train_total/args.epochs*1000:.1f} ms/epoch)")
    print(f"Best loss: {lowest_loss:.4f}")

    # ----- Phase wall summary -----
    print()
    print("=" * 80)
    print("Phase wall summary")
    print("=" * 80)
    print(f"{'phase':14s}  {'wall':>10s}")
    grand = 0.0
    for k, v in phase_wall.items():
        print(f"{k:14s}  {v:8.2f}s")
        grand += v
    print(f"{'TOTAL':14s}  {grand:8.2f}s")

    # ----- Phase 5 per-step breakdown -----
    print()
    print("=" * 80)
    print(f"Phase 5 per-step breakdown ({args.epochs} epochs, ms)")
    print("=" * 80)
    print(f"{'phase':12s}  {'mean':>8s}  {'median':>8s}  {'p95':>8s}  {'sum':>10s}")
    total_sum = 0.0
    for name, times in phase_times.items():
        if not times:
            continue
        ms = [t * 1000 for t in times]
        ms_sorted = sorted(ms)
        p95 = ms_sorted[max(0, int(len(ms) * 0.95) - 1)]
        s = sum(ms) / 1000
        total_sum += s
        print(f"{name:12s}  {statistics.mean(ms):8.2f}  "
              f"{statistics.median(ms):8.2f}  {p95:8.2f}  {s:8.2f}s")
    print(f"{'TOTAL':12s}  {'':>8s}  {'':>8s}  {'':>8s}  {total_sum:8.2f}s")

    # Per-epoch wall stats
    if epoch_walls:
        ms = [w * 1000 for w in epoch_walls]
        print(f"\nPer-epoch wall: mean={statistics.mean(ms):.1f}ms, "
              f"median={statistics.median(ms):.1f}ms, "
              f"min={min(ms):.1f}ms, max={max(ms):.1f}ms")


if __name__ == "__main__":
    main()
