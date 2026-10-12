"""
Pipeline wrapper — Foursquare TIST2015 ETL.

Edit the config section below, then run:
    python pipelines/etl/foursquare.pipe.py

Prerequisites
-------------
1. Download the raw dataset from Dingqi Yang's page:
       https://sites.google.com/site/yangdingqi/home/foursquare-dataset
   Or the Kaggle mirror:
       kaggle datasets download chetanism/foursquare-nyc-and-tokyo-checkin-dataset

2. Place the raw file(s) under data/raw/foursquare/:
       data/raw/foursquare/dataset_TSMC2014_NYC.txt   (for NYC)
       data/raw/foursquare/dataset_TSMC2014_TKY.txt   (for Tokyo)

Output
------
   data/checkins/New York City.parquet    (for CITY = "nyc")
   data/checkins/Tokyo.parquet            (for CITY = "tokyo")
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — edit here
# ---------------------------------------------------------------------------

CITY = "nyc"          # "nyc" or "tokyo"
# RAW_DATA_DIR = None  # defaults to data/raw/foursquare/
# DATA_ROOT    = None  # defaults to data/

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

# Allow running from the project root without installing the package
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.etl.foursquare.main import run  # noqa: E402

if __name__ == "__main__":
    df = run(city=CITY)
    print(f"\nFinal row count: {len(df):,}")
    print(f"Output: data/checkins/{df['city_name'].iloc[0]}.parquet")
