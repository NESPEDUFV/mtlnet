"""Epoch selection — the two conventions, and the rule that they are never mixed.

A joint run produces two different numbers depending on which epoch you read, and the reference
project discovered the hard way that nobody had noticed which one its tables reported:

* **diag-best** — each task at its OWN best validation epoch. Two different epochs per fold. This is
  the convention the published tables use.
* **joint-best** — both tasks at the single epoch `e*` that the checkpoint selector picked. This is
  what the one saved checkpoint actually delivers.

Training saves one checkpoint per fold, gated on `geom_simple`. The tables report diag-best. Nobody
scored the checkpoint, so for a long time the author believed the tables described it. They do not:
diag-best is an upper bound on what a single deployable checkpoint can give.

So both are computed here, in the same pass, and every reported number carries which one it is. A
number without its convention is under-specified — that was the root cause, and it is why this
module exists rather than the selection logic living inline in a runner.

Deliberately stdlib-only (no torch, no numpy), so a post-hoc re-score costs nothing to run.
"""

from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

SCHEMA_VERSION = 1


def selector_value(name: str, cat_f1: float, reg_metric: float,
                   reg_f1: float | None = None) -> float:
    """One epoch's joint-selector value.

    `geom_simple` = sqrt(cat macro-F1 * region top10 RAW). Both operands are bounded in [0, 1], so
    neither head can dominate by scale — which is what the earlier arithmetic-mean selector got
    wrong across a 7-class and a 1109-class head.

    ⚠ O operando de região é o `top10_acc` cru, que é o estimando reportado (§1). Até 23-08 era o
    `top10_acc_indist`, enquanto o braço dedicado já selecionava por cru — os dois braços escolhiam
    por grandezas diferentes, o que o §1 proíbe em "selection symmetry (mandatory)". Medido sobre as
    18 células joint da campanha `v19_defence`: a época escolhida é a MESMA nos 90 folds, então a
    correção não move nenhum número bancado.
    """
    if name == "geom_simple":
        return math.sqrt(max(cat_f1, 0.0) * max(reg_metric, 0.0))
    if name == "joint_f1_mean":
        return 0.5 * ((reg_f1 if reg_f1 is not None else reg_metric) + cat_f1)
    raise ValueError(f"unknown selector {name!r}")


def _first_argmax(values: Sequence[float], start: int = 0) -> tuple[int, float]:
    """Index and value of the maximum, ties going to the EARLIEST index.

    Matches training's strict `>` improvement rule: a later epoch that merely equals the best does
    not replace the checkpoint.
    """
    best_i, best_v = -1, float("-inf")
    for i in range(max(start, 0), len(values)):
        if values[i] > best_v:
            best_i, best_v = i, values[i]
    return (best_i, best_v) if best_i >= 0 else (-1, float("nan"))


def standard_scores(cat_val: Mapping[str, Sequence[float]],
                    reg_val: Mapping[str, Sequence[float]], *,
                    selector: str = "geom_simple",
                    min_best_epoch: int = 0) -> dict[str, Any] | None:
    """Both conventions from two per-epoch validation series.

    Values are fractions in [0, 1] and epochs are 1-based, matching the on-disk series. Returns
    None when either task has nothing scoreable.
    """
    cat_f1 = list(cat_val.get("f1") or [])
    reg_f1 = list(reg_val.get("f1") or [])
    if not cat_f1 or not reg_f1:
        return None

    warnings: list[str] = []
    reg_indist = list(reg_val.get("top10_acc_indist") or [])
    reg_raw = list(reg_val.get("top10_acc") or [])
    # O SELETOR usa o cru, que é o que se reporta; o in-distribution segue alimentando as lanes de
    # diagnóstico abaixo, onde está rotulado como tal.
    if reg_raw:
        reg_series, reg_metric_used = reg_raw, "top10_acc"
    elif reg_indist:
        reg_series, reg_metric_used = reg_indist, "top10_acc_indist"
        warnings.append("region task has no top10_acc series; selecting on in-distribution")
    else:
        reg_series, reg_metric_used = reg_f1, "f1"
        warnings.append("region task has no top-10 series; using its f1")
    diag_series = reg_indist or reg_series

    ood = list(reg_val.get("ood_fraction") or [])
    if not ood:
        warnings.append("region task has no ood_fraction series; treating it as 0")
        ood = [0.0] * len(reg_series)
    elif len(ood) < len(reg_series):
        warnings.append(f"ood_fraction shorter than the metric series ({len(ood)} < {len(reg_series)})")
        ood = ood + [0.0] * (len(reg_series) - len(ood))

    def full(i: int) -> float:
        return diag_series[i] * (1.0 - ood[i])

    # diag-best: each task's own best epoch, over its full series, UNGATED.
    c_i, c_v = _first_argmax(cat_f1)
    r_i, r_v = _first_argmax(diag_series)

    # joint-best: one epoch for both, gated at min_best_epoch (0-based).
    n = min(len(cat_f1), len(reg_series))
    if len(cat_f1) != len(reg_series):
        warnings.append(f"unequal series lengths (cat {len(cat_f1)}, reg {len(reg_series)})")
    series = [selector_value(selector, cat_f1[i], reg_series[i],
                             reg_f1=reg_f1[i] if i < len(reg_f1) else None) for i in range(n)]
    j_i, j_v = _first_argmax(series, start=int(min_best_epoch))

    joint = None
    if j_i < 0:
        warnings.append(f"no epoch is eligible for the joint checkpoint "
                        f"(min_best_epoch={min_best_epoch} >= {n} epochs)")
    else:
        joint = {"epoch": j_i + 1, "selector": j_v, "cat_f1": cat_f1[j_i],
                 "top10_raw": reg_series[j_i],
                 "top10_indist": diag_series[j_i], "ood_fraction": ood[j_i],
                 "top10_full": full(j_i)}

    return {
        "schema_version": SCHEMA_VERSION,
        "selector_name": selector,
        "min_best_epoch": int(min_best_epoch),
        "reg_metric_used": reg_metric_used,
        "units": "fractions in [0,1]; epochs 1-based",
        "cat_diag_best": {"epoch": c_i + 1, "f1": c_v},
        "selector_reg_metric": reg_metric_used,
        "reg_diag_best": {"epoch": r_i + 1, "top10_indist": r_v,
                          "ood_fraction": ood[r_i], "top10_full": full(r_i)},
        "joint_best": joint,
        "warnings": warnings,
    }


def single_task_best(series: Mapping[str, Sequence[float]], metric: str,
                     min_best_epoch: int = 0) -> dict[str, Any]:
    """The best epoch of a dedicated run.

    **Category** is selected by macro-F1, and that is unambiguous.

    **Region is not.** The two families in this system read the region axis differently, in both the
    metric they select on and the estimator they report, and the published tables place the two
    numbers side by side:

    | | selects on | reports |
    |---|---|---|
    | dedicated (the banked ceiling) | plain `top10_acc`, all rows | plain `top10_acc` |
    | joint (diag-best) | `top10_acc_indist` | `top10_acc_indist * (1 - ood_fraction)` |

    The second treats every out-of-distribution row as a miss; the first lets an unseen region hit by
    chance, since it still has an output unit. They are different estimators at different epochs.

    So a region selection returns BOTH lanes. `value` is the **banked** convention — the one every
    v18 dedicated-region cell used — and the joint-convention figures ride alongside so the two can
    be compared knowingly instead of by accident. Whoever reports a number must say which lane.

    `min_best_epoch` gates the SELECTED lane only, and exists so this function and the runner's
    checkpoint tracker can be the same rule. They were not: the tracker followed gated
    `top10_acc_indist` while this returned the ungated argmax of raw `top10_acc`, so a region cell
    persisting predictions would abort on the cross-check whenever the two lanes peaked apart —
    which is most of them. The banked raw lane wins, because raw top-10 is the reported estimand
    (protocol §1) and in-distribution is a diagnostic.
    """
    if metric != "top10_acc_indist":
        values = list(series.get(metric) or [])
        if not values:
            raise ValueError(f"no {metric!r} series to select on")
        index, value = _first_argmax(values, start=int(min_best_epoch))
        if index < 0:
            raise ValueError(f"min_best_epoch={min_best_epoch} leaves no eligible epoch "
                             f"in a {len(values)}-epoch series")
        return {"epoch": index + 1, "metric": metric, "value": value, "lane": "diag_best",
                "min_best_epoch": int(min_best_epoch)}

    raw = list(series.get("top10_acc") or [])
    indist = list(series.get("top10_acc_indist") or [])
    if not raw or not indist:
        raise ValueError("a region selection needs both top10_acc and top10_acc_indist series")
    ood = list(series.get("ood_fraction") or [0.0] * len(indist))
    if len(ood) < len(indist):
        ood = ood + [0.0] * (len(indist) - len(ood))

    # The banked lane: plain top-10 at its OWN best epoch. Gated, because this is the lane whose
    # epoch the runner checkpoints on.
    raw_i, raw_v = _first_argmax(raw, start=int(min_best_epoch))
    if raw_i < 0:
        raise ValueError(f"min_best_epoch={min_best_epoch} leaves no eligible epoch "
                         f"in a {len(raw)}-epoch series")
    # The joint lane: in-distribution top-10 at ITS best epoch, discounted by that epoch's OOD share.
    ind_i, ind_v = _first_argmax(indist)

    return {
        "epoch": raw_i + 1,
        "metric": "top10_acc",
        "value": raw_v,
        "lane": "dedicated_banked",
        "min_best_epoch": int(min_best_epoch),
        "joint_convention": {
            "epoch": ind_i + 1,
            "metric": "top10_acc_indist",
            "top10_indist": ind_v,
            "ood_fraction": ood[ind_i],
            "top10_full": ind_v * (1.0 - ood[ind_i]),
        },
    }


__all__ = ["standard_scores", "single_task_best", "selector_value", "SCHEMA_VERSION"]
