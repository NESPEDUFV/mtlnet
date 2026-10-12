"""Plotting helpers for the embedding-eval ladder.

Two registered, reusable views:
  * ``bar_metric`` — grouped bar chart of one L0/L1 metric across engines,
    grouped by task (the headline "who wins" picture, e.g. kNN accuracy).
  * ``scatter_2d`` — 2D PCA projection of an engine's embedding table coloured
    by label, the visual analogue of the kNN/silhouette geometry metrics
    (tight, separated clusters ⇒ high kNN purity).

PCA (not t-SNE/UMAP) is used deliberately: deterministic, dependency-light, and
a *linear* projection — so what you see is the same linear structure the linear
probe (L1) and CKA exploit, not a non-linear embedding that can manufacture
clusters that aren't linearly there.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

TASK_NAMES = {"cat": "next-cat", "reg": "next-reg", "poi": "next-poi"}


def bar_metric(df: pd.DataFrame, metric: str, out_png: Path, title: Optional[str] = None) -> bool:
    """Grouped bars: x=engine, one bar per task, for a single metric.

    Reads the long metrics frame (level inferred). For L1 metrics it averages
    over seeds and draws the SD as an error bar. Returns False if no data.
    """
    sub = df[df.metric == metric]
    if sub.empty:
        return False
    agg = sub.groupby(["engine", "task"])["value"].agg(["mean", "std"]).reset_index()
    engines = sorted(agg.engine.unique())
    tasks = [t for t in ("cat", "reg", "poi") if t in set(agg.task.unique())]
    x = np.arange(len(engines))
    w = 0.8 / max(len(tasks), 1)

    fig, ax = plt.subplots(figsize=(max(7, 1.4 * len(engines)), 4.5))
    for i, task in enumerate(tasks):
        means = [agg[(agg.engine == e) & (agg.task == task)]["mean"].squeeze() if
                 not agg[(agg.engine == e) & (agg.task == task)].empty else np.nan
                 for e in engines]
        stds = [agg[(agg.engine == e) & (agg.task == task)]["std"].squeeze() if
                not agg[(agg.engine == e) & (agg.task == task)].empty else 0.0
                for e in engines]
        stds = [0.0 if (s is None or (isinstance(s, float) and np.isnan(s))) else s for s in stds]
        ax.bar(x + i * w, means, w, yerr=stds, capsize=3, label=TASK_NAMES.get(task, task))
    ax.set_xticks(x + w * (len(tasks) - 1) / 2)
    ax.set_xticklabels(engines, rotation=30, ha="right", fontsize=8)
    ax.set_ylabel(metric)
    ax.set_title(title or metric)
    ax.legend(title="task")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    return True


def scatter_2d(
    emb: np.ndarray,
    labels: np.ndarray,
    out_png: Path,
    title: str,
    max_points: int = 8000,
    top_classes: int = 12,
    seed: int = 0,
) -> bool:
    """PCA-2D scatter coloured by label. For high-cardinality labels (region),
    only the ``top_classes`` most frequent classes are coloured; the rest are
    drawn grey as 'other'. Returns False if degenerate."""
    if len(emb) < 3 or len(np.unique(labels)) < 2:
        return False
    rng = np.random.default_rng(seed)
    if len(emb) > max_points:
        sel = rng.choice(len(emb), size=max_points, replace=False)
        emb, labels = emb[sel], labels[sel]

    xy = PCA(n_components=2, random_state=seed).fit_transform(
        (emb - emb.mean(0)) / (emb.std(0) + 1e-6)
    )
    uniq, cnt = np.unique(labels, return_counts=True)
    top = set(uniq[np.argsort(cnt)[::-1][:top_classes]])

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    other = ~np.isin(labels, list(top))
    if other.any():
        ax.scatter(xy[other, 0], xy[other, 1], s=3, c="lightgrey", alpha=0.4, label="other")
    cmap = plt.get_cmap("tab20" if len(top) > 10 else "tab10")
    for i, c in enumerate(sorted(top)):
        m = labels == c
        ax.scatter(xy[m, 0], xy[m, 1], s=5, color=cmap(i % cmap.N), alpha=0.6, label=str(c))
    ax.set_title(title, fontsize=10)
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    ax.legend(markerscale=2, fontsize=6, ncol=2, loc="best")
    fig.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_png, dpi=140)
    plt.close(fig)
    return True
