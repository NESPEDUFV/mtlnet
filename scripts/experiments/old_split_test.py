"""Replicate the old StratifiedKFold split protocol (no user isolation) for ablation.

The old codebase (tarik-new/PoiMtlNet_Novo) used independent StratifiedKFold for both
next and category tasks, allowing the same user to appear in both train and val sets.
This script reproduces that behaviour using the current training infrastructure so the
only variable is the split protocol (not the model, loss, or training loop).

Usage:
    python scripts/experiments/old_split_test.py --state florida --engine fusion --embedding-dim 128 --folds 1
    python scripts/experiments/old_split_test.py --state florida --engine fusion --embedding-dim 128 --folds 1 --category-head category_ensemble
"""
from __future__ import annotations

import argparse
import dataclasses
import logging
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
_src = str(Path(_root) / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

import numpy as np
from sklearn.model_selection import StratifiedKFold

from configs.experiment import DatasetSignature, ExperimentConfig
from configs.globals import CATEGORIES_MAP
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import (
    FoldData,
    FoldResult,
    TaskFoldData,
    TaskType,
    _convert_to_tensors,
    _create_dataloader,
    load_category_data,
    load_next_data,
)
from tracking import DatasetHistory, MLHistory
from training.callbacks import ModelCheckpoint
from utils.seed import seed_everything

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def create_old_style_folds(
    state: str,
    engine: EmbeddingEngine,
    n_splits: int = 5,
    batch_size: int = 2048,
    seed: int = 42,
) -> dict:
    """Create MTL folds using the old independent StratifiedKFold protocol.

    Both next and category splits are created independently — the same user
    can appear in train for next and val for category (or vice versa). This
    matches the behaviour of tarik-new/PoiMtlNet_Novo/src/etl/mtl/create_fold.py.
    """
    X_next, y_next, _userids, next_dim = load_next_data(state, engine)
    X_cat, y_cat, _placeids, cat_dim = load_category_data(state, engine)

    import torch
    x_next_t, y_next_t = _convert_to_tensors(X_next, y_next, TaskType.NEXT, embedding_dim=next_dim)
    x_cat_t, y_cat_t = _convert_to_tensors(X_cat, y_cat, TaskType.CATEGORY, embedding_dim=cat_dim)

    skf_next = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    skf_cat = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    next_splits = list(skf_next.split(X_next, y_next))
    cat_splits = list(skf_cat.split(X_cat, y_cat))

    fold_results: dict = {}
    for fold_idx, ((tr_n, val_n), (tr_c, val_c)) in enumerate(zip(next_splits, cat_splits)):
        logger.info(
            "Fold %d/%d: next train=%d val=%d | cat train=%d val=%d",
            fold_idx + 1, n_splits, len(tr_n), len(val_n), len(tr_c), len(val_c),
        )

        next_data = TaskFoldData(
            train=FoldData(
                _create_dataloader(x_next_t[tr_n], y_next_t[tr_n], batch_size, True, False, seed),
                x_next_t[tr_n], y_next_t[tr_n],
            ),
            val=FoldData(
                _create_dataloader(x_next_t[val_n], y_next_t[val_n], batch_size, False, False, seed),
                x_next_t[val_n], y_next_t[val_n],
            ),
        )
        cat_data = TaskFoldData(
            train=FoldData(
                _create_dataloader(x_cat_t[tr_c], y_cat_t[tr_c], batch_size, True, False, seed),
                x_cat_t[tr_c], y_cat_t[tr_c],
            ),
            val=FoldData(
                _create_dataloader(x_cat_t[val_c], y_cat_t[val_c], batch_size, False, False, seed),
                x_cat_t[val_c], y_cat_t[val_c],
            ),
        )

        fold_result = FoldResult()
        fold_result.next = next_data
        fold_result.category = cat_data
        fold_results[fold_idx] = fold_result

    return fold_results


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(
        description="Train MTL with old-style StratifiedKFold (no user isolation).",
    )
    parser.add_argument("--state", required=True)
    parser.add_argument("--engine", required=True, choices=[e.value for e in EmbeddingEngine])
    parser.add_argument("--embedding-dim", type=int, default=None)
    parser.add_argument("--folds", type=int, default=None, help="Max folds to run (1 for quick test)")
    parser.add_argument("--category-head", type=str, default=None,
                        help="Registered category head name, e.g. category_ensemble")
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args(argv)

    seed_everything(args.seed)

    engine = EmbeddingEngine(args.engine)

    # Build config from default_mtl
    config = ExperimentConfig.default_mtl(
        name=f"old_split_{args.state}_{args.engine}",
        state=args.state,
        embedding_engine=args.engine,
    )
    if args.embedding_dim is not None:
        params = dict(config.model_params)
        params["feature_size"] = args.embedding_dim
        config = dataclasses.replace(config, model_params=params)
    if args.category_head is not None:
        params = dict(config.model_params)
        params["category_head"] = args.category_head
        config = dataclasses.replace(config, model_params=params)
    if args.batch_size is not None:
        config = dataclasses.replace(config, batch_size=args.batch_size)
    if args.epochs is not None:
        config = dataclasses.replace(config, epochs=args.epochs)

    n_splits = max(2, args.folds) if args.folds else config.k_folds
    fold_results = create_old_style_folds(
        state=args.state,
        engine=engine,
        n_splits=n_splits,
        batch_size=config.batch_size,
        seed=config.seed,
    )

    if args.folds is not None and args.folds < len(fold_results):
        fold_results = dict(list(fold_results.items())[: args.folds])

    results_path = IoPaths.get_results_dir(args.state, engine)
    results_path.mkdir(parents=True, exist_ok=True)

    history = MLHistory(
        model_name="MTLNet_OldSplit",
        tasks={"next", "category"},
        num_folds=len(fold_results),
        datasets={
            DatasetHistory(
                raw_data=IoPaths.get_next(args.state, engine),
                folds_signature=None,
                description="Next-POI (old StratifiedKFold split)",
            ),
            DatasetHistory(
                raw_data=IoPaths.get_category(args.state, engine),
                folds_signature=None,
                description="Category (old StratifiedKFold split)",
            ),
        },
        label_map=CATEGORIES_MAP,
        save_path=results_path,
        verbose=True,
    )

    from datetime import datetime
    import os
    run_dir = results_path / "checkpoints" / f"mtl_oldsplit_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.getpid()}"
    run_dir.mkdir(parents=True, exist_ok=True)
    config.save(run_dir / "config.json")

    from training.callbacks import ModelCheckpoint
    callbacks = [ModelCheckpoint(save_dir=run_dir, monitor="val_f1_category", mode="max", save_best_only=True)]

    from training.runners.mtl_cv import train_with_cross_validation
    with history:
        train_with_cross_validation(
            dataloaders=fold_results,
            history=history,
            config=config,
            results_path=results_path,
            callbacks=callbacks,
        )

    logger.info("Done. Results written to: %s", results_path)


if __name__ == "__main__":
    main()
