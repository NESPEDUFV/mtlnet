"""Legacy-alias location for the STAN-Flow champion reg head.

The registry key ``next_getnext_hard`` was renamed to ``next_stan_flow`` on
2026-05-01 (see ``docs/PAPER_BASELINES_STRATEGY.md §"STAN-Flow naming"``). The
class and its ``@register_model`` registration both live in
``src/models/next/next_stan_flow/head.py`` — both keys resolve to the same
class object. This module re-exports that class so the legacy import path and
this variant folder stay in sync with the canonical implementation; it adds NO
new registration (the alias is registered once, in next_stan_flow).
"""

from __future__ import annotations

from models.next.next_stan_flow.head import (
    NextHeadGETNextHard,
    NextHeadStanFlow,
)

__all__ = ["NextHeadGETNextHard", "NextHeadStanFlow"]
