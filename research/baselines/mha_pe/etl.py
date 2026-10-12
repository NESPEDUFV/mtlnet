"""Faithful MHA+PE baseline ETL (Zeng, He, Tang, Wen 2019).

Self-contained: depends only on canonical Gowalla check-ins
(``data/checkins/<State>.parquet``). Mirrors the pre-processing in
``nest_poi/tcc_pedro/src/utils/{sequences,to_int}.py`` for paper
faithfulness, with the following adaptations (all documented in
``docs/baselines/next_category/mha_pe.md``):

  * **Window strategy.** Non-overlapping windows of size 8 + 1-step
    target (matches the rest of our baselines). Reference uses
    overlapping prefix-expansion.
  * **Step size = 8** (paper config, matches reference). Other baselines
    in this study use 9; MHA+PE keeps the paper's 8 to stay faithful.
  * **No user embedding fed at ETL time.** Reference relies on
    ``num_users`` and per-user embedding for warm-user splits; we use
    cold-user StratifiedGroupKFold which makes a learned user
    embedding random at val for held-out users. Dropped at the model.

Output columns (per row = one window):

    cat_0..7           int64    7-class category id at position k
    hour_0..7          int64    hour-of-day +24 if weekend (0..47)
    target_category    int64    7-class id of the next check-in
    userid             int64    for StratifiedGroupKFold grouping
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[3]
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import DATA_ROOT, OUTPUT_DIR  # noqa: E402

WINDOW_SIZE = 8
MIN_HISTORY = WINDOW_SIZE + 1
N_CATEGORIES = 7

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


def build_windows(state: str) -> pd.DataFrame:
    raw = pd.read_parquet(
        _checkins_path(state),
        columns=["userid", "placeid", "datetime", "category"],
    )
    raw = raw.dropna(subset=["placeid", "datetime", "category"])
    raw = raw[raw["category"].isin(CATEGORY_LABELS)].copy()
    raw["category_id"] = raw["category"].map(CATEGORY_LABELS).astype(np.int64)
    raw = raw.sort_values(["userid", "datetime"]).reset_index(drop=True)

    rows = []
    for uid, grp in raw.groupby("userid", sort=False):
        if len(grp) < MIN_HISTORY:
            continue
        cat = grp["category_id"].to_numpy()
        wd = pd.DatetimeIndex(grp["datetime"]).dayofweek.to_numpy()
        hr = pd.DatetimeIndex(grp["datetime"]).hour.to_numpy()
        pid = grp["placeid"].to_numpy()

        # Skip consecutive duplicates (paper-faithful)
        keep = np.ones(len(cat), dtype=bool)
        keep[1:] = pid[1:] != pid[:-1]
        cat = cat[keep]; wd = wd[keep]; hr = hr[keep]
        n = len(cat)
        if n < MIN_HISTORY:
            continue

        # Hour token: 0..23 weekday, 24..47 weekend (paper §5.4 / to_int.py).
        hour_tok = (hr + np.where(wd >= 5, 24, 0)).astype(np.int64)

        for start in range(0, n - WINDOW_SIZE, WINDOW_SIZE):
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
            rows.append(row)

    return pd.DataFrame(rows)


def out_path(state: str) -> Path:
    return OUTPUT_DIR / "baselines" / "mha_pe" / state / "inputs.parquet"


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
