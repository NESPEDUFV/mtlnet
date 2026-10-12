"""
Foursquare TIST2015 ETL — main orchestrator.

Supported cities:
    "nyc"   → New York City  (dataset_TSMC2014_NYC.txt)
    "tokyo" → Tokyo          (dataset_TSMC2014_TKY.txt)

Usage (standalone):
    python -m src.etl.foursquare.main --city nyc

Or import and call:
    from src.etl.foursquare.main import run
    run(city="nyc")
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from src.etl.foursquare import stage_1, stage_2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# City configuration
# ---------------------------------------------------------------------------

_CITY_CONFIG: dict[str, dict] = {
    "nyc": {
        "raw_filename": "dataset_TSMC2014_NYC.txt",
        "city_name": "New York City (FSQ)",
        # output_name must equal state.capitalize() so IoPaths.get_city(state) resolves correctly.
        # state slug: "nyc_fsq"  →  capitalize → "Nyc_fsq"
        "output_name": "Nyc_fsq",
        "state_slug": "nyc_fsq",
    },
    "tokyo": {
        "raw_filename": "dataset_TSMC2014_TKY.txt",
        "city_name": "Tokyo (FSQ)",
        "output_name": "Tokyo_fsq",
        "state_slug": "tokyo_fsq",
    },
}

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _resolve_paths(city: str, raw_data_dir: Path, data_root: Path):
    cfg = _CITY_CONFIG[city]

    raw_path = raw_data_dir / cfg["raw_filename"]
    temp_dir = data_root / "temp" / "foursquare" / city

    stage1_path = temp_dir / "stage1.parquet"
    stage2_path = temp_dir / "stage2.parquet"
    venue_index_path = data_root / "miscellaneous" / f"foursquare_{city}_venue_index.csv"
    output_path = data_root / "checkins" / f"{cfg['output_name']}.parquet"

    return raw_path, stage1_path, stage2_path, venue_index_path, output_path, cfg["city_name"], cfg["state_slug"]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run(
    city: str,
    raw_data_dir: Path | None = None,
    data_root: Path | None = None,
) -> pd.DataFrame:
    """Run the full FSQ ETL for one city.

    Parameters
    ----------
    city:
        "nyc" or "tokyo".
    raw_data_dir:
        Directory containing the raw Yang dataset txt files.
        Defaults to <project_root>/data/raw/foursquare/.
    data_root:
        Project data root. Defaults to <project_root>/data/.

    Returns
    -------
    Final DataFrame saved to data/checkins/{city_name}.parquet.
    """
    if city not in _CITY_CONFIG:
        raise ValueError(f"Unknown city '{city}'. Choose from: {list(_CITY_CONFIG)}")

    # Resolve project root relative to this file (src/etl/foursquare/main.py)
    _project_root = Path(__file__).resolve().parents[3]

    if data_root is None:
        data_root = _project_root / "data"
    if raw_data_dir is None:
        raw_data_dir = data_root / "raw" / "foursquare"

    raw_path, stage1_path, stage2_path, venue_index_path, output_path, city_name, state_slug = (
        _resolve_paths(city, raw_data_dir, data_root)
    )

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw Foursquare file not found: {raw_path}\n"
            f"Download from https://sites.google.com/site/yangdingqi/home/foursquare-dataset "
            f"and place at {raw_path}"
        )

    logger.info("=== Foursquare ETL | city=%s ===", city)

    # Stage 1
    if stage1_path.exists():
        logger.info("Stage 1 cache found at %s — skipping.", stage1_path)
    else:
        stage_1.label_categories(raw_path, stage1_path, venue_index_path)

    # Stage 2
    if stage2_path.exists():
        logger.info("Stage 2 cache found at %s — skipping.", stage2_path)
    else:
        stage_2.add_local_datetime(stage1_path, stage2_path)

    # Final assembly
    logger.info("Assembling final output...")
    df = pd.read_parquet(stage2_path)
    df["city_name"] = city_name
    # HGI requires a `spot` column (fine-grained venue type, used as fclass).
    # venue_category_name is the best FSQ proxy (e.g. "Italian Restaurant").
    df["spot"] = df["venue_category_name"]

    # Drop the timezone_offset column (internal use only)
    df = df.drop(columns=["timezone_offset"], errors="ignore")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)

    logger.info(
        "Done. Saved %d check-ins to %s\nCategory distribution:\n%s",
        len(df),
        output_path,
        df["category"].value_counts().to_string(),
    )
    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Foursquare TIST2015 ETL pipeline")
    parser.add_argument("--city", required=True, choices=list(_CITY_CONFIG), help="City to process")
    parser.add_argument("--raw-data-dir", type=Path, default=None, help="Directory with raw txt files")
    parser.add_argument("--data-root", type=Path, default=None, help="Project data root")
    args = parser.parse_args()

    try:
        run(city=args.city, raw_data_dir=args.raw_data_dir, data_root=args.data_root)
    except FileNotFoundError as e:
        logger.error("%s", e)
        sys.exit(1)
