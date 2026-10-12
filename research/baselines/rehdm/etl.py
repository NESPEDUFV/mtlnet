"""ETL for the faithful ReHDM baseline.

Reproduces the preprocessing pipeline described in Li et al., IJCAI 2025
(`Beyond Individual and Point: Next POI Recommendation via Region-aware
Dynamic Hypergraph with Dual-level Modeling`) and adapts only the **target**
to the next-region task on US-state Gowalla splits.

Pipeline
--------
1. Load raw check-ins from `data/checkins/<State>.parquet`.
2. Drop users and POIs with fewer than 10 check-ins (iterated to fixed point).
3. Spatial-join POIs against TIGER tract polygons (`boroughs_area.csv`) to
   produce a GEOID-based region taxonomy that matches check2hgi's source.
4. Encode 6 ReHDM IDs per check-in: user, POI, category, hour-of-day (24),
   day-of-week (7), quadkey-level-10 region.
5. Partition each user's history into 24-hour trajectories (paper §5.1).
6. Drop trajectories with only one check-in.
7. Chronological 80/10/10 split by trajectory start time.
8. Restrict val/test to users + POIs seen in train (paper §5.1).
9. Persist `inputs.parquet` (one row per check-in, ordered) + `vocab.json`.

Outputs
-------
- `output/baselines/rehdm/<state>/inputs.parquet`
- `output/baselines/rehdm/<state>/vocab.json`
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely import wkt


STATE_TIGER_PREFIX = {
    "alabama": "tl_2022_01_tract_AL",
    "arizona": "tl_2022_04_tract_AZ",
    "california": "tl_2022_06_tract_CA",
    "florida": "tl_2022_12_tract_FL",
    "georgia": "tl_2022_13_tract_GA",
    "texas": "tl_2022_48_tract_TX",
}

# Istanbul (Massive-STEPS / Foursquare): region taxonomy = OSM admin_level=8
# mahalle polygons — the TIGER-tract equivalent. Distributed as a GeoJSON whose
# region-id column is '@id' (OSM relation id), NOT 'GEOID'. Mirrors the same
# source of truth that STAN's ETL (research/baselines/stan/etl.py) and the
# check2hgi substrate use, so the ReHDM Istanbul regions match STAN's taxonomy.
ISTANBUL_MAHALLE_GEOJSON = (
    Path("miscellaneous") / "istanbul_mahalle" / "istanbul_mahalle.geojson"
)


def latlon_to_quadkey(lat: float, lon: float, level: int = 10) -> str:
    """Microsoft Tile Map quadkey (base-4 string) at a given zoom level.

    Reference: Lian et al. SIGKDD 2020, also used by ReHDM (paper §4.1).
    """
    sin_lat = math.sin(lat * math.pi / 180.0)
    x = (lon + 180.0) / 360.0
    y = 0.5 - math.log((1.0 + sin_lat) / (1.0 - sin_lat)) / (4.0 * math.pi)
    n = 1 << level
    tx = min(n - 1, max(0, int(x * n)))
    ty = min(n - 1, max(0, int(y * n)))
    qk = []
    for i in range(level, 0, -1):
        digit = 0
        mask = 1 << (i - 1)
        if (tx & mask) != 0:
            digit += 1
        if (ty & mask) != 0:
            digit += 2
        qk.append(str(digit))
    return "".join(qk)


def _filter_min_checkins(df: pd.DataFrame, min_count: int = 10) -> pd.DataFrame:
    """Iteratively drop users / POIs with fewer than `min_count` check-ins."""
    while True:
        n0 = len(df)
        u = df.groupby("userid").size()
        df = df[df["userid"].isin(u[u >= min_count].index)]
        p = df.groupby("placeid").size()
        df = df[df["placeid"].isin(p[p >= min_count].index)]
        if len(df) == n0:
            break
    return df.reset_index(drop=True)


def _load_boroughs(boroughs_csv: Path) -> gpd.GeoDataFrame:
    """Load the GEOID/geometry CSV produced by the check2hgi pipeline.

    The CSV is the WKT export of TIGER/Line tracts for the state and is the
    same source of truth that the in-house pipeline uses.
    """
    b = pd.read_csv(boroughs_csv)
    b["geometry"] = b["geometry"].apply(wkt.loads)
    return gpd.GeoDataFrame(b, geometry="geometry", crs="EPSG:4326")


def _load_regions_geojson(geojson_path: Path) -> gpd.GeoDataFrame:
    """Load a GeoJSON region layer (Istanbul mahalle) as a GEOID/geometry frame.

    Mirrors STAN's ETL id-col handling: TIGER tracts key on 'GEOID', the mahalle
    GeoJSON keys on '@id' (OSM relation id). Normalize the id column to 'GEOID'
    so the downstream sjoin / region_to_idx logic (`_assign_regions`) is shared
    verbatim with the US-state path.
    """
    g = gpd.read_file(geojson_path).to_crs("EPSG:4326")
    rid = "GEOID" if "GEOID" in g.columns else ("@id" if "@id" in g.columns else "name")
    g = g[[rid, "geometry"]].rename(columns={rid: "GEOID"})
    return gpd.GeoDataFrame(g, geometry="geometry", crs="EPSG:4326")


def _assign_regions(checkins: pd.DataFrame, boroughs: gpd.GeoDataFrame):
    pois = (
        checkins.groupby("placeid")
        .agg(latitude=("latitude", "first"), longitude=("longitude", "first"))
        .reset_index()
    )
    pois["geometry"] = gpd.points_from_xy(pois["longitude"], pois["latitude"])
    pois = gpd.GeoDataFrame(pois, geometry="geometry", crs="EPSG:4326")
    pois = pois.sjoin(boroughs[["GEOID", "geometry"]], how="left", predicate="intersects")
    pois = pois.dropna(subset=["GEOID"]).drop_duplicates(subset=["placeid"])

    region_to_idx = {g: i for i, g in enumerate(sorted(pois["GEOID"].unique()))}
    pois["region_idx"] = pois["GEOID"].map(region_to_idx).astype(np.int64)
    return pois[["placeid", "GEOID", "region_idx"]], region_to_idx


# A9 (cleanup): the former `_sessionize_24h` helper was dead code — never called;
# `build_inputs` implements the identical 24h-window sessionization inline (single
# source of truth, see the "sessionize 24h trajectories" block below).


def build_inputs(
    state: str,
    data_root: Path,
    output_root: Path,
    quadkey_level: int = 10,
    min_checkins: int = 10,
    session_hours: int = 24,
    train_frac: float = 0.8,
    val_frac: float = 0.1,
):
    state_lc = state.lower()
    state_title = state.title()

    checkins_file = data_root / "checkins" / f"{state_title}.parquet"

    # Region source: US states use the TIGER-tract WKT CSV; Istanbul uses the
    # OSM mahalle GeoJSON (see ISTANBUL_MAHALLE_GEOJSON). Both resolve to a
    # GeoDataFrame with a 'GEOID' id column consumed by `_assign_regions`.
    is_istanbul = state_lc == "istanbul"
    if is_istanbul:
        istanbul_geojson = data_root / ISTANBUL_MAHALLE_GEOJSON
        if not istanbul_geojson.exists():
            raise FileNotFoundError(
                f"Istanbul mahalle geojson not found at {istanbul_geojson}."
            )
    else:
        boroughs_csv = output_root / "check2hgi" / state_lc / "temp" / "boroughs_area.csv"
        if not boroughs_csv.exists():
            boroughs_csv = output_root / "hgi" / state_lc / "temp" / "boroughs_area.csv"
        if not boroughs_csv.exists():
            raise FileNotFoundError(
                f"boroughs_area.csv not found under output/{{check2hgi,hgi}}/{state_lc}/temp/."
            )

    print(f"[etl] state={state_lc} checkins={checkins_file}")
    df = pd.read_parquet(checkins_file)
    keep = ["userid", "placeid", "datetime", "latitude", "longitude", "category"]
    df = df[keep].dropna(subset=["latitude", "longitude", "datetime"]).copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    print(f"[etl] raw rows={len(df)} users={df.userid.nunique()} pois={df.placeid.nunique()}")

    df = _filter_min_checkins(df, min_count=min_checkins)
    print(f"[etl] after min{min_checkins} filter rows={len(df)}")

    if is_istanbul:
        print("[etl] spatial-join → mahalle regions")
        boroughs = _load_regions_geojson(istanbul_geojson)
    else:
        print("[etl] spatial-join → tract regions")
        boroughs = _load_boroughs(boroughs_csv)
    poi_region, region_to_idx = _assign_regions(df, boroughs)
    df = df.merge(poi_region[["placeid", "region_idx"]], on="placeid", how="inner")
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    print(f"[etl] after region join rows={len(df)} regions={len(region_to_idx)}")

    df["category"] = df["category"].fillna("Unknown")
    df["hour_idx"] = df["datetime"].dt.hour.astype(np.int64)
    df["day_idx"] = df["datetime"].dt.dayofweek.astype(np.int64)
    df["quadkey_str"] = [
        latlon_to_quadkey(la, lo, quadkey_level)
        for la, lo in zip(df["latitude"].values, df["longitude"].values)
    ]

    user_to_idx = {u: i for i, u in enumerate(sorted(df["userid"].unique()))}
    poi_to_idx = {p: i for i, p in enumerate(sorted(df["placeid"].unique()))}
    cat_to_idx = {c: i for i, c in enumerate(sorted(df["category"].unique()))}
    qk_to_idx = {q: i for i, q in enumerate(sorted(df["quadkey_str"].unique()))}

    df["user_idx"] = df["userid"].map(user_to_idx).astype(np.int64)
    df["poi_idx"] = df["placeid"].map(poi_to_idx).astype(np.int64)
    df["category_idx"] = df["category"].map(cat_to_idx).astype(np.int64)
    df["quadkey_idx"] = df["quadkey_str"].map(qk_to_idx).astype(np.int64)

    print("[etl] sessionize 24h trajectories")
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    sub_traj = np.zeros(len(df), dtype=np.int64)
    times = df["datetime"].astype("int64").to_numpy() // 10**9
    users = df["userid"].to_numpy()
    cur_user = None
    cur_id = -1
    cur_start = 0
    win = session_hours * 3600
    for i in range(len(df)):
        if users[i] != cur_user:
            cur_user = users[i]
            cur_id = 0
            cur_start = times[i]
        elif times[i] - cur_start >= win:
            cur_id += 1
            cur_start = times[i]
        sub_traj[i] = cur_id
    df["sub_traj"] = sub_traj
    df["traj_id"] = (
        df["userid"].astype(str) + "_" + df["sub_traj"].astype(str)
    )
    sizes = df.groupby("traj_id").size()
    keep_traj = sizes[sizes >= 2].index
    df = df[df["traj_id"].isin(keep_traj)].reset_index(drop=True)
    print(f"[etl] trajectories={df.traj_id.nunique()} rows={len(df)}")

    traj_codes = {t: i for i, t in enumerate(
        df.groupby("traj_id")["datetime"].min().sort_values().index
    )}
    df["traj_idx"] = df["traj_id"].map(traj_codes).astype(np.int64)

    df = df.sort_values(["traj_idx", "datetime"]).reset_index(drop=True)
    df["pos_in_traj"] = df.groupby("traj_idx").cumcount().astype(np.int64)
    last_mask = df.groupby("traj_idx")["pos_in_traj"].transform("max") == df["pos_in_traj"]
    df["is_target"] = last_mask.astype(np.int8)

    n_traj = df["traj_idx"].nunique()
    n_train = int(round(train_frac * n_traj))
    n_val = int(round(val_frac * n_traj))
    n_test = n_traj - n_train - n_val
    splits = np.array(["train"] * n_train + ["val"] * n_val + ["test"] * n_test)
    df["split"] = splits[df["traj_idx"].values]

    train_users = set(df.loc[df["split"] == "train", "user_idx"].unique())
    train_pois = set(df.loc[df["split"] == "train", "poi_idx"].unique())
    drop_traj = (
        df[~df["user_idx"].isin(train_users) | ~df["poi_idx"].isin(train_pois)]
        .loc[lambda d: d["split"] != "train", "traj_idx"]
        .unique()
    )
    df = df[~((df["split"] != "train") & df["traj_idx"].isin(drop_traj))].reset_index(drop=True)
    print(
        f"[etl] split sizes: train={(df.split=='train').sum()} "
        f"val={(df.split=='val').sum()} test={(df.split=='test').sum()}"
    )

    out_dir = output_root / "baselines" / "rehdm" / state_lc
    out_dir.mkdir(parents=True, exist_ok=True)

    cols = [
        "traj_idx", "pos_in_traj", "is_target", "split",
        "user_idx", "poi_idx", "category_idx", "hour_idx", "day_idx", "quadkey_idx",
        "region_idx", "datetime",
        # A2 (faithfulness): persist coordinates so the trainer can compute the
        # inter-trajectory Δd (s_ij) message term (paper Eq. 9). Legacy parquets
        # without these columns degrade gracefully (TrajectoryStore.has_geo=False).
        "latitude", "longitude",
    ]
    df[cols].to_parquet(out_dir / "inputs.parquet", index=False)

    vocab = {
        "n_users": len(user_to_idx),
        "n_pois": len(poi_to_idx),
        "n_categories": len(cat_to_idx),
        "n_hours": 24,
        "n_days": 7,
        "n_quadkeys": len(qk_to_idx),
        "n_regions": len(region_to_idx),
        "quadkey_level": quadkey_level,
        "session_hours": session_hours,
        "min_checkins": min_checkins,
    }
    with open(out_dir / "vocab.json", "w") as f:
        json.dump(vocab, f, indent=2)
    print(f"[etl] wrote {out_dir/'inputs.parquet'} and vocab.json -> {vocab}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--data-root", default=os.environ.get("DATA_ROOT", "data"))
    p.add_argument("--output-root", default=os.environ.get("OUTPUT_DIR", "output"))
    p.add_argument("--quadkey-level", type=int, default=10)
    p.add_argument("--session-hours", type=int, default=24)
    p.add_argument("--min-checkins", type=int, default=10)
    args = p.parse_args()
    build_inputs(
        state=args.state,
        data_root=Path(args.data_root),
        output_root=Path(args.output_root),
        quadkey_level=args.quadkey_level,
        session_hours=args.session_hours,
        min_checkins=args.min_checkins,
    )


if __name__ == "__main__":
    main()
