"""Parse a Massive-STEPS city (tabular) -> repo check-in schema (Phase E1).

City-generic. Emits data/checkins/<Token>.parquet (IoPaths.get_city(city)). Keeps
all raw check-ins incl. null-coord rows (faithful corpus; the substrate build drops
null-coord / out-of-region POIs downstream, as Gowalla preprocess does). Preserves
Massive-STEPS-native cols (trail_id, split, fsq_category{,_id}).

datetime convention: the Massive-STEPS timestamp is LOCAL civil time — upstream
preprocessing strips the tz offset, so UTC is unrecoverable. We keep the local
wall-clock in `datetime` (check2HGI's hour/dow features use it; local is correct)
and set `local_datetime` equal to it. (Differs from Gowalla, whose datetime is UTC
— a documented, minor divergence; features stay semantically sound.)

Run:  python scripts/second_dataset/parse_city.py --city istanbul
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1].parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from configs.paths import IoPaths  # noqa: E402
from cities import get as get_city, data_dir  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    cfg = get_city(args.city)
    cdir = data_dir(args.city)
    raw = cdir / "raw" / "tabular"

    parts = []
    for s in ["train", "validation", "test"]:
        df = pd.read_parquet(raw / f"{s}-00000-of-00001.parquet")
        df["split"] = "val" if s == "validation" else s
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)
    n_raw = len(df)

    cmap = pd.read_csv(cdir / "category_map.csv", dtype={"venue_category_id": str})
    id2root = dict(zip(cmap["venue_category_id"], cmap["gowalla_root"]))
    df["category"] = df["venue_category_id"].astype(str).map(id2root).fillna("None")
    df["datetime"] = pd.to_datetime(df["timestamp"])   # local civil time

    out = pd.DataFrame({
        "userid": df["user_id"].astype("int64"),
        "placeid": df["venue_id"].astype("int64"),
        "datetime": df["datetime"],
        "latitude": df["latitude"].astype("float64"),
        "longitude": df["longitude"].astype("float64"),
        "category": df["category"].astype(str),
        "spot": df["venue_category"].astype(str),
        "fsq_category": df["venue_category"].astype(str),
        "fsq_category_id": df["venue_category_id"].astype(str),
        "local_datetime": df["datetime"],   # already local; UTC unrecoverable
        "state_name": cfg["state_name"],
        "country_name": cfg["country_name"],
        "trail_id": df["trail_id"].astype(str),
        "split": df["split"].astype(str),
        "venue_city": df["venue_city"].astype(str),
        "name": df["name"].astype(str),
        "address": df["address"].astype(str),
    }).sort_values(["userid", "datetime"]).reset_index(drop=True)

    out_path = IoPaths.get_city(args.city)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(out_path, index=False)

    rep = {
        "city": args.city, "out_path": str(out_path),
        "n_rows": int(len(out)), "n_rows_raw_input": int(n_raw),
        "n_users": int(out["userid"].nunique()), "n_pois": int(out["placeid"].nunique()),
        "n_trails": int(out["trail_id"].nunique()),
        "n_categories_7root": int(out["category"].nunique()),
        "n_fsq_fine": int(out["fsq_category_id"].nunique()),
        "n_null_coord_rows": int(out["latitude"].isna().sum()),
        "n_dup_user_poi_time": int(out.duplicated(subset=["userid", "placeid", "datetime"]).sum()),
        "split_rows": out["split"].value_counts().to_dict(),
        "datetime_range_local": [str(out["datetime"].min()), str(out["datetime"].max())],
        "category_dist": out["category"].value_counts().to_dict(),
    }
    (cdir / "parse_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
