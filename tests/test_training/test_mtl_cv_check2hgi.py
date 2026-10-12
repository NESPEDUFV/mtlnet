"""End-to-end test for the check2HGI MTL runner path on synthetic data.

Covers the check2HGI-specific wiring that legacy regression tests miss:
  * ``train_model(task_set=CHECK2HGI_NEXT_REGION)`` forward + backward
  * Sequential task_a input (both heads consume [B, 9, D])
  * Per-task num_classes (task_a=7, task_b=~100) flowing through
    compute_classification_metrics without OOM
  * Emitted metric keys include ``val_joint_acc1`` and ``val_joint_lift``
  * The ``task_a_*`` / ``task_b_*`` internal rename didn't break anything

Synthetic fold: 4 users, ~10 sequences each, 64-dim embeddings, 9-step
windows. 2 epochs, 1 fold. The goal is "pipeline runs without errors,
metric keys are correct" — not training convergence.
"""

from __future__ import annotations

import numpy as np
import pytest
import torch
from torch.nn import CrossEntropyLoss
from torch.utils.data import DataLoader

from configs.globals import DEVICE
from data.folds import FoldData, FoldResult, POIDataset, TaskFoldData, _batched_collate
from losses.registry import create_loss
from models.mtl import MTLnet
from tasks import CHECK2HGI_NEXT_REGION, resolve_task_set
from training.callbacks import Callback, CallbackContext
from tracking.fold import FoldHistory


N_REGIONS = 50  # small enough for fast tests, large enough to exercise cardinality path


def _make_synthetic_fold(n_train: int, n_val: int, seq_len: int, dim: int, n_regions: int):
    """Build a minimal FoldResult mimicking a check2HGI fold."""
    rng = np.random.default_rng(0)
    # Train
    x_train = torch.from_numpy(rng.standard_normal((n_train, seq_len, dim)).astype(np.float32))
    y_cat_train = torch.from_numpy(rng.integers(0, 7, size=n_train).astype(np.int64))
    y_reg_train = torch.from_numpy(rng.integers(0, n_regions, size=n_train).astype(np.int64))
    # Val
    x_val = torch.from_numpy(rng.standard_normal((n_val, seq_len, dim)).astype(np.float32))
    y_cat_val = torch.from_numpy(rng.integers(0, 7, size=n_val).astype(np.int64))
    y_reg_val = torch.from_numpy(rng.integers(0, n_regions, size=n_val).astype(np.int64))

    def _dl(x, y, bs):
        # POIDataset defines __getitems__ (returns pre-stacked batch tensors via index_select),
        # so it MUST be paired with the passthrough _batched_collate — exactly as the production
        # loaders do (folds.py:454,498). The default collate re-stacks and raises on [B,9,64] vs [B].
        return DataLoader(POIDataset(x, y, device=DEVICE), batch_size=bs, shuffle=False,
                          collate_fn=_batched_collate)

    return FoldResult(
        # Slot B (NEXT in legacy attr naming) == next_region
        next=TaskFoldData(
            train=FoldData(_dl(x_train, y_reg_train, 32), x_train, y_reg_train),
            val=FoldData(_dl(x_val, y_reg_val, 32), x_val, y_reg_val),
        ),
        # Slot A (CATEGORY) == next_category
        category=TaskFoldData(
            train=FoldData(_dl(x_train, y_cat_train, 32), x_train, y_cat_train),
            val=FoldData(_dl(x_val, y_cat_val, 32), x_val, y_cat_val),
        ),
    )


class _MetricCapture(Callback):
    """Records CallbackContext.metrics at each epoch_end."""

    def __init__(self):
        super().__init__()
        self.epoch_metrics = []

    def on_epoch_end(self, ctx: CallbackContext) -> None:
        self.epoch_metrics.append(dict(ctx.metrics))


def test_check2hgi_mtl_runner_runs_end_to_end():
    from training.runners.mtl_cv import train_model

    torch.manual_seed(42)
    seq_len = 9
    dim = 64
    fold = _make_synthetic_fold(
        n_train=128, n_val=32, seq_len=seq_len, dim=dim, n_regions=N_REGIONS,
    )

    task_set = resolve_task_set(CHECK2HGI_NEXT_REGION, task_b_num_classes=N_REGIONS)
    model = MTLnet(
        feature_size=dim,
        shared_layer_size=64,          # small for speed
        num_classes=7,                 # ignored because task_set is provided
        num_heads=4,
        num_layers=2,
        seq_length=seq_len,
        num_shared_layers=2,
        task_set=task_set,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=1e-2, epochs=2,
        steps_per_epoch=max(len(fold.next.train.dataloader), len(fold.category.train.dataloader)),
    )
    mtl_criterion = create_loss("equal_weight", n_tasks=2, device=DEVICE)
    capture = _MetricCapture()
    history = FoldHistory.standalone({task_set.task_a.name, task_set.task_b.name})

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=fold.next,              # slot B
        dataloader_category=fold.category,      # slot A
        next_criterion=CrossEntropyLoss(),      # task_b criterion
        category_criterion=CrossEntropyLoss(),  # task_a criterion
        mtl_criterion=mtl_criterion,
        num_epochs=2,
        num_classes=N_REGIONS,                  # max; per-task values are read from task_set
        fold_history=history,
        callbacks=[capture],
        task_set=task_set,
    )

    assert len(capture.epoch_metrics) == 2, "expected one on_epoch_end per epoch"


def test_check2hgi_metric_keys_use_preset_task_names():
    """After a run with CHECK2HGI_NEXT_REGION, metric keys must use the
    preset's slot names (``next_category``, ``next_region``) — not the
    legacy 'category'/'next' literals — and must include the check2HGI
    scale-coherent joint monitor ``val_joint_lift``.
    """
    from training.runners.mtl_cv import train_model

    torch.manual_seed(7)
    seq_len = 9
    dim = 64
    fold = _make_synthetic_fold(
        n_train=96, n_val=32, seq_len=seq_len, dim=dim, n_regions=N_REGIONS,
    )
    task_set = resolve_task_set(CHECK2HGI_NEXT_REGION, task_b_num_classes=N_REGIONS)

    model = MTLnet(
        feature_size=dim, shared_layer_size=64, num_classes=7,
        num_heads=4, num_layers=2, seq_length=seq_len, num_shared_layers=2,
        task_set=task_set,
    ).to(DEVICE)

    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)
    scheduler = torch.optim.lr_scheduler.OneCycleLR(
        optimizer, max_lr=1e-2, epochs=1,
        steps_per_epoch=max(len(fold.next.train.dataloader), len(fold.category.train.dataloader)),
    )
    capture = _MetricCapture()
    history = FoldHistory.standalone({task_set.task_a.name, task_set.task_b.name})

    train_model(
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        dataloader_next=fold.next,
        dataloader_category=fold.category,
        next_criterion=CrossEntropyLoss(),
        category_criterion=CrossEntropyLoss(),
        mtl_criterion=create_loss("equal_weight", n_tasks=2, device=DEVICE),
        num_epochs=1,
        num_classes=N_REGIONS,
        fold_history=history,
        callbacks=[capture],
        task_set=task_set,
    )

    metrics = capture.epoch_metrics[0]

    assert "val_f1_next_category" in metrics
    assert "val_f1_next_region" in metrics
    assert "val_accuracy_next_category" in metrics
    assert "val_accuracy_next_region" in metrics
    assert "val_joint_score" in metrics
    assert "val_joint_acc1" in metrics
    assert "val_joint_lift" in metrics          # alias
    assert "val_joint_geom_lift" in metrics     # canonical name (geometric mean)
    assert "val_joint_arith_lift" in metrics    # reported for comparison
    # val_joint_lift is the monitor alias for the C21 shipped selector
    # (joint_geom_simple = sqrt(cat_f1 · reg_top10)); see mtl_cv.py emission
    # ("monitor=val_joint_lift tracks the shipped selector"). It must mirror
    # val_joint_geom_simple bit-exactly, NOT the interim acc1-lift geom form.
    assert metrics["val_joint_lift"] == metrics["val_joint_geom_simple"]

    # Legacy names must NOT leak into the metrics dict under a non-legacy preset.
    for legacy_key in ("val_f1_category", "val_f1_next", "val_accuracy_category", "val_accuracy_next"):
        assert legacy_key not in metrics, (
            f"Legacy metric key {legacy_key!r} leaked — task_set renaming is incomplete."
        )
