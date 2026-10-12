"""L1 — linear probe for embedding evaluation.

A single ``Linear`` softmax on frozen embeddings, fixed protocol, multi-seed.
Measures linearly-accessible task signal. Reuses ``compute_classification_metrics``
(which has the O(N+C) high-cardinality path needed for the ~5k-region head).

Fairness controls (from the methodology review):
  * features standardized on the TRAIN split only (no leakage), so engines with
    different vector scales are compared on equal footing;
  * minibatch AdamW with early stopping on a carved-out train-val slice, so the
    7-class and ~5k-class probes are each trained *to convergence* rather than a
    fixed step budget that underfits the high-cardinality head;
  * train accuracy + test-class coverage reported so underfit / unseen-class
    effects are visible rather than silently depressing the score.
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import torch
import torch.nn.functional as F
from sklearn.model_selection import train_test_split

from tracking.metrics import compute_classification_metrics


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


def _stratifiable(y: np.ndarray) -> bool:
    """train_test_split(stratify=) requires every class to have >=2 members."""
    _, cnt = np.unique(y, return_counts=True)
    return cnt.min() >= 2


def fit_probe(
    xtr: np.ndarray,
    ytr: np.ndarray,
    xte: np.ndarray,
    yte: np.ndarray,
    num_classes: int,
    seed: int = 42,
    epochs: int = 300,
    lr: float = 1e-2,
    weight_decay: float = 0.0,
    batch_size: int = 8192,
    patience: int = 20,
) -> Dict[str, float]:
    """Linear probe on EXPLICIT train/test splits (for shared 5-fold CV). Carves
    an early-stop slice out of train; standardizes on train only. Returns test
    metrics + train_acc + test_class_coverage."""
    estrat = ytr if _stratifiable(ytr) else None
    xtr, xes, ytr, yes = train_test_split(
        xtr, ytr, test_size=0.15, random_state=seed, stratify=estrat
    )

    # standardize on TRAIN only, apply to all splits (M3: scale fairness)
    mu = xtr.mean(0, keepdims=True)
    sd = xtr.std(0, keepdims=True) + 1e-6
    xtr, xes, xte = (xtr - mu) / sd, (xes - mu) / sd, (xte - mu) / sd

    dev = _device()
    xtr_t = torch.from_numpy(xtr).to(dev, torch.float32)
    ytr_t = torch.from_numpy(ytr).to(dev, torch.long)
    xes_t = torch.from_numpy(xes).to(dev, torch.float32)
    yes_t = torch.from_numpy(yes).to(dev, torch.long)
    xte_t = torch.from_numpy(xte).to(dev, torch.float32)
    yte_t = torch.from_numpy(yte).to(dev, torch.long)

    torch.manual_seed(seed)
    clf = torch.nn.Linear(xtr_t.shape[1], num_classes).to(dev)
    opt = torch.optim.AdamW(clf.parameters(), lr=lr, weight_decay=weight_decay)

    n = xtr_t.shape[0]
    g = torch.Generator(device="cpu").manual_seed(seed)
    best_es, best_state, bad = float("inf"), None, 0
    for _ in range(epochs):
        clf.train()
        perm = torch.randperm(n, generator=g).to(dev)
        for s in range(0, n, batch_size):
            bidx = perm[s:s + batch_size]
            opt.zero_grad()
            loss = F.cross_entropy(clf(xtr_t[bidx]), ytr_t[bidx])
            loss.backward()
            opt.step()
        clf.eval()
        with torch.no_grad():
            es_loss = F.cross_entropy(clf(xes_t), yes_t).item()
        if es_loss < best_es - 1e-4:
            best_es, bad = es_loss, 0
            best_state = {k: v.detach().clone() for k, v in clf.state_dict().items()}
        else:
            bad += 1
            if bad >= patience:
                break
    if best_state is not None:
        clf.load_state_dict(best_state)

    clf.eval()
    with torch.no_grad():
        logits = clf(xte_t)
        train_logits = clf(xtr_t)
    res = compute_classification_metrics(logits, yte_t, num_classes=num_classes)
    res["train_acc"] = float((train_logits.argmax(1) == ytr_t).float().mean().item())
    seen = np.unique(ytr)
    res["test_class_coverage"] = float(np.isin(np.unique(yte), seen).mean())
    return res


def make_folds(labels: np.ndarray, n_folds: int = 5, seed: int = 42):
    """5-fold split indices. Stratified when every class has >= n_folds members
    (next-cat), else plain KFold (next-region's sparse/singleton classes)."""
    from sklearn.model_selection import KFold, StratifiedKFold
    _, cnt = np.unique(labels, return_counts=True)
    if cnt.min() >= n_folds:
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=seed)
        return list(skf.split(np.zeros(len(labels)), labels))
    return list(KFold(n_splits=n_folds, shuffle=True, random_state=seed).split(labels))


def cv_probe(
    emb: np.ndarray,
    labels: np.ndarray,
    n_folds: int = 5,
    seed: int = 42,
    **kwargs,
) -> List[Dict[str, float]]:
    """5-fold CV linear probe. Returns the per-fold metric dicts (caller
    aggregates mean±SD). Labels densified to [0,C) so num_classes is exact."""
    uniq, dense = np.unique(labels, return_inverse=True)
    num_classes = len(uniq)
    dense = dense.astype(np.int64)
    out = []
    for tr, te in make_folds(dense, n_folds, seed):
        out.append(fit_probe(emb[tr], dense[tr], emb[te], dense[te],
                             num_classes=num_classes, seed=seed, **kwargs))
    return out
