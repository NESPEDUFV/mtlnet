"""Faithful MHA+PE baseline trainer (single-task next_category, 5-fold CV).

Protocol matches our other next_category baselines:
    - StratifiedGroupKFold(folds, shuffle=True, random_state=seed) on
      target_category, grouped by userid.
    - Adam(lr=7e-4, betas=(0.8, 0.9)) — paper hyperparameters for Gowalla.
    - 11 epochs (paper §5.4 Gowalla 'next' model).
    - Best-epoch selection on val macro-F1.

Output JSON layout matches in-house ``next_*`` JSONs.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.model_selection import StratifiedGroupKFold
from torch.utils.data import DataLoader, TensorDataset

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.globals import DEVICE  # noqa: E402
from tracking.metrics import compute_classification_metrics  # noqa: E402
from utils.seed import seed_everything  # noqa: E402

from research.baselines.mha_pe.etl import (  # noqa: E402
    N_CATEGORIES, WINDOW_SIZE, out_path as etl_out_path,
)
from research.baselines.mha_pe.model import MHAPE  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("faithful_mha_pe")


def load_tensors(state: str):
    df = pd.read_parquet(etl_out_path(state))
    cat = np.stack([df[f"cat_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    hour = np.stack([df[f"hour_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    y = df["target_category"].to_numpy(np.int64)
    uid = df["userid"].to_numpy(np.int64)
    return torch.from_numpy(cat), torch.from_numpy(hour), torch.from_numpy(y), uid


def _make_loader(idx, cat, hour, y, batch_size, shuffle):
    ds = TensorDataset(cat[idx], hour[idx], y[idx])
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=0)


def train_one_fold(cat, hour, y, train_idx, val_idx, *,
                   epochs, batch_size, seed, lr) -> dict:
    seed_everything(seed)
    train_dl = _make_loader(train_idx, cat, hour, y, batch_size, True)
    val_dl = _make_loader(val_idx, cat, hour, y, batch_size, False)

    model = MHAPE(n_categories=N_CATEGORIES, step_size=WINDOW_SIZE).to(DEVICE)
    optim = torch.optim.Adam(model.parameters(), lr=lr, betas=(0.8, 0.9))
    crit = nn.CrossEntropyLoss()

    best_f1 = -1.0
    best = {}
    patience = 0
    for epoch in range(epochs):
        model.train()
        for cb, hb, yb in train_dl:
            cb, hb, yb = cb.to(DEVICE), hb.to(DEVICE), yb.to(DEVICE)
            optim.zero_grad(set_to_none=True)
            out = model(cb, hb)
            loss = crit(out, yb)
            loss.backward()
            optim.step()

        model.eval()
        logits, targets = [], []
        with torch.no_grad():
            for cb, hb, yb in val_dl:
                cb, hb = cb.to(DEVICE), hb.to(DEVICE)
                logits.append(model(cb, hb).cpu())
                targets.append(yb)
        logits = torch.cat(logits)
        targets = torch.cat(targets)
        m = compute_classification_metrics(logits, targets, num_classes=N_CATEGORIES, top_k=(3, 5))
        if m.get("f1", 0) > best_f1:
            best_f1 = m["f1"]
            best = dict(m, best_epoch=epoch + 1)
            patience = 0
        else:
            patience += 1
            if patience >= 3:
                logger.info("    early-stop at epoch %d (best_f1=%.4f)", epoch + 1, best_f1)
                break
    return best


def run(state: str, folds: int, epochs: int, batch_size: int, seed: int, lr: float,
        tag: str | None) -> None:
    cat, hour, y, uid = load_tensors(state)
    logger.info("Loaded %s: rows=%d  n_cat=%d", state, cat.shape[0], N_CATEGORIES)

    sgkf = StratifiedGroupKFold(n_splits=max(2, folds), shuffle=True, random_state=seed)
    splits = list(sgkf.split(np.zeros(len(y)), y.numpy(), groups=uid))[:folds]

    out_dir = Path("docs/results/baselines")
    out_dir.mkdir(parents=True, exist_ok=True)
    tag_s = f"_{tag}" if tag else ""
    out_file = out_dir / f"faithful_mha_pe_{state}_{folds}f_{epochs}ep{tag_s}.json"

    fold_metrics = []
    for fold_idx, (tr, va) in enumerate(splits):
        t0 = time.time()
        m = train_one_fold(
            cat, hour, y, tr, va,
            epochs=epochs, batch_size=batch_size, seed=seed + fold_idx, lr=lr,
        )
        fold_metrics.append(m)
        logger.info("  fold %d: f1=%.4f acc=%.4f acc@5=%.4f mrr=%.4f (%.1fs, best_ep=%d)",
                    fold_idx, m.get("f1", 0), m.get("accuracy", 0),
                    m.get("top5_acc", 0), m.get("mrr", 0),
                    time.time() - t0, m.get("best_epoch", 0))

    agg = {}
    for k in ["accuracy", "top3_acc", "top5_acc", "mrr", "f1", "f1_weighted", "accuracy_macro"]:
        vals = [m.get(k, 0.0) for m in fold_metrics]
        agg[f"{k}_mean"] = float(np.mean(vals))
        agg[f"{k}_std"] = float(np.std(vals))
    logger.info("AGGREGATE: " + " ".join(f"{k}={v:.4f}" for k, v in agg.items()))

    payload = {
        "state": state, "folds": folds, "epochs": epochs, "seed": seed,
        "n_categories": N_CATEGORIES,
        "config": {"lr": lr, "batch_size": batch_size, "betas": [0.8, 0.9]},
        "per_fold": fold_metrics, "aggregate": agg,
    }
    out_file.write_text(json.dumps(payload, indent=2))
    logger.info("Saved: %s", out_file)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--epochs", type=int, default=11)
    p.add_argument("--batch-size", type=int, default=400)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--lr", type=float, default=7e-4)
    p.add_argument("--tag", type=str, default=None)
    args = p.parse_args()
    run(args.state, args.folds, args.epochs, args.batch_size, args.seed, args.lr, args.tag)


if __name__ == "__main__":
    main()
