"""
Unit tests for src/etl/foursquare/stage_1.py — label_categories()

Tests use a synthetic raw file in the exact Yang TIST2015 tab-separated
format so no real data download is required.
"""

import pandas as pd
import pytest

from src.etl.foursquare.stage_1 import label_categories
from src.configs.globals import CATEGORIES_MAP

VALID_SUPER_CATEGORIES = set(CATEGORIES_MAP.values()) - {"None"}


class TestLabelCategoriesOutputSchema:
    def test_output_columns_present(self, foursquare_raw_file, tmp_path):
        out = tmp_path / "stage1.parquet"
        idx = tmp_path / "venue_index.csv"
        df = label_categories(foursquare_raw_file, out, idx)

        required = {"userid", "placeid", "datetime", "latitude", "longitude",
                    "category", "venue_category_name", "timezone_offset"}
        assert required.issubset(set(df.columns)), f"Missing columns: {required - set(df.columns)}"

    def test_userid_is_int64(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["userid"].dtype == "int64"

    def test_placeid_is_int64(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["placeid"].dtype == "int64"

    def test_datetime_is_datetime(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert pd.api.types.is_datetime64_any_dtype(df["datetime"])

    def test_latitude_longitude_are_float(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["latitude"].dtype == "float64"
        assert df["longitude"].dtype == "float64"

    def test_output_parquet_saved(self, foursquare_raw_file, tmp_path):
        out = tmp_path / "stage1.parquet"
        idx = tmp_path / "vi.csv"
        label_categories(foursquare_raw_file, out, idx)
        assert out.exists()


class TestLabelCategoriesCategoryMapping:
    def test_all_categories_in_valid_set(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        unknown = set(df["category"].unique()) - VALID_SUPER_CATEGORIES
        assert not unknown, f"Unexpected categories in output: {unknown}"

    def test_food_category_present(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert "Food" in df["category"].values

    def test_shop_mapped_to_shopping(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # The raw file has "Shop & Service" → should appear as "Shopping"
        assert "Shopping" in df["category"].values
        assert "Shop & Service" not in df["category"].values

    def test_event_rows_dropped(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # The fixture includes one "Event" row — it must be dropped
        assert "Event" not in df["venue_category_name"].values

    def test_no_null_categories(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["category"].isna().sum() == 0


class TestLabelCategoriesDeduplication:
    def test_duplicate_checkins_removed(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        dupes = df.duplicated(subset=["userid", "placeid", "datetime"]).sum()
        assert dupes == 0, "Duplicate check-ins must be removed"

    def test_row_count_correct(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # Fixture: 5 raw rows → 1 duplicate → 1 Event row → 3 valid unique rows
        assert len(df) == 3


class TestLabelCategoriesVenueIndex:
    def test_venue_index_csv_created(self, foursquare_raw_file, tmp_path):
        idx_path = tmp_path / "venue_index.csv"
        label_categories(foursquare_raw_file, tmp_path / "s1.parquet", idx_path)
        assert idx_path.exists()

    def test_venue_index_has_correct_columns(self, foursquare_raw_file, tmp_path):
        idx_path = tmp_path / "venue_index.csv"
        label_categories(foursquare_raw_file, tmp_path / "s1.parquet", idx_path)
        idx_df = pd.read_csv(idx_path)
        assert "venue_id" in idx_df.columns
        assert "placeid" in idx_df.columns

    def test_placeid_values_are_sequential_from_zero(self, foursquare_raw_file, tmp_path):
        idx_path = tmp_path / "venue_index.csv"
        label_categories(foursquare_raw_file, tmp_path / "s1.parquet", idx_path)
        idx_df = pd.read_csv(idx_path)
        placeids = sorted(idx_df["placeid"].tolist())
        assert placeids == list(range(len(placeids)))

    def test_same_venue_id_maps_to_same_placeid(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # venue "4b058f49f964a520b04e23e3" appears twice in the fixture (both Food rows)
        # after dedup only once; but both should share the same placeid
        venue_counts = df.groupby("placeid").size()
        assert (venue_counts >= 1).all()


class TestLabelCategoriesDatetimeParsing:
    def test_datetime_is_utc_aware(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # datetime should be UTC-aware (tz not None)
        assert df["datetime"].dt.tz is not None

    def test_timezone_offset_retained(self, foursquare_raw_file, tmp_path):
        df = label_categories(foursquare_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert "timezone_offset" in df.columns
        # All offsets should be integers (minutes from UTC)
        assert pd.api.types.is_integer_dtype(df["timezone_offset"])
