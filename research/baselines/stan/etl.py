"""Faithful STAN baseline ETL.

Self-contained: depends only on the canonical Gowalla check-ins
(``data/checkins/<State>.parquet``) and the TIGER/Line 2022 census-tract
shapefile for the state (``data/miscellaneous/tl_2022_*_tract_*/``). It
does NOT consume any artifact from the Check2HGI / HGI embedding
pipelines, so the baseline cannot inherit substrate-side filtering or
encoding decisions.

Region target derivation matches what the in-house pipelines do, but as
an independent step:

    1. Group check-ins by ``placeid`` and take the first (lat, lon) as
       the POI's representative location.
    2. Spatial-join POIs to tracts via ``geopandas.sjoin(predicate='intersects')``.
    3. Drop POIs outside every tract (~few %, matches Check2HGI behaviour).
    4. Assign deterministic ``placeid_to_idx`` and ``region_to_idx``
       (order = first appearance in the post-join POI frame).

Then slide 9+1 non-overlapping windows over each user's check-ins
(after sorting by datetime) — same window strategy as
``src/data/inputs/core.py::generate_sequences`` — and emit one row per
window:

    poi_idx_0..8        int64    POI index in [0, n_pois) (PAD=-1)
    lat_0..8            float32  latitude of the check-in at position k
    lon_0..8            float32  longitude of the check-in at position k
    t_minutes_0..8      int64    minutes since the window's first check-in
    target_region_idx   int64    region index in [0, n_regions)
    target_category     str      target check-in's raw category (for stratification)
    userid              int64    user id (for StratifiedGroupKFold)

Padded positions get ``poi_idx=-1`` and ``lat=lon=t_minutes=0``; the
model masks those positions in attention.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import DATA_ROOT, OUTPUT_DIR, Resources  # noqa: E402

# Audit fix #4 (2026-06-26): STAN's NATIVE sequence construction is full-trajectory
# PREFIX-EXPANSION (reference load.py truncates each user to the last max_len, train.py's
# expanding causal mask supervises EVERY position t from its causal prefix -> L-1 targets/user),
# NOT our stride-9 single-target windows. CONTEXT_LEN = STAN's max_len (paper 100; 50 here as a
# memory-feasible value — covers AL/AZ p90 and most of FL, and the matching layer's [B, n, R]
# tensors stay GPU-bounded at large region counts). Tunable via --context-len.
CONTEXT_LEN = 50
PAD = -1
MIN_HISTORY = 5  # skip users with fewer than this many check-ins (too short to learn from)

_STATE_TO_SHAPEFILE = {
    "alabama": Resources.TL_AL,
    "arizona": Resources.TL_AZ,
    "florida": Resources.TL_FL,
    "california": Resources.TL_CA,
    "texas": Resources.TL_TX,
    "georgia": Resources.TL_GA,
    "newyork": Resources.TL_NY,
    # Istanbul (Massive-STEPS): region = OSM admin_level=8 mahalle polygons (the
    # TIGER-tract equivalent). GeoJSON instead of a .shp; region-id col is '@id'.
    "istanbul": DATA_ROOT / "miscellaneous" / "istanbul_mahalle" / "istanbul_mahalle.geojson",
}


def _checkins_path(state: str) -> Path:
    return DATA_ROOT / "checkins" / f"{state.capitalize()}.parquet"


def _shapefile_path(state: str) -> Path:
    key = state.lower().replace(" ", "")
    if key not in _STATE_TO_SHAPEFILE:
        raise KeyError(f"No TIGER shapefile registered for state={state}")
    return _STATE_TO_SHAPEFILE[key]


def _assign_regions_from_shapefile(checkins: pd.DataFrame, shapefile: Path
                                   ) -> tuple[pd.DataFrame, dict, dict]:
    """Spatial-join unique POIs to tracts; return (poi_df, placeid_to_idx, region_to_idx).

    ``poi_df`` has columns: ``placeid, latitude, longitude, GEOID, region_idx, poi_idx``.
    POIs outside every tract are dropped.
    """
    pois = (
        checkins.groupby("placeid", as_index=False)
        .agg(latitude=("latitude", "first"), longitude=("longitude", "first"))
    )
    pois_geom = gpd.GeoDataFrame(
        pois,
        geometry=gpd.points_from_xy(pois["longitude"], pois["latitude"]),
        crs="EPSG:4326",
    )
    _tr = gpd.read_file(shapefile).to_crs("EPSG:4326")
    # Region-id column: TIGER tracts use 'GEOID'; the Istanbul mahalle GeoJSON uses
    # '@id' (OSM relation id). Normalize to 'GEOID' so the rest is substrate-agnostic.
    _rid = "GEOID" if "GEOID" in _tr.columns else ("@id" if "@id" in _tr.columns else "name")
    tracts = _tr[[_rid, "geometry"]].rename(columns={_rid: "GEOID"})

    pois_geom = pois_geom.sjoin(tracts, how="left", predicate="intersects")
    pois_geom = pois_geom.dropna(subset=["GEOID"]).reset_index(drop=True)
    # Some POIs may sit on a tract boundary and join multiple — keep first.
    pois_geom = pois_geom.drop_duplicates(subset=["placeid"], keep="first").reset_index(drop=True)

    region_to_idx = {g: i for i, g in enumerate(pois_geom["GEOID"].unique())}
    pois_geom["region_idx"] = pois_geom["GEOID"].map(region_to_idx).astype(np.int64)

    placeid_to_idx = {pid: i for i, pid in enumerate(pois_geom["placeid"].tolist())}
    pois_geom["poi_idx"] = pois_geom["placeid"].map(placeid_to_idx).astype(np.int64)

    # Region centroid in EPSG:4326 (lat/lon). Used by STAN's matching-layer
    # candidate-side Δd bias (paper §4.1.2 / Eq. 4 — interpolated distance
    # embedding from each candidate to each trajectory position).
    tracts_proj = tracts.to_crs(epsg=3857)  # planar for accurate centroid
    centroids = tracts_proj.set_index("GEOID").geometry.centroid.to_crs(epsg=4326)
    geoid_to_centroid = {g: (pt.y, pt.x) for g, pt in centroids.items()}
    centroid_rows = [
        {"region_idx": region_to_idx[g],
         "GEOID": g,
         "centroid_lat": geoid_to_centroid[g][0],
         "centroid_lon": geoid_to_centroid[g][1]}
        for g in region_to_idx
    ]
    centroid_df = pd.DataFrame(centroid_rows).sort_values("region_idx").reset_index(drop=True)

    return (
        pd.DataFrame(pois_geom.drop(columns="geometry")),
        placeid_to_idx,
        region_to_idx,
        centroid_df,
    )


def _prepare_raw(state: str):
    """Shared, windowing-independent prelude: load + region-assign + feature-annotate.

    Returns ``(raw_sorted, n_pois, n_regions, centroid_df)``. Used verbatim by both
    ``build_windows`` (in-memory) and ``build_windows_streaming`` (chunked) so the two
    paths cannot diverge on the input frame.
    """
    raw = pd.read_parquet(
        _checkins_path(state),
        columns=["userid", "placeid", "datetime", "latitude", "longitude", "category"],
    )
    raw = raw.dropna(subset=["placeid", "datetime", "latitude", "longitude", "category"])
    raw["placeid"] = raw["placeid"].astype(np.int64)

    poi_df, placeid_to_idx, region_to_idx, centroid_df = _assign_regions_from_shapefile(
        raw, _shapefile_path(state),
    )
    n_pois = len(placeid_to_idx)
    n_regions = len(region_to_idx)

    raw = raw[raw["placeid"].isin(placeid_to_idx)].copy()
    raw["poi_idx"] = raw["placeid"].map(placeid_to_idx).astype(np.int64)
    raw["region_idx"] = raw["poi_idx"].map(
        dict(zip(poi_df["poi_idx"], poi_df["region_idx"]))
    ).astype(np.int64)
    raw = raw.sort_values(["userid", "datetime"]).reset_index(drop=True)
    raw["t_minutes"] = (
        raw["datetime"].astype("int64") // (60 * 1_000_000_000)
    ).astype(np.int64)
    # STAN's hour-of-week token: 1..168 (paper §4.1.1; reference layers.py:104
    # `(t-1) % hours + 1` with hours=24*7). Distinct from the Δt scalar that
    # the pairwise bias consumes.
    raw["hour_of_week"] = (
        raw["datetime"].dt.dayofweek * 24 + raw["datetime"].dt.hour
    ).astype(np.int64) + 1  # 1..168 (0 reserved for pad)
    return raw, n_pois, n_regions, centroid_df


def _expand_user(uid, grp: pd.DataFrame, context_len: int) -> list[dict]:
    """STAN-native prefix-expansion for ONE user's (time-sorted) check-in group.

    Predicts EVERY position t (1..n-1) from its causal prefix = the last ``context_len``
    check-ins before t (left-aligned, right-padded). Yields n-1 window-row dicts for a
    user with n >= MIN_HISTORY check-ins, else ``[]``. This is the single, verbatim
    per-user window definition shared by ``build_windows`` and ``build_windows_streaming``
    — do NOT duplicate it, or the CA/TX (streamed) windows could silently diverge from the
    AL/AZ/FL (in-memory) ones and confound the STAN cross-state comparison.
    """
    n = len(grp)
    if n < MIN_HISTORY:
        return []
    poi_seq = grp["poi_idx"].to_numpy()
    reg_seq = grp["region_idx"].to_numpy()
    cat_seq = grp["category"].to_numpy()
    lat_seq = grp["latitude"].to_numpy(dtype=np.float32)
    lon_seq = grp["longitude"].to_numpy(dtype=np.float32)
    t_seq = grp["t_minutes"].to_numpy()
    hour_seq = grp["hour_of_week"].to_numpy()

    out: list[dict] = []
    for t in range(1, n):
        ctx_start = max(0, t - context_len)
        hist_idx = range(ctx_start, t)               # length 1..context_len
        target_region = int(reg_seq[t])
        target_category = str(cat_seq[t])

        poi_pad = [PAD] * context_len
        lat_pad = [0.0] * context_len
        lon_pad = [0.0] * context_len
        t_pad = [0] * context_len
        hour_pad = [0] * context_len  # 0 = pad token; real values 1..168
        for k, idx in enumerate(hist_idx):
            poi_pad[k] = int(poi_seq[idx])
            lat_pad[k] = float(lat_seq[idx])
            lon_pad[k] = float(lon_seq[idx])
            t_pad[k] = int(t_seq[idx])
            hour_pad[k] = int(hour_seq[idx])
        t0 = next((tt for tt in t_pad if tt > 0), 0)
        t_rel = [int(max(0, tt - t0)) if tt > 0 else 0 for tt in t_pad]

        row = {
            "userid": int(uid),
            "target_region_idx": target_region,
            "target_category": target_category,
        }
        for k in range(context_len):
            row[f"poi_idx_{k}"] = poi_pad[k]
            row[f"lat_{k}"] = lat_pad[k]
            row[f"lon_{k}"] = lon_pad[k]
            row[f"t_minutes_{k}"] = t_rel[k]
            row[f"hour_of_week_{k}"] = hour_pad[k]
        out.append(row)
    return out


def _stream_schema(context_len: int):
    """Explicit pyarrow schema pinned to the in-memory ``pd.DataFrame(rows)`` dtypes:
    int64 ids/idx/time, float64 lat/lon (the ``float()`` cast — NOT float32), string
    category, no index column. Guarantees the streamed parquet's column dtypes equal the
    monolithic path's, independent of per-chunk inference (e.g. an all-pad edge chunk).
    """
    import pyarrow as pa
    fields = [
        ("userid", pa.int64()),
        ("target_region_idx", pa.int64()),
        ("target_category", pa.string()),
    ]
    for k in range(context_len):
        fields += [
            (f"poi_idx_{k}", pa.int64()),
            (f"lat_{k}", pa.float64()),
            (f"lon_{k}", pa.float64()),
            (f"t_minutes_{k}", pa.int64()),
            (f"hour_of_week_{k}", pa.int64()),
        ]
    return pa.schema(fields)


def build_windows(state: str, context_len: int = CONTEXT_LEN):
    """Build the per-window input frame for ``state`` via STAN-native prefix-expansion.

    Returns ``(df, n_pois, n_regions, centroid_df)``. ``context_len`` = STAN max_len.
    In-memory path (holds all windows at once) — fine for AL/AZ/FL; use
    ``build_windows_streaming`` for CA/TX (see the OOM note there).
    """
    raw, n_pois, n_regions, centroid_df = _prepare_raw(state)
    rows: list[dict] = []
    for uid, grp in raw.groupby("userid", sort=False):
        rows.extend(_expand_user(uid, grp, context_len))
    return pd.DataFrame(rows), n_pois, n_regions, centroid_df


def build_windows_streaming(state: str, out: Path, cent_out: Path,
                            context_len: int = CONTEXT_LEN, chunk_users: int = 2000):
    """Memory-bounded equivalent of ``build_windows`` + ``to_parquet``, for large states.

    The in-memory path accumulates ~1 fat Python dict per check-in (CA 3.2M / TX 4.1M →
    ~112 GB RAM → OOM). This streams the same rows to parquet in whole-user chunks, so
    RAM stays bounded to ~``chunk_users`` users (a few hundred MB) regardless of state size.

    **Content-identical** to the in-memory path (same rows, same order via
    ``groupby(sort=False)`` + whole-user flushing, same dtypes via the pinned schema).
    The parquet *file* is not byte-identical (row-group layout differs) but ``train.py``
    reads the whole frame back, so the tensors + StratifiedGroupKFold split are identical.
    Returns ``(n_pois, n_regions, n_written)``.
    """
    import pyarrow as pa
    import pyarrow.parquet as pq

    raw, n_pois, n_regions, centroid_df = _prepare_raw(state)
    out.parent.mkdir(parents=True, exist_ok=True)
    schema = _stream_schema(context_len)

    buf: list[dict] = []
    users_in_buf = 0
    n_written = 0
    writer = pq.ParquetWriter(str(out), schema)
    try:
        for uid, grp in raw.groupby("userid", sort=False):
            urows = _expand_user(uid, grp, context_len)
            if urows:
                buf.extend(urows)
                users_in_buf += 1
            if users_in_buf >= chunk_users:
                writer.write_table(pa.Table.from_pylist(buf, schema=schema))
                n_written += len(buf)
                buf, users_in_buf = [], 0
        if buf:  # final partial chunk (last whole users)
            writer.write_table(pa.Table.from_pylist(buf, schema=schema))
            n_written += len(buf)
    finally:
        writer.close()
    centroid_df.to_parquet(cent_out, index=False)
    return n_pois, n_regions, n_written


def out_path(state: str) -> Path:
    return OUTPUT_DIR / "baselines" / "stan" / state / "inputs.parquet"


def centroids_path(state: str) -> Path:
    return OUTPUT_DIR / "baselines" / "stan" / state / "region_centroids.parquet"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--context-len", type=int, default=CONTEXT_LEN,
                   help="STAN max trajectory length (prefix-expansion context).")
    p.add_argument("--streaming", action="store_true",
                   help="Memory-bounded: stream windows to parquet in whole-user chunks "
                        "(content-identical to the default path; use for large states "
                        "CA/TX where the in-memory build OOMs). Default OFF so AL/AZ/FL "
                        "keep the exact byte-path.")
    p.add_argument("--chunk-users", type=int, default=2000,
                   help="[--streaming only] flush the parquet writer every N whole users.")
    args = p.parse_args()

    out = out_path(args.state)
    cent = centroids_path(args.state)
    out.parent.mkdir(parents=True, exist_ok=True)
    if args.streaming:
        n_pois, n_regions, n_written = build_windows_streaming(
            args.state, out, cent, context_len=args.context_len, chunk_users=args.chunk_users,
        )
        print(
            f"[{args.state}] (streaming, chunk_users={args.chunk_users}) wrote "
            f"{n_written:,} windows  n_pois={n_pois}  n_regions={n_regions}  → {out}\n"
            f"          centroids → {cent}"
        )
    else:
        df, n_pois, n_regions, centroid_df = build_windows(args.state, context_len=args.context_len)
        df.to_parquet(out, index=False)
        centroid_df.to_parquet(cent, index=False)
        print(
            f"[{args.state}] wrote {len(df):,} windows  n_pois={n_pois}  "
            f"n_regions={n_regions}  → {out}\n"
            f"          centroids ({len(centroid_df)} regions) → {cent}"
        )


if __name__ == "__main__":
    main()
