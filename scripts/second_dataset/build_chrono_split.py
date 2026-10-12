"""Build the Phase E2 CHRONOLOGICAL per-user split for a city (no embeddings). City-generic.

This is the temporal-split protocol bridge (roadmap A5) and the corrective to F1
(the Massive-STEPS *shipped* split is user-stratified RANDOM over short trails, NOT
temporal). The corpus carries per-check-in timestamps, so we build our OWN
chronological per-user split — the field-standard protocol.

PROTOCOL (per user, against the graph-mapped check-ins = set-(a) universe):
  1. Order the user's check-ins by datetime (LOCAL civil time is correct for
     per-user ordering; tie-break by placeid for determinism).
  2. Cut a positional per-user 80/10/10 split: first 80% of the user's timeline
     -> train, next 10% -> val, last 10% -> test (floor()-based, so it is
     deterministic and reproducible).
  3. Generate the length-9 windowed sequences + next_category/next_region labels
     using the SAME core.convert_user_checkins_to_sequences machinery as set (a) —
     but windowed SEPARATELY WITHIN EACH SPLIT PORTION, so a window's 9 inputs and
     its target ALWAYS fall in the SAME split portion (the critical temporal-split
     leak guard — no window spans a split boundary).
  4. Discard users whose TRAIN portion is too short to yield >=1 windowed sample
     (train portion needs >=5 check-ins, the core MIN_SEQUENCE_LENGTH floor).
  5. Build ONE train-portion-ONLY region-transition prior (log_T) per city via the
     compute_region_transition machinery, from TRAIN rows only (never val/test).
     The chronological split is a SINGLE split (no CV folds), tagged deterministically
     as fold="chrono".

NO learned embeddings needed: sequences/labels/prior depend only on the corpus +
the geography-only poi->region map. Phase V regenerates the embedding-bearing
parquets; these structural artifacts line up.

Outputs (under output/check2hgi/<city>/chrono_split/ — namespaced, parallel to
shipped_split/; NO set-(a) artifact touched):
    chrono_split/sequences_next_chrono.parquet            (POI seqs, with `split` col)
    chrono_split/next_region_labels_chrono.parquet        (labels, with `split` col)
    chrono_split/region_transition_log_chrono_train.pt    (train-ONLY prior)
    chrono_split/split_assignment.parquet                 (per-checkin split audit trail)

Run:  python scripts/second_dataset/build_chrono_split.py --city nyc
      python scripts/second_dataset/build_chrono_split.py --city istanbul

Istanbul note: this builds against the PRIMARY mahalle region set (top-level
output/check2hgi/istanbul/). The H3 secondary variant can be re-run later by
pointing --city at an H3-region graph (build_region_variant pattern).
"""
from __future__ import annotations

import argparse
import json
import pickle as pkl
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[1].parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import torch  # noqa: E402
from configs.globals import CATEGORIES_MAP  # noqa: E402
from configs.paths import IoPaths  # noqa: E402
from data.inputs.core import convert_user_checkins_to_sequences  # noqa: E402
from compute_region_transition import _log_probs_from_rows  # noqa: E402
from cities import data_dir, get as get_city  # noqa: E402

WINDOW = 9
SMOOTH_EPS = 0.01
MIN_SEQ_LEN = 5  # core.MIN_SEQUENCE_LENGTH — a portion shorter than this yields no windows
TRAIN_FRAC, VAL_FRAC = 0.80, 0.10  # test = remainder
INV_CAT = {v: k for k, v in CATEGORIES_MAP.items()}
POI_COLS = [f"poi_{i}" for i in range(WINDOW)]
SPLITS = ["train", "val", "test"]


def _graph(city):
    g = pkl.load(open(IoPaths.CHECK2HGI.get_graph_data_file(city), "rb"))
    p2r = g["poi_to_region"]
    if hasattr(p2r, "cpu"):
        p2r = p2r.cpu().numpy()
    return g, g["placeid_to_idx"], np.asarray(p2r, dtype=np.int64)


def _region_of_target(target_poi, p2i, p2r):
    return p2r[pd.Series(target_poi).map(p2i).to_numpy(dtype=np.int64)]


def _last_region(poi_mat, p2i, p2r):
    valid = poi_mat >= 0
    last_pos = np.where(valid.any(axis=1),
                        valid.shape[1] - 1 - valid[:, ::-1].argmax(axis=1), -1)
    N = poi_mat.shape[0]
    last_poi = np.where(last_pos >= 0, poi_mat[np.arange(N), np.clip(last_pos, 0, None)], -1)
    out = np.full(N, -1, dtype=np.int64)
    vm = last_poi >= 0
    if vm.any():
        out[vm] = p2r[pd.Series(last_poi[vm]).map(p2i).to_numpy(dtype=np.int64)]
    return out


def _chrono_split_user(n: int) -> np.ndarray:
    """Positional 80/10/10 per-user split labels for n chronologically ordered
    check-ins. Returns an array of {"train","val","test"} of length n.
    First floor(0.8n) -> train, next floor(0.1n) -> val, the rest -> test."""
    n_tr = int(n * TRAIN_FRAC)
    n_va = int(n * VAL_FRAC)
    labels = np.array(["test"] * n, dtype=object)
    labels[:n_tr] = "train"
    labels[n_tr:n_tr + n_va] = "val"
    return labels


def build_split_assignment(meta: pd.DataFrame) -> pd.DataFrame:
    """Order each user's check-ins by (datetime, placeid) and assign a positional
    chronological split. Adds `_order` (per-user 0-based rank) + `split`."""
    meta = meta.sort_values(["userid", "datetime", "placeid"]).reset_index(drop=True)
    meta["_order"] = meta.groupby("userid").cumcount()
    sizes = meta.groupby("userid")["userid"].transform("size").to_numpy()
    split = np.empty(len(meta), dtype=object)
    for uid, gdf in meta.groupby("userid", sort=False):
        idx = gdf.index.to_numpy()
        split[idx] = _chrono_split_user(len(gdf))
    meta["split"] = split
    meta["_user_len"] = sizes
    return meta


def _sequences_within_portion(portion: pd.DataFrame, split_name: str) -> pd.DataFrame:
    """Window WITHIN one split portion only (per user), reusing the repo's own
    core.convert_user_checkins_to_sequences. Because windowing is confined to the
    portion's rows, no window can span a split boundary."""
    portion = portion.copy()
    portion["d0"] = np.float32(0.0)
    rows = []
    for _uid, gdf in portion.groupby("userid", sort=True):
        if len(gdf) < MIN_SEQ_LEN:
            continue
        gdf = gdf.sort_values(["datetime", "placeid"]).reset_index(drop=True)
        emb_res, poi_seqs = convert_user_checkins_to_sequences(gdf, ["d0"], WINDOW, 1, stride=None)
        for er, ps in zip(emb_res, poi_seqs):
            # ps = [poi_0..poi_8, target_poi, userid]; er[-2] = target_category
            rows.append(ps[:WINDOW + 1] + [int(ps[-1]), str(er[-2])])
    df = pd.DataFrame(rows, columns=POI_COLS + ["target_poi", "userid", "next_category"])
    if len(df):
        for c in POI_COLS + ["target_poi"]:
            df[c] = df[c].astype(np.int64)
        df["userid"] = df["userid"].astype(np.int64)
    else:
        for c in POI_COLS + ["target_poi", "userid"]:
            df[c] = pd.Series(dtype=np.int64)
        df["next_category"] = pd.Series(dtype=object)
    df["split"] = split_name
    return df


def leak_check_1_no_boundary_span(seq: pd.DataFrame, assign: pd.DataFrame) -> dict:
    """LEAK CHECK 1: assert no window's input check-ins + target fall in >1 split
    portion. Each non-pad (userid, placeid) in a window must map to the same split
    as that window's `split` label. We verify via the per-user split assignment.

    Because real placeids can recur across portions within a user (same POI visited
    in train and again in test), we cannot map placeid->split globally. Instead we
    rely on the construction invariant — windows are built strictly within a portion
    — and verify it structurally: every window's userid has, in that split portion,
    at least (window_real_len + 1) check-ins, i.e. enough rows existed in-portion to
    source the window without borrowing from another portion."""
    # portion sizes per (userid, split)
    psize = assign.groupby(["userid", "split"]).size().to_dict()
    bad = 0
    examples = []
    poi_mat = seq[POI_COLS].to_numpy(np.int64)
    real_len = (poi_mat >= 0).sum(axis=1)  # non-pad history length
    uids = seq["userid"].to_numpy(np.int64)
    splits = seq["split"].to_numpy()
    for i in range(len(seq)):
        need = int(real_len[i]) + 1  # history + target
        have = psize.get((int(uids[i]), splits[i]), 0)
        if have < need:
            bad += 1
            if len(examples) < 5:
                examples.append({"row": i, "userid": int(uids[i]), "split": splits[i],
                                 "need": need, "portion_have": have})
    return {"pass": bad == 0, "n_violations": int(bad), "examples": examples}


def leak_check_3_chronology(seq_test_users, assign: pd.DataFrame) -> dict:
    """LEAK CHECK 3: for users present in BOTH train and test windows, the earliest
    TEST check-in datetime must be strictly later than the latest TRAIN check-in
    datetime (the split is genuinely chronological, not random). Quantify how many
    such users satisfy test-after-train (should be 100%)."""
    bounds = assign.groupby(["userid", "split"])["datetime"].agg(["min", "max"])
    violations = []
    n_users_both = 0
    for uid in seq_test_users:
        if (uid, "train") in bounds.index and (uid, "test") in bounds.index:
            n_users_both += 1
            train_max = bounds.loc[(uid, "train"), "max"]
            test_min = bounds.loc[(uid, "test"), "min"]
            if not (test_min > train_max):
                violations.append({"userid": int(uid),
                                   "train_max": str(train_max), "test_min": str(test_min)})
    return {"pass": len(violations) == 0,
            "n_users_train_and_test": int(n_users_both),
            "n_violations": len(violations),
            "examples": violations[:5]}


def build_city(city: str) -> dict:
    g, p2i, p2r = _graph(city)
    n_regions = int(p2r.max()) + 1
    meta = g["metadata"].copy()
    meta["userid"] = meta["userid"].astype(np.int64)
    meta["placeid"] = meta["placeid"].astype(np.int64)

    # 1+2: per-user chronological split assignment
    assign = build_split_assignment(meta)

    # 3: window WITHIN each portion (no boundary span by construction)
    seq_parts = [_sequences_within_portion(assign[assign["split"] == s], s) for s in SPLITS]
    seq = pd.concat(seq_parts, ignore_index=True)

    # discard users with no TRAIN windows (train portion too short)
    train_users = set(seq.loc[seq["split"] == "train", "userid"].astype(int))
    seq = seq[seq["userid"].isin(train_users)].reset_index(drop=True)

    # labels (region of target + last-observed region) — geography only
    seq["region_idx"] = _region_of_target(seq["target_poi"].to_numpy(), p2i, p2r)
    seq["last_region_idx"] = _last_region(seq[POI_COLS].to_numpy(), p2i, p2r)

    # ---- LEAK CHECKS ----
    lc1 = leak_check_1_no_boundary_span(seq, assign)
    if not lc1["pass"]:
        raise SystemExit(f"[{city}] LEAK CHECK 1 FAILED (window spans split boundary): {lc1}")
    test_users = set(seq.loc[seq["split"] == "test", "userid"].astype(int))
    lc3 = leak_check_3_chronology(test_users, assign)
    if not lc3["pass"]:
        raise SystemExit(f"[{city}] LEAK CHECK 3 FAILED (split not chronological): {lc3}")

    # ---- write structural artifacts ----
    out_dir = IoPaths.CHECK2HGI.get_state_dir(city)
    chrono = out_dir / "chrono_split"
    chrono.mkdir(parents=True, exist_ok=True)

    # POI sequences (set-(a) schema: str POI cols + int64 userid) + split col
    seq_canon = seq[POI_COLS + ["target_poi", "userid", "split"]].copy()
    for c in POI_COLS + ["target_poi"]:
        seq_canon[c] = seq_canon[c].astype(str)
    seq_canon.to_parquet(chrono / "sequences_next_chrono.parquet", index=False)

    seq[["userid", "next_category", "region_idx", "last_region_idx", "split"]].to_parquet(
        chrono / "next_region_labels_chrono.parquet", index=False)

    # per-checkin split audit trail
    assign[["userid", "placeid", "datetime", "split", "_order", "_user_len"]].to_parquet(
        chrono / "split_assignment.parquet", index=False)

    # ---- train-ONLY region-transition prior ----
    tr = seq[seq["split"] == "train"]
    # LEAK CHECK 2: prior is built from TRAIN rows only — quote the partitioning line.
    leak2_line = "tr = seq[seq['split'] == 'train']  -> log_T from tr['poi_8'], tr['target_poi'] ONLY"
    log_probs = _log_probs_from_rows(
        tr["poi_8"].to_numpy(np.int64), tr["target_poi"].to_numpy(np.int64),
        p2i, p2r, n_regions, SMOOTH_EPS)
    # verify val/test transitions are NOT in the prior: a content audit comparing the
    # train-only matrix against an all-rows matrix must differ (val/test add counts).
    log_probs_all = _log_probs_from_rows(
        seq["poi_8"].to_numpy(np.int64), seq["target_poi"].to_numpy(np.int64),
        p2i, p2r, n_regions, SMOOTH_EPS)
    train_only_differs = bool(not np.allclose(log_probs, log_probs_all))
    lc2 = {"pass": train_only_differs, "partitioning_line": leak2_line,
           "train_only_differs_from_all_rows": train_only_differs,
           "n_train_rows": int(len(tr)), "n_total_rows": int(len(seq))}
    if not lc2["pass"]:
        raise SystemExit(f"[{city}] LEAK CHECK 2 FAILED (prior not train-only / no diff): {lc2}")

    torch.save({"log_transition": torch.from_numpy(log_probs), "smoothing_eps": SMOOTH_EPS,
                "n_regions": n_regions, "split": "train", "fold": "chrono",
                "protocol": "chrono_per_user_80_10_10"},
               chrono / "region_transition_log_chrono_train.pt")

    # ---- stats ----
    split_counts = {s: int((seq["split"] == s).sum()) for s in SPLITS}
    n_users_kept = int(seq["userid"].nunique())
    # mean per-user timeline length over KEPT users (full graph-mapped timeline)
    kept_lens = assign[assign["userid"].isin(set(seq["userid"].astype(int)))] \
        .groupby("userid").size()
    return {
        "city": city,
        "n_users_total_mapped": int(meta["userid"].nunique()),
        "n_users_kept": n_users_kept,
        "n_users_dropped_short_train": int(meta["userid"].nunique() - n_users_kept),
        "seq_counts": split_counts,
        "n_regions": n_regions,
        "n_categories_7root": int(seq["next_category"].nunique()),
        "mean_user_timeline_len_kept": round(float(kept_lens.mean()), 2),
        "median_user_timeline_len_kept": float(kept_lens.median()),
        "leak_check_1_no_boundary_span": lc1,
        "leak_check_2_prior_train_only": lc2,
        "leak_check_3_chronological": lc3,
        "artifacts": {
            "sequences": str(chrono / "sequences_next_chrono.parquet"),
            "labels": str(chrono / "next_region_labels_chrono.parquet"),
            "prior": str(chrono / "region_transition_log_chrono_train.pt"),
            "split_assignment": str(chrono / "split_assignment.parquet"),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    get_city(args.city)
    rep = build_city(args.city)
    (data_dir(args.city) / "chrono_split_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
