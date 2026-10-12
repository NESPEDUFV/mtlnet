"""Build E4 structural inputs for a city — BOTH protocols (no embeddings). City-generic.

(a) GOWALLA-PARITY [primary]: within-USER window=9 + user-grouped 5-fold
    StratifiedGroupKFold(seed) + per-fold TRAIN-ONLY region priors. The controlled
    external-validity protocol (same as Gowalla; only the corpus changes).
        output/check2hgi/<city>/temp/sequences_next.parquet
        output/check2hgi/<city>/region_transition_log_seed{S}_fold{N}.pt
(b) NATIVE-TRAIL [secondary]: within-TRAIL window=9 + shipped split + train-split
    prior. Massive-STEPS-protocol-faithful but power-session-biased (most trails are
    too short for window=9). Namespaced under output/check2hgi/<city>/shipped_split/.

NO learned embeddings needed: sequences/labels/folds/priors depend only on the
corpus + the geography-only poi->region map + the seed — NOT the substrate encoder.
Phase V regenerates the embedding-bearing parquets; the folds it computes match
these priors bit-for-bit. Sequence generation reuses the repo's own
core.convert_user_checkins_to_sequences; priors reuse compute_region_transition.

NOTE: a 3rd "native-shape" set (within-trail, window=5, overlapping) is recommended
by the methodology review as a robustness check — built separately (build_inputs_native.py).

Run:  python scripts/second_dataset/build_inputs.py --city istanbul
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

from sklearn.model_selection import StratifiedGroupKFold  # noqa: E402
from configs.globals import CATEGORIES_MAP  # noqa: E402
from configs.paths import IoPaths  # noqa: E402
from data.inputs.core import convert_user_checkins_to_sequences  # noqa: E402
from compute_region_transition import (_log_probs_from_rows,  # noqa: E402
                                       build_transition_matrix_from_userids, save)
from cities import data_dir, get as get_city  # noqa: E402

WINDOW = 9
SEEDS = [0, 1, 7, 100, 42]
N_SPLITS = 5
SMOOTH_EPS = 0.01
INV_CAT = {v: k for k, v in CATEGORIES_MAP.items()}
POI_COLS = [f"poi_{i}" for i in range(WINDOW)]


def _graph(city):
    g = pkl.load(open(IoPaths.CHECK2HGI.get_graph_data_file(city), "rb"))
    return g, g["placeid_to_idx"], np.asarray(g["poi_to_region"], dtype=np.int64)


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


def _sequences(meta, group_col):
    meta = meta.copy()
    meta["d0"] = np.float32(0.0)
    rows, gids = [], []
    for gid, gdf in meta.groupby(group_col, sort=True):
        if len(gdf) < 5:
            continue
        gdf = gdf.reset_index(drop=True)
        emb_res, poi_seqs = convert_user_checkins_to_sequences(gdf, ["d0"], WINDOW, 1, stride=None)
        for er, ps in zip(emb_res, poi_seqs):
            rows.append(ps[:WINDOW + 1] + [int(ps[-1]), str(er[-2])])
            gids.append(gid)
    df = pd.DataFrame(rows, columns=POI_COLS + ["target_poi", "userid", "next_category"])
    for c in POI_COLS + ["target_poi"]:
        df[c] = df[c].astype(np.int64)
    df["userid"] = df["userid"].astype(np.int64)
    if group_col != "userid":
        df[group_col] = gids
    return df


def build_set_a(city, meta, p2i, p2r):
    out_dir = IoPaths.CHECK2HGI.get_state_dir(city)
    seq = _sequences(meta, "userid")
    seq["region_idx"] = _region_of_target(seq["target_poi"].to_numpy(), p2i, p2r)
    seq["last_region_idx"] = _last_region(seq[POI_COLS].to_numpy(), p2i, p2r)

    (out_dir / "temp").mkdir(parents=True, exist_ok=True)
    seq_canon = seq[POI_COLS + ["target_poi", "userid"]].copy()
    for c in POI_COLS + ["target_poi"]:
        seq_canon[c] = seq_canon[c].astype(str)
    seq_canon.to_parquet(out_dir / "temp" / "sequences_next.parquet", index=False)

    (out_dir / "input").mkdir(parents=True, exist_ok=True)
    seq[["userid", "next_category", "region_idx", "last_region_idx"]].to_parquet(
        out_dir / "input" / "next_region_labels.parquet", index=False)

    y = seq["next_category"].map(INV_CAT).to_numpy(dtype=np.int64)
    uids = seq["userid"].to_numpy(dtype=np.int64)
    Xz = np.zeros((len(seq), 1), dtype=np.float32)
    fold_spec = {}
    for s in SEEDS:
        sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=s)
        fold_spec[s] = []
        for fold, (tr, va) in enumerate(sgkf.split(Xz, y, groups=uids)):
            train_userids = set(int(u) for u in uids[tr])
            log_probs, _ = build_transition_matrix_from_userids(
                city, train_userids=train_userids, smoothing_eps=SMOOTH_EPS, seq_df=seq)
            save(city, log_probs, SMOOTH_EPS,
                 filename=f"region_transition_log_seed{s}_fold{fold + 1}.pt",
                 n_splits=N_SPLITS, seed=s)
            fold_spec[s].append({"fold": fold + 1, "n_train": int(len(tr)),
                                 "n_val": int(len(va)), "n_train_users": len(train_userids)})
    (out_dir / "folds").mkdir(parents=True, exist_ok=True)
    (out_dir / "folds" / "fold_spec_userGrouped.json").write_text(
        json.dumps({"n_splits": N_SPLITS, "seeds": SEEDS, "folds": fold_spec}, indent=2))
    return {"n_sequences": int(len(seq)), "n_regions": int(p2r.max()) + 1,
            "seeds": SEEDS, "n_prior_files": len(SEEDS) * N_SPLITS}


def build_set_b(city, meta, p2i, p2r):
    out_dir = IoPaths.CHECK2HGI.get_state_dir(city)
    ship = out_dir / "shipped_split"
    seq = _sequences(meta, "trail_id")
    trail_split = meta.drop_duplicates("trail_id").set_index("trail_id")["split"]
    seq["split"] = seq["trail_id"].map(trail_split)
    seq["region_idx"] = _region_of_target(seq["target_poi"].to_numpy(), p2i, p2r)
    seq["last_region_idx"] = _last_region(seq[POI_COLS].to_numpy(), p2i, p2r)

    ship.mkdir(parents=True, exist_ok=True)
    seq.to_parquet(ship / "sequences_next_trail.parquet", index=False)

    tr = seq[seq["split"] == "train"]
    nreg = int(p2r.max()) + 1
    log_probs = _log_probs_from_rows(tr["poi_8"].to_numpy(np.int64), tr["target_poi"].to_numpy(np.int64),
                                     p2i, p2r, nreg, SMOOTH_EPS)
    import torch
    torch.save({"log_transition": torch.from_numpy(log_probs), "smoothing_eps": SMOOTH_EPS,
                "n_regions": nreg, "split": "train", "protocol": "shipped_per_trail"},
               ship / "region_transition_log_shipped_train.pt")
    return {"n_sequences": int(len(seq)), "split_rows": seq["split"].value_counts().to_dict(),
            "n_regions": nreg}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", required=True)
    args = ap.parse_args()
    get_city(args.city)
    g, p2i, p2r = _graph(args.city)
    meta = g["metadata"].copy()
    meta["userid"] = meta["userid"].astype(np.int64)
    meta["placeid"] = meta["placeid"].astype(np.int64)
    corpus = pd.read_parquet(IoPaths.get_city(args.city),
                             columns=["userid", "placeid", "datetime", "trail_id", "split"])
    meta = meta.merge(corpus, on=["userid", "placeid", "datetime"], how="left", validate="m:1")
    assert meta["trail_id"].notna().all(), "trail_id join left NaNs — key not unique?"

    rep = {"city": args.city,
           "set_a_gowalla_parity": build_set_a(args.city, meta, p2i, p2r),
           "set_b_native_trail": build_set_b(args.city, meta, p2i, p2r)}
    (data_dir(args.city) / "inputs_report.json").write_text(json.dumps(rep, indent=2))
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
