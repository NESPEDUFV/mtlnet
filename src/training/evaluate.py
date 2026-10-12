"""Shared evaluation helpers — extracted in Phase 4a.

Each task runner calls these. MTL calls them twice (once per task head).
Next adds attention extraction on top. No monolithic evaluate() is forced.
"""

from typing import Callable, Optional

import numpy as np
import torch
from sklearn.metrics import classification_report
from torch import nn
from torch.utils.data import DataLoader


@torch.no_grad()
def collect_predictions(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device,
    forward_fn: Optional[Callable] = None,
) -> tuple[np.ndarray, np.ndarray, torch.Tensor]:
    """Run model over loader, return ``(predictions, targets, logits)``.

    Logits are preserved (on-device, detached) so downstream code can compute
    ranking metrics (Top-K, MRR, NDCG@K) without a second pass. ``predictions``
    and ``targets`` are still returned as numpy for the sklearn
    classification_report path.

    Args:
        model: The model to evaluate (will be set to ``.eval()``).
        loader: DataLoader yielding ``(X_batch, y_batch)`` tuples.
        device: Device to run on.
        forward_fn: Optional ``callable(model, X_batch) -> logits``.
            If ``None``, uses ``model(X_batch)``. Useful for MTL where the
            model returns a tuple and only one head is needed.

    Returns:
        Tuple ``(preds, targets, logits)``:
            * ``preds`` — ``np.ndarray[int]`` of argmax predictions.
            * ``targets`` — ``np.ndarray[int]`` of true labels.
            * ``logits`` — ``torch.Tensor`` of shape ``(N, C)`` (detached),
              kept on ``device`` to avoid unnecessary transfers when the
              caller wants to run ``compute_classification_metrics``.
    """
    model.eval()
    logits_list, targets_list = [], []

    for X_batch, y_batch in loader:
        X_batch = X_batch.to(device, non_blocking=True)

        if forward_fn is not None:
            logits = forward_fn(model, X_batch)
        else:
            logits = model(X_batch)

        logits_list.append(logits.detach())
        targets_list.append(y_batch)

    all_logits = torch.cat(logits_list)
    preds = all_logits.argmax(dim=1).cpu().numpy()
    targets = torch.cat(targets_list).cpu().numpy()
    return preds, targets, all_logits


def build_report(
    preds: np.ndarray,
    targets: np.ndarray,
    output_dict: bool = True,
) -> dict:
    """Wrap sklearn classification_report with standard options.

    Args:
        preds: Predicted class indices.
        targets: True class indices.
        output_dict: If True (default), return dict. If False, return string.

    Returns:
        Classification report as dict (or string if output_dict=False).
    """
    return classification_report(
        targets,
        preds,
        output_dict=output_dict,
        zero_division=0,
    )
