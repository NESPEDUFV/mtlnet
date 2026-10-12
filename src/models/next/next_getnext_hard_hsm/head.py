"""Legacy-alias location for the STAN-Flow hierarchical-additive (HSM) reg head.

The registry key ``next_getnext_hard_hsm`` was renamed to
``next_stan_flow_hsm`` on 2026-05-01. The class and its ``@register_model``
registration both live in ``src/models/next/next_stan_flow_hsm/head.py`` — both
keys resolve to the same class object. This module re-exports that class so the
legacy import path and this variant folder stay in sync with the canonical
implementation; it adds NO new registration (the alias is registered once, in
next_stan_flow_hsm).
"""

from __future__ import annotations

from models.next.next_stan_flow_hsm.head import (
    NextHeadGETNextHardHSM,
    NextHeadStanFlowHSM,
)

__all__ = ["NextHeadGETNextHardHSM", "NextHeadStanFlowHSM"]
