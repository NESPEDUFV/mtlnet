"""L0 — training-free geometry metrics for embedding evaluation.

All metrics operate on a frozen ``[N, D]`` embedding matrix with integer labels.
Zero training, so zero head confound. GPU-accelerated (chunked) where the naive
form would be O(N^2) in memory.

╔══════════════════════════════════════════════════════════════════════════════╗
║ L0 IS TASK-SPECIFIC — read docs/studies/embedding_eval/L0_METHODOLOGY.md       ║
║                                                                                ║
║ These metrics (kNN-LOO / silhouette / centroid-sep) measure OWN-LABEL static   ║
║ separability. That is the right quantity ONLY for static-attribute tasks:      ║
║                                                                                ║
║  • next-cat (label = category): L0 is a VALID RANKER. Own-category lives in the ║
║      geometry, so L0 tracks L2-cat. Use these metrics to compare substrates.    ║
║  • next-reg (transition task): NO static L0 RANKS substrates. The signal lives  ║
║      in the transition operator (log_T), not the region geometry (empirically:  ║
║      corr(region-cosine, T_ij) ~= 0.05). Region metrics here are DIAGNOSTICS    ║
║      ONLY (region-silhouette flags the spatial-cohesion axis; see region_eval). ║
║      RANK next-reg substrates at L2 (next_stan_flow + log_T, 5-fold, multi-seed).║
║                                                                                ║
║ So: label by CATEGORY to rank next-cat; for next-reg use region_eval.py and     ║
║ treat its output as a diagnostic, then defer the verdict to L2.                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
from __future__ import annotations

from typing import Dict

import numpy as np
import torch
from sklearn.metrics import accuracy_score, f1_score, silhouette_score


def _device() -> torch.device:
    import os
    forced = os.environ.get("EMBED_EVAL_DEVICE")
    if forced:
        return torch.device(forced)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if getattr(torch.backends, "mps", None) is not None and torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def knn_loo(
    emb: np.ndarray,
    labels: np.ndarray,
    k: int = 10,
    chunk: int = 2048,
) -> Dict[str, float]:
    """Leave-one-out cosine kNN: predict each item's label by **similarity-
    weighted** vote of its k nearest neighbours (self excluded). Returns
    micro-acc + macro-F1.

    Similarity weighting (not raw majority) breaks ties by neighbour distance
    instead of by smallest class index, removing the low-id-class bias of
    ``torch.mode``. Labels are densified to ``[0, C)`` internally so the
    per-class vote accumulator is exact for sparse (region) label spaces.

    Chunked top-k on GPU keeps memory at O(chunk * N) instead of O(N^2).
    """
    uniq, dense = np.unique(labels, return_inverse=True)
    num_classes = len(uniq)
    dev = _device()
    x = torch.from_numpy(emb).to(dev, torch.float32)
    x = torch.nn.functional.normalize(x, dim=1)
    y = torch.from_numpy(dense.astype(np.int64)).to(dev)
    n = x.shape[0]
    k_eff = min(k, n - 1)
    preds = torch.empty(n, dtype=torch.long, device=dev)

    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        b = end - start
        sims = x[start:end] @ x.T               # [b, N] cosine sims
        idx = torch.arange(start, end, device=dev)
        sims[torch.arange(b, device=dev), idx] = float("-inf")  # exclude self
        top = sims.topk(k_eff, dim=1)
        nbr_lab = y[top.indices]                # [b, k]
        # weight each neighbour by cosine remapped to [0,1] = (cos+1)/2, so the
        # weight is strictly positive: an all-negative-similarity row still casts
        # a real vote instead of collapsing to argmax->class-0 (low-id bias).
        w = (top.values + 1.0) / 2.0           # [b, k]
        votes = torch.zeros(b, num_classes, device=dev)
        votes.scatter_add_(1, nbr_lab, w)
        preds[start:end] = votes.argmax(dim=1)

    yp = preds.cpu().numpy()
    yt = dense.astype(np.int64)
    return {
        f"knn{k}_acc": float(accuracy_score(yt, yp)),
        f"knn{k}_macro_f1": float(f1_score(yt, yp, average="macro", zero_division=0)),
    }


def knn_predict(
    ref_emb: np.ndarray,
    ref_labels: np.ndarray,
    q_emb: np.ndarray,
    k: int = 10,
    chunk: int = 2048,
) -> np.ndarray:
    """Predict query labels by similarity-weighted cosine kNN against a SEPARATE
    reference set (for proper train/test CV — no leave-one-out leakage). Returns
    predicted labels in the original label space."""
    uniq, ref_dense = np.unique(ref_labels, return_inverse=True)
    num_classes = len(uniq)
    dev = _device()
    rx = torch.nn.functional.normalize(torch.from_numpy(ref_emb).to(dev, torch.float32), dim=1)
    qx = torch.nn.functional.normalize(torch.from_numpy(q_emb).to(dev, torch.float32), dim=1)
    ry = torch.from_numpy(ref_dense.astype(np.int64)).to(dev)
    k_eff = min(k, rx.shape[0])
    preds = torch.empty(qx.shape[0], dtype=torch.long, device=dev)
    for s in range(0, qx.shape[0], chunk):
        e = min(s + chunk, qx.shape[0])
        sims = qx[s:e] @ rx.T
        top = sims.topk(k_eff, dim=1)
        w = (top.values + 1.0) / 2.0
        votes = torch.zeros(e - s, num_classes, device=dev)
        votes.scatter_add_(1, ry[top.indices], w)
        preds[s:e] = votes.argmax(dim=1)
    return uniq[preds.cpu().numpy()]


def centroid_separability(emb: np.ndarray, labels: np.ndarray) -> Dict[str, float]:
    """Cohesion vs separation from class centroids (cosine geometry).

    cohesion     = mean cosine(item, its own class centroid)   (higher = tighter)
    inter_sim    = mean cosine between distinct class centroids (lower = better)
    sep_ratio    = cohesion / max(inter_sim, eps)              (higher = better)
    """
    x = emb / (np.linalg.norm(emb, axis=1, keepdims=True) + 1e-8)
    classes = np.unique(labels)
    cents = np.stack([x[labels == c].mean(0) for c in classes])
    cents_n = cents / (np.linalg.norm(cents, axis=1, keepdims=True) + 1e-8)

    cls_to_row = {int(c): i for i, c in enumerate(classes)}
    own = cents_n[[cls_to_row[int(l)] for l in labels]]
    cohesion = float((x * own).sum(1).mean())

    if len(classes) > 1:
        g = cents_n @ cents_n.T
        iu = np.triu_indices(len(classes), k=1)
        inter_sim = float(g[iu].mean())
    else:
        inter_sim = 1.0
    return {
        "cohesion": cohesion,
        "centroid_inter_sim": inter_sim,
        "sep_ratio": cohesion / max(inter_sim, 1e-6),
    }


def silhouette(emb: np.ndarray, labels: np.ndarray, sample: int = 10000, seed: int = 0) -> float:
    """Cosine silhouette on a subsample (full N is O(N^2))."""
    n = len(emb)
    if len(np.unique(labels)) < 2:
        return float("nan")
    if n > sample:
        rng = np.random.default_rng(seed)
        sel = rng.choice(n, size=sample, replace=False)
        emb, labels = emb[sel], labels[sel]
    # silhouette needs >=2 items per retained label to be meaningful; drop singletons
    uniq, cnt = np.unique(labels, return_counts=True)
    keep = np.isin(labels, uniq[cnt >= 2])
    if keep.sum() < 2 or len(np.unique(labels[keep])) < 2:
        return float("nan")
    return float(silhouette_score(emb[keep], labels[keep], metric="cosine"))


def linear_cka(x: np.ndarray, y: np.ndarray) -> float:
    """Linear CKA between two aligned embedding matrices (same rows/order).

    1.0 = representations are linear reparametrisations of each other.
    """
    xc = x - x.mean(0, keepdims=True)
    yc = y - y.mean(0, keepdims=True)
    hsic = np.linalg.norm(yc.T @ xc, "fro") ** 2
    nx = np.linalg.norm(xc.T @ xc, "fro")
    ny = np.linalg.norm(yc.T @ yc, "fro")
    return float(hsic / (nx * ny + 1e-12))


def l0_metrics(
    emb: np.ndarray,
    labels: np.ndarray,
    k: int = 10,
    silhouette_sample: int = 10000,
    seed: int = 0,
) -> Dict[str, float]:
    """All single-engine L0 metrics for one (emb, labels) pair."""
    out: Dict[str, float] = {}
    out.update(knn_loo(emb, labels, k=k))
    out.update(centroid_separability(emb, labels))
    out["silhouette"] = silhouette(emb, labels, sample=silhouette_sample, seed=seed)
    return out
