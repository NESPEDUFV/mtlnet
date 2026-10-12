"""Faithful POI-RGNN baseline trainer (single-task next_category, 5-fold CV).

Protocol matches our other next_category baselines:
    - StratifiedGroupKFold(folds, shuffle=True, random_state=seed) on
      target_category, grouped by userid.
    - Adam(lr=1e-3, betas=(0.8, 0.9), eps=1e-7) — paper hyperparameters.
    - 35 epochs (paper §5).
    - Best-epoch selection on val macro-F1.
    - Per-fold graph matrices (adj / cat_dist / cat_dur) computed on
      training rows only, so val never leaks into the graph statistics.

Output JSON layout matches in-house ``next_*`` JSONs.

Usage::

    PYTHONPATH=src DATA_ROOT=... OUTPUT_DIR=... \\
        python -m research.baselines.poi_rgnn.train \\
            --state alabama --folds 5 --epochs 35 \\
            --tag FAITHFUL_POIRGNN_al_5f35ep
"""

from __future__ import annotations

import argparse
import json
import logging
import statistics as st
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedGroupKFold
from torch.utils.data import DataLoader, TensorDataset

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.globals import DEVICE  # noqa: E402
from tracking.metrics import compute_classification_metrics  # noqa: E402
from utils.seed import seed_everything  # noqa: E402

from research.baselines.poi_rgnn.etl import (  # noqa: E402
    N_CATEGORIES,
    WINDOW_SIZE,
    out_path as etl_out_path,
)
from research.baselines.poi_rgnn.model import POIRGNN  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("faithful_poi_rgnn")


def load_tensors(state: str):
    df = pd.read_parquet(etl_out_path(state))
    cat = np.stack([df[f"cat_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    hour = np.stack([df[f"hour_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    dist = np.stack([df[f"dist_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    dur = np.stack([df[f"dur_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    y = df["target_category"].to_numpy(np.int64)
    uid = df["userid"].to_numpy(np.int64)
    return (
        torch.from_numpy(cat),
        torch.from_numpy(hour),
        torch.from_numpy(dist),
        torch.from_numpy(dur),
        torch.from_numpy(y),
        uid,
    )


def _build_graph_matrices(cat_seq: np.ndarray, hour_seq: np.ndarray,
                          dist_seq: np.ndarray, dur_seq: np.ndarray):
    """Compute (adj_normalized, cat_dist, cat_dur) over the train rows.

    Mirrors mtl_poi/src/etl/rgnn/splits.py::_build_graph_matrices but
    aggregated globally over the fold's training rows (vs per-user).
    """
    n = N_CATEGORIES
    cat_flat = cat_seq.flatten()
    hour_flat = hour_seq.flatten()
    dist_flat = dist_seq.flatten()
    dur_flat = dur_seq.flatten()

    adj = np.zeros((n, n), dtype=np.float64)
    dist_lists = [[[] for _ in range(n)] for _ in range(n)]
    dur_lists = [[[] for _ in range(n)] for _ in range(n)]

    # Iterate consecutive pairs within each window (skip window boundaries).
    win = cat_seq.shape[1]
    for r in range(cat_seq.shape[0]):
        base = r * win
        for k in range(1, win):
            i = base + k
            c = cat_flat[i]
            c_prev = cat_flat[i - 1]
            d = dist_flat[i]
            du = dur_flat[i]
            dist_lists[c][c_prev].append(d)
            dist_lists[c_prev][c].append(d)
            dur_lists[c][c_prev].append(du)
            dur_lists[c_prev][c].append(du)
            adj[c, c_prev] += 1
            adj[c_prev, c] += 1

    def _median(grid):
        return np.array(
            [[0.0 if not g else st.median(g) for g in row] for row in grid],
            dtype=np.float32,
        )

    cat_dist = _median(dist_lists)
    cat_dur = _median(dur_lists)
    adj = adj + 0.001  # min smoothing

    # Symmetric normalization: D^(-1/2) (A+I) D^(-1/2)
    a_self = adj + np.eye(n)
    deg = a_self.sum(axis=1)
    d_inv_sqrt = np.power(deg, -0.5)
    d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0
    D = np.diag(d_inv_sqrt)
    adj_norm = (D @ a_self @ D).astype(np.float32)
    return adj_norm, cat_dist, cat_dur


def _make_loader(idx, cat, hour, dist, dur, y, batch_size, shuffle):
    ds = TensorDataset(cat[idx], hour[idx], dist[idx], dur[idx], y[idx])
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0)


def train_one_fold(cat, hour, dist, dur, y, train_idx, val_idx, *,
                   epochs, batch_size, seed, lr) -> dict:
    seed_everything(seed)
    train_dl = _make_loader(train_idx, cat, hour, dist, dur, y, batch_size, True)
    val_dl = _make_loader(val_idx, cat, hour, dist, dur, y, batch_size, False)

    # Build per-fold graphs from training rows only.
    adj_np, cat_dist_np, cat_dur_np = _build_graph_matrices(
        cat[train_idx].numpy(), hour[train_idx].numpy(),
        dist[train_idx].numpy(), dur[train_idx].numpy(),
    )
    adj_t = torch.from_numpy(adj_np).to(DEVICE)
    cat_dist_t = torch.from_numpy(cat_dist_np).to(DEVICE)
    cat_dur_t = torch.from_numpy(cat_dur_np).to(DEVICE)

    model = POIRGNN(n_categories=N_CATEGORIES, step_size=WINDOW_SIZE).to(DEVICE)
    optim = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.8, 0.9), eps=1e-7)
    sched = torch.optim.lr_scheduler.ReduceLROnPlateau(optim, mode="max", patience=3, factor=0.5)
    crit = nn.CrossEntropyLoss()

    best_f1 = -1.0
    best = {}
    patience = 0
    for epoch in range(epochs):
        model.train()
        for cb, hb, db, ub, yb in train_dl:
            cb, hb, db, ub, yb = (
                cb.to(DEVICE), hb.to(DEVICE), db.to(DEVICE), ub.to(DEVICE), yb.to(DEVICE),
            )
            optim.zero_grad(set_to_none=True)
            out = model(cb, hb, db, ub, adj_t, cat_dist_t, cat_dur_t)
            loss = crit(out, yb)
            loss.backward()
            optim.step()

        model.eval()
        logits, targets = [], []
        with torch.no_grad():
            for cb, hb, db, ub, yb in val_dl:
                cb, hb, db, ub = cb.to(DEVICE), hb.to(DEVICE), db.to(DEVICE), ub.to(DEVICE)
                logits.append(model(cb, hb, db, ub, adj_t, cat_dist_t, cat_dur_t).cpu())
                targets.append(yb)
        logits = torch.cat(logits)
        targets = torch.cat(targets)
        m = compute_classification_metrics(logits, targets, num_classes=N_CATEGORIES, top_k=(3, 5))
        sched.step(m.get("f1", 0))
        if m.get("f1", 0) > best_f1:
            best_f1 = m["f1"]
            best = dict(m, best_epoch=epoch + 1)
            patience = 0
        else:
            patience += 1
            if patience >= 10:
                logger.info("    early-stop at epoch %d (best_f1=%.4f)", epoch + 1, best_f1)
                break
    return best


def run(state: str, folds: int, epochs: int, batch_size: int, seed: int, lr: float,
        tag: str | None) -> None:
    cat, hour, dist, dur, y, uid = load_tensors(state)
    logger.info("Loaded %s: rows=%d  n_cat=%d", state, cat.shape[0], N_CATEGORIES)

    sgkf = StratifiedGroupKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    splits = list(sgkf.split(np.zeros(len(y)), y.numpy(), groups=uid))[:folds]

    out_dir = Path("docs/results/baselines")
    out_dir.mkdir(parents=True, exist_ok=True)
    tag_s = f"_{tag}" if tag else ""
    out_file = out_dir / f"faithful_poi_rgnn_{state}_{folds}f_{epochs}ep{tag_s}.json"

    fold_metrics = []
    for fold_idx, (tr, va) in enumerate(splits):
        t0 = time.time()
        m = train_one_fold(
            cat, hour, dist, dur, y, tr, va,
            epochs=epochs, batch_size=batch_size, seed=seed + fold_idx, lr=lr,
        )
        fold_metrics.append(m)
        logger.info("  fold %d: f1=%.4f acc=%.4f acc@5=%.4f mrr=%.4f (%.1fs, best_ep=%d)",
                    fold_idx, m.get("f1", 0), m.get("accuracy", 0),
                    m.get("top5_acc", 0), m.get("mrr", 0),
                    time.time() - t0, m.get("best_epoch", 0))

    agg = {}
    for k in ["accuracy", "top3_acc", "top5_acc", "mrr", "f1", "f1_weighted", "accuracy_macro"]:
        vals = [m.get(k, 0.0) for m in fold_metrics]
        agg[f"{k}_mean"] = float(np.mean(vals))
        agg[f"{k}_std"] = float(np.std(vals))
    logger.info("AGGREGATE: " + " ".join(f"{k}={v:.4f}" for k, v in agg.items()))

    payload = {
        "state": state, "folds": folds, "epochs": epochs, "seed": seed,
        "n_categories": N_CATEGORIES,
        "config": {"lr": lr, "batch_size": batch_size, "betas": [0.8, 0.9], "eps": 1e-7},
        "per_fold": fold_metrics, "aggregate": agg,
    }
    out_file.write_text(json.dumps(payload, indent=2))
    logger.info("Saved: %s", out_file)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--epochs", type=int, default=35)
    p.add_argument("--batch-size", type=int, default=400)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--tag", type=str, default=None)
    args = p.parse_args()
    run(args.state, args.folds, args.epochs, args.batch_size, args.seed, args.lr, args.tag)


if __name__ == "__main__":
    main()
