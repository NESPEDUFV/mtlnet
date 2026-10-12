"""Equal scalarization baseline."""

from __future__ import annotations

from typing import Dict, List, Tuple

import torch


class EqualWeightLoss:
    """Equal loss scalarization: ``L = sum_i L_i``."""

    def __init__(self, n_tasks: int, device: torch.device):
        self.n_tasks = n_tasks
        self.device = device

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        weights = torch.ones(self.n_tasks, dtype=losses.dtype, device=losses.device)
        return torch.sum(losses * weights), {"weights": weights.detach()}

    def backward(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        loss, extra_outputs = self.get_weighted_loss(losses, **kwargs)
        loss.backward()
        return loss, extra_outputs

    def __call__(self, losses: torch.Tensor, **kwargs):
        return self.backward(losses, **kwargs)

    def parameters(self) -> List[torch.Tensor]:
        return []


__all__ = ["EqualWeightLoss"]
