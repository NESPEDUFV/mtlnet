"""FAMO-style adaptive task weighting."""

from __future__ import annotations

from typing import Dict, List, Tuple, Union

import torch
import torch.nn.functional as F

from losses.equal_weight.loss import EqualWeightLoss


class FAMOLoss(EqualWeightLoss):
    """Fast Adaptive Multitask Optimization-style dynamic weighting."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        weight_lr: float = 0.025,
        gamma: float = 0.001,
        eps: float = 1e-8,
        min_losses: Union[float, list[float], tuple[float, ...], None] = None,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        self.eps = float(eps)
        if min_losses is None:
            min_losses_tensor = torch.zeros(n_tasks, device=device)
        elif isinstance(min_losses, (float, int)):
            min_losses_tensor = torch.full((n_tasks,), float(min_losses), device=device)
        else:
            if len(min_losses) != n_tasks:
                raise ValueError(
                    f"min_losses length must match n_tasks={n_tasks}, got {len(min_losses)}"
                )
            min_losses_tensor = torch.tensor(min_losses, dtype=torch.float32, device=device)

        self.min_losses = min_losses_tensor
        self.logits = torch.nn.Parameter(torch.zeros(n_tasks, device=device))
        self._optimizer = torch.optim.Adam([self.logits], lr=weight_lr, weight_decay=gamma)
        self._previous_losses: torch.Tensor | None = None

    def _positive_losses(self, losses: torch.Tensor, detach: bool = True) -> torch.Tensor:
        min_losses = self.min_losses.to(device=losses.device, dtype=losses.dtype)
        source = losses.detach() if detach else losses
        return torch.clamp(source - min_losses, min=self.eps)

    def _update_logits(self, current_losses: torch.Tensor) -> None:
        current = self._positive_losses(current_losses, detach=True)
        if self._previous_losses is None:
            self._previous_losses = current
            return

        previous = self._previous_losses.to(device=current.device, dtype=current.dtype)
        delta = torch.log(previous) - torch.log(current)

        with torch.enable_grad():
            weights = F.softmax(self.logits, dim=-1)
            grad = torch.autograd.grad(
                weights,
                self.logits,
                grad_outputs=delta.detach(),
                retain_graph=False,
            )[0]

        self._optimizer.zero_grad(set_to_none=True)
        self.logits.grad = grad
        self._optimizer.step()
        self._previous_losses = current

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        self._update_logits(losses)

        weights = F.softmax(self.logits, dim=-1).to(device=losses.device, dtype=losses.dtype)
        positive_losses = self._positive_losses(losses, detach=False).to(dtype=losses.dtype)
        normalizer = torch.sum(weights.detach() / positive_losses).detach()
        weighted = torch.sum(torch.log(positive_losses) * weights.detach() / normalizer)

        return weighted, {
            "weights": weights.detach(),
        }

    def parameters(self) -> List[torch.Tensor]:
        # FAMO owns a private optimizer for task logits.
        return []


__all__ = ["FAMOLoss"]
