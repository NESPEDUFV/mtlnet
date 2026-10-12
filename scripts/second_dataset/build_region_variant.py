"""Build an ALTERNATIVE region definition for an already-parsed city, as a
self-contained variant under output/check2hgi/<city>/<variant>/ (Phase E3/E4).

Use case: Istanbul with REAL administrative boundaries (OSM mahalle, the practical
TIGER-equivalent) alongside the synthetic H3 build. The corpus + sequences logic is
identical to the primary build; only the region definition (boroughs polygons ->
poi_to_region, region count/features) and the derived region labels + priors change.

This is a FULL self-contained build (its own graph + sequences + labels + priors)
because a different region polygon set drops a slightly different POI/check-in set
than the primary; each variant is internally consistent (mirrors how each Gowalla
state / NYC is self-contained).

Run: python scripts/second_dataset/build_region_variant.py \
        --city istanbul --variant mahalle \
        --geojson data/miscellaneous/istanbul_mahalle/istanbul_mahalle.geojson
"""
from __future__ import annotations

import argparse
import json
import pickle as pkl
import sys
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import torch

_root = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research" / "embeddings" / "check2hgi"))
sys.path.insert(0, str(_root / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from configs.globals import CATEGORIES_MAP  # noqa: E402
from configs.paths import IoPaths  # noqa: E402
from preprocess import Check2HGIPreprocess  # noqa: E402
from compute_region_transition import _log_probs_from_rows  # noqa: E402
from cities import data_dir, get as get_city  # noqa: E402
from build_inputs import (_sequences, _region_of_target, _last_region,  # noqa: E402
                          WINDOW, POI_COLS, SEEDS, N_SPLITS, SMOOTH_EPS, INV_CAT)


def _boroughs_csv(geojson: Path, out_csv: Path) -> int:
    """Real admin polygons (GeoJSON) -> GEOID,geometry(WKT) boroughs CSV."""
    g = gpd.read_file(geojson).to_crs(4326)
    g = g[g.geometry.notna() & ~g.geometry.is_empty].reset_index(drop=True)
    gid = g["@id"] if "@id" in g.columns else pd.Series([f"r{i}" for i in range(len(g))])
    out = pd.DataFrame({"GEOID": gid.astype(str).values,
                        "geometry": g.geometry.apply(lambda x: x.wkt).values})
    out = out.drop_duplicates("GEOID")
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    return len(out)


def _h3_boroughs_csv(city: str, out_csv: Path) -> int:
    """H3 hexagons over populated, in-bbox POI cells -> boroughs CSV (secondary variant)."""
    import h3
    from shapely.geometry import Polygon
    cfg = get_city(city)
    res = cfg["h3_res"]; lat0, lat1, lon0, lon1 = cfg["bbox"]
    df = IoPaths.load_city(city)[["placeid", "latitude", "longitude"]].dropna().drop_duplicates("placeid")
    inbb = df[(df.latitude.between(lat0, lat1)) & (df.longitude.between(lon0, lon1))]
    cells = sorted({h3.latlng_to_cell(r.latitude, r.longitude, res) for r in inbb.itertuples()})
    out = pd.DataFrame({"GEOID": cells,
                        "geometry": [Polygon([(lng, lat) for lat, lng in h3.cell_to_boundary(c)]).wkt
                                     for c in cells]})
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    return len(out)


def _save_prior(path: Path, log_probs, nreg, **extra):
    payload = {"log_transition": torch.from_numpy(log_probs), "smoothing_eps": SMOOTH_EPS,
               "n_regions": nreg, **extra}
    torch.save(payload, path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    ap.add_argument("--variant", required=True)
    ap.add_argument("--source", choices=["admin", "h3"], default="admin")
    ap.add_argument("--geojson", help="admin polygons GeoJSON (required for --source admin)")
    args = ap.parse_args()
    vdir = IoPaths.CHECK2HGI.get_state_dir(args.city) / args.variant
    (vdir / "temp").mkdir(parents=True, exist_ok=True)

    # 1. boroughs CSV (real admin polygons OR H3 hexes)
    if args.source == "h3":
        n_polys = _h3_boroughs_csv(args.city, vdir / "temp" / "boroughs_area.csv")
    else:
        if not args.geojson:
            raise SystemExit("--source admin requires --geojson")
        n_polys = _boroughs_csv(Path(args.geojson), vdir / "temp" / "boroughs_area.csv")

    # 2. graph (repo class; same construction as primary, different boroughs)
    pre = Check2HGIPreprocess(
        checkins_file=str(IoPaths.get_city(args.city)),
        boroughs_file=str(vdir / "temp" / "boroughs_area.csv"),
        temp_path=vdir / "temp", edge_type="user_sequence", temporal_decay=3600.0)
    g = pre.get_data()
    with open(vdir / "temp" / "checkin_graph.pt", "wb") as f:
        pkl.dump(g, f)
    p2i = g["placeid_to_idx"]
    p2r = np.asarray(g["poi_to_region"], dtype=np.int64)
    nreg = int(g["num_regions"])

    # corpus join for trail_id/split
    meta = g["metadata"].copy()
    meta["userid"] = meta["userid"].astype(np.int64); meta["placeid"] = meta["placeid"].astype(np.int64)
    corpus = pd.read_parquet(IoPaths.get_city(args.city),
                             columns=["userid", "placeid", "datetime", "trail_id", "split"])
    meta = meta.merge(corpus, on=["userid", "placeid", "datetime"], how="left", validate="m:1")

    # 3a. set (a) within-user sequences + labels + folds + priors
    seq = _sequences(meta, "userid")
    seq["region_idx"] = _region_of_target(seq["target_poi"].to_numpy(), p2i, p2r)
    seq["last_region_idx"] = _last_region(seq[POI_COLS].to_numpy(), p2i, p2r)
    (vdir / "input").mkdir(parents=True, exist_ok=True)
    seq_canon = seq[POI_COLS + ["target_poi", "userid"]].copy()
    for c in POI_COLS + ["target_poi"]:
        seq_canon[c] = seq_canon[c].astype(str)
    seq_canon.to_parquet(vdir / "temp" / "sequences_next.parquet", index=False)
    seq[["userid", "next_category", "region_idx", "last_region_idx"]].to_parquet(
        vdir / "input" / "next_region_labels.parquet", index=False)

    y = seq["next_category"].map(INV_CAT).to_numpy(dtype=np.int64)
    uids = seq["userid"].to_numpy(dtype=np.int64)
    Xz = np.zeros((len(seq), 1), dtype=np.float32)
    for s in SEEDS:
        sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=s)
        for fold, (tr, _va) in enumerate(sgkf.split(Xz, y, groups=uids)):
            sub = seq.iloc[tr]
            lp = _log_probs_from_rows(sub["poi_8"].to_numpy(np.int64),
                                      sub["target_poi"].to_numpy(np.int64), p2i, p2r, nreg, SMOOTH_EPS)
            _save_prior(vdir / f"region_transition_log_seed{s}_fold{fold + 1}.pt", lp, nreg,
                        n_splits=N_SPLITS, seed=s)

    # 3b. set (b) within-trail + shipped split + train-split prior
    sb = _sequences(meta, "trail_id")
    sb["split"] = sb["trail_id"].map(meta.drop_duplicates("trail_id").set_index("trail_id")["split"])
    sb["region_idx"] = _region_of_target(sb["target_poi"].to_numpy(), p2i, p2r)
    sb["last_region_idx"] = _last_region(sb[POI_COLS].to_numpy(), p2i, p2r)
    (vdir / "shipped_split").mkdir(parents=True, exist_ok=True)
    sb.to_parquet(vdir / "shipped_split" / "sequences_next_trail.parquet", index=False)
    trn = sb[sb["split"] == "train"]
    lp = _log_probs_from_rows(trn["poi_8"].to_numpy(np.int64), trn["target_poi"].to_numpy(np.int64),
                              p2i, p2r, nreg, SMOOTH_EPS)
    _save_prior(vdir / "shipped_split" / "region_transition_log_shipped_train.pt", lp, nreg,
                split="train", protocol="shipped_per_trail")

    counts = np.bincount(p2r, minlength=nreg)
    rep = {"city": args.city, "variant": args.variant, "geojson": args.geojson,
           "n_admin_polygons": n_polys, "num_checkins_in_graph": int(g["num_checkins"]),
           "num_pois_in_graph": int(g["num_pois"]), "num_regions_populated": nreg,
           "pois_per_region": {"min": int(counts.min()), "median": float(np.median(counts)),
                               "mean": float(counts.mean()), "max": int(counts.max())},
           "set_a_sequences": int(len(seq)), "set_b_sequences": int(len(sb)),
           "set_b_split_rows": sb["split"].value_counts().to_dict(),
           "n_prior_files_set_a": len(SEEDS) * N_SPLITS}
    (data_dir(args.city) / f"region_variant_{args.variant}_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
