"""
Stage 2 — Derive local_datetime from the timezone_offset field.

The Yang TIST2015 dataset already includes a `timezone_offset` column
(integer minutes from UTC), so no shapefile spatial join is required.

Input  : stage-1 parquet
Output : stage-1 columns + local_datetime (naive datetime in local time)
"""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def add_local_datetime(input_path: Path, output_path: Path) -> pd.DataFrame:
    """Compute local_datetime from UTC datetime + timezone_offset.

    Parameters
    ----------
    input_path:
        Stage-1 parquet.
    output_path:
        Destination parquet for stage-2 output.

    Returns
    -------
    DataFrame with local_datetime column added.
    """
    logger.info("Stage 2 — computing local_datetime from %s", input_path)

    df = pd.read_parquet(input_path)

    # timezone_offset is in minutes; shift UTC datetime by the offset.
    # Result is a naive local datetime (no tz info — consistent with Gowalla output).
    offset_td = pd.to_timedelta(df["timezone_offset"], unit="m")
    local_dt = (df["datetime"] + offset_td).dt.tz_localize(None)
    df["local_datetime"] = local_dt

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)
    logger.info("Stage 2 output saved to %s (%d rows).", output_path, len(df))

    return df
