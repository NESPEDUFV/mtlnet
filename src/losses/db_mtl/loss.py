"""Dual-balancing multitask weighting."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses._common import compute_task_gradients
from losses.equal_weight.loss import EqualWeightLoss


class DBMTLLoss(EqualWeightLoss):
    """Dual-Balancing MTL style weighting from buffered log-loss gradients."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        beta: float = 0.9,
        beta_sigma: float = 0.5,
        eps: float = 1e-8,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if beta < 0:
            raise ValueError(f"beta must be >= 0, got {beta}")
        if beta_sigma < 0:
            raise ValueError(f"beta_sigma must be >= 0, got {beta_sigma}")
        self.beta = float(beta)
        self.beta_sigma = float(beta_sigma)
        self.eps = float(eps)
        self.step = 0
        self.grad_buffer: torch.Tensor | None = None

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        self.step += 1
        log_losses = torch.log(losses + self.eps)
        batch_grads = compute_task_gradients(log_losses, shared_parameters).detach()
        if batch_grads.numel() == 0:
            weights = torch.ones(self.n_tasks, dtype=losses.dtype, device=losses.device)
            return torch.sum(losses * weights), {"weights": weights.detach()}

        if self.grad_buffer is None:
            self.grad_buffer = torch.zeros_like(batch_grads)
        self.grad_buffer = self.grad_buffer.to(device=batch_grads.device, dtype=batch_grads.dtype)

        beta_t = self.beta / (float(self.step) ** self.beta_sigma)
        self.grad_buffer = batch_grads + beta_t * (self.grad_buffer - batch_grads)

        grad_norms = torch.norm(self.grad_buffer, dim=-1)
        alpha = grad_norms.max() / torch.clamp(grad_norms, min=self.eps)
        alpha = alpha / torch.clamp(alpha.sum(), min=self.eps) * self.n_tasks

        weighted = torch.sum(losses * alpha.detach())
        return weighted, {"weights": alpha.detach()}


__all__ = ["DBMTLLoss"]
