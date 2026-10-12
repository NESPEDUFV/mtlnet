"""ExcessMTL-style robust weighting."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses._common import compute_task_gradients
from losses.equal_weight.loss import EqualWeightLoss


class ExcessMTLLoss(EqualWeightLoss):
    """ExcessMTL-style robust weighting from gradient excess risk."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        robust_step_size: float = 1e-2,
        eps: float = 1e-7,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if robust_step_size <= 0:
            raise ValueError(f"robust_step_size must be > 0, got {robust_step_size}")
        self.robust_step_size = float(robust_step_size)
        self.eps = float(eps)
        # Lazy-reshaped on first call to match grads shape from
        # compute_task_gradients (n_tasks, flattened_params).
        self.grad_sum = torch.empty(0, device=device)
        self.initial_w = torch.zeros(n_tasks, device=device)
        self._initial_w_set = False
        self.loss_weight = torch.ones(n_tasks, device=device)

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        grads = compute_task_gradients(losses, shared_parameters).detach()
        if grads.numel() == 0:
            weights = torch.ones(self.n_tasks, dtype=losses.dtype, device=losses.device)
            return torch.sum(losses * weights), {"weights": weights.detach()}

        if self.grad_sum.shape != grads.shape:
            self.grad_sum = torch.zeros_like(grads)
        self.grad_sum = self.grad_sum.to(device=grads.device, dtype=grads.dtype)

        self.grad_sum = self.grad_sum + grads.pow(2)
        h = torch.sqrt(self.grad_sum + self.eps)
        w = torch.sum((grads * grads) / h, dim=1)

        if not self._initial_w_set:
            self.initial_w = torch.clamp(w.detach(), min=self.eps)
            self._initial_w_set = True
        else:
            normalized = w / torch.clamp(
                self.initial_w.to(device=w.device, dtype=w.dtype),
                min=self.eps,
            )
            step_size = float(kwargs.get("robust_step_size", self.robust_step_size))
            updated = self.loss_weight.to(device=w.device, dtype=w.dtype) * torch.exp(normalized * step_size)
            updated = updated / torch.clamp(updated.sum(), min=self.eps) * self.n_tasks
            self.loss_weight = updated.detach()

        weights = self.loss_weight.to(device=losses.device, dtype=losses.dtype)
        weighted = torch.sum(losses * weights.detach())
        return weighted, {"weights": weights.detach()}


__all__ = ["ExcessMTLLoss"]
