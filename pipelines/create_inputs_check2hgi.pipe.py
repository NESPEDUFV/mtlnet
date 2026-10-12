"""Create next-region input for the check2HGI MTL track.

Usage::

    python pipelines/create_inputs_check2hgi.pipe.py --state alabama
    python pipelines/create_inputs_check2hgi.pipe.py --state florida

Prerequisite: ``pipelines/embedding/check2hgi.pipe.py`` must have run
for the state. This script consumes the ``checkin_graph.pt`` +
``sequences_next.parquet`` + ``next.parquet`` triple it produces.

Output: ``output/check2hgi/<state>/input/next_region.parquet``.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import EmbeddingEngine, IoPaths
from data.inputs.next_region import build_next_region_frame

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_next_region_input(state: str) -> int:
    out_path = IoPaths.get_next_region(state, EmbeddingEngine.CHECK2HGI)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info("[%s] Building next_region frame…", state)
    df, n_regions = build_next_region_frame(state)

    logger.info(
        "[%s] rows=%d, region_cardinality=%d, class_head_top5=%s",
        state,
        len(df),
        n_regions,
        df["region_idx"].value_counts().head(5).to_dict(),
    )

    df.to_parquet(out_path)
    logger.info("[%s] Saved: %s (n_regions=%d)", state, out_path, n_regions)
    return n_regions


def main() -> None:
    parser = argparse.ArgumentParser(description="Build check2HGI next_region inputs")
    parser.add_argument(
        "--state",
        type=str,
        action="append",
        default=None,
        help="State name (repeat for multiple). Defaults to ['alabama','florida'].",
    )
    args = parser.parse_args()
    states = args.state if args.state else ["alabama", "florida"]

    for state in states:
        try:
            n_regions = generate_next_region_input(state)
            logger.info("[%s] OK (n_regions=%d)", state, n_regions)
        except Exception as exc:
            logger.error("[%s] FAILED: %s", state, exc, exc_info=True)
            raise


if __name__ == "__main__":
    main()
