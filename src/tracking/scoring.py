"""Standard MTL scoring — the SINGLE SOURCE OF TRUTH for epoch-selection conventions.

Why this module exists (2026-07 scoring-standardization fix): the MobiWac Table-3 MTL
cells were produced by ``scripts/closing_data/a40_score_matched.py`` under the per-task
DIAGNOSTIC-BEST convention (cat = macro-F1 at the cat-F1-best epoch; reg = full top10
= ``top10_acc_indist * (1 - ood_fraction)`` at the indist-best epoch — TWO different
epochs per fold), while training saves ONE joint checkpoint per fold gated by the
``geom_simple`` selector (``mtl_cv._compute_joint_selectors``). Nobody ever scored the
joint checkpoint; the author believed the paper numbers were joint-checkpoint numbers.
To make that mistake unrepeatable, every MTL fold now self-reports BOTH conventions in
one canonical write-only artifact, and any post-hoc re-scoring must go through the pure
functions here (``scripts/closing_data/score_joint_best.py`` imports this module).
Full story + usage: ``docs/studies/closing_data/JOINT_BEST_SCORING.md``.

The two conventions
-------------------
* **diag-best** (per-task diagnostic-best; the submitted-paper convention, disclosed in
  the paper's §6.2): each task reported at its OWN best validation epoch. UNGATED
  (matches ``a40_score_matched.py``: argmax over all epochs; note training's per-task
  ``BestModelTracker`` applies ``min_epoch`` — identical on the v17 board where
  ``min_best_epoch=0``).
* **joint-best** (single-checkpoint; the deployable convention): both tasks reported at
  the SAME epoch ``e* = argmax_e selector(e)`` over epochs with 0-based index
  ``>= min_best_epoch`` (the exact ``joint_eligible`` gate in ``mtl_cv.py``); ties go to
  the EARLIEST epoch (training uses strict ``>`` improvement). For the default
  ``geom_simple`` selector, ``selector(e) = sqrt(max(cat_f1(e),0) * max(reg_top10_indist(e),0))``
  with the training-time fallback ``reg_top10_indist -> reg f1`` when the reg task has
  no ``top10_acc_indist`` metric.

Artifact contract — ``metrics/fold{N}_standard_scores.json``
------------------------------------------------------------
Written per fold at fold end by ``HistoryStorage`` (see ``storage.py``), named by REAL
fold id (fan-out safe), default-on, write-only, exception-proof. All metric values are
RAW FRACTIONS in [0, 1] (same units as the ``fold{N}_{task}_val.csv`` files); epochs are
1-BASED (same as the CSV ``epoch`` column). Schema (``schema_version`` 1)::

    {
      "schema_version": 1,
      "fold": <1-based real fold id>,            # added by the storage hook
      "cat_task": "...", "reg_task": "...",      # added by the storage hook
      "selector_name": "geom_simple",
      "min_best_epoch": 0,                        # the 0-based joint gate value
      "reg_metric_used": "top10_acc_indist",     # or "f1" (training-time fallback)
      "selector_source": "model_task_val_f1" | "recomputed",
      "cat_diag_best":  {"epoch", "f1"},
      "reg_diag_best":  {"epoch", "top10_indist", "ood_fraction", "top10_full"},
      "joint_best":     {"epoch", "selector", "cat_f1",
                         "top10_indist", "ood_fraction", "top10_full"} | null,
      "checkpoint_epoch": <1-based epoch of the ACTUALLY-SAVED joint checkpoint> | null,
      "warnings": [...]
    }

This module is deliberately stdlib-pure (no torch / pandas / numpy imports) so the
CPU-only post-hoc scorer can load it directly without the package ``__init__``.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

SCHEMA_VERSION = 1

# Selectors recomputable from the two per-task metric series alone.
# ``geom_lift`` needs the per-fold majority fractions (not in the CSVs) and is
# only scorable from a recorded selector series (``model_task`` val ``f1``).
RECOMPUTABLE_SELECTORS = ("geom_simple", "joint_f1_mean")


def _first_argmax(values: Sequence[float], start: int = 0) -> Tuple[int, float]:
    """Index/value of the max over ``values[start:]``; ties -> EARLIEST index
    (matches the strict ``>`` improvement rule of training's trackers).
    Returns ``(-1, nan)`` when no eligible index exists."""
    best_i, best_v = -1, float("-inf")
    for i in range(max(start, 0), len(values)):
        if values[i] > best_v:
            best_i, best_v = i, values[i]
    if best_i < 0:
        return -1, float("nan")
    return best_i, best_v


def selector_value(selector_name: str, cat_f1: float, reg_metric: float,
                   reg_f1: Optional[float] = None) -> float:
    """One epoch's joint-selector value. Mirrors ``mtl_cv._compute_joint_selectors``:
    ``geom_simple`` = sqrt(max(cat_f1,0) * max(reg_metric,0));
    ``joint_f1_mean`` = 0.5 * (reg_f1 + cat_f1) (the v11 legacy selector)."""
    if selector_name == "joint_f1_mean":
        rf = reg_f1 if reg_f1 is not None else reg_metric
        return 0.5 * (rf + cat_f1)
    if selector_name == "geom_simple":
        return math.sqrt(max(cat_f1, 0.0) * max(reg_metric, 0.0))
    raise ValueError(
        f"selector {selector_name!r} is not recomputable from per-task series; "
        f"supported: {RECOMPUTABLE_SELECTORS} (or pass selector_series)"
    )


def compute_standard_scores(
    cat_val: Mapping[str, Sequence[float]],
    reg_val: Mapping[str, Sequence[float]],
    *,
    selector_name: str = "geom_simple",
    min_best_epoch: int = 0,
    selector_series: Optional[Sequence[float]] = None,
) -> Optional[Dict[str, Any]]:
    """Compute the standard scores dict (see module docstring schema, minus the
    hook-added keys) from two per-epoch metric-series mappings.

    Parameters
    ----------
    cat_val / reg_val:
        ``{metric_name: [v_epoch1, v_epoch2, ...]}`` — the val series of the cat and
        reg task (a ``MetricStore`` works directly; so does a dict built from a
        ``fold{N}_{task}_val.csv``). Positional alignment: index ``i`` of every series
        is epoch ``i+1`` (1-based CSV convention).
    selector_name:
        The configured ``--checkpoint-selector``. ``geom_simple`` (default) and
        ``joint_f1_mean`` are recomputed; anything else requires ``selector_series``.
    min_best_epoch:
        The 0-based joint-checkpoint gate (``joint_eligible = epoch_idx >= joint_min_epoch``
        in ``mtl_cv.py``). NOT applied to the diag-best blocks (a40 convention).
    selector_series:
        Optional per-epoch selector values recorded at training time
        (``fold.model_task.val['f1']`` — exact for ANY selector). Used only if its
        length matches the aligned joint range.

    Returns ``None`` when either task lacks an ``f1`` series (nothing to score).
    """
    warnings: List[str] = []
    cat_f1 = list(cat_val.get("f1") or [])
    reg_f1 = list(reg_val.get("f1") or [])
    if not cat_f1 or not reg_f1:
        return None

    reg_top10 = list(reg_val.get("top10_acc_indist") or [])
    if reg_top10:
        reg_metric_used = "top10_acc_indist"
        reg_series = reg_top10
    else:
        # Training-time fallback: reg_acc10_val = metrics.get('top10_acc_indist', f1).
        reg_metric_used = "f1"
        reg_series = reg_f1
        warnings.append(
            "reg task has no top10_acc_indist series; using its f1 "
            "(mirrors the training-time selector fallback)"
        )

    ood = list(reg_val.get("ood_fraction") or [])
    if not ood:
        warnings.append("reg task has no ood_fraction series; treating ood_fraction as 0.0")
        ood = [0.0] * len(reg_series)
    elif len(ood) < len(reg_series):
        warnings.append(
            f"ood_fraction series shorter than reg metric series "
            f"({len(ood)} < {len(reg_series)}); padding with 0.0"
        )
        ood = ood + [0.0] * (len(reg_series) - len(ood))

    def _full(idx: int) -> float:
        return reg_series[idx] * (1.0 - ood[idx])

    # --- diag-best: each task at its OWN best epoch, over its FULL series, UNGATED
    # (the a40_score_matched.py / paper-Table-3 convention).
    c_i, c_v = _first_argmax(cat_f1)
    r_i, r_v = _first_argmax(reg_series)
    cat_diag = {"epoch": c_i + 1, "f1": c_v}
    reg_diag = {
        "epoch": r_i + 1,
        "top10_indist": r_v,
        "ood_fraction": ood[r_i],
        "top10_full": _full(r_i),
    }

    # --- joint-best: one epoch for both tasks, min-epoch gated.
    n = min(len(cat_f1), len(reg_series))
    if len(cat_f1) != len(reg_series):
        warnings.append(
            f"unequal series lengths (cat {len(cat_f1)} vs reg {len(reg_series)}); "
            f"joint selection restricted to the common {n} epochs"
        )

    selector_source = "recomputed"
    if selector_series is not None and len(selector_series) >= n:
        sel = list(selector_series[:n])
        selector_source = "model_task_val_f1"
        if len(selector_series) != n:
            warnings.append(
                f"selector_series length {len(selector_series)} != joint range {n}; truncated"
            )
    else:
        if selector_series is not None:
            warnings.append(
                f"selector_series shorter ({len(selector_series)}) than joint range {n}; recomputing"
            )
        sel = [
            selector_value(selector_name, cat_f1[i], reg_series[i], reg_f1=reg_f1[i] if i < len(reg_f1) else None)
            for i in range(n)
        ]

    j_i, j_v = _first_argmax(sel, start=int(min_best_epoch))
    if j_i < 0:
        warnings.append(
            f"no epoch eligible for the joint checkpoint (min_best_epoch={min_best_epoch} >= {n} epochs)"
        )
        joint_best: Optional[Dict[str, Any]] = None
    else:
        joint_best = {
            "epoch": j_i + 1,
            "selector": j_v,
            "cat_f1": cat_f1[j_i],
            "top10_indist": reg_series[j_i],
            "ood_fraction": ood[j_i],
            "top10_full": _full(j_i),
        }

    return {
        "schema_version": SCHEMA_VERSION,
        "selector_name": selector_name,
        "min_best_epoch": int(min_best_epoch),
        "epoch_convention": "1-based (matches the epoch column of fold{N}_{task}_val.csv)",
        "units": "fractions in [0,1] (same as the val CSVs); multiply by 100 for paper-style numbers",
        "reg_metric_used": reg_metric_used,
        "selector_source": selector_source,
        "cat_diag_best": cat_diag,
        "reg_diag_best": reg_diag,
        "joint_best": joint_best,
        "warnings": warnings,
    }


def fold_standard_scores(
    fold: Any,
    *,
    cat_task: str,
    reg_task: str,
    selector_name: str = "geom_simple",
    min_best_epoch: int = 0,
) -> Optional[Dict[str, Any]]:
    """Standard scores for one in-memory ``FoldHistory`` (duck-typed; no import needed).

    Extracts the two tasks' val ``MetricStore`` series, prefers the training-time
    selector series (``fold.model_task.val['f1']`` — since C21 that column IS the
    configured joint selector, exact for any selector incl. ``geom_lift``), and
    cross-checks the recomputed joint-best epoch against the epoch of the ACTUALLY
    SAVED joint checkpoint (``fold.model_task.best.best_epoch``). Returns ``None``
    when either task is absent or has no scoreable series.
    """
    tasks = getattr(fold, "tasks", {}) or {}
    th_cat = tasks.get(cat_task)
    th_reg = tasks.get(reg_task)
    if th_cat is None or th_reg is None:
        return None

    cat_series = {k: list(v) for k, v in th_cat.val.items()}
    reg_series = {k: list(v) for k, v in th_reg.val.items()}

    selector_series = None
    model_task = getattr(fold, "model_task", None)
    if model_task is not None:
        selector_series = model_task.val.get("f1")

    out = compute_standard_scores(
        cat_series, reg_series,
        selector_name=selector_name,
        min_best_epoch=min_best_epoch,
        selector_series=selector_series,
    )
    if out is None:
        return None

    checkpoint_epoch = None
    if model_task is not None and getattr(model_task.best, "best_epoch", -1) >= 0:
        checkpoint_epoch = int(model_task.best.best_epoch) + 1  # 0-based tracker -> 1-based
        if out["joint_best"] is not None and checkpoint_epoch != out["joint_best"]["epoch"]:
            out["warnings"].append(
                f"joint_best epoch {out['joint_best']['epoch']} != saved-checkpoint epoch "
                f"{checkpoint_epoch} (early-stop / selector mismatch?)"
            )
    out["checkpoint_epoch"] = checkpoint_epoch
    return out


def identify_cat_reg_tasks(fold: Any, task_names: Sequence[str]) -> Optional[Tuple[str, str]]:
    """Best-effort (cat_task, reg_task) identification for legacy callers that did not
    annotate the history (``history.scoring_task_names``). Exactly-2-task runs only:
    the task with a ``top10_acc_indist`` val series is the reg task; else fall back to
    name heuristics ('category' in name -> cat / 'region' or 'next' in name -> reg).
    Returns ``None`` when identification is ambiguous."""
    names = list(task_names)
    if len(names) != 2:
        return None
    tasks = getattr(fold, "tasks", {}) or {}
    with_top10 = [
        n for n in names
        if n in tasks and "top10_acc_indist" in getattr(tasks[n], "val", {})
    ]
    if len(with_top10) == 1:
        reg = with_top10[0]
        cat = names[0] if names[1] == reg else names[1]
        return cat, reg
    cat_like = [n for n in names if "category" in n.lower()]
    if len(cat_like) == 1:
        cat = cat_like[0]
        reg = names[0] if names[1] == cat else names[1]
        if "region" in reg.lower() or "next" in reg.lower():
            return cat, reg
    return None


__all__ = [
    "SCHEMA_VERSION",
    "RECOMPUTABLE_SELECTORS",
    "selector_value",
    "compute_standard_scores",
    "fold_standard_scores",
    "identify_cat_reg_tasks",
]
