#!/usr/bin/env python3
"""Run a single embedding pipeline for one state."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one embedding pipeline for one state.")
    parser.add_argument("--state", required=True, help="State name in lowercase (e.g. florida)")
    parser.add_argument(
        "--engine",
        required=True,
        choices=("sphere2vec", "time2vec", "hgi"),
        help="Embedding engine",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_dir = Path(__file__).resolve().parents[1]
    for sub in ("src", "research"):
        p = str(repo_dir / sub)
        if p not in sys.path:
            sys.path.insert(0, p)

    from configs.paths import Resources

    state = args.state.lower()
    state_key = state.capitalize()

    shapefiles = {
        "florida": Resources.TL_FL,
        "alabama": Resources.TL_AL,
        "georgia": Resources.TL_GA,
        "california": Resources.TL_CA,
        "texas": Resources.TL_TX,
        "arizona": Resources.TL_AZ,
    }

    pipe_path = repo_dir / f"pipelines/embedding/{args.engine}.pipe.py"
    if not pipe_path.exists():
        raise FileNotFoundError(f"Pipeline not found: {pipe_path}")

    spec = importlib.util.spec_from_file_location(f"_pipe_{args.engine}_{state}", pipe_path)
    pipe = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(pipe)

    if args.engine == "hgi":
        shapefile = shapefiles.get(state)
        if shapefile is None:
            raise ValueError(f'No shapefile registered for state "{state}"')
        pipe.STATES = {state_key: {"shapefile": shapefile}}
    else:
        pipe.STATES = {state_key: {}}

    pipe.run_pipeline()


if __name__ == "__main__":
    main()
