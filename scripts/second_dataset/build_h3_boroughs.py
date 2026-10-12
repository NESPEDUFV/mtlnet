"""Generate an H3-hexagon 'boroughs' CSV for a non-US city (Phase E3, h3 mode).

Produces a GEOID,geometry(WKT) CSV — the SAME format the check2HGI preprocessor
reads for TIGER tracts — where each row is one populated H3 cell (within the city
bbox) and its hexagon polygon. Passed to preprocess_check2hgi via ``cta_file``, so
the existing point-in-polygon region pipeline (sjoin, area, adjacency, similarity)
works unchanged: in-bbox POIs land in their cell; out-of-bbox / null-coord POIs
match nothing and drop (exactly like out-of-NY POIs against NY tracts).

Cells are generated only for in-bbox POI locations (populated cells), mirroring how
only POI-bearing TIGER tracts become regions. Adjacency among populated cells works
because edge-sharing hexagons intersect.

Output: output/check2hgi/<city>/temp/boroughs_area.csv
Run:    python scripts/second_dataset/build_h3_boroughs.py --city istanbul
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from shapely.geometry import Polygon

_root = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import h3  # noqa: E402
from configs.paths import IoPaths  # noqa: E402
from cities import get as get_city  # noqa: E402


def _hex_wkt(cell: str) -> str:
    # h3 v4: cell_to_boundary -> tuple of (lat, lng) pairs
    boundary = h3.cell_to_boundary(cell)
    return Polygon([(lng, lat) for lat, lng in boundary]).wkt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    cfg = get_city(args.city)
    if cfg["region_mode"] != "h3":
        raise SystemExit(f"{args.city} is region_mode={cfg['region_mode']}, not h3")
    res = cfg["h3_res"]
    lat0, lat1, lon0, lon1 = cfg["bbox"]

    df = IoPaths.load_city(args.city)[["placeid", "latitude", "longitude"]].dropna()
    df = df.drop_duplicates("placeid")
    inbb = df[(df.latitude.between(lat0, lat1)) & (df.longitude.between(lon0, lon1))]
    cells = {h3.latlng_to_cell(r.latitude, r.longitude, res) for r in inbb.itertuples()}

    out = pd.DataFrame({"GEOID": sorted(cells)})
    out["geometry"] = out["GEOID"].map(_hex_wkt)

    dest = IoPaths.CHECK2HGI.get_temp_dir(args.city)
    dest.mkdir(parents=True, exist_ok=True)
    out_path = dest / "boroughs_area.csv"
    out.to_csv(out_path, index=False)
    print(f"[{args.city}] H3 res={res} populated cells={len(out)} "
          f"(in-bbox POIs {len(inbb)}/{len(df)}) -> {out_path}")


if __name__ == "__main__":
    main()
