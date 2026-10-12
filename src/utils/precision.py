"""fp16 is a documented DEFECT in this study, not a neutral speed knob — say so out loud.

Three separate code paths enable fp16 autocast **by default** on CUDA (`mtl_eval.eval_autocast_ctx`,
`_single_task_train`, `mtl_cv`), each switched off only by an env var the caller must remember:
`MTL_DISABLE_AMP=1`. Safety therefore rests on every launcher, every wave script and every future
agent getting that right, silently, every time.

That has already failed once, with consequences. `docs/studies/closing_data/v18/PRECISION_CAVEAT.md`
records a bare `export MTL_DISABLE_AMP=1` inside one shell function leaking into later cells in the
same shell: dedicated-category cells then ran **fp32 if some earlier joint cell had run first, and
fp16 otherwise** — a precision that depended on whether the wave had been resumed. Every v18
dedicated-cat number produced before the fix is affected, and the sidecars claimed fp32 throughout.

Separately, fp16 without a GradScaler NaN-collapses the wide-logit states: see
`docs/studies/closing_data/CA_MTL_DIVERGENCE.md` and the 2026-06-23 root-cause finding, where the
CA/TX epoch-30 collapse and what looked like a genuine regression gap turned out to be a precision
artifact rather than a property of the model.

So this module does not try to choose the precision — the recipe does that. It makes the choice
**audible**: a run that engages fp16 says so once, loudly, naming the caveat; and under
`MTL_STRICT=1` (which `run_lane.sh` sets on every study cell) it refuses to start at all. bf16 is
the documented fix and passes without comment.
"""
from __future__ import annotations

import logging
import os

import torch

logger = logging.getLogger(__name__)

_WARNED: set[str] = set()

_MSG = (
    "fp16 autocast is ACTIVE at %s. fp16 is a documented defect in this study, not a speed "
    "knob: it silently produced wrong dedicated-category numbers once already "
    "(docs/studies/closing_data/v18/PRECISION_CAVEAT.md — a leaked `export` made precision "
    "depend on whether the wave had been resumed), and without a GradScaler it NaN-collapses "
    "the wide-logit states (CA_MTL_DIVERGENCE.md). Every v18 cell is meant to run fp32. Pass "
    "MTL_DISABLE_AMP=1 for fp32, or MTL_AUTOCAST_BF16=1 for the documented bf16 fix."
)


def check_amp_dtype(where: str, dtype: torch.dtype) -> None:
    """Warn once per site when fp16 is engaged; hard-fail under ``MTL_STRICT=1``.

    Deliberately NOT a default flip. Changing what a bare `train.py` does would alter every
    unpinned run at once, and this repo's convention (`_preflight_canon_guards`,
    DEFAULTS_AND_GUARDS.md) is to make a silent stumble loud rather than to move the ground under
    existing recipes. What it does guarantee is that no study cell can be produced in fp16 without
    someone seeing it: the lane sets MTL_STRICT=1, so there the warning becomes a refusal.
    """
    if dtype is not torch.float16:
        return
    if os.environ.get("MTL_STRICT", "0").strip() in ("1", "true", "True"):
        raise RuntimeError(
            (_MSG % where) + " Refusing to start because MTL_STRICT=1."
        )
    if where not in _WARNED:
        _WARNED.add(where)
        logger.warning(_MSG, where)
