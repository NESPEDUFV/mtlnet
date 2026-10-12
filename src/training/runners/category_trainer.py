"""Category task trainer — thin wrapper around the unified single-task loop."""

from typing import Optional

import torch
from torch import nn
from torch.optim import Optimizer
from torch.optim.lr_scheduler import LRScheduler
from torch.utils.data import DataLoader

from tracking.fold import FoldHistory
from training.runners._single_task_train import train_single_task


def train(
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: Optimizer,
        scheduler: Optional[LRScheduler],
        device: torch.device,
        history: FoldHistory,
        num_classes: int,
        epochs: int = 2,
        max_grad_norm: float = 1.0,
        timeout: Optional[int] = None,
        target_cutoff: Optional[float] = None,
        callbacks: Optional[list] = None,
) -> None:
    train_single_task(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        history=history,
        task_name='category',
        num_classes=num_classes,
        epochs=epochs,
        max_grad_norm=max_grad_norm,
        timeout=timeout,
        target_cutoff=target_cutoff,
        callbacks=callbacks,
        compute_train_f1=False,
    )
