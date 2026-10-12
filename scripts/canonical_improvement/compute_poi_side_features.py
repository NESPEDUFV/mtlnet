"""T4.3 — Compute per-POI side features for Check2HGI augmentation.

Three derived POI features, all computed from the same check-in data the
encoder sees (no external labels, no fclass):

  1. popularity       — log(visit_count), float                            (1d)
  2. opening_hours    — 24-bin hour-of-day histogram of check-ins, normed (24d)
  3. covisit_category — 7-bin normalised category distribution of POIs   ( 7d)
                       co-visited (= consecutive in same user's check-in
                       sequence) with the host POI

Total per-POI feature dim = 32. Output saved as a (num_pois, 32) torch tensor.

Usage:
    python scripts/compute_poi_side_features.py --state Florida

Reads from:
    output/check2hgi/{state}/temp/checkin_graph.pt (preprocess cache; needs
        checkin_to_poi, metadata DataFrame, num_pois)

Writes to:
    output/check2hgi/{state}/poi_side_features.pt
        {'features': tensor(num_pois, 32),
         'columns':  ['popularity', 'oh_00', ..., 'oh_23', 'cv_0', ..., 'cv_6'],
         'num_pois': int,
         'num_categories': int}

Leak note (T4.3 audit, 2026-05-16): features are computed from ALL check-ins
(both train- and val-fold rows), not per-fold. This is a simplification — the
held-out-fclass-split probe-leak test from the T4.3 spec is the validating
guardrail. If the linear leak probe drifts > +3 pp vs canonical, re-implement
as per-fold (each fold's side features built from train-fold rows only).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_repo / "src"))
sys.path.insert(0, str(_repo / "research"))

import numpy as np
import pandas as pd
import torch

from configs.paths import IoPaths


def _resolve_state_name(state: str) -> str:
    """Map CLI state name (lowercase or CamelCase) → CamelCase folder name."""
    state_lower = state.lower()
    mapping = {
        "alabama": "Alabama",
        "arizona": "Arizona",
        "florida": "Florida",
        "georgia": "Georgia",
        "california": "California",
        "texas": "Texas",
    }
    return mapping.get(state_lower, state)


def compute_side_features(
    state: str,
    *,
    subset: str = "all",
    drop_last_pair: bool = True,
) -> None:
    """Compute per-POI side features and write to disk.

    Args:
        state: state name (lowercase or CamelCase).
        subset: which features to compute & save into the 32-d tensor.
            'all'      → popularity(1) + hours(24) + covisit(7), full 32d.
            'popular'  → popularity only; cols 1..32 zero-padded.
            'hours'    → hours only; cols [0] + [25..32] zero-padded.
            'covisit'  → covisit only; cols [0..25] zero-padded.
            'no_covisit' → popularity + hours; cols [25..32] zero-padded.
            (zero-padding keeps the on-disk shape stable so the encoder
             constructor doesn't need to know which subset is active.)
        drop_last_pair: when True, drop the LAST within-user consecutive
            pair from the cv aggregation (audit advisor blocker 1 mitigation).
    """
    state_camel = _resolve_state_name(state)
    temp_dir = IoPaths.CHECK2HGI.get_temp_dir(state_camel)
    cache_path = temp_dir / "checkin_graph.pt"
    if not cache_path.exists():
        raise FileNotFoundError(
            f"missing preprocess cache {cache_path} — run create_embedding "
            f"first to populate the check-in graph"
        )

    print(f"[T4.3] loading {cache_path}")
    # checkin_graph.pt is a regular pickle (preprocess.py saves via pickle.dump),
    # NOT a torch.save file. torch.load barfs on the magic bytes.
    import pickle as _pickle
    with open(cache_path, "rb") as _fh:
        data_dict = _pickle.load(_fh)
    metadata = data_dict["metadata"]                  # df: userid, placeid, datetime, category
    checkin_to_poi = data_dict["checkin_to_poi"]       # np.array (N_checkins,)
    num_pois = int(data_dict["num_pois"])

    # metadata's row order matches checkin_to_poi's order by preprocess contract.
    assert len(metadata) == len(checkin_to_poi), (
        f"metadata len {len(metadata)} != checkin_to_poi len {len(checkin_to_poi)}; "
        f"row order mismatch — preprocess cache is corrupt"
    )

    # Materialise as a working DataFrame with poi_idx + datetime parsed.
    df = pd.DataFrame({
        "userid":   metadata["userid"].values,
        "placeid":  metadata["placeid"].values,
        "datetime": pd.to_datetime(metadata["datetime"], utc=False, errors="coerce"),
        "category": metadata["category"].values,
        "poi_idx":  checkin_to_poi,
    }).dropna(subset=["datetime"]).reset_index(drop=True)

    n_categories = int(df["category"].nunique())
    if n_categories > 7:
        # Truncate gracefully (the canonical pipeline expects 7 categories).
        print(f"[T4.3] warn: n_categories={n_categories} > 7; using top-7 by frequency")
        top7 = df["category"].value_counts().head(7).index.tolist()
        df = df[df["category"].isin(top7)].reset_index(drop=True)
        n_categories = 7

    # ── (1) popularity ──────────────────────────────────────────────────
    print("[T4.3] computing popularity (log visit count)")
    pop = (
        df.groupby("poi_idx").size()
          .reindex(range(num_pois), fill_value=0)
          .to_numpy(dtype=np.float32)
    )
    popularity = np.log1p(pop).astype(np.float32)        # log(1+count) ∈ [0, ~ln(N)]

    # ── (2) opening hours histogram ─────────────────────────────────────
    print("[T4.3] computing 24-bin opening-hours histogram")
    df["hour"] = df["datetime"].dt.hour.astype(np.int64)
    # Build sparse (poi_idx, hour) → count, then dense
    oh_counts = np.zeros((num_pois, 24), dtype=np.float32)
    np.add.at(oh_counts, (df["poi_idx"].to_numpy(), df["hour"].to_numpy()), 1.0)
    # Row-normalise (POIs with zero check-ins get an all-zero row, NOT 1/24).
    row_sum = oh_counts.sum(axis=1, keepdims=True)
    opening_hours = np.where(row_sum > 0, oh_counts / np.maximum(row_sum, 1e-8), 0.0).astype(np.float32)

    # ── (3) co-visit category-mix ───────────────────────────────────────
    # For each user, sort by datetime and build consecutive pairs (poi_t, poi_{t+1}).
    # The covisit_category[poi_a] = histogram of categories of POIs paired with poi_a.
    # NB: directed (cv tracks the *next* POI category) — symmetric variant would
    # double-count and add no info; using directed-next matches the next-poi task semantics.
    #
    # LEAK CONTROL (T4.3 audit advisor 2026-05-16 blocker 1):
    # The probe target is "next_category" predicted from slot-8 of a 9-window
    # sequence — exactly what cv[src_poi] aggregates. To break the direct
    # construction leak, drop the LAST consecutive pair PER USER from the
    # aggregation. This is the user's most-recent transition, which is the one
    # the probe most likely targets in its window construction. Lighter than
    # per-fold computation but closes the dominant leak channel.
    print("[T4.3] computing 7-bin co-visit category mix "
          f"(drop_last_pair_per_user={drop_last_pair})")
    df_sorted = df.sort_values(["userid", "datetime"], kind="stable").reset_index(drop=True)
    # Category index map (using sorted unique to match preprocess's LabelEncoder).
    cat_categories = sorted(df_sorted["category"].astype(str).unique())
    cat_to_idx = {c: i for i, c in enumerate(cat_categories)}
    df_sorted["category_idx"] = df_sorted["category"].astype(str).map(cat_to_idx).astype(np.int64)

    user_arr = df_sorted["userid"].to_numpy()
    poi_arr = df_sorted["poi_idx"].to_numpy()
    cat_arr = df_sorted["category_idx"].to_numpy()

    # Find within-user consecutive pairs: indices where user[i] == user[i+1]
    same_user = (user_arr[:-1] == user_arr[1:])
    if drop_last_pair:
        # For each user, mark the LAST same-user pair as excluded. A pair at
        # index i is the user's last pair iff same_user[i]==True AND
        # same_user[i+1]==False (i.e. the next row starts a new user). The
        # final row needs special handling since same_user has length N-1.
        is_last_pair = np.zeros_like(same_user)
        if len(same_user) >= 2:
            # Pair i is "last" if same_user[i] AND (i+1 == len(same_user) OR not same_user[i+1])
            # Equivalent: pair i is last iff after it the user changes.
            transitions = np.concatenate([same_user[1:], np.array([False])])
            is_last_pair = same_user & ~transitions
        # The very last row of the dataframe is also a last-pair if same_user[-1] is True
        # (the boolean array above already handles this via the appended False).
        keep_pair = same_user & ~is_last_pair
    else:
        keep_pair = same_user

    src_poi = poi_arr[:-1][keep_pair]
    dst_cat = cat_arr[1:][keep_pair]

    cv = np.zeros((num_pois, n_categories), dtype=np.float32)
    np.add.at(cv, (src_poi, dst_cat), 1.0)
    cv_row_sum = cv.sum(axis=1, keepdims=True)
    covisit = np.where(cv_row_sum > 0, cv / np.maximum(cv_row_sum, 1e-8), 0.0).astype(np.float32)
    print(f"[T4.3]   covisit kept {int(keep_pair.sum())}/{int(same_user.sum())} "
          f"within-user pairs")

    # Pad covisit to 7d if n_categories < 7 (preserves output shape contract).
    if covisit.shape[1] < 7:
        pad = np.zeros((num_pois, 7 - covisit.shape[1]), dtype=np.float32)
        covisit = np.concatenate([covisit, pad], axis=1)

    # ── Assemble (num_pois, 32) — gate by `subset` ──────────────────────
    # Subset gating: zero-out features NOT in the active subset. Keep the
    # 32-d shape constant so the encoder layer architecture is shape-stable
    # across ablations.
    pop_col = popularity[:, None]  # (P, 1)
    if subset in ("hours", "covisit"):
        pop_col = np.zeros_like(pop_col)
    hrs = opening_hours
    if subset in ("popular", "covisit"):
        hrs = np.zeros_like(hrs)
    cv7 = covisit[:, :7]
    if subset in ("popular", "hours", "no_covisit"):
        cv7 = np.zeros_like(cv7)
    features = np.concatenate([pop_col, hrs, cv7], axis=1).astype(np.float32)
    print(f"[T4.3]   subset={subset}  active_dims={int((features != 0).any(axis=0).sum())}/32")
    assert features.shape == (num_pois, 32), f"expected (num_pois, 32) got {features.shape}"

    # Sanity: no NaN/Inf
    if not np.isfinite(features).all():
        n_bad = (~np.isfinite(features)).sum()
        raise ValueError(f"{n_bad} non-finite values in side features")

    out_path = IoPaths.CHECK2HGI.get_state_dir(state_camel) / "poi_side_features.pt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "features": torch.from_numpy(features),
        "columns": (
            ["popularity"]
            + [f"oh_{h:02d}" for h in range(24)]
            + [f"cv_{c}" for c in range(7)]
        ),
        "num_pois": num_pois,
        "num_categories": n_categories,
        "state": state_camel,
    }
    torch.save(payload, out_path)
    print(f"[T4.3] saved {out_path}  shape={tuple(features.shape)}")
    print(f"[T4.3]   popularity range: [{popularity.min():.2f}, {popularity.max():.2f}]")
    print(f"[T4.3]   POIs with ≥1 check-in: {(pop > 0).sum()}/{num_pois}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--state", required=True,
                    help="state name (lowercase 'florida' or CamelCase 'Florida')")
    ap.add_argument("--subset", default="no_covisit",
                    choices=("all", "popular", "hours", "covisit", "no_covisit"),
                    help="which feature subset to enable; default 'no_covisit' "
                         "(popularity + hours, drops the leak-prone cv).")
    ap.add_argument("--no-drop-last-pair", action="store_true",
                    help="disable the dropping of each user's LAST within-user "
                         "pair from the cv aggregation (audit advisor blocker 1 "
                         "mitigation; on by default).")
    args = ap.parse_args()
    compute_side_features(args.state, subset=args.subset,
                          drop_last_pair=not args.no_drop_last_pair)
