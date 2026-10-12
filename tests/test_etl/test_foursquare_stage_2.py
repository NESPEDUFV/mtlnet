"""
Unit tests for src/etl/foursquare/stage_2.py — add_local_datetime()

Verifies that local_datetime is computed correctly from timezone_offset
without any external shapefile dependency.
"""

import pandas as pd
import pytest

from src.etl.foursquare.stage_2 import add_local_datetime


def _write_stage1_parquet(path, rows: list[dict]) -> None:
    """Helper: write a minimal stage-1 parquet for stage-2 input."""
    df = pd.DataFrame(rows)
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    df["latitude"] = df["latitude"].astype("float64")
    df["longitude"] = df["longitude"].astype("float64")
    df["timezone_offset"] = df["timezone_offset"].astype("int64")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


class TestAddLocalDatetime:
    def test_output_has_local_datetime_column(self, tmp_path):
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 18:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
        ])
        df = add_local_datetime(inp, out)
        assert "local_datetime" in df.columns

    def test_negative_offset_shifts_backward(self, tmp_path):
        """UTC - 5h (offset=-300) → local = UTC - 5h."""
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 18:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
        ])
        df = add_local_datetime(inp, out)
        local = df["local_datetime"].iloc[0]
        # 18:00 UTC - 5h = 13:00 local
        assert local.hour == 13
        assert local.minute == 0

    def test_positive_offset_shifts_forward(self, tmp_path):
        """UTC + 9h (offset=+540, Tokyo) → local = UTC + 9h."""
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 01:00:00",
             "latitude": 35.6, "longitude": 139.7, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": 540},
        ])
        df = add_local_datetime(inp, out)
        local = df["local_datetime"].iloc[0]
        # 01:00 UTC + 9h = 10:00 local
        assert local.hour == 10

    def test_zero_offset_equals_utc(self, tmp_path):
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 12:00:00",
             "latitude": 51.5, "longitude": -0.1, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": 0},
        ])
        df = add_local_datetime(inp, out)
        local = df["local_datetime"].iloc[0]
        assert local.hour == 12

    def test_local_datetime_is_tz_naive(self, tmp_path):
        """local_datetime should be a naive datetime (no tz info), like Gowalla output."""
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 18:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
        ])
        df = add_local_datetime(inp, out)
        assert df["local_datetime"].dt.tz is None

    def test_row_count_preserved(self, tmp_path):
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        rows = [
            {"userid": i, "placeid": i, "datetime": "2012-04-03 18:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300}
            for i in range(5)
        ]
        _write_stage1_parquet(inp, rows)
        df = add_local_datetime(inp, out)
        assert len(df) == 5

    def test_output_parquet_saved(self, tmp_path):
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 18:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
        ])
        add_local_datetime(inp, out)
        assert out.exists()

    def test_date_boundary_crossing(self, tmp_path):
        """A large negative offset that pushes datetime to previous day."""
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            # 02:00 UTC - 5h = 21:00 previous day
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 02:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
        ])
        df = add_local_datetime(inp, out)
        local = df["local_datetime"].iloc[0]
        assert local.hour == 21
        assert local.day == 2   # previous day

    def test_mixed_offsets(self, tmp_path):
        inp = tmp_path / "stage1.parquet"
        out = tmp_path / "stage2.parquet"
        _write_stage1_parquet(inp, [
            {"userid": 1, "placeid": 0, "datetime": "2012-04-03 12:00:00",
             "latitude": 40.7, "longitude": -74.0, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": -300},
            {"userid": 2, "placeid": 1, "datetime": "2012-04-03 12:00:00",
             "latitude": 35.6, "longitude": 139.7, "category": "Food",
             "venue_category_name": "Food", "timezone_offset": 540},
        ])
        df = add_local_datetime(inp, out)
        hours = df.set_index("userid")["local_datetime"].dt.hour
        assert hours[1] == 7    # 12 - 5
        assert hours[2] == 21   # 12 + 9
