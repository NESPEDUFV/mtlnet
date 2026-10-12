"""End-to-end smoke test for the check2HGI next_region MTL track.

Exercises:
  - TaskConfig / TaskSet preset with runtime-resolved num_regions
  - MTLnet(task_set=CHECK2HGI_NEXT_REGION) two-sequential-head topology
  - Per-task fold loading (next.parquet for next_category, next_region.parquet
    for next_region) with shared userid partition
  - train_model(..., task_set=...) for 2 epochs on 1 fold

Not a full training run. Run with::

    DATA_ROOT=... OUTPUT_DIR=... python scripts/smoke_check2hgi_mtl.py --state alabama
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold
from torch.nn import CrossEntropyLoss

from configs.globals import DEVICE
from configs.model import InputsConfig
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import FoldData, FoldResult, POIDataset, TaskFoldData
from losses.registry import create_loss
from models.mtl import MTLnet
from tasks import CHECK2HGI_NEXT_REGION, resolve_task_set
from torch.utils.data import DataLoader
from tracking.fold import FoldHistory
from training.runners.mtl_cv import train_model

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


CATEGORIES_MAP = {
    "Community": 0,
    "Entertainment": 1,
    "Food": 2,
    "Nightlife": 3,
    "Outdoors": 4,
    "Shopping": 5,
    "Travel": 6,
}


def _load_data(state: str):
    """Return (X_seq, y_cat, y_region, userids, n_regions)."""
    next_df = IoPaths.load_next(state, EmbeddingEngine.CHECK2HGI)
    region_df = IoPaths.load_next_region(state, EmbeddingEngine.CHECK2HGI)

    feature_cols = sorted([c for c in next_df.columns if c.isdigit()], key=int)
    slide_window = InputsConfig.SLIDE_WINDOW
    emb_dim = len(feature_cols) // slide_window
    logger.info(f"emb_dim={emb_dim}, slide_window={slide_window}, rows={len(next_df)}")

    X = next_df[feature_cols].to_numpy(dtype=np.float32)
    y_cat = next_df["next_category"].map(CATEGORIES_MAP).to_numpy(dtype=np.int64)
    y_region = region_df["region_idx"].to_numpy(dtype=np.int64)
    userids = next_df["userid"].astype(str).to_numpy()

    nan_mask = ~pd.Series(y_cat).isna().values
    if (~nan_mask).any():
        logger.warning(f"Dropping {(~nan_mask).sum()} NaN category rows")
        X = X[nan_mask]
        y_cat = y_cat[nan_mask]
        y_region = y_region[nan_mask]
        userids = userids[nan_mask]

    n_regions = int(y_region.max()) + 1
    return X, y_cat, y_region, userids, emb_dim, n_regions


def _dataloader(x, y, batch_size, shuffle):
    ds = POIDataset(x, y, device=DEVICE)
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0)


def smoke(state: str, batch_size: int = 2048, epochs: int = 2):
    X, y_cat, y_region, userids, emb_dim, n_regions = _load_data(state)
    logger.info(f"n_regions={n_regions}, class balance top5={pd.Series(y_region).value_counts().head().to_dict()}")

    # Single-fold split to keep the smoke test fast.
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    train_idx, val_idx = next(sgkf.split(X, y_cat, groups=userids))
    logger.info(f"train rows={len(train_idx)}, val rows={len(val_idx)}")

    slide_window = InputsConfig.SLIDE_WINDOW
    X_seq = torch.from_numpy(X).view(-1, slide_window, emb_dim)
    y_cat_t = torch.from_numpy(y_cat)
    y_region_t = torch.from_numpy(y_region)

    # FoldResult: slot A (.category) ← next_category, slot B (.next) ← next_region.
    fold = FoldResult(
        category=TaskFoldData(
            train=FoldData(
                _dataloader(X_seq[train_idx], y_cat_t[train_idx], batch_size, True),
                X_seq[train_idx], y_cat_t[train_idx],
            ),
            val=FoldData(
                _dataloader(X_seq[val_idx], y_cat_t[val_idx], batch_size, False),
                X_seq[val_idx], y_cat_t[val_idx],
            ),
        ),
        next=TaskFoldData(
            train=FoldData(
                _dataloader(X_seq[train_idx], y_region_t[train_idx], batch_size, True),
                X_seq[train_idx], y_region_t[train_idx],
            ),
            val=FoldData(
                _dataloader(X_seq[val_idx], y_region_t[val_idx], batch_size, False),
                X_seq[val_idx], y_region_t[val_idx],
            ),
        ),
    )

    resolved = resolve_task_set(CHECK2HGI_NEXT_REGION, task_b_num_classes=n_regions)
    logger.info(f"task_set: task_a={resolved.task_a.name}/{resolved.task_a.num_classes}, task_b={resolved.task_b.name}/{resolved.task_b.num_classes}")

    # Build the model. num_classes arg is ignored when task_set is provided.
    torch.manual_seed(42)
    model = MTLnet(
        feature_size=emb_dim,
        shared_layer_size=256,
        num_classes=7,                 # legacy arg — ignored because task_set given
        num_heads=8,
        num_layers=4,
        seq_length=slide_window,
        num_shared_layers=4,
        task_set=resolved,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=1e-3, epochs=epochs,
        steps_per_epoch=max(len(fold.next.train.dataloader), len(fold.category.train.dataloader)),
    )
    # Per-head criteria. next_criterion (runner arg name) handles task_b (region);
    # category_criterion handles task_a (next_category).
    next_criterion = CrossEntropyLoss()
    category_criterion = CrossEntropyLoss()
    mtl_criterion = create_loss("nash_mtl", n_tasks=2, device=DEVICE)

    # NOTE: compute_classification_metrics receives a single num_classes in the
    # current runner. We pass max(7, n_regions) so the region head doesn't see
    # a smaller label space than its logits. macro-F1 for next_category will be
    # under-computed (many empty classes), but this smoke test only cares that
    # the pipeline executes end-to-end. Full per-task num_classes wiring is a
    # follow-up for scripts/train.py integration.
    hist = FoldHistory.standalone({resolved.task_a.name, resolved.task_b.name})

    train_model(
        model, optimizer, scheduler,
        fold.next, fold.category,
        next_criterion, category_criterion, mtl_criterion,
        num_epochs=epochs,
        num_classes=max(resolved.task_a.num_classes, resolved.task_b.num_classes),
        fold_history=hist,
        task_set=resolved,
    )

    logger.info("Smoke train_model completed.")
    task_a_best = hist.task(resolved.task_a.name).best.best_value
    task_b_best = hist.task(resolved.task_b.name).best.best_value
    logger.info(f"  {resolved.task_a.name} best F1: {task_a_best:.4f}")
    logger.info(f"  {resolved.task_b.name} best F1: {task_b_best:.4f}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=2048)
    args = parser.parse_args()
    smoke(args.state, args.batch_size, args.epochs)


if __name__ == "__main__":
    main()
