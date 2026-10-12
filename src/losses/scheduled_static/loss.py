"""Scheduled static-weight scalarization with linear cat → reg handover.

F40 design: keep static_weight's clean scalarization, but interpolate
``category_weight`` linearly from ``cat_weight_start`` (epoch 0) to
``cat_weight_end`` (epoch ``total_epochs - 1``). Optional ``warmup_epochs``
hold weight at ``cat_weight_start`` before the linear ramp begins.

Hypothesis: cat converges quickly under high cat_weight in the first
epochs (matching B3's behaviour), then the gradient budget shifts to
reg in the second half (matching F45's α-growth window). Pareto-lift
target — cat F1 ≥ B3 - 1 pp AND reg Acc@10 > B3 + 3 pp.

Epoch state is owned by the trainer — call ``set_epoch(e)`` at the
start of each epoch from ``mtl_cv.py``. Without that hook the loss
silently behaves like ``StaticWeightLoss(cat_weight_start)``.
"""

from __future__ import annotations

from typing import Dict, Tuple

import torch

from losses.equal_weight.loss import EqualWeightLoss


class ScheduledStaticWeightLoss(EqualWeightLoss):
    """Two-task scalarization with linearly-scheduled cat weight.

    Args:
        n_tasks: Must be 2.
        device: Torch device for output tensors.
        cat_weight_start: cat loss weight at epoch 0 (and during warmup).
        cat_weight_end: cat loss weight at epoch ``total_epochs - 1``.
        total_epochs: Total epochs the schedule should span. Required so
            the linear interpolation knows where end-of-training is.
        warmup_epochs: Epochs to hold ``cat_weight_start`` before ramping.
            Default 0 = ramp from epoch 0.

    Notes:
        ``losses[1]`` is the cat task (per StaticWeightLoss convention).
    """

    def __init__(
        self,
        n_tasks: int,
        device: torch.device,
        cat_weight_start: float = 0.75,
        cat_weight_end: float = 0.25,
        total_epochs: int = 50,
        warmup_epochs: int = 0,
        mode: str = "linear",
    ):
        if n_tasks != 2:
            raise ValueError(
                "ScheduledStaticWeightLoss currently expects exactly 2 tasks"
            )
        for name, val in (("cat_weight_start", cat_weight_start),
                          ("cat_weight_end", cat_weight_end)):
            if not 0.0 <= val <= 1.0:
                raise ValueError(f"{name} must be in [0, 1], got {val}")
        if total_epochs < 1:
            raise ValueError(f"total_epochs must be >= 1, got {total_epochs}")
        if warmup_epochs < 0 or warmup_epochs >= total_epochs:
            raise ValueError(
                f"warmup_epochs must be in [0, total_epochs), "
                f"got warmup={warmup_epochs}, total={total_epochs}"
            )
        if mode not in ("linear", "step"):
            raise ValueError(
                f"mode must be 'linear' or 'step', got {mode!r}"
            )
        super().__init__(n_tasks=n_tasks, device=device)
        self.cat_weight_start = float(cat_weight_start)
        self.cat_weight_end = float(cat_weight_end)
        self.total_epochs = int(total_epochs)
        self.warmup_epochs = int(warmup_epochs)
        self.mode = mode
        self._current_epoch = 0

    def set_epoch(self, epoch: int) -> None:
        """Record the current 0-indexed epoch. Call at start of each epoch."""
        self._current_epoch = int(epoch)

    def _current_cat_weight(self) -> float:
        e = self._current_epoch
        if e < self.warmup_epochs:
            return self.cat_weight_start
        # F50 B3 (F62) — step mode: hard transition at warmup_epochs.
        # ``cat_weight_start`` runs through the entire warmup window,
        # then jumps to ``cat_weight_end`` for the rest of training.
        # Combined with ``cat_weight_start=0.0``, this is the canonical
        # two-phase recipe: phase 1 = reg-only training (cat ignored
        # via zero loss weight; encoder still receives gradient via the
        # shared backbone), phase 2 = joint MTL fine-tune.
        if self.mode == "step":
            return self.cat_weight_end
        denom = max(1, self.total_epochs - 1 - self.warmup_epochs)
        frac = min(max((e - self.warmup_epochs) / denom, 0.0), 1.0)
        return self.cat_weight_start + frac * (self.cat_weight_end - self.cat_weight_start)

    def get_weighted_loss(self, losses: torch.Tensor, **kwargs) -> Tuple[torch.Tensor, Dict]:
        cat_w = self._current_cat_weight()
        weights = torch.tensor(
            [1.0 - cat_w, cat_w],
            dtype=losses.dtype,
            device=losses.device,
        )
        return torch.sum(losses * weights), {
            "weights": weights.detach(),
            "cat_weight_current": cat_w,
            "epoch": self._current_epoch,
        }


__all__ = ["ScheduledStaticWeightLoss"]
