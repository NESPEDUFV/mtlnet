"""Homoscedastic uncertainty weighting."""

from __future__ import annotations

from typing import Dict, List, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class UncertaintyWeightingLoss(EqualWeightLoss):
    """Homoscedastic uncertainty weighting for task losses."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        initial_log_var: float = 0.0,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        self.log_vars = torch.nn.Parameter(
            torch.full((n_tasks,), float(initial_log_var), device=device)
        )

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        log_vars = self.log_vars.to(device=losses.device, dtype=losses.dtype)
        precision = torch.exp(-log_vars)
        weighted = torch.sum(precision * losses + log_vars)
        return weighted, {
            "weights": precision.detach(),
            "log_vars": log_vars.detach(),
        }

    def parameters(self) -> List[torch.Tensor]:
        return [self.log_vars]


__all__ = ["UncertaintyWeightingLoss"]
