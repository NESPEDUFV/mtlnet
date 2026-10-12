"""City registry for the second_dataset (Massive-STEPS) ETL.

Each city is one Massive-STEPS corpus mapped into the repo's per-"state" check-in
schema. Region definition is per-city:
  - tiger : US Census TIGER tract shapefile (point-in-polygon) — US cities only.
  - h3    : H3 hexagonal cells over a city bbox — non-US cities (no TIGER).

State token == dict key (lower-case). IoPaths.get_city(token) -> <Token>.parquet,
output dir output/check2hgi/<token>/.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1].parent
if str(_root / "src") not in sys.path:
    sys.path.insert(0, str(_root / "src"))
from configs.paths import Resources  # noqa: E402

CITIES = {
    "nyc": {
        "hf_repo": "CRUISEResearchGroup/Massive-STEPS-New-York",
        "state_name": "New York",
        "country_name": "United States of America",
        "region_mode": "tiger",
        "shapefile": str(Resources.TL_NY),
    },
    "istanbul": {
        "hf_repo": "cruiseresearchgroup/Massive-STEPS-Istanbul",
        "state_name": "Istanbul",
        "country_name": "Turkey",
        # PRIMARY region def = real administrative units (mahalle), the practical
        # TIGER-equivalent — preserves the "predict a real admin region" task identity
        # used for every Gowalla state + NYC (advisor 2026-06-15). H3 is the
        # granularity-matched SECONDARY/robustness variant (build_region_variant).
        "region_mode": "admin",
        "admin_geojson": "data/miscellaneous/istanbul_mahalle/istanbul_mahalle.geojson",
        # H3 params retained for the secondary variant:
        "h3_res": 9,                       # ~2,585 cells (≈ NYC's 1,912 tracts)
        # (lat_min, lat_max, lon_min, lon_max) — captures 98.4% of POIs-with-coords.
        "bbox": (40.70, 41.50, 28.40, 29.60),
    },
}


def get(city: str) -> dict:
    if city not in CITIES:
        raise SystemExit(f"unknown city '{city}'. Known: {list(CITIES)}")
    return CITIES[city]


def data_dir(city: str) -> Path:
    return Path("data") / f"massive_steps_{city}"
