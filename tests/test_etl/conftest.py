"""
Shared fixtures for ETL tests.

Provides synthetic raw-file builders that mimic the exact byte format of
each upstream dataset, so stage functions can be tested end-to-end without
downloading real data.
"""

import io
import textwrap
from pathlib import Path

import pandas as pd
import pytest


# ---------------------------------------------------------------------------
# Yang TIST2015 (Foursquare NYC / Tokyo) raw file helpers
# ---------------------------------------------------------------------------

# Date format used in the raw Yang dataset
YANG_DATE_FMT = "%a %b %d %H:%M:%S +0000 %Y"


def build_foursquare_raw_tsv(rows: list[dict]) -> str:
    """Build a tab-separated raw Yang dataset string.

    Each dict in ``rows`` should have keys:
        userid, venue_id, venue_category_id, venue_category_name,
        latitude, longitude, timezone_offset, utc_time
    """
    lines = []
    for r in rows:
        lines.append(
            "\t".join(
                str(r[k])
                for k in [
                    "userid",
                    "venue_id",
                    "venue_category_id",
                    "venue_category_name",
                    "latitude",
                    "longitude",
                    "timezone_offset",
                    "utc_time",
                ]
            )
        )
    return "\n".join(lines)


@pytest.fixture
def foursquare_raw_file(tmp_path) -> Path:
    """Write a small valid Yang TIST2015 file and return its path."""
    rows = [
        {
            "userid": 1,
            "venue_id": "4b058f49f964a520b04e23e3",
            "venue_category_id": "4bf58dd8d48988d1d4941735",
            "venue_category_name": "Food",
            "latitude": 40.719985,
            "longitude": -74.002065,
            "timezone_offset": -300,
            "utc_time": "Fri Apr 03 18:00:09 +0000 2012",
        },
        {
            "userid": 1,
            "venue_id": "4b058f49f964a520b04e23e3",
            "venue_category_id": "4bf58dd8d48988d1d4941735",
            "venue_category_name": "Food",
            "latitude": 40.719985,
            "longitude": -74.002065,
            "timezone_offset": -300,
            "utc_time": "Fri Apr 03 18:00:09 +0000 2012",   # duplicate — should be removed
        },
        {
            "userid": 2,
            "venue_id": "4a43c0adf964a520c9361fe3",
            "venue_category_id": "4bf58dd8d48988d116941735",
            "venue_category_name": "Shop & Service",
            "latitude": 40.721231,
            "longitude": -73.994028,
            "timezone_offset": -300,
            "utc_time": "Sat Apr 04 09:15:00 +0000 2012",
        },
        {
            "userid": 3,
            "venue_id": "5b1234abcd0000001234abcd",
            "venue_category_id": "4bf58dd8d48988d1e0931735",
            "venue_category_name": "Nightlife Spot",
            "latitude": 40.730610,
            "longitude": -73.935242,
            "timezone_offset": -240,  # EDT
            "utc_time": "Sun Apr 05 22:00:00 +0000 2012",
        },
        {
            "userid": 4,
            "venue_id": "6c999900000000000000cafe",
            "venue_category_id": "4d4b7105d754a06374d81259",
            "venue_category_name": "Event",   # should be dropped (unmapped)
            "latitude": 40.748817,
            "longitude": -73.985428,
            "timezone_offset": -300,
            "utc_time": "Mon Apr 06 12:00:00 +0000 2012",
        },
    ]
    raw_path = tmp_path / "dataset_TSMC2014_NYC.txt"
    raw_path.write_text(build_foursquare_raw_tsv(rows), encoding="utf-8")
    return raw_path


# ---------------------------------------------------------------------------
# Massive-STEPS raw file helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def massive_steps_raw_file(tmp_path) -> Path:
    """Write a small valid Massive-STEPS city CSV and return its path."""
    data = {
        "user_id": [10, 10, 11, 12, 12],
        "venue_id": ["aaa111", "bbb222", "aaa111", "ccc333", "ccc333"],
        "local_datetime": [
            "2017-03-01 10:00:00",
            "2017-03-01 11:30:00",
            "2017-03-02 09:00:00",
            "2017-03-01 10:00:00",
            "2017-03-01 10:00:00",   # duplicate
        ],
        "venue_category_id": ["cat1", "cat2", "cat1", "cat3", "cat3"],
        "venue_category_name": ["Food", "Shop & Service", "Food", "Arts & Entertainment", "Arts & Entertainment"],
        "latitude":  [35.680, 35.685, 35.680, 35.690, 35.690],
        "longitude": [139.760, 139.765, 139.760, 139.770, 139.770],
    }
    raw_path = tmp_path / "new_york.csv"
    pd.DataFrame(data).to_csv(raw_path, index=False)
    return raw_path


@pytest.fixture
def massive_steps_categories_csv(tmp_path) -> Path:
    """Write a minimal Massive-STEPS categories.csv and return its path."""
    data = {
        "category_id": ["cat_food", "cat_shop", "cat_arts", "cat_italian"],
        "category_name": ["Food", "Shop & Service", "Arts & Entertainment", "Italian Restaurant"],
        "parent_id":   ["", "", "", "cat_food"],
        "parent_name": ["", "", "", "Food"],
    }
    p = tmp_path / "categories.csv"
    pd.DataFrame(data).to_csv(p, index=False)
    return p
