"""FairGrad-style task weighting."""

from __future__ import annotations

import logging
from typing import Dict, Tuple

import torch

from losses._common import compute_task_gradients
from losses.equal_weight.loss import EqualWeightLoss

logger = logging.getLogger(__name__)


class FairGradLoss(EqualWeightLoss):
    """FairGrad-style weighting using gradient Gram matrix matching."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        alpha: float = 1.0,
        solver_steps: int = 25,
        step_size: float = 0.1,
        eps: float = 1e-8,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if alpha <= 0:
            raise ValueError(f"alpha must be > 0, got {alpha}")
        if solver_steps <= 0:
            raise ValueError(f"solver_steps must be > 0, got {solver_steps}")
        if step_size <= 0:
            raise ValueError(f"step_size must be > 0, got {step_size}")
        self.alpha = float(alpha)
        self.solver_steps = int(solver_steps)
        self.step_size = float(step_size)
        self.eps = float(eps)
        self._weights = torch.full((n_tasks,), 1.0 / n_tasks, device=device)

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        shared_parameters=None,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        grads = compute_task_gradients(losses, shared_parameters)
        if grads.numel() == 0:
            weights = torch.full((self.n_tasks,), 1.0 / self.n_tasks, device=losses.device, dtype=losses.dtype)
            return torch.sum(losses * weights), {"weights": weights.detach()}

        gtg = torch.mm(grads, grads.t()).detach().to(device=losses.device, dtype=losses.dtype)
        gtg = gtg + self.eps * torch.eye(self.n_tasks, device=gtg.device, dtype=gtg.dtype)

        weights = self._weights.to(device=losses.device, dtype=losses.dtype)
        residual_norm = torch.tensor(float("nan"), device=losses.device, dtype=losses.dtype)
        converged = False
        for _ in range(self.solver_steps):
            rhs = torch.pow(torch.clamp(weights, min=self.eps), -1.0 / self.alpha)
            residual = torch.mv(gtg, weights) - rhs
            residual_norm = torch.norm(residual)
            if residual_norm < 1e-6:
                converged = True
                break
            weights = torch.clamp(weights - self.step_size * residual, min=self.eps)
            weights = weights / torch.clamp(torch.sum(weights), min=self.eps)
        if not converged:
            logger.warning(
                "FairGrad solver did not converge after %d steps "
                "(residual_norm=%.4e). Consider tuning step_size or solver_steps.",
                self.solver_steps,
                residual_norm.item(),
            )

        self._weights = weights.detach().to(device=self.device, dtype=torch.float32)
        weighted = torch.sum(losses * weights.detach())
        return weighted, {
            "weights": weights.detach(),
            "solver_residual": residual_norm.detach(),
        }


__all__ = ["FairGradLoss"]
