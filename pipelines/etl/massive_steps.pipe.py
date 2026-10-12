"""
Pipeline wrapper — Massive-STEPS ETL.

Edit the config section below, then run:
    python pipelines/etl/massive_steps.pipe.py

Prerequisites
-------------
1. Download the dataset from GitHub or HuggingFace:

   Option A — Clone the full GitHub repository:
       git clone https://github.com/cruiseresearchgroup/Massive-STEPS
       # Then copy the CSV files to data/raw/massive_steps/

   Option B — HuggingFace (per-city):
       pip install huggingface_hub
       python - <<'EOF'
       from huggingface_hub import hf_hub_download
       import shutil, pathlib
       out = pathlib.Path("data/raw/massive_steps")
       out.mkdir(parents=True, exist_ok=True)
       for city_slug, repo_suffix in [
           ("new_york", "New-York"),
           ("tokyo",    "Tokyo"),
           ("sao_paulo","Sao-Paulo"),
       ]:
           p = hf_hub_download(
               repo_id=f"w11wo/Massive-STEPS-{repo_suffix}",
               filename="checkins.csv",
               repo_type="dataset",
           )
           shutil.copy(p, out / f"{city_slug}.csv")
       EOF

2. Place the per-city CSV files under data/raw/massive_steps/:
       data/raw/massive_steps/new_york.csv
       data/raw/massive_steps/tokyo.csv
       ...

3. Optionally place the category hierarchy at:
       data/raw/massive_steps/categories.csv

Output
------
   data/checkins/{CityName}.parquet  for each city in CITIES
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — edit here
# ---------------------------------------------------------------------------

# Subset of cities to process. See src/etl/massive_steps/main.py for the
# full list of supported city slugs.
CITIES = [
    "new_york",
    "tokyo",
    "sao_paulo",
]

# RAW_DATA_DIR = None  # defaults to data/raw/massive_steps/
# DATA_ROOT    = None  # defaults to data/
# TIMEZONES_SHP = None  # defaults to data/miscellaneous/combined-shapefile-with-oceans.shp

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.etl.massive_steps.main import run  # noqa: E402

if __name__ == "__main__":
    for city in CITIES:
        print(f"\n{'='*60}")
        print(f"Processing city: {city}")
        print("="*60)
        try:
            df = run(city=city)
            print(f"Done: {len(df):,} check-ins → data/checkins/{df['city_name'].iloc[0]}.parquet")
        except FileNotFoundError as e:
            print(f"SKIP — {e}")
