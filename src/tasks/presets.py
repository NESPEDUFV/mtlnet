"""Canonical ``TaskSet`` presets: legacy (category+next) and check2HGI (next+region).

A ``TaskSet`` is a pair ``(task_a, task_b)`` — the MTLnet shared-backbone
topology is always two tasks. Adding a third task would require a
different architecture (``MTLnetCGC`` / ``MTLnetPLE`` and a rewritten
runner); for now we stay with the 2-slot contract to avoid that work.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Dict, Iterator, Optional

from tasks.registry import PrimaryMetric, TaskConfig


@dataclass(frozen=True)
class TaskSet:
    """Ordered pair of task configs and a preset name.

    ``task_a`` maps to the category-slot in the legacy MTLnet topology
    (flat input by default, first in the tuple passed to ``forward``),
    ``task_b`` maps to the next-slot (sequential input). When both new
    tasks are sequential (check2HGI case), ``task_a.is_sequential`` is
    simply set to True.
    """

    name: str
    task_a: TaskConfig
    task_b: TaskConfig

    def __iter__(self) -> Iterator[TaskConfig]:
        yield self.task_a
        yield self.task_b

    @property
    def names(self) -> tuple[str, str]:
        return self.task_a.name, self.task_b.name


LEGACY_CATEGORY_NEXT = TaskSet(
    name="legacy_category_next",
    task_a=TaskConfig(
        name="category",
        num_classes=7,
        # ``head_factory=None`` routes MTLnet through its hardcoded
        # historical ``CategoryHeadTransformer`` default path (with
        # ``num_tokens=2``, ``token_dim=shared_layer_size//2``,
        # ``dropout=0.1``). That path is tied to the regression floors
        # in ``tests/test_regression`` — do not swap to an explicit
        # registry name without re-pinning the checkpoint shapes.
        head_factory=None,
        is_sequential=False,
        primary_metric=PrimaryMetric.F1,
    ),
    task_b=TaskConfig(
        name="next",
        num_classes=7,
        # Same argument: ``None`` hits the historical ``NextHeadMTL``
        # default in ``_build_next_head`` (``dropout=0.1``), bit-exact
        # with the pre-parameterisation model.
        head_factory=None,
        is_sequential=True,
        primary_metric=PrimaryMetric.F1,
    ),
)
"""The historical MTLnet pair. Defaults reproduce the pre-parameterisation
behaviour bit-exactly; do not change these fields without recalibrating
``tests/test_regression``."""


CHECK2HGI_NEXT_REGION = TaskSet(
    name="check2hgi_next_region",
    task_a=TaskConfig(
        name="next_category",
        num_classes=7,
        # Use the historical NextHeadMTL default path (dropout=0.1,
        # num_heads/seq_length/num_layers injected by MTLnet) so the
        # head is constructed identically to the legacy next slot.
        head_factory=None,
        is_sequential=True,
        primary_metric=PrimaryMetric.F1,
    ),
    task_b=TaskConfig(
        # num_classes is a placeholder — the runner resolves it from the
        # check2HGI region map before constructing the model. Alabama
        # has 1109 regions, Florida is similar in scale; see P-1 in
        # docs/plans/CHECK2HGI_MTL_BRANCH_PLAN.md.
        name="next_region",
        num_classes=0,
        # GRU head is the region-task champion per P1 head ablation on
        # AL 5f × 50ep: `next_gru` 56.94 ± 4.01 Acc@10 vs `next_mtl`
        # (Transformer) 7.40% (below random-tier for a 1109-class task).
        # The Transformer head is tuned for low-cardinality outputs
        # (7-class next-category) and does not scale to 1109/4702-class
        # region. See issues/REGION_HEAD_MISMATCH.md for the full audit.
        head_factory="next_gru",
        is_sequential=True,
        # C25 (2026-06-05): select the reg checkpoint by Acc@10 (the headline
        # metric), not Acc@1 — the deployable reg number was lagging the headline
        # ~2-3pp because the Acc@1-best epoch ≠ the Acc@10-best epoch. The disjoint
        # ``per_metric_best.top10_acc_indist`` (oracle Acc@10 epoch) is unaffected.
        primary_metric=PrimaryMetric.TOP10,
    ),
)
"""Check2HGI-track pair. Task-a (`next_category`, 7 classes) uses the
historical NextHeadMTL Transformer (its design target). Task-b
(`next_region`, ~10^3 classes) uses `next_gru` because the Transformer
collapses on high-cardinality region output."""


_PRESETS: Dict[str, TaskSet] = {
    LEGACY_CATEGORY_NEXT.name: LEGACY_CATEGORY_NEXT,
    CHECK2HGI_NEXT_REGION.name: CHECK2HGI_NEXT_REGION,
}


def get_preset(name: str) -> TaskSet:
    if name not in _PRESETS:
        raise KeyError(
            f"TaskSet preset '{name}' not found. Available: {sorted(_PRESETS)}"
        )
    return _PRESETS[name]


def list_presets() -> list[str]:
    return sorted(_PRESETS)


def resolve_task_set(
    preset: TaskSet,
    *,
    task_a_num_classes: Optional[int] = None,
    task_b_num_classes: Optional[int] = None,
    task_a_head_params: Optional[dict] = None,
    task_b_head_params: Optional[dict] = None,
    task_a_head_factory: Optional[str] = None,
    task_b_head_factory: Optional[str] = None,
) -> TaskSet:
    """Return a ``TaskSet`` with per-slot fields overridden at runtime.

    The ``CHECK2HGI_NEXT_REGION`` preset hardcodes ``task_b.num_classes=0``
    because the true region cardinality is only known after the fold
    data loads. Without this helper, callers had to reconstruct the
    whole preset field-by-field (see the pre-1.1 smoke-test code in
    ``scripts/smoke_check2hgi_mtl.py``). ``resolve_task_set`` applies
    the same overrides via ``dataclasses.replace``, staying safe under
    ``frozen=True`` and keeping call sites to one line.

    Example::

        resolved = resolve_task_set(
            CHECK2HGI_NEXT_REGION,
            task_b_num_classes=1109,   # derived from next_region.parquet
        )

    Pass ``None`` to leave a field unchanged. Passing both slot-level
    overrides in a single call is supported.
    """
    task_a = preset.task_a
    task_b = preset.task_b
    if task_a_num_classes is not None:
        task_a = dataclasses.replace(task_a, num_classes=task_a_num_classes)
    if task_a_head_params is not None:
        task_a = dataclasses.replace(task_a, head_params=task_a_head_params)
    if task_a_head_factory is not None:
        task_a = dataclasses.replace(task_a, head_factory=task_a_head_factory)
    if task_b_num_classes is not None:
        task_b = dataclasses.replace(task_b, num_classes=task_b_num_classes)
    if task_b_head_params is not None:
        task_b = dataclasses.replace(task_b, head_params=task_b_head_params)
    if task_b_head_factory is not None:
        task_b = dataclasses.replace(task_b, head_factory=task_b_head_factory)
    if task_a is preset.task_a and task_b is preset.task_b:
        return preset  # No-op; return the original so identity checks keep working.
    return dataclasses.replace(preset, task_a=task_a, task_b=task_b)


__all__ = [
    "TaskSet",
    "LEGACY_CATEGORY_NEXT",
    "CHECK2HGI_NEXT_REGION",
    "get_preset",
    "list_presets",
    "resolve_task_set",
]
