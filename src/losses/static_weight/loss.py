"""Static two-task scalarization baseline."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class StaticWeightLoss(EqualWeightLoss):
    """Static two-task scalarization.

    ``category_weight`` applies to ``losses[1]``.
    The next-task weight is ``1 - category_weight``.
    """

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        category_weight: float = 0.5,
    ):
        if n_tasks != 2:
            raise ValueError("StaticWeightLoss currently expects exactly 2 tasks")
        if not 0.0 <= category_weight <= 1.0:
            raise ValueError(
                f"category_weight must be in [0, 1], got {category_weight}"
            )
        super().__init__(n_tasks=n_tasks, device=device)
        self.category_weight = float(category_weight)

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        weights = torch.tensor(
            [1.0 - self.category_weight, self.category_weight],
            dtype=losses.dtype,
            device=losses.device,
        )
        return torch.sum(losses * weights), {"weights": weights.detach()}


__all__ = ["StaticWeightLoss"]
