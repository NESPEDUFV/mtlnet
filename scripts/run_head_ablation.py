"""CLI entrypoint for standalone head ablation.

Trains each registered head variant independently for a given task
(category or next) and ranks them by F1 score.

Usage:
    # Run all category heads
    python scripts/run_head_ablation.py --task category --state florida --engine dgi --epochs 10 --folds 1

    # Run all next-POI heads
    python scripts/run_head_ablation.py --task next --state florida --engine hgi --epochs 50 --folds 2

    # Run specific candidates
    python scripts/run_head_ablation.py --task category --candidate cat_ensemble --candidate cat_gated

    # Run all heads (both tasks)
    python scripts/run_head_ablation.py --task all --state florida --engine dgi
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from ablation.runner import HeadAblationConfig, run_head_ablation


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run standalone head ablation — train each head variant and rank by F1.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--task",
        choices=("category", "next", "all"),
        default="category",
        help="Which task heads to ablate.",
    )
    parser.add_argument("--state", default="alabama", help="Dataset state.")
    parser.add_argument("--engine", default="dgi", help="Embedding engine.")
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="Run specific candidates (repeatable). Omit to run all for the task.",
    )
    parser.add_argument("--epochs", type=int, default=10, help="Training epochs per candidate.")
    parser.add_argument("--folds", type=int, default=1, help="CV folds per candidate.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed.")
    parser.add_argument(
        "--embedding-dim",
        type=int,
        default=None,
        help="Override embedding dimension (e.g. 128 for fusion).",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=_root / "results" / "ablations",
        help="Root directory for ablation results.",
    )
    parser.add_argument(
        "--data-root",
        type=Path,
        default=Path(os.environ.get("DATA_ROOT", str(_root / "data"))),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(os.environ.get("OUTPUT_DIR", str(_root / "output"))),
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = _parse_args(argv)
    config = HeadAblationConfig(
        task=args.task,
        state=args.state,
        engine=args.engine,
        candidate_names=tuple(args.candidate),
        epochs=args.epochs,
        folds=args.folds,
        seed=args.seed,
        embedding_dim=args.embedding_dim,
        results_root=args.results_root,
        data_root=args.data_root,
        output_dir=args.output_dir,
    )
    run_head_ablation(config)


if __name__ == "__main__":
    main()
