"""
Unit tests for src/etl/utils/venue_index.py — VenueIndex class.
"""

import pandas as pd
import pytest

from src.etl.utils.venue_index import VenueIndex


class TestVenueIndexBuild:
    def test_empty_input_produces_empty_index(self):
        idx = VenueIndex.build([])
        assert len(idx) == 0

    def test_single_venue_gets_index_zero(self):
        idx = VenueIndex.build(["abc123"])
        series = idx.map_series(pd.Series(["abc123"]))
        assert series.iloc[0] == 0

    def test_indices_are_zero_based_sequential(self):
        vids = ["aaa", "bbb", "ccc"]
        idx = VenueIndex.build(vids)
        result = idx.map_series(pd.Series(vids))
        assert list(result) == [0, 1, 2]

    def test_insertion_order_preserved(self):
        """First occurrence gets the lowest index."""
        idx = VenueIndex.build(["z", "a", "m"])
        r = idx.map_series(pd.Series(["z", "a", "m"]))
        assert r["z" == pd.Series(["z", "a", "m"])].iloc[0] == 0
        # Simpler assertion: sorted by insertion
        assert list(r) == [0, 1, 2]

    def test_duplicate_ids_get_same_index(self):
        idx = VenueIndex.build(["x", "y", "x", "x", "y"])
        result = idx.map_series(pd.Series(["x", "y", "x"]))
        assert result.iloc[0] == result.iloc[2]
        assert result.iloc[0] != result.iloc[1]

    def test_len_counts_unique_venues(self):
        idx = VenueIndex.build(["a", "b", "a", "c", "b"])
        assert len(idx) == 3

    def test_result_dtype_is_int64(self):
        idx = VenueIndex.build(["v1", "v2"])
        series = idx.map_series(pd.Series(["v1", "v2"]))
        assert series.dtype == "int64"

    def test_large_set_unique_indices(self):
        n = 1000
        vids = [f"venue_{i}" for i in range(n)]
        idx = VenueIndex.build(vids)
        result = idx.map_series(pd.Series(vids))
        assert result.nunique() == n
        assert result.min() == 0
        assert result.max() == n - 1


class TestVenueIndexPersistence:
    def test_save_creates_csv_file(self, tmp_path):
        idx = VenueIndex.build(["abc", "def"])
        p = tmp_path / "index.csv"
        idx.save(p)
        assert p.exists()

    def test_save_csv_has_correct_columns(self, tmp_path):
        idx = VenueIndex.build(["abc", "def"])
        p = tmp_path / "index.csv"
        idx.save(p)
        df = pd.read_csv(p)
        assert "venue_id" in df.columns
        assert "placeid" in df.columns

    def test_save_and_load_roundtrip(self, tmp_path):
        original = VenueIndex.build(["alpha", "beta", "gamma"])
        p = tmp_path / "idx.csv"
        original.save(p)

        loaded = VenueIndex.load(p)
        s_orig = original.map_series(pd.Series(["alpha", "beta", "gamma"]))
        s_load = loaded.map_series(pd.Series(["alpha", "beta", "gamma"]))
        assert list(s_orig) == list(s_load)

    def test_save_creates_parent_dirs(self, tmp_path):
        idx = VenueIndex.build(["x"])
        nested = tmp_path / "a" / "b" / "c" / "idx.csv"
        idx.save(nested)
        assert nested.exists()

    def test_load_preserves_types(self, tmp_path):
        original = VenueIndex.build(["4b058f49f964a520b04e23e3", "aaa000"])
        p = tmp_path / "idx.csv"
        original.save(p)

        loaded = VenueIndex.load(p)
        result = loaded.map_series(pd.Series(["4b058f49f964a520b04e23e3", "aaa000"]))
        assert result.dtype == "int64"


class TestVenueIndexMapSeries:
    def test_map_returns_series(self):
        idx = VenueIndex.build(["a", "b"])
        result = idx.map_series(pd.Series(["a", "b"]))
        assert isinstance(result, pd.Series)

    def test_map_preserves_series_length(self):
        idx = VenueIndex.build(["a", "b", "c"])
        s = pd.Series(["a", "b", "a", "c", "b"])
        result = idx.map_series(s)
        assert len(result) == len(s)

    def test_map_empty_series(self):
        idx = VenueIndex.build(["a", "b"])
        result = idx.map_series(pd.Series([], dtype=str))
        assert len(result) == 0
