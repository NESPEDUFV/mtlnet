"""
Stage 2 — Add local_datetime via timezone shapefile spatial join.

Massive-STEPS does not include a timezone offset column, so we use the same
geopandas spatial join approach as the Gowalla ETL (stage_2.py).

The ``local_datetime`` column is derived by localising the parsed datetime
to the timezone inferred from the POI coordinates.

If the datetime in stage-1 is already a local time (Massive-STEPS stores
``local_datetime``), this stage passes it through unchanged and sets
``local_datetime = datetime`` with a log warning rather than failing.

Input  : stage-1 parquet
Output : stage-1 columns + local_datetime
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def add_local_datetime(
    input_path: Path,
    output_path: Path,
    timezones_shp: Path | None = None,
) -> pd.DataFrame:
    """Derive local_datetime from coordinates using a timezone shapefile.

    Parameters
    ----------
    input_path:
        Stage-1 parquet.
    output_path:
        Destination parquet for stage-2 output.
    timezones_shp:
        Path to the timezone shapefile (same as used in Gowalla ETL).
        When None, attempts to locate it at the default project path
        ``data/miscellaneous/combined-shapefile-with-oceans.shp``.
        If the shapefile is absent, ``local_datetime`` is set equal to
        ``datetime`` and a warning is issued.

    Returns
    -------
    DataFrame with local_datetime column added.
    """
    logger.info("Stage 2 — adding local_datetime for %s", input_path)

    df = pd.read_parquet(input_path)

    # If the stage-1 datetime is already timezone-naive local time
    # (Massive-STEPS stores local_datetime), skip the shapefile join.
    if df["datetime"].dt.tz is None:
        logger.info(
            "datetime column is tz-naive — assuming it is already local time. "
            "Setting local_datetime = datetime."
        )
        df["local_datetime"] = df["datetime"]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        logger.info("Stage 2 output saved to %s (%d rows).", output_path, len(df))
        return df

    # UTC datetime: derive local_datetime via shapefile spatial join.
    if timezones_shp is None:
        _project_root = Path(__file__).resolve().parents[3]
        timezones_shp = _project_root / "data" / "miscellaneous" / "combined-shapefile-with-oceans.shp"

    if not timezones_shp.exists():
        logger.warning(
            "Timezone shapefile not found at %s. Setting local_datetime = datetime (UTC). "
            "Download the shapefile to get correct local times.",
            timezones_shp,
        )
        df["local_datetime"] = df["datetime"].dt.tz_localize(None)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_path, index=False)
        return df

    import geopandas as gp

    gdf = gp.GeoDataFrame(
        df[["datetime"]],
        geometry=gp.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326",
    )

    timezones = gp.read_file(timezones_shp)
    timezones = timezones.to_crs("EPSG:4326")

    df_tz = gp.sjoin(timezones[["tzid", "geometry"]], gdf, predicate="contains")
    df_tz = df_tz.rename(columns={"index_right": "index"})
    df_tz = df_tz.set_index("index").sort_index()
    df_tz = df_tz[~df_tz.index.duplicated(keep="first")]

    df_tz["local_datetime"] = [
        dt.tz_convert(tz).strftime("%Y-%m-%d %H:%M:%S")
        for dt, tz in zip(df_tz["datetime"], df_tz["tzid"])
    ]
    df_tz["local_datetime"] = pd.to_datetime(df_tz["local_datetime"])

    df_out = df.join(df_tz[["local_datetime"]], how="inner")
    total_loss = len(df) - len(df_out)
    logger.info("Timezone join loss: %d rows (%.1f%%).", total_loss, 100 * total_loss / max(len(df), 1))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_parquet(output_path, index=False)
    logger.info("Stage 2 output saved to %s (%d rows).", output_path, len(df_out))

    return df_out
