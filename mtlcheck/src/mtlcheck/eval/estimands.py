"""The metrics, computed from rows — one implementation, used by everything.

Two implementations of one definition is two chances to disagree, and this project has already paid
for that: the reference kept two metric paths and switched between them at 256 classes. So every
number the protocol reports comes through here, and `train/metrics.py` keeps its own streaming
implementation only for the *training loop*, where it decides checkpoints and never reports.

## Pooled, not averaged — and the difference is not rounding

Macro-F1 over pooled out-of-fold predictions is not the mean of five per-fold macro-F1 values, and
the gap is not symmetric noise: averaging is biased under class imbalance because a rare class
absent from one fold contributes a 0 to that fold's mean instead of pooling its counts. Measured on
Alabama's structure the bias is about -0.24 pp — over half a typical equivalence margin. Pool the
counts, then divide (Forman & Scholz 2010).

## Sufficient statistics, so the bootstrap is cheap

Ten thousand bootstrap replicates that each rescan millions of rows is not a design, it is a wait. So
rows reduce ONCE to per-user counts, and a replicate is then a weighted sum over users:

  category → per-user, per-class (tp, fp, fn)
  region   → per-user (hits@k, windows)

Both are additive over users, which is exactly what makes resampling users a sum rather than a rescan.
The reduction is lossless for these metrics and for no others — a metric that is not a function of
per-user additive counts cannot use this path and must say so.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

#: The category label space is CLOSED at seven (`data.splits.CATEGORY_ORDER`). Inferring it from the
#: observed labels instead is a silent inflation: a class that neither appears nor is predicted
#: leaves the denominator, and macro-F1 rises by 1/C for free. Two arms can then be compared at two
#: different C, and the arm that failed to predict a rare class scores HIGHER for it.
NUM_CATEGORIES = 7


# ---------------------------------------------------------------- category


@dataclass(frozen=True)
class CategoryCounts:
    """Per-user, per-class confusion counts. Additive over users by construction."""

    users: np.ndarray            # [U] the user id of each row of the matrices
    tp: np.ndarray               # [U, C]
    fp: np.ndarray               # [U, C]
    fn: np.ndarray               # [U, C]

    @property
    def num_classes(self) -> int:
        return int(self.tp.shape[1])


def category_counts(frame: pd.DataFrame, num_classes: int | None = None) -> CategoryCounts:
    """Reduce prediction rows to per-user per-class TP/FP/FN.

    `num_classes=None` means the closed category space (`NUM_CATEGORIES`), NOT "infer from the
    data" — see that constant for why inference is a bug rather than a convenience.
    """
    y_true = frame["y_true"].to_numpy(dtype=np.int64)
    y_pred = frame["y_pred"].to_numpy(dtype=np.int64)
    raw_users = frame["userid"].to_numpy(dtype=np.int64)

    users, index = np.unique(raw_users, return_inverse=True)
    classes = int(num_classes if num_classes is not None else NUM_CATEGORIES)
    observed = int(max(y_true.max(initial=-1), y_pred.max(initial=-1))) + 1
    if observed > classes:
        raise ValueError(f"rows carry class {observed - 1} but the label space is {classes} wide; "
                         f"pass num_classes explicitly if this is not the category task")
    shape = (len(users), classes)

    tp = np.zeros(shape, dtype=np.int64)
    fp = np.zeros(shape, dtype=np.int64)
    fn = np.zeros(shape, dtype=np.int64)

    correct = y_true == y_pred
    np.add.at(tp, (index[correct], y_true[correct]), 1)
    np.add.at(fp, (index[~correct], y_pred[~correct]), 1)
    np.add.at(fn, (index[~correct], y_true[~correct]), 1)
    return CategoryCounts(users=users, tp=tp, fp=fp, fn=fn)


def macro_f1(counts: CategoryCounts, weights: np.ndarray | None = None) -> float:
    """Macro-F1 from pooled counts. `weights` gives each user a multiplicity, for the bootstrap.

    The convention is pinned because two non-equivalent definitions of "macro-F1" circulate: per-class
    F1 computed from pooled counts, then averaged unweighted over classes, with F1 = 0 for a class
    that has no support and no predictions (`zero_division=0`). The alternative — averaging per-sample
    or per-fold F1 — is a different number (Opitz & Burst 2019).

    A class with zero support AND zero predictions contributes 0 to the mean but still counts in the
    denominator, matching sklearn's default. That is a choice, not a law; it is stated so a reader can
    see it rather than infer it.
    """
    w = np.ones(len(counts.users)) if weights is None else np.asarray(weights, dtype=np.float64)
    tp = w @ counts.tp
    fp = w @ counts.fp
    fn = w @ counts.fn

    denominator = 2 * tp + fp + fn
    per_class = np.divide(2 * tp, denominator, out=np.zeros_like(denominator, dtype=np.float64),
                          where=denominator > 0)
    return float(per_class.mean())


def per_class_f1(counts: CategoryCounts) -> np.ndarray:
    """The per-class vector behind the macro average — a macro win carried by one rare class is
    visible only here, and the protocol requires it beside every headline delta."""
    tp = counts.tp.sum(axis=0).astype(np.float64)
    fp = counts.fp.sum(axis=0).astype(np.float64)
    fn = counts.fn.sum(axis=0).astype(np.float64)
    denominator = 2 * tp + fp + fn
    return np.divide(2 * tp, denominator, out=np.zeros_like(denominator), where=denominator > 0)


# ---------------------------------------------------------------- region


@dataclass(frozen=True)
class RegionCounts:
    """Per-user hit and window counts at a given k, plus the OOD split."""

    users: np.ndarray            # [U]
    hits: np.ndarray             # [U] windows whose true region ranked <= k
    windows: np.ndarray          # [U]
    ood_windows: np.ndarray      # [U] windows whose true region was absent from training
    ood_hits: np.ndarray         # [U] of those, how many still ranked <= k


def region_counts(frame: pd.DataFrame, *, k: int = 10,
                  train_labels: frozenset[int] | None = None) -> RegionCounts:
    """Reduce prediction rows to per-user hit counts at k."""
    rank = frame["rank_of_true"].to_numpy(dtype=np.int64)
    y_true = frame["y_true"].to_numpy(dtype=np.int64)
    raw_users = frame["userid"].to_numpy(dtype=np.int64)

    users, index = np.unique(raw_users, return_inverse=True)
    hit = (rank >= 1) & (rank <= k)
    ood = (np.zeros(len(y_true), dtype=bool) if train_labels is None
           else ~np.isin(y_true, np.fromiter(train_labels, dtype=np.int64, count=len(train_labels))))

    def total(mask):
        out = np.zeros(len(users), dtype=np.int64)
        np.add.at(out, index[mask], 1)
        return out

    return RegionCounts(users=users, hits=total(hit), windows=total(np.ones(len(rank), bool)),
                        ood_windows=total(ood), ood_hits=total(ood & hit))


def top_k_accuracy(counts: RegionCounts, weights: np.ndarray | None = None) -> float:
    """`top10_raw` — hits over ALL windows, full vocabulary.

    Deployment-faithful: no train-label bookkeeping exists at inference, so a row whose true region
    was never trained still counts as a row the model got wrong. The in-distribution variant is a
    diagnostic, never the claim (protocol §1).
    """
    w = np.ones(len(counts.users)) if weights is None else np.asarray(weights, dtype=np.float64)
    windows = float(w @ counts.windows)
    return float(w @ counts.hits) / windows if windows > 0 else float("nan")


def ood_diagnostics(counts: RegionCounts) -> dict[str, float]:
    """`ood_fraction` and the leak canary.

    A never-trained output unit essentially cannot rank in the top ten of 1 109 to 8 501 classes, so
    a non-trivial `ood_hit_rate` means information about the held-out label reached the model. This
    guards the stale-transition-prior failure class already documented at +8 to +12 pp.
    """
    windows = float(counts.windows.sum())
    ood = float(counts.ood_windows.sum())
    return {
        "ood_fraction": ood / windows if windows > 0 else 0.0,
        "ood_hit_rate": float(counts.ood_hits.sum()) / ood if ood > 0 else 0.0,
        "n_windows": windows,
        "n_users": float(len(counts.users)),
    }


# ---------------------------------------------------------------- dispatch


def pooled_metric(frame: pd.DataFrame, task: str, *, num_classes: int | None = None,
                  k: int = 10) -> float:
    """The pooled out-of-fold metric for a task, from rows. The single entry point."""
    if task == "cat":
        return macro_f1(category_counts(frame, num_classes))
    if task == "reg":
        return top_k_accuracy(region_counts(frame, k=k))
    raise ValueError(f"unknown task {task!r}; expected 'cat' or 'reg'")


def per_class_delta(frame_a: pd.DataFrame, frame_b: pd.DataFrame,
                    num_classes: int | None = None) -> list[dict[str, float]]:
    """A tabela por classe que o §1 exige ao lado de todo delta manchete.

    Descritiva, e é o ponto: uma vitória macro carregada por uma classe rara só é visível aqui.
    `users` é a contagem de usuários que contribuem para a classe, o número que o §3 manda reportar.
    """
    a = category_counts(frame_a, num_classes)
    b = category_counts(frame_b, num_classes)
    users = np.intersect1d(a.users, b.users)
    ia, ib = np.searchsorted(a.users, users), np.searchsorted(b.users, users)
    a = CategoryCounts(users, a.tp[ia], a.fp[ia], a.fn[ia])
    b = CategoryCounts(users, b.tp[ib], b.fp[ib], b.fn[ib])

    f1_a, f1_b = per_class_f1(a), per_class_f1(b)
    contribui = lambda c: ((c.tp + c.fp + c.fn) > 0).sum(axis=0)
    users_a, users_b = contribui(a), contribui(b)
    return [{"class": index, "f1_a": float(f1_a[index]), "f1_b": float(f1_b[index]),
             "delta": float((f1_b[index] - f1_a[index]) * 100),
             "users": int(max(users_a[index], users_b[index]))}
            for index in range(len(f1_a))]


def region_report(frame: pd.DataFrame, train_labels: dict[str, list[int]], *,
                  k: int = 10) -> dict[str, float]:
    """Os diagnósticos por estado × braço do §1, agregados sobre os folds.

    Por fold e depois somados, porque o conjunto de treino difere entre folds: agrupar sob a UNIÃO
    dos rótulos subestima o OOD.
    """
    total = ood = hits = ood_hits = 0
    for fold in sorted(frame["fold"].unique().tolist()):
        chave = f"reg/{fold}"
        if chave not in train_labels:
            continue
        parte = frame[frame["fold"] == fold]
        counts = region_counts(parte, k=k, train_labels=frozenset(train_labels[chave]))
        total += int(counts.windows.sum())
        ood += int(counts.ood_windows.sum())
        hits += int(counts.hits.sum())
        ood_hits += int(counts.ood_hits.sum())

    indist = total - ood
    return {
        "top10_raw": hits / total if total else float("nan"),
        # Os dois são diagnósticos DISTINTOS do §1 e diferem no denominador: `full` divide por todas
        # as janelas e fecha a identidade `ood_hit_rate = (raw − full)/ood_fraction`; `indist` divide
        # só pelas in-distribution. `indist >= full` sempre.
        "top10_full": (hits - ood_hits) / total if total else float("nan"),
        "top10_acc_indist": (hits - ood_hits) / indist if indist else float("nan"),
        "ood_fraction": ood / total if total else 0.0,
        "ood_hit_rate": ood_hits / ood if ood else 0.0,
        "n_windows": float(total),
    }


def mean_of_folds(frame: pd.DataFrame, task: str, *, num_classes: int | None = None,
                  k: int = 10) -> float:
    """The per-fold average — computed ONLY to demonstrate that it differs from pooling.

    Not an estimand. It exists so a test can pin the bias rather than the documentation asserting it.
    """
    values = [pooled_metric(part, task, num_classes=num_classes, k=k)
              for _, part in frame.groupby("fold", sort=True)]
    return float(np.mean(values)) if values else float("nan")


__all__ = ["NUM_CATEGORIES", "CategoryCounts", "RegionCounts", "category_counts", "region_counts",
           "macro_f1", "per_class_f1", "per_class_delta", "top_k_accuracy", "ood_diagnostics",
           "region_report", "pooled_metric", "mean_of_folds"]
