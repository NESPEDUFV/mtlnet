"""
Massive-STEPS ETL — main orchestrator.

Supported cities (slug → human name):
    new_york   → New York
    tokyo      → Tokyo
    sao_paulo  → Sao Paulo
    melbourne  → Melbourne
    sydney     → Sydney
    beijing    → Beijing
    shanghai   → Shanghai
    moscow     → Moscow
    istanbul   → Istanbul
    jakarta    → Jakarta
    bandung    → Bandung
    tangerang  → Tangerang
    palembang  → Palembang
    petaling_jaya → Petaling Jaya
    kuwait_city   → Kuwait City

Usage (standalone):
    python -m src.etl.massive_steps.main --city new_york

Or import and call:
    from src.etl.massive_steps.main import run
    run(city="new_york")
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

from src.etl.massive_steps import stage_1, stage_2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# City configuration
# ---------------------------------------------------------------------------

CITY_CONFIG: dict[str, dict] = {
    # state_slug must equal output_name.lower() so IoPaths.get_city(state_slug) resolves correctly.
    # Convention: {city}_ms   →   capitalize → {City}_ms.parquet
    "new_york":     {"raw_filename": "new_york.csv",     "city_name": "New York (MS)",     "state_slug": "new_york_ms"},
    "tokyo":        {"raw_filename": "tokyo.csv",        "city_name": "Tokyo (MS)",        "state_slug": "tokyo_ms"},
    "sao_paulo":    {"raw_filename": "sao_paulo.csv",    "city_name": "Sao Paulo (MS)",    "state_slug": "sao_paulo_ms"},
    "melbourne":    {"raw_filename": "melbourne.csv",    "city_name": "Melbourne (MS)",    "state_slug": "melbourne_ms"},
    "sydney":       {"raw_filename": "sydney.csv",       "city_name": "Sydney (MS)",       "state_slug": "sydney_ms"},
    "beijing":      {"raw_filename": "beijing.csv",      "city_name": "Beijing (MS)",      "state_slug": "beijing_ms"},
    "shanghai":     {"raw_filename": "shanghai.csv",     "city_name": "Shanghai (MS)",     "state_slug": "shanghai_ms"},
    "moscow":       {"raw_filename": "moscow.csv",       "city_name": "Moscow (MS)",       "state_slug": "moscow_ms"},
    "istanbul":     {"raw_filename": "istanbul.csv",     "city_name": "Istanbul (MS)",     "state_slug": "istanbul_ms"},
    "jakarta":      {"raw_filename": "jakarta.csv",      "city_name": "Jakarta (MS)",      "state_slug": "jakarta_ms"},
    "bandung":      {"raw_filename": "bandung.csv",      "city_name": "Bandung (MS)",      "state_slug": "bandung_ms"},
    "tangerang":    {"raw_filename": "tangerang.csv",    "city_name": "Tangerang (MS)",    "state_slug": "tangerang_ms"},
    "palembang":    {"raw_filename": "palembang.csv",    "city_name": "Palembang (MS)",    "state_slug": "palembang_ms"},
    "petaling_jaya":{"raw_filename": "petaling_jaya.csv","city_name": "Petaling Jaya (MS)","state_slug": "petaling_jaya_ms"},
    "kuwait_city":  {"raw_filename": "kuwait_city.csv",  "city_name": "Kuwait City (MS)",  "state_slug": "kuwait_city_ms"},
}

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _resolve_paths(city: str, raw_data_dir: Path, data_root: Path):
    cfg = CITY_CONFIG[city]
    raw_path = raw_data_dir / cfg["raw_filename"]
    categories_csv = raw_data_dir / "categories.csv"

    state_slug = cfg["state_slug"]
    temp_dir = data_root / "temp" / "massive_steps" / city
    stage1_path = temp_dir / "stage1.parquet"
    stage2_path = temp_dir / "stage2.parquet"
    venue_index_path = data_root / "miscellaneous" / f"massive_steps_{city}_venue_index.csv"
    # output_name = state_slug.capitalize() so IoPaths.get_city(state_slug) resolves correctly.
    output_path = data_root / "checkins" / f"{state_slug.capitalize()}.parquet"

    return raw_path, categories_csv, stage1_path, stage2_path, venue_index_path, output_path, cfg["city_name"], state_slug


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def run(
    city: str,
    raw_data_dir: Path | None = None,
    data_root: Path | None = None,
    timezones_shp: Path | None = None,
) -> pd.DataFrame:
    """Run the full Massive-STEPS ETL for one city.

    Parameters
    ----------
    city:
        One of the slugs in CITY_CONFIG (e.g. "new_york").
    raw_data_dir:
        Directory containing the per-city CSV files and categories.csv.
        Defaults to <project_root>/data/raw/massive_steps/.
    data_root:
        Project data root. Defaults to <project_root>/data/.
    timezones_shp:
        Path to timezone shapefile. When None, uses the default project path.

    Returns
    -------
    Final DataFrame saved to data/checkins/{city_name}.parquet.
    """
    if city not in CITY_CONFIG:
        raise ValueError(f"Unknown city '{city}'. Choose from: {list(CITY_CONFIG)}")

    _project_root = Path(__file__).resolve().parents[3]

    if data_root is None:
        data_root = _project_root / "data"
    if raw_data_dir is None:
        raw_data_dir = data_root / "raw" / "massive_steps"

    raw_path, categories_csv, stage1_path, stage2_path, venue_index_path, output_path, city_name, state_slug = (
        _resolve_paths(city, raw_data_dir, data_root)
    )

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw Massive-STEPS file not found: {raw_path}\n"
            f"Download from https://github.com/cruiseresearchgroup/Massive-STEPS "
            f"and place at {raw_path}"
        )

    logger.info("=== Massive-STEPS ETL | city=%s ===", city)

    # Stage 1
    if stage1_path.exists():
        logger.info("Stage 1 cache found at %s — skipping.", stage1_path)
    else:
        stage_1.load_and_label(
            raw_path=raw_path,
            output_path=stage1_path,
            venue_index_path=venue_index_path,
            categories_csv=categories_csv if categories_csv.exists() else None,
        )

    # Stage 2
    if stage2_path.exists():
        logger.info("Stage 2 cache found at %s — skipping.", stage2_path)
    else:
        stage_2.add_local_datetime(
            input_path=stage1_path,
            output_path=stage2_path,
            timezones_shp=timezones_shp,
        )

    # Final assembly
    logger.info("Assembling final output...")
    df = pd.read_parquet(stage2_path)
    df["city_name"] = city_name
    # HGI requires a `spot` column (fine-grained venue type, used as fclass).
    # venue_category_name is the best STEPS proxy (e.g. "Italian Restaurant").
    df["spot"] = df["venue_category_name"]

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
    parser = argparse.ArgumentParser(description="Massive-STEPS ETL pipeline")
    parser.add_argument("--city", required=True, choices=list(CITY_CONFIG), help="City slug to process")
    parser.add_argument("--raw-data-dir", type=Path, default=None)
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--timezones-shp", type=Path, default=None)
    args = parser.parse_args()

    try:
        run(
            city=args.city,
            raw_data_dir=args.raw_data_dir,
            data_root=args.data_root,
            timezones_shp=args.timezones_shp,
        )
    except FileNotFoundError as e:
        logger.error("%s", e)
        sys.exit(1)
