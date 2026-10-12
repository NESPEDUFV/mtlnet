import contextlib
import os
from typing import Union

import numpy as np
import torch
from sklearn.metrics import classification_report
from torch import nn
from torch.utils.data import DataLoader


def evaluate(model: nn.Module, loader: DataLoader, device: torch.device,
             best_state: dict = None
             ) -> Union[str, dict]:
    model.eval()
    if best_state is not None:
        model.load_state_dict(best_state)
    preds_list, truths_list = [], []

    # Match the training-loop precision: DISABLE_AMP=1 / MTL_DISABLE_AMP=1 forces fp32
    # eval (board baseline protocol + NaN-safety at large-state scale).
    _disable_amp = (
        os.environ.get("DISABLE_AMP") == "1"
        or os.environ.get("MTL_DISABLE_AMP") == "1"
    )
    _autocast_ctx = (
        torch.autocast(device.type, dtype=torch.float16)
        if device.type == 'cuda' and not _disable_amp
        else contextlib.nullcontext()
    )

    with torch.no_grad():
        for X_batch, y_batch in loader:
            if X_batch.device != device:
                X_batch = X_batch.to(device, non_blocking=(device.type == "cuda"))
            with _autocast_ctx:
                logits = model(X_batch)
            preds_list.append(logits.argmax(dim=1))
            truths_list.append(y_batch)

    # Single GPU→CPU transfer for all predictions
    preds = torch.cat(preds_list).cpu().numpy()
    truths = torch.cat(truths_list).cpu().numpy()

    report = classification_report(
        truths,
        preds,
        output_dict=True,
        zero_division=0,
    )
    return report
