"""GO4Align-inspired risk-aware task weighting."""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class GO4AlignLoss(EqualWeightLoss):
    """GO4Align-style risk-guided weighting with dynamic task interaction signals."""

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        temperature: float = 1.0,
        ema_beta: float = 0.9,
        window_size: int = 12,
        corr_floor: float = 0.0,
        eps: float = 1e-8,
    ):
        super().__init__(n_tasks=n_tasks, device=device)
        if temperature <= 0:
            raise ValueError(f"temperature must be > 0, got {temperature}")
        if not 0.0 <= ema_beta < 1.0:
            raise ValueError(f"ema_beta must be in [0, 1), got {ema_beta}")
        if window_size < 2:
            raise ValueError(f"window_size must be >= 2, got {window_size}")
        self.temperature = float(temperature)
        self.ema_beta = float(ema_beta)
        self.window_size = int(window_size)
        self.corr_floor = float(corr_floor)
        self.eps = float(eps)
        self.ema_losses: torch.Tensor | None = None
        self.risk_history: list[torch.Tensor] = []

    def _history_correlation(self, device: torch.device, dtype: torch.dtype) -> torch.Tensor:
        if len(self.risk_history) < 2:
            return torch.eye(self.n_tasks, device=device, dtype=dtype)

        hist = torch.stack(
            [entry.to(device=device, dtype=dtype) for entry in self.risk_history],
            dim=0,
        )
        centered = hist - hist.mean(dim=0, keepdim=True)
        norm = torch.norm(centered, dim=0, keepdim=True).clamp(min=self.eps)
        corr = torch.mm(centered.t(), centered) / torch.mm(norm.t(), norm)
        corr = torch.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
        corr = torch.clamp(corr, min=-1.0, max=1.0)
        diag_idx = torch.arange(self.n_tasks, device=device)
        corr[diag_idx, diag_idx] = 1.0
        return corr

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        observed = losses.detach().to(device=losses.device, dtype=losses.dtype)
        if self.ema_losses is None:
            self.ema_losses = observed
        else:
            ema = self.ema_losses.to(device=observed.device, dtype=observed.dtype)
            self.ema_losses = (self.ema_beta * ema + (1.0 - self.ema_beta) * observed).detach()

        ema_losses = self.ema_losses.to(device=losses.device, dtype=losses.dtype)
        risk = observed / torch.clamp(ema_losses, min=self.eps)

        self.risk_history.append(risk.detach())
        if len(self.risk_history) > self.window_size:
            self.risk_history.pop(0)

        corr = self._history_correlation(device=losses.device, dtype=losses.dtype)
        interaction = torch.clamp(corr, min=self.corr_floor).mean(dim=1)
        indicators = risk * (1.0 + interaction)
        weights = torch.softmax(indicators / self.temperature, dim=-1)
        weighted = torch.sum(losses * weights.detach())

        return weighted, {
            "weights": weights.detach(),
            "risk": risk.detach(),
            "interaction": interaction.detach(),
        }


__all__ = ["GO4AlignLoss"]
