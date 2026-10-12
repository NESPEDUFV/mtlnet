"""
Unit tests for src/etl/massive_steps/stage_2.py — add_local_datetime()

Covers the two primary code paths:
1. tz-naive datetime → passes through unchanged (local_datetime = datetime)
2. UTC datetime + missing shapefile → fallback warning, local_datetime = datetime (UTC stripped)
"""

import pandas as pd
import pytest

from src.etl.massive_steps.stage_2 import add_local_datetime


def _write_stage1_parquet(path, rows: list[dict], utc: bool = False) -> None:
    df = pd.DataFrame(rows)
    if utc:
        df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    else:
        df["datetime"] = pd.to_datetime(df["datetime"])   # tz-naive
    df["latitude"] = df["latitude"].astype("float64")
    df["longitude"] = df["longitude"].astype("float64")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


_BASE_ROW = {
    "userid": 1, "placeid": 0,
    "datetime": "2017-03-01 10:00:00",
    "latitude": 35.68, "longitude": 139.76,
    "category": "Food", "venue_category_name": "Food",
}


class TestNaiveDatetimePassthrough:
    """When stage-1 datetime is tz-naive (Massive-STEPS stores local time),
    stage-2 should set local_datetime = datetime without modification."""

    def test_local_datetime_column_added(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        df = add_local_datetime(inp, out)
        assert "local_datetime" in df.columns

    def test_local_datetime_equals_datetime(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        df = add_local_datetime(inp, out)
        assert df["local_datetime"].iloc[0] == df["datetime"].iloc[0]

    def test_row_count_preserved(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        rows = [dict(_BASE_ROW, userid=i) for i in range(10)]
        _write_stage1_parquet(inp, rows)
        df = add_local_datetime(inp, out)
        assert len(df) == 10

    def test_output_parquet_saved(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        add_local_datetime(inp, out)
        assert out.exists()

    def test_original_columns_preserved(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        df = add_local_datetime(inp, out)
        for col in ["userid", "placeid", "datetime", "category", "venue_category_name"]:
            assert col in df.columns


class TestUTCDatetimeMissingShapefile:
    """When datetime is UTC-aware but the timezone shapefile is absent,
    stage-2 should fall back gracefully (warn + strip tz)."""

    def test_fallback_when_shapefile_missing(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        nonexistent_shp = tmp_path / "does_not_exist.shp"
        _write_stage1_parquet(inp, [_BASE_ROW], utc=True)

        # Should not raise; falls back silently
        df = add_local_datetime(inp, out, timezones_shp=nonexistent_shp)
        assert "local_datetime" in df.columns

    def test_fallback_local_datetime_is_tz_naive(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        nonexistent_shp = tmp_path / "no.shp"
        _write_stage1_parquet(inp, [_BASE_ROW], utc=True)

        df = add_local_datetime(inp, out, timezones_shp=nonexistent_shp)
        assert df["local_datetime"].dt.tz is None

    def test_fallback_row_count_unchanged(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        rows = [dict(_BASE_ROW, userid=i) for i in range(5)]
        _write_stage1_parquet(inp, rows, utc=True)

        df = add_local_datetime(inp, out, timezones_shp=tmp_path / "no.shp")
        assert len(df) == 5

    def test_output_parquet_saved_on_fallback(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW], utc=True)
        add_local_datetime(inp, out, timezones_shp=tmp_path / "no.shp")
        assert out.exists()


class TestOutputSchemaConsistency:
    """The output schema from stage_2 must be downstream-compatible."""

    def test_local_datetime_is_datetime_type(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        df = add_local_datetime(inp, out)
        assert pd.api.types.is_datetime64_any_dtype(df["local_datetime"])

    def test_all_downstream_columns_present(self, tmp_path):
        inp = tmp_path / "s1.parquet"
        out = tmp_path / "s2.parquet"
        _write_stage1_parquet(inp, [_BASE_ROW])
        df = add_local_datetime(inp, out)
        required = {"userid", "placeid", "datetime", "latitude", "longitude",
                    "category", "venue_category_name", "local_datetime"}
        assert required.issubset(set(df.columns))
