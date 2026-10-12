"""
Stage 1 — Load raw Foursquare TIST2015 file and label categories.

Input  : raw tab-separated txt file (Yang dataset)
Output : parquet with columns
         [userid, placeid, datetime, latitude, longitude,
          category, venue_category_name, timezone_offset]

The venue_id is an alphanumeric hex string; this stage builds a VenueIndex
and maps it to a stable integer placeid. The index CSV is saved alongside
the output parquet for traceability.
"""

import logging
from pathlib import Path

import pandas as pd

from src.etl.utils.category_mapping import map_category
from src.etl.utils.venue_index import VenueIndex

logger = logging.getLogger(__name__)

# Column positions in the raw tab-separated file (no header row).
_RAW_COLUMNS = [
    "raw_userid",
    "raw_venue_id",
    "venue_category_id",
    "venue_category_name",
    "latitude",
    "longitude",
    "timezone_offset",
    "raw_utc_time",
]


def label_categories(
    raw_path: Path,
    output_path: Path,
    venue_index_path: Path,
) -> pd.DataFrame:
    """Load raw FSQ txt, deduplicate, map categories, save parquet.

    Parameters
    ----------
    raw_path:
        Path to the raw Yang dataset file (e.g. dataset_TSMC2014_NYC.txt).
    output_path:
        Destination parquet for stage-1 output.
    venue_index_path:
        CSV path where the venue-id → placeid mapping is saved.

    Returns
    -------
    DataFrame with the stage-1 schema.
    """
    logger.info("Stage 1 — loading raw Foursquare data from %s", raw_path)

    df = pd.read_csv(
        raw_path,
        sep="\t",
        header=None,
        names=_RAW_COLUMNS,
        dtype={
            "raw_userid": "int64",
            "raw_venue_id": str,
            "venue_category_id": str,
            "venue_category_name": str,
            "latitude": "float64",
            "longitude": "float64",
            "timezone_offset": "int64",
            "raw_utc_time": str,
        },
        encoding="latin1",
    )
    logger.info("Loaded %d rows.", len(df))

    # Parse datetime
    df["datetime"] = pd.to_datetime(df["raw_utc_time"], format="%a %b %d %H:%M:%S +0000 %Y", utc=True)

    # Rename user column
    df = df.rename(columns={"raw_userid": "userid"})

    # Build venue index from all unique venue IDs in this file
    venue_index = VenueIndex.build(df["raw_venue_id"].tolist())
    venue_index.save(venue_index_path)
    logger.info("Built venue index with %d unique venues. Saved to %s", len(venue_index), venue_index_path)

    df["placeid"] = venue_index.map_series(df["raw_venue_id"])

    # Remove duplicates
    n_before = len(df)
    df = df.drop_duplicates(subset=["userid", "placeid", "datetime"])
    logger.info("Removed %d duplicate check-ins. Remaining: %d", n_before - len(df), len(df))

    # Map categories
    df["venue_category_name"] = df["venue_category_name"].str.strip()
    df["category"] = df["venue_category_name"].apply(map_category)

    n_unmapped = df["category"].isna().sum()
    unmapped_counts = df.loc[df["category"].isna(), "venue_category_name"].value_counts()
    logger.info("Unmapped categories (%d rows): %s", n_unmapped, unmapped_counts.to_dict())

    df = df.dropna(subset=["category"])
    logger.info("After dropping unmapped categories: %d rows.", len(df))

    # Select output columns
    result = df[[
        "userid", "placeid", "datetime",
        "latitude", "longitude",
        "category", "venue_category_name",
        "timezone_offset",
    ]].copy()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    logger.info("Stage 1 output saved to %s", output_path)

    return result
