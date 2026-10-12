"""
Unit tests for src/etl/massive_steps/stage_1.py — load_and_label()
"""

import pandas as pd
import pytest

from src.etl.massive_steps.stage_1 import load_and_label
from src.configs.globals import CATEGORIES_MAP

VALID_SUPER_CATEGORIES = set(CATEGORIES_MAP.values()) - {"None"}


class TestLoadAndLabelOutputSchema:
    def test_required_columns_present(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(
            massive_steps_raw_file,
            tmp_path / "stage1.parquet",
            tmp_path / "vi.csv",
        )
        required = {"userid", "placeid", "datetime", "latitude", "longitude",
                    "category", "venue_category_name"}
        assert required.issubset(set(df.columns))

    def test_userid_is_integer(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert pd.api.types.is_integer_dtype(df["userid"])

    def test_placeid_is_int64(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["placeid"].dtype == "int64"

    def test_datetime_is_datetime(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert pd.api.types.is_datetime64_any_dtype(df["datetime"])

    def test_output_parquet_saved(self, massive_steps_raw_file, tmp_path):
        out = tmp_path / "stage1.parquet"
        load_and_label(massive_steps_raw_file, out, tmp_path / "vi.csv")
        assert out.exists()


class TestLoadAndLabelCategoryMapping:
    def test_all_categories_valid(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        bad = set(df["category"].unique()) - VALID_SUPER_CATEGORIES
        assert not bad, f"Invalid categories in output: {bad}"

    def test_no_null_categories(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert df["category"].isna().sum() == 0

    def test_food_mapped_correctly(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert "Food" in df["category"].values

    def test_arts_mapped_to_entertainment(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert "Entertainment" in df["category"].values
        assert "Arts & Entertainment" not in df["category"].values

    def test_subcategory_resolved_with_hierarchy(
        self, massive_steps_raw_file, massive_steps_categories_csv, tmp_path
    ):
        """When categories.csv is provided, subcategories should resolve."""
        import pandas as pd
        # Add a row with a subcategory name to the raw file
        raw = pd.read_csv(massive_steps_raw_file)
        new_row = {
            "user_id": 99, "venue_id": "subcatxyz",
            "local_datetime": "2017-04-01 10:00:00",
            "venue_category_id": "cat_italian",
            "venue_category_name": "Italian Restaurant",
            "latitude": 35.680, "longitude": 139.760,
        }
        raw = pd.concat([raw, pd.DataFrame([new_row])], ignore_index=True)
        enriched_raw = tmp_path / "enriched.csv"
        raw.to_csv(enriched_raw, index=False)

        df = load_and_label(
            enriched_raw,
            tmp_path / "s1.parquet",
            tmp_path / "vi.csv",
            categories_csv=massive_steps_categories_csv,
        )
        italian_rows = df[df["venue_category_name"] == "Italian Restaurant"]
        assert len(italian_rows) == 1
        assert italian_rows["category"].iloc[0] == "Food"


class TestLoadAndLabelDeduplication:
    def test_duplicates_removed(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        dupes = df.duplicated(subset=["userid", "placeid", "datetime"]).sum()
        assert dupes == 0

    def test_row_count_after_dedup_and_drop(self, massive_steps_raw_file, tmp_path):
        df = load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        # Fixture: 5 rows, 1 duplicate → 4 unique rows; all 4 have valid categories
        assert len(df) == 4


class TestLoadAndLabelVenueIndex:
    def test_venue_index_csv_created(self, massive_steps_raw_file, tmp_path):
        idx_path = tmp_path / "vi.csv"
        load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", idx_path)
        assert idx_path.exists()

    def test_venue_index_correct_columns(self, massive_steps_raw_file, tmp_path):
        idx_path = tmp_path / "vi.csv"
        load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", idx_path)
        idx = pd.read_csv(idx_path)
        assert "venue_id" in idx.columns
        assert "placeid" in idx.columns

    def test_placeid_sequential_from_zero(self, massive_steps_raw_file, tmp_path):
        idx_path = tmp_path / "vi.csv"
        load_and_label(massive_steps_raw_file, tmp_path / "s1.parquet", idx_path)
        idx = pd.read_csv(idx_path)
        placeids = sorted(idx["placeid"].tolist())
        assert placeids == list(range(len(placeids)))


class TestLoadAndLabelColumnNameVariants:
    def test_alternative_column_names_accepted(self, tmp_path):
        """Stage 1 should accept 'userId', 'venueId', etc. column names."""
        data = {
            "userId": [1, 2],
            "venueId": ["abc", "def"],
            "timestamp": ["2017-01-01 10:00:00", "2017-01-02 11:00:00"],
            "venue_category_name": ["Food", "Shop & Service"],
            "lat": [35.6, 35.7],
            "lng": [139.7, 139.8],
        }
        raw = tmp_path / "alt_cols.csv"
        pd.DataFrame(data).to_csv(raw, index=False)

        df = load_and_label(raw, tmp_path / "s1.parquet", tmp_path / "vi.csv")
        assert "userid" in df.columns
        assert "placeid" in df.columns
        assert len(df) == 2
