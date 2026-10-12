"""Build the Check2HGI graph artifact for a city (Phase E3). City-generic.

Calls the repo's OWN ``preprocess_check2hgi`` so region assignment, edges, and
features are byte-identical in construction to the Gowalla states. No GNN training
(that is Phase V). Region mode per city:
  - tiger : pass the TIGER tract shapefile; preprocess builds boroughs_area.csv.
  - h3    : pre-build boroughs_area.csv as H3 hexagons (build_h3_boroughs), then
            preprocess finds it and skips the shapefile path. Identical downstream.

Output: output/check2hgi/<city>/temp/checkin_graph.pt (+ boroughs_area.csv)
Run:    python scripts/second_dataset/build_graph.py --city istanbul
"""
from __future__ import annotations

import argparse
import json
import pickle as pkl
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research" / "embeddings" / "check2hgi"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from configs.paths import IoPaths  # noqa: E402
from preprocess import preprocess_check2hgi  # noqa: E402
from cities import get as get_city, data_dir  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    cfg = get_city(args.city)

    if cfg["region_mode"] == "h3":
        # pre-build the H3 boroughs CSV (preprocess will find + use it)
        subprocess.run([sys.executable,
                        str(Path(__file__).resolve().parent / "build_h3_boroughs.py"),
                        "--city", args.city], check=True)
        shapefile = ""   # unused: boroughs_area.csv already exists
    elif cfg["region_mode"] == "admin":
        # pre-build boroughs from real admin polygons (GeoJSON) — same drop-in path
        import geopandas as gpd
        g = gpd.read_file(cfg["admin_geojson"]).to_crs(4326)
        g = g[g.geometry.notna() & ~g.geometry.is_empty].reset_index(drop=True)
        gid = g["@id"].astype(str) if "@id" in g.columns else g.index.map(lambda i: f"r{i}")
        bor = pd.DataFrame({"GEOID": list(gid),
                            "geometry": g.geometry.apply(lambda x: x.wkt)}).drop_duplicates("GEOID")
        tmp = IoPaths.CHECK2HGI.get_temp_dir(args.city); tmp.mkdir(parents=True, exist_ok=True)
        bor.to_csv(tmp / "boroughs_area.csv", index=False)
        shapefile = ""   # unused: boroughs_area.csv already exists
    else:
        shapefile = cfg["shapefile"]

    out_path = preprocess_check2hgi(args.city, str(shapefile))
    g = pkl.load(open(out_path, "rb"))
    p2r = np.asarray(g["poi_to_region"]); n_regions = int(g["num_regions"])
    counts = np.bincount(p2r, minlength=n_regions)
    n_raw_ck = len(IoPaths.load_city(args.city))
    rep = {
        "city": args.city, "region_mode": cfg["region_mode"],
        "graph_path": str(out_path),
        "num_checkins_in_graph": int(g["num_checkins"]),
        "num_pois_in_graph": int(g["num_pois"]),
        "num_regions": n_regions,
        "n_checkins_dropped": n_raw_ck - int(g["num_checkins"]),
        "pois_per_region": {"min": int(counts.min()), "median": float(np.median(counts)),
                            "mean": float(counts.mean()), "max": int(counts.max())},
        "num_edges": int(len(g["edge_weight"])),
        "graph_keys": sorted(g.keys()),
    }
    (data_dir(args.city) / "graph_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
