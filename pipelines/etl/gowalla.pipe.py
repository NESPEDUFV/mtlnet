"""
Pipeline wrapper — Gowalla ETL.

Edit the config section below, then run:
    python pipelines/etl/gowalla.pipe.py

Prerequisites
-------------
1. Raw Gowalla files placed under ``data/gowalla/``::

       data/gowalla/gowalla_checkins.parquet
       data/gowalla/gowalla_spots_subset1.csv
       data/gowalla/gowalla_spots_subset2.csv
       data/gowalla/gowalla_category_structure.json
       data/gowalla/callback_categories.json
       data/gowalla/extra_categories.json

   Source dataset: SNAP Gowalla check-ins
   (https://snap.stanford.edu/data/loc-Gowalla.html), with the auxiliary
   POI / category tables released alongside the original Gowalla dump.

2. U.S. states shapefile under ``data/miscellaneous/`` (Census TIGER 2022)::

       data/miscellaneous/tl_2022_us_state/tl_2022_us_state.shp

   Download: https://www2.census.gov/geo/tiger/TIGER2022/STATE/tl_2022_us_state.zip

3. (Optional, only if you want ``local_datetime``) Timezone polygons under
   ``data/miscellaneous/``::

       data/miscellaneous/combined-shapefile-with-oceans/combined-shapefile-with-oceans.shp

   Download: https://github.com/evansiroky/timezone-boundary-builder/releases
   (the *combined-shapefile-with-oceans* asset).

Output
------
   data/temp/gowalla/stage1_categorised.parquet     (intermediate)
   data/temp/gowalla/stage2_localised.parquet       (intermediate, optional)
   data/temp/gowalla/stage3_states.parquet          (intermediate)
   data/checkins/<State>.csv                         (per-state files,
                                                     consumed by HGI / Check2HGI
                                                     embedding pipelines)
"""

import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# CONFIG — edit here
# ---------------------------------------------------------------------------

FORCE = False         # Recompute every stage from scratch.
SKIP_LOCALISE = True  # Skip the timezone-based local_datetime step
                      # (BRACIS pipeline doesn't need it).

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

# Allow running from the project root without installing the package
_project_root = Path(__file__).resolve().parents[2]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from src.etl.gowalla.main import run  # noqa: E402

if __name__ == "__main__":
    df = run(force=FORCE, skip_localise=SKIP_LOCALISE)
    print(f"\nFinal row count: {len(df):,}")
    print("Per-state CSVs (if Stage 3 ran): data/checkins/<State>.csv")
