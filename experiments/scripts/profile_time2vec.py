"""
Profile a single Time2Vec training epoch on Alabama to find the hot spots.

Reports:
  - Dataset construction time (one-off, not the training loop)
  - Per-batch average time (DataLoader + forward + backward + step)
  - Breakdown: data fetch vs compute vs transfer
  - Total time for 1 epoch

Usage:
  PYTHONPATH=src:research .venv/bin/python scripts/profile_time2vec.py

Output is printed to stdout. Nothing is written to disk.
"""
from __future__ import annotations

import sys
import time
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "research"))

from configs.paths import IoPaths
from embeddings.time2vec.model.Time2VecModule import Time2VecContrastiveModel
from embeddings.time2vec.model.dataset import TemporalContrastiveDataset


def main(state: str = "Alabama") -> None:
    device = torch.device("cpu")
    print(f"Profiling Time2Vec on {state} ({device})")

    # --- Load check-ins ---
    t0 = time.perf_counter()
    checkins = pd.read_parquet(IoPaths.get_city(state))
    print(f"Load check-ins:       {time.perf_counter() - t0:6.2f}s  ({len(checkins):,} rows)")

    # --- Extract time features ---
    t0 = time.perf_counter()
    time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(checkins)
    print(f"Extract time feats:   {time.perf_counter() - t0:6.2f}s  (shape {time_feats.shape})")

    # --- Build dataset ---
    t0 = time.perf_counter()
    dataset = TemporalContrastiveDataset(
        time_hours=time_hours,
        time_feats=time_feats,
        r_pos_hours=1.0,
        r_neg_hours=24.0,
        max_pairs=2_000_000,
        k_neg_per_i=5,
        max_pos_per_i=20,
        seed=42,
    )
    print(f"Build dataset:        {time.perf_counter() - t0:6.2f}s  ({len(dataset):,} pairs)")

    # --- Build DataLoader ---
    # Mirror the current production settings
    batch_size = 256
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=8,
        persistent_workers=True,
        prefetch_factor=5,
    )
    print(f"Batches per epoch:    {len(loader):,}  (batch_size={batch_size})")

    # --- Build model + optimizer ---
    model = Time2VecContrastiveModel(
        activation="sin", out_features=64, embed_dim=64, in_features=2
    ).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    param_count = sum(p.numel() for p in model.parameters())
    print(f"Model parameters:     {param_count:,}")

    # --- Warmup batch ---
    it = iter(loader)
    ti, tj, lbl = next(it)
    ti = ti.to(device, dtype=torch.float32)
    tj = tj.to(device, dtype=torch.float32)
    lbl = lbl.to(device, dtype=torch.float32)
    z_i, z_j = model(ti, tj)
    loss = model.contrastive_loss(z_i, z_j, lbl, tau=0.3)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    # --- Time a full epoch with per-phase breakdown ---
    n_batches = 200  # ~3% of an epoch — enough for stable averages
    print(f"\nTiming {n_batches} batches ...")

    t_data = 0.0
    t_to_dev = 0.0
    t_forward = 0.0
    t_loss = 0.0
    t_backward = 0.0
    t_step = 0.0

    model.train()
    start_epoch = time.perf_counter()
    it = iter(loader)

    for i in range(n_batches):
        t0 = time.perf_counter()
        ti, tj, lbl = next(it)
        t_data += time.perf_counter() - t0

        t0 = time.perf_counter()
        ti = ti.to(device, dtype=torch.float32)
        tj = tj.to(device, dtype=torch.float32)
        lbl = lbl.to(device, dtype=torch.float32)
        t_to_dev += time.perf_counter() - t0

        t0 = time.perf_counter()
        z_i, z_j = model(ti, tj)
        t_forward += time.perf_counter() - t0

        t0 = time.perf_counter()
        loss = model.contrastive_loss(z_i, z_j, lbl, tau=0.3)
        t_loss += time.perf_counter() - t0

        t0 = time.perf_counter()
        optimizer.zero_grad()
        loss.backward()
        t_backward += time.perf_counter() - t0

        t0 = time.perf_counter()
        optimizer.step()
        t_step += time.perf_counter() - t0

    total = time.perf_counter() - start_epoch
    total_ms = total * 1000

    def pct(x: float) -> str:
        return f"{100 * x / total:5.1f}%"

    print(f"\n{'='*54}")
    print(f"  {n_batches} batches = {total:.2f}s  ({total_ms/n_batches:.2f} ms/batch)")
    print(f"  Extrapolated epoch ({len(loader)} batches): {total * len(loader) / n_batches:.1f}s")
    print(f"{'='*54}")
    print(f"  {'phase':<16} {'time (s)':>10} {'ms/batch':>10} {'pct':>8}")
    print(f"  {'-'*52}")
    for name, t in [
        ("data fetch",    t_data),
        ("to device",     t_to_dev),
        ("forward",       t_forward),
        ("loss",          t_loss),
        ("backward+zero", t_backward),
        ("optimizer.step",t_step),
    ]:
        print(f"  {name:<16} {t:>10.3f} {t*1000/n_batches:>10.2f} {pct(t):>8}")
    other = total - (t_data + t_to_dev + t_forward + t_loss + t_backward + t_step)
    print(f"  {'other/overhead':<16} {other:>10.3f} {other*1000/n_batches:>10.2f} {pct(other):>8}")
    print(f"{'='*54}")


if __name__ == "__main__":
    main()
