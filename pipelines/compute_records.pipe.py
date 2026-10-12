"""Standalone pipeline to compute/recompute best_record.json for result directories.

Usage:
    # Compute records for a specific engine+state
    python pipelines/compute_records.pipe.py --engine hgi --state alabama

    # Compute records for all engine+state combos found under results/
    python pipelines/compute_records.pipe.py --all
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_src = str(Path(__file__).resolve().parent.parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import RESULTS_ROOT, EmbeddingEngine, IoPaths
from tracking.records import compute_best_record

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

_VALID_ENGINES = [e.value for e in EmbeddingEngine]


def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute best_record.json for training result directories.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--engine",
        type=str,
        default=None,
        choices=_VALID_ENGINES,
        help="Embedding engine.",
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help="Dataset state (e.g. florida, alabama).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Compute records for all engine+state directories found under results/.",
    )
    return parser.parse_args(argv)


def _process_dir(results_dir: Path, label: str) -> None:
    """Compute best_record.json for a single results directory."""
    # Check if any runs exist before writing.
    if not list(results_dir.glob("*/summary/full_summary.json")):
        logger.info("  %s: no runs found, skipping.", label)
        return

    record_path = compute_best_record(results_dir)
    logger.info("  %s: wrote %s", label, record_path)

    import json
    data = json.loads(record_path.read_text(encoding="utf-8"))
    for task, info in sorted(data.get("tasks", {}).items()):
        logger.info("    %s: F1=%.4f (%s)", task, info["f1_mean"], info["run_folder"])


def main(argv=None) -> None:
    args = _parse_args(argv)

    if args.all:
        if not RESULTS_ROOT.exists():
            logger.error("Results root not found: %s", RESULTS_ROOT)
            sys.exit(1)

        count = 0
        for engine_dir in sorted(RESULTS_ROOT.iterdir()):
            if not engine_dir.is_dir():
                continue
            for state_dir in sorted(engine_dir.iterdir()):
                if not state_dir.is_dir():
                    continue
                label = f"{engine_dir.name}/{state_dir.name}"
                _process_dir(state_dir, label)
                count += 1

        logger.info("Processed %d engine+state directories.", count)

    elif args.engine is not None and args.state is not None:
        engine = EmbeddingEngine(args.engine)
        results_dir = IoPaths.get_results_dir(args.state, engine)
        if not results_dir.exists():
            logger.error("Results directory not found: %s", results_dir)
            sys.exit(1)
        label = f"{args.engine}/{args.state}"
        _process_dir(results_dir, label)

    else:
        logger.error("Provide --engine and --state, or use --all.")
        sys.exit(1)


if __name__ == "__main__":
    main()
