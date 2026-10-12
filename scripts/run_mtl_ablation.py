"""Canonical CLI entrypoint for staged MTL ablations.

This script is the editable control surface (profiles/defaults/flags).
Execution logic lives in ``src/ablation/runner.py``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)
_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from ablation.runner import AblationRunConfig, run_ablation


_PROFILE_PRESETS: dict[str, dict[str, int]] = {
    # Preserves historical defaults.
    "manual": {
        "epochs": 10,
        "folds": 1,
        "promote_top": 0,
        "promote_epochs": 15,
        "promote_folds": 2,
    },
    # Fast diagnostic pass.
    "quick": {
        "epochs": 3,
        "folds": 1,
        "promote_top": 0,
        "promote_epochs": 5,
        "promote_folds": 2,
    },
    # Staged ablation protocol.
    "staged": {
        "epochs": 10,
        "folds": 1,
        "promote_top": 3,
        "promote_epochs": 15,
        "promote_folds": 2,
    },
    # Higher-budget run with no internal promotion step.
    "full": {
        "epochs": 50,
        "folds": 2,
        "promote_top": 0,
        "promote_epochs": 15,
        "promote_folds": 2,
    },
}


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run staged MTL ablation candidates.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--state", default="alabama")
    parser.add_argument("--engine", default="dgi")
    parser.add_argument("--stage", choices=("phase1", "phase2", "phase3", "phase4", "all"), default="phase1")
    parser.add_argument("--candidate", action="append", default=[])

    parser.add_argument(
        "--profile",
        choices=tuple(_PROFILE_PRESETS.keys()),
        default="manual",
        help="Preset budget profile for epochs/folds/promotion parameters.",
    )
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--folds", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--promote-top", type=int, default=None)
    parser.add_argument("--promote-epochs", type=int, default=None)
    parser.add_argument("--promote-folds", type=int, default=None)
    parser.add_argument(
        "--embedding-dim", type=int, default=None,
        help="Override embedding dimension (e.g. 128 for fusion engine).",
    )
    parser.add_argument("--list-profiles", action="store_true")

    parser.add_argument("--results-root", type=Path, default=None)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args(argv)


def _resolve_int_arg(
    args: argparse.Namespace,
    arg_name: str,
    profile_name: str,
) -> int:
    explicit = getattr(args, arg_name)
    if explicit is not None:
        return int(explicit)
    return int(_PROFILE_PRESETS[profile_name][arg_name])


def _build_config(args: argparse.Namespace) -> AblationRunConfig:
    kwargs = {}
    if args.results_root is not None:
        kwargs["results_root"] = args.results_root
    if args.data_root is not None:
        kwargs["data_root"] = args.data_root
    if args.output_dir is not None:
        kwargs["output_dir"] = args.output_dir

    return AblationRunConfig(
        state=args.state,
        engine=args.engine,
        stage=args.stage,
        candidate_names=tuple(args.candidate),
        epochs=_resolve_int_arg(args, "epochs", args.profile),
        folds=_resolve_int_arg(args, "folds", args.profile),
        seed=args.seed,
        embedding_dim=args.embedding_dim,
        promote_top=_resolve_int_arg(args, "promote_top", args.profile),
        promote_epochs=_resolve_int_arg(args, "promote_epochs", args.profile),
        promote_folds=_resolve_int_arg(args, "promote_folds", args.profile),
        **kwargs,
    )


def main(argv=None) -> None:
    args = _parse_args(argv)
    if args.list_profiles:
        print(json.dumps(_PROFILE_PRESETS, indent=2))
        return
    config = _build_config(args)
    run_ablation(config)


if __name__ == "__main__":
    main()
