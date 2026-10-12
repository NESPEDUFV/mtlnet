"""``TaskConfig`` — per-slot description of an MTL head.

Keeping the dataclass narrow on purpose: fields are what the model and
runner actually read. Wider knobs (loss weights, class-weight overrides)
belong on ``ExperimentConfig`` where the existing knobs already live.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PrimaryMetric(str, Enum):
    """Which scalar drives checkpoint monitoring for this head.

    Key names match ``tracking.metrics.compute_classification_metrics``
    (``f1`` = macro-F1, ``accuracy`` = Acc@1, ``mrr`` = mean reciprocal
    rank), so a ``PrimaryMetric`` value is a valid monitor key after the
    per-task ``val_<name>_`` prefix is added.
    """

    F1 = "f1"
    ACCURACY = "accuracy"
    MRR = "mrr"
    # C25 (2026-06-05): the headline reg metric is Acc@10 (``top10_acc_indist``,
    # merged into the reg val-metrics dict by mtl_eval — NOT from
    # compute_classification_metrics, but a valid monitor key in
    # ``val_metrics_task_b``; mtl_cv.py:849,884). The high-cardinality region head
    # should select its checkpoint by Acc@10, not Acc@1 — else the DEPLOYABLE reg
    # number lags the headline ~2-3pp (the Acc@1-best epoch ≠ the Acc@10-best epoch).
    TOP10 = "top10_acc_indist"


@dataclass(frozen=True)
class TaskConfig:
    """Per-slot task description consumed by MTLnet and the runner.

    Attributes:
        name: stable task label used in metric keys, tracking, and logs.
            Legacy slots are ``"category"`` and ``"next"``.
        num_classes: label-space size for this head. Data-derived for
            ``next_region`` (run-time); fixed at 7 for category/next.
        head_factory: model-registry name for the head, or ``None`` to
            route through ``MTLnet``'s hardcoded historical-default
            construction path (used by the legacy preset to preserve the
            bit-exact checkpoint contract).
        head_params: extra kwargs for the head factory. Required when
            ``head_factory`` names a registry model that has
            non-defaultable constructor args (e.g.
            ``category_transformer`` needs ``num_tokens`` /
            ``token_dim``). Ignored on the ``head_factory is None`` path.
        is_sequential: ``True`` if the head expects ``[B, T, D]`` inputs
            with left-padding masking, ``False`` for ``[B, D]`` flat input.
            Category-slot defaults to flat; next-slot and region heads are
            sequential.
        primary_metric: which metric drives the per-head checkpoint monitor.
            Category/next_category default to F1; next_region defaults to
            Accuracy (Acc@1) per the HMT-GRN / MGCL ranking-metric lineage
            — see ``docs/plans/CHECK2HGI_MTL_OVERVIEW.md`` §2.
    """

    name: str
    num_classes: int
    head_factory: Optional[str]
    head_params: Optional[dict] = None
    is_sequential: bool = True
    primary_metric: PrimaryMetric = PrimaryMetric.F1


__all__ = ["PrimaryMetric", "TaskConfig"]
