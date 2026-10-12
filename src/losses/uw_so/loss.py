"""Soft-optimal uncertainty weighting."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class SoftOptimalUncertaintyWeightingLoss(EqualWeightLoss):
    """Soft Optimal Uncertainty weighting (UW-SO style)."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        temperature: float = 1.0,
        eps: float = 1e-8,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if temperature <= 0:
            raise ValueError(f"temperature must be > 0, got {temperature}")
        if eps <= 0:
            raise ValueError(f"eps must be > 0, got {eps}")
        self.temperature = float(temperature)
        self.eps = float(eps)

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        safe_losses = torch.clamp(losses.detach(), min=self.eps)
        logits = -torch.log(safe_losses) / self.temperature
        weights = torch.softmax(logits, dim=-1).to(dtype=losses.dtype, device=losses.device)
        weighted = torch.sum(losses * weights.detach())
        return weighted, {"weights": weights.detach()}


__all__ = ["SoftOptimalUncertaintyWeightingLoss"]
