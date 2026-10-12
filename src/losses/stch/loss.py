"""Smooth Tchebycheff scalarization."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class STCHLoss(EqualWeightLoss):
    """Smooth Tchebycheff scalarization with warmup and nadir estimate."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        mu: float = 0.5,
        warmup_epochs: int = 1,
        eps: float = 1e-20,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if mu <= 0:
            raise ValueError(f"mu must be > 0, got {mu}")
        if warmup_epochs < 0:
            raise ValueError(f"warmup_epochs must be >= 0, got {warmup_epochs}")
        self.mu = float(mu)
        self.warmup_epochs = int(warmup_epochs)
        self.eps = float(eps)
        self.nadir_vector: torch.Tensor | None = None
        self.average_loss: torch.Tensor | None = None
        self.average_loss_count = 0

    def get_weighted_loss(self, losses: torch.Tensor, epoch: int | None = None, **kwargs) -> Tuple[torch.Tensor, Dict]:
        epoch_idx = int(epoch) if epoch is not None else 0
        ones = torch.ones(self.n_tasks, dtype=losses.dtype, device=losses.device)
        log_losses = torch.log(losses + self.eps)

        if epoch_idx < self.warmup_epochs:
            return torch.sum(log_losses), {"weights": ones.detach()}

        if epoch_idx == self.warmup_epochs and self.nadir_vector is None:
            if self.average_loss is None:
                self.average_loss = torch.zeros_like(losses.detach())
            self.average_loss = self.average_loss.to(device=losses.device, dtype=losses.dtype)
            self.average_loss = self.average_loss + losses.detach()
            self.average_loss_count += 1
            return torch.sum(log_losses), {"weights": ones.detach()}

        if self.nadir_vector is None:
            if self.average_loss is not None and self.average_loss_count > 0:
                nadir = self.average_loss / float(self.average_loss_count)
            else:
                nadir = losses.detach()
            self.nadir_vector = torch.clamp(nadir, min=self.eps).detach()

        nadir_vector = self.nadir_vector.to(device=losses.device, dtype=losses.dtype)
        stch_losses = torch.log((losses / nadir_vector) + self.eps)
        reg_losses = stch_losses - torch.max(stch_losses.detach())
        weighted = self.mu * torch.logsumexp(reg_losses / self.mu, dim=0) * self.n_tasks
        weights = torch.softmax(reg_losses / self.mu, dim=-1)
        return weighted, {
            "weights": weights.detach(),
            "nadir_vector": nadir_vector.detach(),
        }


__all__ = ["STCHLoss"]
