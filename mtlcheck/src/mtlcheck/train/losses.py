"""The three criteria this system actually uses.

The reference carries a composable criterion with seven knobs — logit adjustment, focal, label
smoothing, balanced weights, class-balanced weights, LDAM margins, and a logit scale. v18 uses
exactly three configurations of it, and the catalogue of levers records focal, class-balanced
weights and LDAM as measured and refuted. So this module implements the three, and the shapes that
were tried and rejected are not carried forward.

    plain CE                — the region head, at every state
    balanced-weighted CE    — the category head's PREVIOUS recipe, kept because it is the
                              comparator the logit-adjustment gain was measured against. It comes
                              in two reductions and they are NOT interchangeable: `weighted_mean`
                              (torch's, dividing by the sum of the batch's weights) is the v17/v18
                              incumbent that logit adjustment displaced; `batch_mean` (dividing by
                              the batch size) is the stride-9 T1.4 arm. Default is the incumbent.
    logit-adjusted CE       — the category head's current recipe (tau = 0.5)

**Every class statistic comes from the training split.** That is the leak guard, and it lives in the
caller passing training labels — so the constructor takes counts, never a dataset.

One subtlety worth stating because it changes what an ablation means: in the reference,
`--logit-adjust-tau 0` does not give plain CE. The flag only populates a calibration dict when it is
truthy, so tau=0 falls through to the *balanced-weighted* branch. The measured lever is therefore
"logit adjustment REPLACES balanced weights", not "logit adjustment versus nothing" — which is why
the middle configuration above has to exist.
"""

from __future__ import annotations

import logging

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class CategoricalLoss(nn.Module):
    """Cross-entropy with at most one calibration applied.

    `logit_adjust_tau > 0` adds `tau * log P_train(y)` to the logits **at train time only** (Menon
    et al., ICLR'21) — the Bayes-consistent estimator for balanced error, which is what macro-F1
    rewards. `balanced_weights` applies sklearn-style `w_c = N / (C * n_c)`.

    The two are mutually exclusive by construction, not by convention: stacking them was measured
    and it craters. Passing both raises.
    """

    def __init__(self, num_classes: int, *, class_counts: torch.Tensor | None = None,
                 logit_adjust_tau: float = 0.0, balanced_weights: bool = False,
                 label_smoothing: float = 0.0,
                 weight_reduction: str = "weighted_mean") -> None:
        super().__init__()
        if weight_reduction not in ("weighted_mean", "batch_mean"):
            raise ValueError(f"weight_reduction must be weighted_mean or batch_mean, "
                             f"got {weight_reduction!r}")
        self.weight_reduction = weight_reduction
        if logit_adjust_tau > 0 and balanced_weights:
            raise ValueError(
                "logit adjustment and balanced weights are mutually exclusive: the first replaces "
                "the second (stacking them was measured and it craters)"
            )
        self.num_classes = int(num_classes)
        self.logit_adjust_tau = float(logit_adjust_tau)
        self.label_smoothing = float(label_smoothing)

        needs_counts = logit_adjust_tau > 0 or balanced_weights
        if needs_counts:
            if class_counts is None:
                raise ValueError("class_counts (from the TRAIN split only) are required here")
            counts = class_counts.detach().float().clamp(min=1.0)
            if counts.numel() != self.num_classes:
                raise ValueError(
                    f"class_counts has {counts.numel()} entries, expected {self.num_classes}"
                )
        else:
            counts = None

        if logit_adjust_tau > 0:
            prior = counts / counts.sum()
            self.register_buffer("la_offset", logit_adjust_tau * torch.log(prior + 1e-12))
        else:
            self.register_buffer("la_offset", None)

        if balanced_weights:
            self.register_buffer("weight", counts.sum() / (self.num_classes * counts))
        else:
            self.register_buffer("weight", None)

    def forward(self, logits: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        if self.la_offset is not None:
            logits = logits + self.la_offset
        # With class weights, the two reductions are DIFFERENT ESTIMATORS: torch's weighted mean
        # divides by the sum of the batch's weights, the per-row mean divides by the batch size. On
        # a skewed prior they differ by a factor of several, varying per batch — a different
        # training trajectory, not a rounding difference.
        #
        # Both exist in the reference, in different places, and which one is "the comparator" for
        # the logit-adjustment lever depends on which arm you mean:
        #   weighted_mean  nn.CrossEntropyLoss(weight=alpha, reduction='mean') — the v17/v18
        #                  incumbent that logit adjustment DISPLACED (next_cv.py's else branch)
        #   batch_mean     CalibratedLoss(tail_mode='balanced') — the stride-9 T1.4 arm
        if self.weight is None or self.weight_reduction == "batch_mean":
            per_row = F.cross_entropy(
                logits, target, reduction="none",
                label_smoothing=self.label_smoothing, weight=self.weight,
            )
            return per_row.mean()
        return F.cross_entropy(
            logits, target, reduction="mean",
            label_smoothing=self.label_smoothing, weight=self.weight,
        )

    def extra_repr(self) -> str:
        kind = ("logit_adjust tau=%.2f" % self.logit_adjust_tau if self.la_offset is not None
                else "balanced" if self.weight is not None else "plain")
        return f"num_classes={self.num_classes}, {kind}"


def class_counts(labels, num_classes: int) -> torch.Tensor:
    """Per-class counts from the TRAINING split.

    Takes labels rather than a dataset so that the leak guard is visible at the call site: whoever
    calls this has to name which split they are passing.
    """
    values = torch.as_tensor(np.asarray(labels)).detach().cpu().reshape(-1).to(torch.long)
    return torch.bincount(values, minlength=num_classes)


def build(num_classes: int, train_labels, *, logit_adjust_tau: float = 0.0,
          balanced_weights: bool = False, label_smoothing: float = 0.0,
          weight_reduction: str = "weighted_mean",
          device: torch.device | None = None) -> CategoricalLoss:
    """Factory. `train_labels` must be the training split's labels — never validation's."""
    counts = (class_counts(train_labels, num_classes)
              if (logit_adjust_tau > 0 or balanced_weights) else None)
    loss = CategoricalLoss(
        num_classes, class_counts=counts,
        logit_adjust_tau=logit_adjust_tau, balanced_weights=balanced_weights,
        label_smoothing=label_smoothing, weight_reduction=weight_reduction,
    )
    return loss.to(device) if device is not None else loss


__all__ = ["CategoricalLoss", "build", "class_counts"]
