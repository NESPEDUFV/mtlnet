"""STL ReHDM ETL — joins precomputed Check2HGI or HGI embeddings.

Identical sessionisation / filtering / split logic as `etl.py`, but the
per-check-in feature vector is the precomputed embedding instead of the 6
ReHDM IDs. Engine selects the source:

  --engine check2hgi  → output/check2hgi/<state>/embeddings.parquet (per-check-in)
  --engine hgi        → output/hgi/<state>/embeddings.parquet      (per-POI)

Output: `output/baselines/rehdm/<state>_<engine>/inputs.parquet` with columns
`traj_idx, pos_in_traj, is_target, split, region_idx, datetime, e0..e63`
(64-dim embedding columns).
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from research.baselines.rehdm.etl import (
    _filter_min_checkins, _load_boroughs, _assign_regions,
)


def _load_emb_per_checkin(engine: str, state_lc: str, output_root: Path) -> pd.DataFrame:
    p = output_root / engine / state_lc / "embeddings.parquet"
    return pd.read_parquet(p)


def build_inputs(state: str, engine: str, data_root: Path, output_root: Path,
                 min_checkins: int = 10, session_hours: int = 24,
                 train_frac: float = 0.8, val_frac: float = 0.1):
    state_lc = state.lower()
    state_title = state.title()
    assert engine in {"check2hgi", "hgi"}

    checkins_file = data_root / "checkins" / f"{state_title}.parquet"
    boroughs_csv = output_root / "check2hgi" / state_lc / "temp" / "boroughs_area.csv"
    if not boroughs_csv.exists():
        boroughs_csv = output_root / "hgi" / state_lc / "temp" / "boroughs_area.csv"
    print(f"[etl-stl] state={state_lc} engine={engine}")

    df = pd.read_parquet(checkins_file)
    df = df[["userid", "placeid", "datetime", "latitude", "longitude", "category"]]
    df = df.dropna(subset=["latitude", "longitude", "datetime"]).copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    print(f"[etl-stl] raw rows={len(df)}")

    df = _filter_min_checkins(df, min_count=min_checkins)
    print(f"[etl-stl] after min{min_checkins} filter rows={len(df)}")

    boroughs = _load_boroughs(boroughs_csv)
    poi_region, region_to_idx = _assign_regions(df, boroughs)
    df = df.merge(poi_region[["placeid", "region_idx"]], on="placeid", how="inner")
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    print(f"[etl-stl] after region join rows={len(df)} regions={len(region_to_idx)}")

    emb = _load_emb_per_checkin(engine, state_lc, output_root)
    emb_cols = [c for c in emb.columns if c.isdigit()]
    emb_dim = len(emb_cols)
    print(f"[etl-stl] {engine} emb_dim={emb_dim} rows={len(emb)}")

    if engine == "check2hgi":
        emb["datetime"] = pd.to_datetime(emb["datetime"])
        df = df.merge(
            emb[["userid", "placeid", "datetime"] + emb_cols],
            on=["userid", "placeid", "datetime"], how="inner",
        )
    else:  # hgi: per-POI
        df = df.merge(emb[["placeid"] + emb_cols], on="placeid", how="inner")
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    print(f"[etl-stl] after emb join rows={len(df)}")

    sub_traj = np.zeros(len(df), dtype=np.int64)
    times = df["datetime"].astype("int64").to_numpy() // 10**9
    users = df["userid"].to_numpy()
    cur_user, cur_id, cur_start = None, -1, 0
    win = session_hours * 3600
    for i in range(len(df)):
        if users[i] != cur_user:
            cur_user, cur_id, cur_start = users[i], 0, times[i]
        elif times[i] - cur_start >= win:
            cur_id += 1
            cur_start = times[i]
        sub_traj[i] = cur_id
    df["sub_traj"] = sub_traj
    df["traj_id"] = df["userid"].astype(str) + "_" + df["sub_traj"].astype(str)
    sizes = df.groupby("traj_id").size()
    df = df[df["traj_id"].isin(sizes[sizes >= 2].index)].reset_index(drop=True)

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

    train_users = set(df.loc[df["split"] == "train", "userid"].unique())
    train_pois = set(df.loc[df["split"] == "train", "placeid"].unique())
    drop_traj = (
        df[~df["userid"].isin(train_users) | ~df["placeid"].isin(train_pois)]
        .loc[lambda d: d["split"] != "train", "traj_idx"]
        .unique()
    )
    df = df[~((df["split"] != "train") & df["traj_idx"].isin(drop_traj))].reset_index(drop=True)
    print(
        f"[etl-stl] split sizes: train={(df.split=='train').sum()} "
        f"val={(df.split=='val').sum()} test={(df.split=='test').sum()}"
    )

    user_to_idx = {u: i for i, u in enumerate(sorted(df["userid"].unique()))}
    poi_to_idx = {p: i for i, p in enumerate(sorted(df["placeid"].unique()))}
    df["user_idx"] = df["userid"].map(user_to_idx).astype(np.int64)
    df["poi_idx"] = df["placeid"].map(poi_to_idx).astype(np.int64)

    rename = {c: f"e{c}" for c in emb_cols}
    df = df.rename(columns=rename)
    feat_cols = [f"e{c}" for c in emb_cols]
    keep = [
        "traj_idx", "pos_in_traj", "is_target", "split",
        "user_idx", "poi_idx", "region_idx", "datetime",
    ] + feat_cols
    df_out = df[keep].copy()

    out_dir = output_root / "baselines" / "rehdm" / f"{state_lc}_{engine}"
    out_dir.mkdir(parents=True, exist_ok=True)
    df_out.to_parquet(out_dir / "inputs.parquet", index=False)
    vocab = {
        "n_users": len(user_to_idx), "n_pois": len(poi_to_idx),
        "n_regions": len(region_to_idx), "emb_dim": emb_dim,
        "session_hours": session_hours, "min_checkins": min_checkins,
        "engine": engine,
    }
    with open(out_dir / "vocab.json", "w") as f:
        json.dump(vocab, f, indent=2)
    print(f"[etl-stl] wrote {out_dir/'inputs.parquet'} vocab={vocab}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    p.add_argument("--engine", required=True, choices=["check2hgi", "hgi"])
    p.add_argument("--data-root", default=os.environ.get("DATA_ROOT", "data"))
    p.add_argument("--output-root", default=os.environ.get("OUTPUT_DIR", "output"))
    args = p.parse_args()
    build_inputs(state=args.state, engine=args.engine,
                 data_root=Path(args.data_root), output_root=Path(args.output_root))


if __name__ == "__main__":
    main()
