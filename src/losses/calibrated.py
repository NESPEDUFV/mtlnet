"""STL loss calibration for the MTL-improvement study (T1.4).

A single composable criterion for the leak-free per-task HP tune of the
incumbent STL heads (the T1.4 floor). All calibration knobs derive their
class statistics from the **training split only** (counts passed in as
``class_counts``) — never from validation — so there is no F49-class leak.

Knobs (all default to OFF → the criterion reduces to plain ``CrossEntropyLoss``):

- ``logit_adjust_tau`` > 0 — Menon et al. (ICLR'21) *logit adjustment*. Adds
  ``tau * log P_train(y)`` to the logits at train time; the Bayes-consistent
  estimator for the *balanced* (macro) error. The cat arm's primary lever
  (macro-F1 is the cat metric).
- ``focal_gamma`` > 0 — Lin et al. focal down-weighting ``(1 - p_t)^gamma``.
- ``label_smoothing`` — standard CE label smoothing (passed straight through).
- ``tail_mode`` — imbalance handling (class re-weighting / margins):
    * ``'balanced'`` — sklearn-style balanced weights ``w_c = N / (C · n_c)``
      (== ``compute_class_weights``; reproduces the next_cv.py cat ceiling).
    * ``'cb'``  — Class-Balanced weights (Cui et al. CVPR'19):
      ``w_c ∝ (1 - beta) / (1 - beta^{n_c})``, normalised to mean 1.
    * ``'ldam'`` — LDAM margins (Cao et al. NeurIPS'19): enforce a per-class
      margin ``m_c ∝ n_c^{-1/4}`` (scaled so ``max_c m_c = ldam_max_m``) and a
      logit ``scale``.

The knobs compose: logit-adjust shifts the logits, LDAM subtracts the
true-class margin, then CE/focal is computed with optional CB class weights.
At all-default settings ``forward`` is bit-identical to
``F.cross_entropy(logits, target, reduction='mean')``.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = ["CalibratedLoss", "build_calibrated_loss"]


class CalibratedLoss(nn.Module):
    """Composable, train-statistics-only calibrated cross-entropy.

    Parameters
    ----------
    num_classes : int
    class_counts : 1-D LongTensor[num_classes] | None
        Per-class TRAIN counts. Required when ``logit_adjust_tau > 0`` or
        ``tail_mode`` is set; ignored otherwise. Must come from the training
        split only (the caller's leak guard).
    label_smoothing, focal_gamma, logit_adjust_tau : float
    tail_mode : {'balanced', 'cb', 'ldam', None}
    cb_beta : float            # Class-Balanced re-weighting beta
    ldam_max_m, ldam_scale : float
    """

    def __init__(
        self,
        num_classes: int,
        *,
        class_counts: torch.Tensor | None = None,
        label_smoothing: float = 0.0,
        focal_gamma: float = 0.0,
        logit_adjust_tau: float = 0.0,
        tail_mode: str | None = None,
        cb_beta: float = 0.999,
        ldam_max_m: float = 0.5,
        ldam_scale: float = 30.0,
    ) -> None:
        super().__init__()
        self.num_classes = int(num_classes)
        self.label_smoothing = float(label_smoothing)
        self.focal_gamma = float(focal_gamma)
        self.logit_adjust_tau = float(logit_adjust_tau)
        self.tail_mode = tail_mode
        self.ldam_scale = float(ldam_scale)

        needs_counts = logit_adjust_tau > 0 or tail_mode in ("balanced", "cb", "ldam")
        if needs_counts:
            if class_counts is None:
                raise ValueError(
                    "class_counts (train-only) required for logit-adjust / tail-loss"
                )
            counts = class_counts.detach().float().clamp(min=1.0)
            if counts.numel() != self.num_classes:
                raise ValueError(
                    f"class_counts has {counts.numel()} entries, expected {self.num_classes}"
                )
        else:
            counts = None

        # --- logit-adjustment offset: tau * log(prior) -----------------------
        if logit_adjust_tau > 0:
            prior = counts / counts.sum()
            self.register_buffer("la_offset", logit_adjust_tau * torch.log(prior + 1e-12))
        else:
            self.register_buffer("la_offset", None)

        # --- class re-weighting (balanced / class-balanced) ------------------
        if tail_mode == "balanced":
            # sklearn 'balanced': w_c = N / (C * n_c). Matches compute_class_weights
            # so this reproduces the next_cv.py cat ceiling exactly.
            w = counts.sum() / (self.num_classes * counts)
            self.register_buffer("cb_weight", w)
        elif tail_mode == "cb":
            eff_num = 1.0 - torch.pow(torch.as_tensor(cb_beta, dtype=counts.dtype), counts)
            w = (1.0 - cb_beta) / eff_num
            w = w / w.sum() * self.num_classes  # normalise to mean 1
            self.register_buffer("cb_weight", w)
        else:
            self.register_buffer("cb_weight", None)

        # --- LDAM per-class margins ------------------------------------------
        if tail_mode == "ldam":
            m = 1.0 / torch.sqrt(torch.sqrt(counts))  # n_c^{-1/4}
            m = m * (ldam_max_m / m.max())
            self.register_buffer("ldam_m", m)
        else:
            self.register_buffer("ldam_m", None)

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        if self.la_offset is not None:
            logits = logits + self.la_offset

        if self.ldam_m is not None:
            batch_m = self.ldam_m[target]  # [B]
            adjusted = logits.clone()
            idx = torch.arange(logits.size(0), device=logits.device)
            adjusted[idx, target] = adjusted[idx, target] - batch_m
            logits = self.ldam_scale * adjusted

        ce = F.cross_entropy(
            logits, target, reduction="none",
            label_smoothing=self.label_smoothing,
            weight=self.cb_weight,
        )
        if self.focal_gamma > 0:
            # p_t from the (logit-adjusted / LDAM-scaled) logits actually used.
            with torch.no_grad():
                pt = F.softmax(logits, dim=-1).gather(1, target.unsqueeze(1)).squeeze(1)
            ce = (1.0 - pt) ** self.focal_gamma * ce
        return ce.mean()

    def extra_repr(self) -> str:
        return (
            f"num_classes={self.num_classes}, ls={self.label_smoothing}, "
            f"focal_gamma={self.focal_gamma}, la_tau={self.logit_adjust_tau}, "
            f"tail_mode={self.tail_mode}"
        )


def build_calibrated_loss(
    num_classes: int,
    y_train: torch.Tensor | None = None,
    *,
    label_smoothing: float = 0.0,
    focal_gamma: float = 0.0,
    logit_adjust_tau: float = 0.0,
    tail_mode: str | None = None,
    cb_beta: float = 0.999,
    ldam_max_m: float = 0.5,
    ldam_scale: float = 30.0,
    device: torch.device | str | None = None,
) -> CalibratedLoss:
    """Factory: derive the train-only class counts from ``y_train`` and build.

    ``y_train`` is a 1-D LongTensor of TRAIN labels (the leak guard lives in the
    caller passing the training-split labels). Required when any class-statistic
    knob is active; may be ``None`` for the plain-CE configuration.
    """
    needs_counts = logit_adjust_tau > 0 or tail_mode in ("balanced", "cb", "ldam")
    counts = None
    if needs_counts:
        if y_train is None:
            raise ValueError("y_train required when logit-adjust / tail-loss is active")
        # Coerce numpy / MPS / CUDA tensors to a CPU long tensor for bincount.
        yt = torch.as_tensor(y_train)
        counts = torch.bincount(yt.detach().cpu().to(torch.long).reshape(-1), minlength=num_classes)
    crit = CalibratedLoss(
        num_classes,
        class_counts=counts,
        label_smoothing=label_smoothing,
        focal_gamma=focal_gamma,
        logit_adjust_tau=logit_adjust_tau,
        tail_mode=tail_mode,
        cb_beta=cb_beta,
        ldam_max_m=ldam_max_m,
        ldam_scale=ldam_scale,
    )
    if device is not None:
        crit = crit.to(device)
    return crit
