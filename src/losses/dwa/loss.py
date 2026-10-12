"""Dynamic Weight Average (DWA) for multi-task learning.

Reference:
    Liu et al., "End-to-End Multi-Task Learning with Attention",
    CVPR 2019. https://arxiv.org/abs/1803.10704

Adapted from LibMTL integration:
    https://github.com/median-research-group/LibMTL
"""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class DWALoss(EqualWeightLoss):
    """Dynamic Weight Average: weights based on loss rate of change.

    Tasks whose loss decreased less (or increased) get higher weight.
    Temperature T controls sensitivity: high T -> equal weighting,
    low T -> aggressive rebalancing.
    """

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        temperature: float = 2.0,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if temperature <= 0:
            raise ValueError(f"temperature must be > 0, got {temperature}")
        self.temperature = float(temperature)
        self.prev_losses: torch.Tensor | None = None
        self.prev_prev_losses: torch.Tensor | None = None

    def get_weighted_loss(
        self,
        losses: torch.Tensor,
        **kwargs,
    ) -> Tuple[torch.Tensor, Dict]:
        current = losses.detach()

        if self.prev_losses is None or self.prev_prev_losses is None:
            # Not enough history yet -- use equal weights.
            if self.prev_losses is not None:
                self.prev_prev_losses = self.prev_losses
            self.prev_losses = current
            weights = torch.ones(self.n_tasks, dtype=losses.dtype, device=losses.device)
            return torch.sum(losses * weights), {"weights": weights}

        # Rate of change: r_t(i) = L_{t-1}(i) / L_{t-2}(i).
        prev = self.prev_losses.to(device=losses.device, dtype=losses.dtype)
        prev_prev = self.prev_prev_losses.to(device=losses.device, dtype=losses.dtype)
        ratio = prev / prev_prev.clamp(min=1e-12)

        # Softmax weighting with temperature.
        weights = torch.softmax(ratio / self.temperature, dim=-1) * self.n_tasks

        # Update history.
        self.prev_prev_losses = self.prev_losses
        self.prev_losses = current

        weighted = torch.sum(losses * weights.detach())
        return weighted, {"weights": weights.detach()}


__all__ = ["DWALoss"]
