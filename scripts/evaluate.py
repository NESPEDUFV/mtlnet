"""CLI entrypoint for checkpoint evaluation (Phase 6).

Usage:
    python scripts/evaluate.py --checkpoint results/dgi/florida/model/best.pt \\
        --state florida --engine dgi

Loads a saved checkpoint and evaluates it on the validation set.
All imports use final Phase 5 canonical paths.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.experiment import ExperimentConfig
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import FoldCreator, TaskType
from tracking.metrics import compute_classification_metrics
from training.evaluate import collect_predictions, build_report

import torch

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_VALID_ENGINES = [e.value for e in EmbeddingEngine]


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a saved checkpoint on the validation fold.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--checkpoint",
        type=str,
        required=True,
        help="Path to .pt checkpoint file (state dict).",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to config.json saved alongside results (if not provided, "
             "defaults to <results_dir>/config.json).",
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help="Dataset state (used to locate data when --config is absent).",
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        choices=_VALID_ENGINES,
        help="Embedding engine (used to locate data when --config is absent).",
    )
    parser.add_argument(
        "--task",
        type=str,
        default="mtl",
        choices=("mtl", "category", "next"),
        help="Which task head to evaluate.",
    )
    parser.add_argument(
        "--fold",
        type=int,
        default=0,
        help="Which fold index to evaluate (0-based).",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = _parse_args(argv)

    checkpoint_path = Path(args.checkpoint)
    if not checkpoint_path.exists():
        logger.error("Checkpoint not found: %s", checkpoint_path)
        sys.exit(1)

    # Load config
    config_path = args.config
    if config_path is None:
        # Look for config.json next to checkpoint or in parent results dir
        for candidate in (
            checkpoint_path.parent / "config.json",
            checkpoint_path.parent.parent / "config.json",
        ):
            if candidate.exists():
                config_path = str(candidate)
                break

    if config_path is not None:
        config = ExperimentConfig.load(config_path)
        logger.info("Loaded config from %s", config_path)
    else:
        if args.state is None or args.engine is None:
            logger.error("Provide --config or both --state and --engine.")
            sys.exit(1)
        config = ExperimentConfig.default_mtl(
            name=f"eval_{args.state}_{args.engine}",
            state=args.state,
            embedding_engine=args.engine,
        )

    engine = EmbeddingEngine(config.embedding_engine)
    task = args.task

    # Create fold data
    task_type_map = {"mtl": TaskType.MTL, "category": TaskType.CATEGORY, "next": TaskType.NEXT}
    creator = FoldCreator(
        task_type=task_type_map[task],
        n_splits=config.k_folds,
        batch_size=config.batch_size,
        seed=config.seed,
        use_weighted_sampling=False,
    )
    fold_results = creator.create_folds(config.state, engine)

    if args.fold >= len(fold_results):
        logger.error("--fold %d out of range (max: %d)", args.fold, len(fold_results) - 1)
        sys.exit(1)

    fold = fold_results[args.fold]

    # Load checkpoint and model
    from configs.globals import DEVICE
    from models.registry import create_model

    state_dict = torch.load(checkpoint_path, map_location=DEVICE)
    model = create_model(config.model_name, **config.model_params).to(DEVICE)
    model.load_state_dict(state_dict)
    logger.info("Loaded checkpoint: %s", checkpoint_path)

    # Evaluate
    num_classes = config.model_params.get("num_classes", 7)

    def _log_metrics(label: str, logits, targets_np):
        targets_t = torch.as_tensor(targets_np)
        metrics = compute_classification_metrics(
            logits, targets_t, num_classes=num_classes,
        )
        logger.info(
            "%s metrics: %s",
            label,
            {k: round(v, 4) for k, v in metrics.items()},
        )

    if task == "mtl":
        # MTLnet exposes per-head entry points (cat_forward / next_forward).
        # For the original MTLnet (FiLM-based), each path is fully independent.
        # For expert-routing variants (CGC, MMoE, PLE) the unused task still
        # runs through its expert stack with a zero input, but its output is
        # discarded — the active task's output is unaffected. See
        # src/models/mtl/ for per-variant implementations.
        cat_preds, cat_targets, cat_logits = collect_predictions(
            model, fold.category.val.dataloader, DEVICE,
            forward_fn=lambda m, x: m.cat_forward(x),
        )
        next_preds, next_targets, next_logits = collect_predictions(
            model, fold.next.val.dataloader, DEVICE,
            forward_fn=lambda m, x: m.next_forward(x),
        )
        cat_report = build_report(cat_preds, cat_targets)
        next_report = build_report(next_preds, next_targets)
        logger.info(
            "Evaluation report (fold %d, task=mtl, head=category):\n%s",
            args.fold, cat_report,
        )
        _log_metrics("category", cat_logits, cat_targets)
        logger.info(
            "Evaluation report (fold %d, task=mtl, head=next):\n%s",
            args.fold, next_report,
        )
        _log_metrics("next", next_logits, next_targets)
        return

    if task == "category":
        loader = fold.category.val.dataloader
        preds, targets, logits = collect_predictions(model, loader, DEVICE)
    else:
        loader = fold.next.val.dataloader
        preds, targets, logits = collect_predictions(model, loader, DEVICE)

    report = build_report(preds, targets)
    logger.info("Evaluation report (fold %d, task=%s):\n%s", args.fold, task, report)
    _log_metrics(task, logits, targets)


if __name__ == "__main__":
    main()
