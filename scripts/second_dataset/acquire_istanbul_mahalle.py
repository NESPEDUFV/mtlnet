"""Acquire the Istanbul mahalle (OSM admin_level=8) admin polygons -> GeoJSON.

The primary Istanbul region def (region_mode="admin") needs real administrative
units. `acquire.py` only auto-downloads the NY TIGER shapefile; for Istanbul the
documented source is OSM `admin_level=8` mahalle (ODbL, EPSG:4326). This NEW helper
(the main acquire.py never fetched it) queries Overpass for every admin_level=8
boundary relation inside the Istanbul province (admin_level=4), assembles each
relation's outer/inner ways into a (multi)polygon, and writes a GeoJSON whose `@id`
column is the OSM relation id (the column build_graph.py / build_region_variant.py
read for GEOID).

Output: data/miscellaneous/istanbul_mahalle/istanbul_mahalle.geojson
Run:    python scripts/second_dataset/acquire_istanbul_mahalle.py
CPU-only, network (Overpass). Idempotent: skips if the geojson already exists.
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

import geopandas as gpd
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import polygonize, unary_union

OUT = Path("data/miscellaneous/istanbul_mahalle/istanbul_mahalle.geojson")
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
QUERY = """
[out:json][timeout:300];
area["name"="İstanbul"]["admin_level"="4"]->.ist;
( relation["boundary"="administrative"]["admin_level"="8"](area.ist); );
out body;
>;
out skel qt;
"""


def fetch() -> dict:
    last = None
    for ep in ENDPOINTS:
        for attempt in range(3):
            try:
                req = urllib.request.Request(
                    ep, data=QUERY.encode("utf-8"),
                    headers={"Content-Type": "text/plain", "User-Agent": "PoiMtlNet-ETL/1.0"})
                with urllib.request.urlopen(req, timeout=320) as r:
                    return json.loads(r.read().decode("utf-8"))
            except Exception as e:  # noqa: BLE001
                last = e
                print(f"  [{ep}] attempt {attempt+1} failed: {str(e)[:120]}")
                time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"all Overpass endpoints failed: {last}")


def build_polygons(osm: dict):
    nodes = {e["id"]: (e["lon"], e["lat"]) for e in osm["elements"] if e["type"] == "node"}
    ways = {e["id"]: e["nodes"] for e in osm["elements"] if e["type"] == "way"}
    rels = [e for e in osm["elements"] if e["type"] == "relation"]

    feats = []
    for rel in rels:
        outer_lines, inner_lines = [], []
        for m in rel.get("members", []):
            if m["type"] != "way" or m["ref"] not in ways:
                continue
            coords = [nodes[n] for n in ways[m["ref"]] if n in nodes]
            if len(coords) < 2:
                continue
            (inner_lines if m.get("role") == "inner" else outer_lines).append(LineString(coords))
        if not outer_lines:
            continue
        outer = list(polygonize(unary_union(outer_lines)))
        if not outer:
            continue
        inner = list(polygonize(unary_union(inner_lines))) if inner_lines else []
        poly = unary_union(outer)
        if inner:
            poly = poly.difference(unary_union(inner))
        if poly.is_empty:
            continue
        if isinstance(poly, Polygon):
            poly = MultiPolygon([poly])
        elif not isinstance(poly, MultiPolygon):
            # GeometryCollection fallback: keep only polygonal parts
            polys = [g for g in getattr(poly, "geoms", []) if isinstance(g, Polygon)]
            if not polys:
                continue
            poly = MultiPolygon(polys)
        feats.append({
            "id": rel["id"],
            "name": rel.get("tags", {}).get("name", ""),
            "geometry": poly,
        })
    return feats


def main() -> None:
    if OUT.exists():
        print(f"present: {OUT}")
        return
    print("querying Overpass for Istanbul admin_level=8 mahalle ...")
    osm = fetch()
    n_rel = sum(1 for e in osm["elements"] if e["type"] == "relation")
    print(f"  fetched {len(osm['elements'])} elements ({n_rel} relations)")
    feats = build_polygons(osm)
    print(f"  assembled {len(feats)} mahalle polygons")
    gdf = gpd.GeoDataFrame(
        {"@id": [f"relation/{f['id']}" for f in feats],
         "name": [f["name"] for f in feats]},
        geometry=[f["geometry"] for f in feats], crs="EPSG:4326")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(OUT, driver="GeoJSON")
    print(f"wrote {OUT}  ({len(gdf)} polygons)")


if __name__ == "__main__":
    main()
