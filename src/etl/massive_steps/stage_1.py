"""
Stage 1 — Load a Massive-STEPS city CSV and label categories.

Input  : per-city CSV from the Massive-STEPS dataset
Output : parquet with columns
         [userid, placeid, datetime, latitude, longitude,
          category, venue_category_name]

Massive-STEPS venue IDs are alphanumeric Foursquare strings; a VenueIndex
is built here and saved as a CSV for traceability.
"""

import logging
from pathlib import Path

import pandas as pd

from src.etl.massive_steps.utils.category_mapping import load_hierarchy, map_category
from src.etl.utils.venue_index import VenueIndex

logger = logging.getLogger(__name__)

# Accepted column name variants across different Massive-STEPS releases
_COLUMN_ALIASES: dict[str, list[str]] = {
    "raw_userid":   ["user_id", "userId", "userid"],
    "raw_venue_id": ["venue_id", "venueId", "poi_id"],
    "raw_datetime": ["local_datetime", "datetime", "timestamp", "check_in_time"],
    "venue_category_name": ["venue_category", "venue_category_name", "category_name", "category"],
    "latitude":  ["latitude", "lat"],
    "longitude": ["longitude", "lng", "lon"],
}


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise column names to canonical names using _COLUMN_ALIASES."""
    rename_map = {}
    for canonical, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in df.columns and canonical not in df.columns:
                rename_map[alias] = canonical
                break
    return df.rename(columns=rename_map)


def load_and_label(
    raw_path: Path,
    output_path: Path,
    venue_index_path: Path,
    categories_csv: Path | None = None,
) -> pd.DataFrame:
    """Load raw Massive-STEPS city CSV, deduplicate, map categories, save parquet.

    Parameters
    ----------
    raw_path:
        Path to the per-city CSV file (e.g. new_york.csv).
    output_path:
        Destination parquet for stage-1 output.
    venue_index_path:
        CSV path where the venue-id → placeid mapping is saved.
    categories_csv:
        Optional path to the Massive-STEPS ``categories.csv``. When provided,
        subcategory names are resolved to super-categories via the hierarchy.

    Returns
    -------
    DataFrame with the stage-1 schema.
    """
    logger.info("Stage 1 — loading Massive-STEPS data from %s", raw_path)

    df = pd.read_csv(raw_path, dtype=str, low_memory=False)
    df = _rename_columns(df)
    logger.info("Loaded %d rows. Columns: %s", len(df), list(df.columns))

    # Parse coordinates
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    # Parse datetime — Massive-STEPS typically stores local datetime strings
    df["datetime"] = pd.to_datetime(df["raw_datetime"], errors="coerce", utc=False)
    df = df.dropna(subset=["datetime"])

    # userid — keep as integer where possible, fall back to string-indexed
    try:
        df["userid"] = df["raw_userid"].astype("int64")
    except (ValueError, TypeError):
        uid_index = {v: i for i, v in enumerate(df["raw_userid"].unique())}
        df["userid"] = df["raw_userid"].map(uid_index).astype("int64")
        logger.info("userid was non-integer; index-mapped %d unique users.", len(uid_index))

    # Assign placeid — if raw_venue_id is already numeric, use directly;
    # otherwise build a VenueIndex (alphanumeric FSQ-style IDs).
    try:
        df["placeid"] = pd.to_numeric(df["raw_venue_id"], errors="raise").astype("int64")
        # Save a minimal venue index for traceability
        unique_ids = df["raw_venue_id"].unique()
        venue_index_path.parent.mkdir(parents=True, exist_ok=True)
        pd.DataFrame({"venue_id": unique_ids, "placeid": unique_ids.astype("int64")}).to_csv(
            venue_index_path, index=False
        )
        logger.info("venue_id is numeric; using directly as placeid (%d unique venues).", len(unique_ids))
    except (ValueError, TypeError):
        venue_index = VenueIndex.build(df["raw_venue_id"].astype(str).tolist())
        venue_index.save(venue_index_path)
        df["placeid"] = venue_index.map_series(df["raw_venue_id"].astype(str))
        logger.info("Built venue index with %d unique venues. Saved to %s", len(venue_index), venue_index_path)

    # Deduplicate
    n_before = len(df)
    df = df.drop_duplicates(subset=["userid", "placeid", "datetime"])
    logger.info("Removed %d duplicate check-ins. Remaining: %d", n_before - len(df), len(df))

    # Load category hierarchy if provided
    hierarchy = None
    if categories_csv is not None and categories_csv.exists():
        hierarchy = load_hierarchy(categories_csv)
        logger.info("Loaded category hierarchy with %d entries.", len(hierarchy))
    else:
        logger.warning("No categories.csv provided; only top-level category names will be mapped.")

    # Map categories
    df["venue_category_name"] = df["venue_category_name"].str.strip()
    df["category"] = df["venue_category_name"].apply(lambda x: map_category(x, hierarchy))

    n_unmapped = df["category"].isna().sum()
    if n_unmapped:
        unmapped = df.loc[df["category"].isna(), "venue_category_name"].value_counts().head(20)
        logger.info("Unmapped categories (%d rows, top 20): %s", n_unmapped, unmapped.to_dict())

    df = df.dropna(subset=["category"])
    logger.info("After dropping unmapped categories: %d rows.", len(df))

    result = df[[
        "userid", "placeid", "datetime",
        "latitude", "longitude",
        "category", "venue_category_name",
    ]].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    logger.info("Stage 1 output saved to %s", output_path)

    return result
