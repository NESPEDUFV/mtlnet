"""Faithful POI-RGNN baseline ETL.

Self-contained: depends only on canonical Gowalla check-ins
(``data/checkins/<State>.parquet``). Mirrors the pre-processing in
``mtl_poi/src/etl/rgnn/sequence_generator.py`` + ``splits.py`` for
faithfulness to Capanema 2023 (Ad Hoc Networks), but adapts:

  * **Window strategy.** Non-overlapping windows of size 9 + 1-step
    target (matches the rest of our baselines + the in-house pipeline
    so cross-method comparisons are apples-to-apples).
  * **Graph matrices** (adj / cat-distance / cat-duration) are computed
    **per-fold on train rows only**, not per-user, since 7-class graphs
    over a single user's history are sparse and unstable. The paper's
    population-level transition statistics are preserved; the per-user
    aggregation is dropped. Built in the trainer, not here, so this ETL
    only needs to emit windowed inputs.

Output columns (per row = one window):

    cat_0..8           int64    7-class category id at position k
    hour_0..8          int64    hour-of-day +24 if weekend (0..47); 0=PAD
    dist_0..8          int64    distance bucket km, capped at 50; 0=PAD
    dur_0..8           int64    duration bucket hr, capped at 48; 0=PAD
    target_category    int64    7-class id of the next check-in
    userid             int64    for StratifiedGroupKFold grouping
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import haversine_distances

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import DATA_ROOT, OUTPUT_DIR  # noqa: E402

WINDOW_SIZE = 9
PAD = 0
MIN_HISTORY = 5
N_CATEGORIES = 7
DIST_CAP_KM = 50
DUR_CAP_HR = 48

# Order matches mtl_poi RgnnConfig.CATEGORY_LABELS (Capanema 2023)
CATEGORY_LABELS = {
    "Shopping": 0,
    "Community": 1,
    "Food": 2,
    "Entertainment": 3,
    "Travel": 4,
    "Outdoors": 5,
    "Nightlife": 6,
}


def _checkins_path(state: str) -> Path:
    return DATA_ROOT / "checkins" / f"{state.capitalize()}.parquet"


def _haversine_km(lat1, lon1, lat2, lon2) -> float:
    p1 = np.radians([[lat1, lon1]])
    p2 = np.radians([[lat2, lon2]])
    return float(haversine_distances(p1, p2)[0][0]) * 6371.0


def build_windows(state: str) -> pd.DataFrame:
    raw = pd.read_parquet(
        _checkins_path(state),
        columns=["userid", "placeid", "datetime", "latitude", "longitude", "category"],
    )
    raw = raw.dropna(subset=["placeid", "datetime", "latitude", "longitude", "category"])
    raw = raw[raw["category"].isin(CATEGORY_LABELS)].copy()
    raw["category_id"] = raw["category"].map(CATEGORY_LABELS).astype(np.int64)
    raw = raw.sort_values(["userid", "datetime"]).reset_index(drop=True)

    rows = []
    for uid, grp in raw.groupby("userid", sort=False):
        if len(grp) < MIN_HISTORY:
            continue
        cat = grp["category_id"].to_numpy()
        ts = grp["datetime"].to_numpy()
        wd = pd.DatetimeIndex(grp["datetime"]).dayofweek.to_numpy()
        hr = pd.DatetimeIndex(grp["datetime"]).hour.to_numpy()
        lat = grp["latitude"].to_numpy()
        lon = grp["longitude"].to_numpy()
        pid = grp["placeid"].to_numpy()
        n = len(grp)

        # Pre-compute per-position dist/dur (relative to previous check-in).
        dist = np.zeros(n, dtype=np.int64)
        dur = np.zeros(n, dtype=np.int64)
        for i in range(1, n):
            if pid[i] == pid[i - 1]:
                # mark with -1 to flag for "skip duplicate" filtering downstream
                dist[i] = -1
                continue
            dist[i] = int(min(_haversine_km(lat[i - 1], lon[i - 1], lat[i], lon[i]), DIST_CAP_KM))
            dur[i] = int(min(max((ts[i] - ts[i - 1]) / np.timedelta64(1, "h"), 0), DUR_CAP_HR))

        # Filter consecutive duplicates (paper-faithful)
        keep = (dist >= 0)
        cat = cat[keep]; ts = ts[keep]; wd = wd[keep]; hr = hr[keep]
        dist = dist[keep]; dur = dur[keep]
        n = len(cat)
        if n < WINDOW_SIZE + 1:
            continue

        # Hour token: weekday hour is 0..23, weekend hour is 24..47.
        # Reserve 0 as PAD by shifting all real hours by +1 (so range is 1..48).
        # Actually paper uses 0..47 directly; to keep PAD=0 distinguishable we
        # shift: real = (hour + (24 if weekend else 0)) + 1, giving 1..48; PAD=0.
        # nn.Embedding(49, 3) covers the new range.
        hour_tok = (hr + np.where(wd >= 5, 24, 0)).astype(np.int64) + 1

        # Distance bucket: 0 reserved PAD, real values shift +1 to range 1..51 -> Embedding(52, 3).
        dist_tok = (dist + 1).astype(np.int64)
        # Duration bucket: similarly 1..49 -> Embedding(50, 3).
        dur_tok = (dur + 1).astype(np.int64)

        for start in range(0, n - WINDOW_SIZE):
            # Non-overlapping windows: jump by WINDOW_SIZE.
            if start % WINDOW_SIZE != 0:
                continue
            end = start + WINDOW_SIZE
            target_pos = end
            if target_pos >= n:
                break
            row = {
                "userid": int(uid),
                "target_category": int(cat[target_pos]),
            }
            for k in range(WINDOW_SIZE):
                idx = start + k
                row[f"cat_{k}"] = int(cat[idx])
                row[f"hour_{k}"] = int(hour_tok[idx])
                row[f"dist_{k}"] = int(dist_tok[idx])
                row[f"dur_{k}"] = int(dur_tok[idx])
            rows.append(row)

    return pd.DataFrame(rows)


def out_path(state: str) -> Path:
    return OUTPUT_DIR / "baselines" / "poi_rgnn" / state / "inputs.parquet"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    args = p.parse_args()
    df = build_windows(args.state)
    out = out_path(args.state)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    print(f"[{args.state}] wrote {len(df):,} windows  n_cat={N_CATEGORIES}  → {out}")


if __name__ == "__main__":
    main()
