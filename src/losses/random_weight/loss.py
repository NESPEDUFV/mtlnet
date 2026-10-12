"""Random task weighting baseline."""

from __future__ import annotations

from typing import Dict, Tuple, Union

import torch

from losses.equal_weight.loss import EqualWeightLoss


class RandomWeightLoss(EqualWeightLoss):
    """Random Loss Weighting using Dirichlet-sampled task weights."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        alpha: Union[float, list[float], tuple[float, ...]] = 1.0,
        scale: float = 1.0,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if isinstance(alpha, (float, int)):
            alpha_tensor = torch.full((n_tasks,), float(alpha), device=device)
        else:
            if len(alpha) != n_tasks:
                raise ValueError(
                    f"alpha length must match n_tasks={n_tasks}, got {len(alpha)}"
                )
            alpha_tensor = torch.tensor(alpha, dtype=torch.float32, device=device)
        if torch.any(alpha_tensor <= 0):
            raise ValueError("Dirichlet alpha values must be > 0")
        if scale <= 0:
            raise ValueError(f"scale must be > 0, got {scale}")
        self.alpha = alpha_tensor
        self.scale = float(scale)

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        # MPS does not implement Dirichlet sampling; sample weights on CPU and
        # move the small vector back to the active loss device.
        alpha = self.alpha.to(device=torch.device("cpu"), dtype=torch.float32)
        weights = torch.distributions.Dirichlet(alpha).sample().to(
            device=losses.device,
            dtype=losses.dtype,
        ) * self.scale
        return torch.sum(losses * weights), {"weights": weights.detach()}


__all__ = ["RandomWeightLoss"]
