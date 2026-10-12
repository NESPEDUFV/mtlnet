"""Next-POI task trainer — thin wrapper around the unified single-task loop."""

from typing import Optional

import torch
from torch import nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from torch.utils.data import DataLoader

from configs.globals import CATEGORIES_MAP
from tracking.fold import FoldHistory
from training.runners._single_task_train import train_single_task


def train(
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: Optimizer,
        scheduler: Optional[LRScheduler],
        history: FoldHistory,
        device: torch.device,
        epochs: int = 100,
        max_grad_norm: float = 1.0,
        early_stopping_patience: int = -1,
        timeout: Optional[int] = None,
        target_cutoff: Optional[float] = None,
        callbacks: Optional[list] = None,
) -> None:
    num_classes = len(CATEGORIES_MAP) - 1  # exclude 'None' class (key 7)
    class_names = [CATEGORIES_MAP[i] for i in range(num_classes)]

    train_single_task(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        history=history,
        task_name='next',
        num_classes=num_classes,
        epochs=epochs,
        max_grad_norm=max_grad_norm,
        early_stopping_patience=early_stopping_patience,
        timeout=timeout,
        target_cutoff=target_cutoff,
        callbacks=callbacks,
        compute_train_f1=True,
        diagnostic_class_names=class_names,
    )
