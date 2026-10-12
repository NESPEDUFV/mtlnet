"""
Grid-based synthetic borough generator for cities without census tract shapefiles.

For cities where US Census TIGER data is not available (e.g. Tokyo, Sao Paulo),
this utility creates a regular grid of equal-area cells over the POI bounding box.
Each cell acts as a "census tract" for HGI's spatial graph construction.

The output CSV has the same schema as the boroughs_area.csv produced by HGI
preprocessing from a real shapefile: columns [GEOID, geometry] where geometry
is a WKT polygon string.

Usage
-----
    from src.etl.utils.grid_boroughs import create_grid_boroughs
    create_grid_boroughs("data/checkins/Tokyo_fsq.parquet", "output/hgi/tokyo_fsq/temp/boroughs_area.csv")
"""

import logging
from pathlib import Path

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def create_grid_boroughs(
    checkins_path: str | Path,
    output_path: str | Path,
    cell_size_deg: float = 0.01,
    padding: float = 0.005,
) -> Path:
    """Create a regular-grid synthetic boroughs CSV from a checkins parquet.

    Parameters
    ----------
    checkins_path:
        Path to the city checkins parquet (must have latitude/longitude columns).
    output_path:
        Destination CSV path.
    cell_size_deg:
        Grid cell size in degrees. 0.01° ≈ 1.1 km at mid-latitudes (default).
        Use 0.02°–0.05° for sparser datasets to ensure every POI lands in a cell
        with at least a few neighbours.
    padding:
        Extra margin around the bounding box so edge POIs fall inside a cell.

    Returns
    -------
    Path to the written CSV.
    """
    checkins_path = Path(checkins_path)
    output_path = Path(output_path)

    df = pd.read_parquet(checkins_path, columns=["latitude", "longitude"])
    df = df.dropna(subset=["latitude", "longitude"])

    lat_min = df["latitude"].min() - padding
    lat_max = df["latitude"].max() + padding
    lon_min = df["longitude"].min() - padding
    lon_max = df["longitude"].max() + padding

    lat_edges = np.arange(lat_min, lat_max + cell_size_deg, cell_size_deg)
    lon_edges = np.arange(lon_min, lon_max + cell_size_deg, cell_size_deg)

    rows = []
    geoid_counter = 0
    for i in range(len(lat_edges) - 1):
        for j in range(len(lon_edges) - 1):
            s = lat_edges[i]
            n = lat_edges[i + 1]
            w = lon_edges[j]
            e = lon_edges[j + 1]
            wkt = f"POLYGON (({w} {s}, {e} {s}, {e} {n}, {w} {n}, {w} {s}))"
            geoid = f"GRID{geoid_counter:06d}"
            rows.append({"GEOID": geoid, "geometry": wkt})
            geoid_counter += 1

    result = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)

    n_lat = len(lat_edges) - 1
    n_lon = len(lon_edges) - 1
    logger.info(
        "Grid boroughs: %d x %d = %d cells (%.3fdeg each) for bbox "
        "lat [%.3f,%.3f] lon [%.3f,%.3f]",
        n_lat, n_lon, len(result), cell_size_deg,
        lat_min, lat_max, lon_min, lon_max,
    )
    return output_path
