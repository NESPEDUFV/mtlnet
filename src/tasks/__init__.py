"""Task configuration for MTLnet.

Two-slot MTL stays the only supported topology; the ``TaskConfig`` /
``TaskSet`` pair just renames the slots and picks their heads, metrics
and label spaces. Defaults reproduce the legacy ``{category, next}``
pair bit-exactly so regression floors stay pinned.

See ``docs/plans/CHECK2HGI_MTL_BRANCH_PLAN.md`` and
``docs/plans/CHECK2HGI_MTL_OVERVIEW.md`` for the task-selection
rationale (next-region over next-time-gap / revisit).
"""

from tasks.registry import PrimaryMetric, TaskConfig
from tasks.presets import (
    LEGACY_CATEGORY_NEXT,
    CHECK2HGI_NEXT_REGION,
    TaskSet,
    get_preset,
    resolve_task_set,
)

__all__ = [
    "PrimaryMetric",
    "TaskConfig",
    "TaskSet",
    "LEGACY_CATEGORY_NEXT",
    "CHECK2HGI_NEXT_REGION",
    "get_preset",
    "resolve_task_set",
]
