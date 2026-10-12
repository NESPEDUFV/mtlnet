"""Bayesian uncertainty-inspired multitask weighting."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses._common import compute_task_gradients
from losses.equal_weight.loss import EqualWeightLoss


class BayesAggMTLLoss(EqualWeightLoss):
    """Bayesian gradient-uncertainty aggregation (diagonal approximation)."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        ema_beta: float = 0.9,
        uncertainty_power: float = 1.0,
        eps: float = 1e-8,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if not 0.0 <= ema_beta < 1.0:
            raise ValueError(f"ema_beta must be in [0, 1), got {ema_beta}")
        if uncertainty_power <= 0:
            raise ValueError(f"uncertainty_power must be > 0, got {uncertainty_power}")
        self.ema_beta = float(ema_beta)
        self.uncertainty_power = float(uncertainty_power)
        self.eps = float(eps)
        self.running_var = torch.ones(n_tasks, device=device)
        self._initialized = False

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        grads = compute_task_gradients(losses, shared_parameters).detach()
        if grads.numel() == 0:
            weights = torch.full((self.n_tasks,), 1.0 / self.n_tasks, dtype=losses.dtype, device=losses.device)
            return torch.sum(losses * weights), {"weights": weights.detach()}

        grad_var = torch.mean(grads.pow(2), dim=1).to(device=losses.device, dtype=losses.dtype)
        if not self._initialized:
            self.running_var = torch.clamp(grad_var, min=self.eps).detach()
            self._initialized = True
        else:
            running = self.running_var.to(device=grad_var.device, dtype=grad_var.dtype)
            self.running_var = (
                self.ema_beta * running + (1.0 - self.ema_beta) * grad_var
            ).detach()

        running_var = self.running_var.to(device=losses.device, dtype=losses.dtype)
        precision = 1.0 / torch.pow(torch.clamp(running_var, min=self.eps), self.uncertainty_power)
        weights = precision / torch.clamp(precision.sum(), min=self.eps)

        weighted = torch.sum(losses * weights.detach())
        return weighted, {
            "weights": weights.detach(),
            "grad_var": running_var.detach(),
        }


__all__ = ["BayesAggMTLLoss"]
