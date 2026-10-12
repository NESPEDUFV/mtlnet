"""
Benchmark several Time2Vec training configurations on Alabama.

For each config, runs 2 short epochs and reports:
  - seconds per epoch (averaged over epoch 2, ignoring warmup)
  - final loss (for a rough convergence check)

The baseline is the production config (batch=256, num_workers=8). The goal is
to find a config that's faster without drifting final-loss more than a few
percent from baseline on this short run.

Usage:
  PYTHONPATH=src:research .venv/bin/python scripts/bench_time2vec_configs.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "research"))

from torch.utils.data import TensorDataset

from configs.paths import IoPaths
from embeddings.time2vec.model.Time2VecModule import Time2VecContrastiveModel
from embeddings.time2vec.model.dataset import TemporalContrastiveDataset


def build_tensor_dataset(base: TemporalContrastiveDataset) -> TensorDataset:
    """Pre-gather (feat_i, feat_j, label) as contiguous tensors.

    Eliminates per-item Python overhead in __getitem__ — DataLoader can now
    slice-index across the whole batch.
    """
    pairs = np.asarray(base.pairs, dtype=np.int64)  # [N, 3] -> i, j, label
    ii = pairs[:, 0]
    jj = pairs[:, 1]
    ll = pairs[:, 2].astype(np.float32)

    feat_i = torch.from_numpy(base.feats[ii]).float()
    feat_j = torch.from_numpy(base.feats[jj]).float()
    label  = torch.from_numpy(ll)
    return TensorDataset(feat_i, feat_j, label)


def train_one_epoch(model, loader, optimizer, device, tau, concat_forward=False):
    model.train()
    total_loss = 0.0
    n = 0
    for ti, tj, lbl in loader:
        ti = ti.to(device, dtype=torch.float32, non_blocking=True)
        tj = tj.to(device, dtype=torch.float32, non_blocking=True)
        lbl = lbl.to(device, dtype=torch.float32, non_blocking=True)

        if concat_forward:
            # Single forward pass over concatenated inputs
            B = ti.shape[0]
            t_cat = torch.cat([ti, tj], dim=0)
            z_cat = model.encode(t_cat)
            z_i, z_j = z_cat.split(B, dim=0)
        else:
            z_i, z_j = model(ti, tj)

        loss = model.contrastive_loss(z_i, z_j, lbl, tau=tau)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n += 1
    return total_loss / n


def build_loader(dataset, batch_size: int, num_workers: int):
    kwargs = dict(
        batch_size=batch_size,
        shuffle=True,
        drop_last=True,
        num_workers=num_workers,
    )
    if num_workers > 0:
        kwargs["persistent_workers"] = True
        kwargs["prefetch_factor"] = 5
    return DataLoader(dataset, **kwargs)


def bench_config(
    name: str,
    dataset,
    *,
    batch_size: int,
    num_workers: int,
    concat_forward: bool,
    num_threads: int | None,
    seed: int = 0,
):
    if num_threads is not None:
        torch.set_num_threads(num_threads)
    else:
        torch.set_num_threads(torch.get_num_threads())

    torch.manual_seed(seed)
    np.random.seed(seed)

    device = torch.device("cpu")
    model = Time2VecContrastiveModel("sin", 64, 64, 2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    loader = build_loader(dataset, batch_size, num_workers)
    n_batches = len(loader)

    # Warmup epoch
    _ = train_one_epoch(model, loader, optimizer, device, tau=0.3, concat_forward=concat_forward)

    # Timed epoch
    t0 = time.perf_counter()
    loss = train_one_epoch(model, loader, optimizer, device, tau=0.3, concat_forward=concat_forward)
    dt = time.perf_counter() - t0

    print(
        f"  {name:<45} epoch={dt:6.2f}s  "
        f"batches={n_batches:>5}  "
        f"last_loss={loss:.4f}"
    )
    return dt, loss


def main():
    print("Loading Alabama...")
    checkins = pd.read_parquet(IoPaths.get_city("Alabama"))
    time_hours, time_feats = TemporalContrastiveDataset.extract_time_features(checkins)
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
    print(f"Dataset: {len(dataset):,} pairs")
    print(f"Torch threads available: {torch.get_num_threads()}\n")

    print("Benchmarking (warmup epoch + timed epoch each, lower = better):\n")

    print("--- Python-list dataset (current) ---")
    configs_list = [
        # (name, batch, workers, concat, threads)
        ("baseline: bs=256  nw=8",   256, 8, False, None),
        ("bs=2048  nw=8",           2048, 8, False, None),
    ]
    for name, bs, nw, cat, th in configs_list:
        bench_config(name, dataset, batch_size=bs, num_workers=nw,
                     concat_forward=cat, num_threads=th)

    print("\n--- Tensor-backed dataset (precomputed feat_i/feat_j) ---")
    t0 = time.perf_counter()
    tensor_ds = build_tensor_dataset(dataset)
    print(f"  build time: {time.perf_counter() - t0:.2f}s  "
          f"memory: ~{sum(t.numel()*t.element_size() for t in tensor_ds.tensors)/1e6:.1f}MB")
    configs_tensor = [
        ("bs=2048  nw=0",   2048, 0, False, None),
        ("bs=2048  nw=8",   2048, 8, False, None),
        ("bs=4096  nw=8",   4096, 8, False, None),
    ]
    for name, bs, nw, cat, th in configs_tensor:
        bench_config(name, tensor_ds, batch_size=bs, num_workers=nw,
                     concat_forward=cat, num_threads=th)

    print("\n--- Manual slicing (no DataLoader, precomputed tensors) ---")
    for bs in (2048, 4096, 8192):
        _bench_manual(tensor_ds, batch_size=bs)


def _bench_manual(tensor_ds: TensorDataset, *, batch_size: int):
    torch.set_num_threads(torch.get_num_threads())
    torch.manual_seed(0)
    np.random.seed(0)

    device = torch.device("cpu")
    model = Time2VecContrastiveModel("sin", 64, 64, 2).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    feat_i, feat_j, label = tensor_ds.tensors
    N = feat_i.shape[0]
    n_full = (N // batch_size) * batch_size  # drop last
    n_batches = n_full // batch_size

    def one_epoch():
        model.train()
        perm = torch.randperm(N)[:n_full]
        total_loss = 0.0
        for s in range(0, n_full, batch_size):
            idx = perm[s:s + batch_size]
            ti = feat_i[idx]
            tj = feat_j[idx]
            lbl = label[idx]
            z_i, z_j = model(ti, tj)
            loss = model.contrastive_loss(z_i, z_j, lbl, tau=0.3)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        return total_loss / n_batches

    _ = one_epoch()  # warmup
    t0 = time.perf_counter()
    loss = one_epoch()
    dt = time.perf_counter() - t0
    print(
        f"  manual   bs={batch_size:<5d}                       "
        f" epoch={dt:6.2f}s  batches={n_batches:>5}  last_loss={loss:.4f}"
    )


if __name__ == "__main__":
    main()
