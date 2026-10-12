"""A2 feature-concat — faithful per-visit raw-feature builder.

A2 asks: is Check2HGI's next-category lift the hierarchical-infomax *learning*, or just
*feature injection*? Check2HGI's check-in nodes carry exactly:

    node_features = [category_one_hot (n_cat) | hour_sin, hour_cos, dow_sin, dow_cos]

(see research/embeddings/check2hgi/preprocess.py:_build_node_features). The control is
HGI ⊕ those SAME raw per-visit features → matched heads. This module builds the per-visit
[N, 9, F] feature block that row-aligns to a given sequences_next.parquet.

FAITHFULNESS (the whole gate hinges on this — see HANDOFF advisor note):
  • PER-VISIT, not per-POI. Each window position carries ITS OWN check-in's raw features
    (a placeid recurs across visits with different hour/dow), recovered by replaying the
    canonical windowing over check-in ROW positions.
  • PAST-ONLY. Only the 9 history positions get features; the target check-in never enters.
  • ALIGNMENT-VALIDATED. We replay generate_sequences on local row positions (identical
    window/shift/pad logic, value-independent for non-negative inputs), then ASSERT the
    reconstructed placeids equal seq_df's poi_0..poi_8 row-for-row. A mismatch aborts.

Mirrors check2hgi's encoding exactly: LabelEncoder (sorted) over `category` for the one-hot,
sin/cos(2π·hour/24), sin/cos(2π·dow/7).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))

from configs.model import InputsConfig
from data.inputs.core import generate_sequences, PADDING_VALUE

WINDOW = InputsConfig.SLIDE_WINDOW  # 9


def compute_checkin_features(checkins_df: pd.DataFrame, category_classes=None):
    """Per-check-in [N, F] features = category one-hot ⊕ temporal sin/cos.

    Mirrors Check2HGIPreprocess._build_node_features. Returns (features, classes).
    If ``category_classes`` is given, the one-hot uses that fixed class order
    (so every arm/state shares an encoding); otherwise sorted-unique is used.
    """
    if category_classes is None:
        category_classes = sorted(checkins_df["category"].astype(str).unique())
    cls_to_idx = {c: i for i, c in enumerate(category_classes)}
    n = len(checkins_df)
    n_cat = len(category_classes)

    cat_oh = np.zeros((n, n_cat), dtype=np.float32)
    cat_idx = checkins_df["category"].astype(str).map(cls_to_idx).to_numpy()
    if np.isnan(cat_idx.astype(float)).any():
        raise ValueError("category value outside provided class list")
    cat_oh[np.arange(n), cat_idx.astype(np.int64)] = 1.0

    dt = pd.to_datetime(checkins_df["datetime"])
    hour = dt.dt.hour.to_numpy()
    dow = dt.dt.dayofweek.to_numpy()
    temporal = np.zeros((n, 4), dtype=np.float32)
    temporal[:, 0] = np.sin(2 * np.pi * hour / 24)
    temporal[:, 1] = np.cos(2 * np.pi * hour / 24)
    temporal[:, 2] = np.sin(2 * np.pi * dow / 7)
    temporal[:, 3] = np.cos(2 * np.pi * dow / 7)

    return np.concatenate([cat_oh, temporal], axis=1), category_classes


def build_per_visit_features(
    seq_df: pd.DataFrame,
    checkins_df: pd.DataFrame,
    category_classes=None,
    validate: bool = True,
    stride: int = None,
    min_sequence_length: int = None,
    emit_tail: bool = True,
) -> np.ndarray:
    """Build [N, 9, F] per-visit features row-aligned to ``seq_df``.

    ``seq_df`` is the authoritative sequences_next.parquet (poi_0..poi_8, target_poi,
    userid). ``checkins_df`` MUST be the same check-in set the sequences were built from
    (raw load_city for HGI; check2hgi metadata for the c2hgi reg path) — the alignment
    assert is the proof.
    """
    checkins_df = checkins_df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    feats, category_classes = compute_checkin_features(checkins_df, category_classes)
    F = feats.shape[1]

    placeids_all = checkins_df["placeid"].to_numpy()

    out_feats = []
    recon_pois = []  # reconstructed placeid windows, for validation
    # groupby('userid') sorts groups by key — same flatten order as the builders.
    for _userid, sub in checkins_df.groupby("userid", sort=True):
        local_rows = sub.index.to_numpy()  # positions into checkins_df / feats
        n_visits = len(local_rows)
        # Replay the canonical windowing on LOCAL POSITIONS (0..n_visits-1).
        # Same shift/pad logic as on placeids (value-independent for >=0 inputs).
        # [2026-08-16] O JANELAMENTO E PARAMETRIZADO. Antes era sempre o nao-sobreposto, que e o
        # do estudo original; sob o janelamento atual, stride 1 com sequencia minima 10 e sem
        # cauda, a contagem de janelas e outra e a validacao abortava com razao. Os defaults
        # mantidos abaixo reproduzem o comportamento anterior byte a byte quando nada e passado.
        _kw = {}
        if stride is not None:
            _kw["stride"] = stride
        if min_sequence_length is not None:
            _kw["min_sequence_length"] = min_sequence_length
        _kw["emit_tail"] = emit_tail
        seqs = generate_sequences(list(range(n_visits)), **_kw)
        for seq in seqs:
            hist = seq[:WINDOW]  # local positions, -1 = pad
            fblock = np.zeros((WINDOW, F), dtype=np.float32)
            pwin = []
            for k, pos in enumerate(hist):
                if pos == PADDING_VALUE:
                    pwin.append(PADDING_VALUE)
                else:
                    grow = local_rows[pos]
                    fblock[k] = feats[grow]
                    pwin.append(int(placeids_all[grow]))
            out_feats.append(fblock)
            recon_pois.append(pwin)

    feat_arr = np.stack(out_feats, axis=0)  # [N, 9, F]

    if validate:
        if len(seq_df) != feat_arr.shape[0]:
            raise AssertionError(
                f"Row count mismatch: seq_df={len(seq_df)} vs reconstructed={feat_arr.shape[0]}. "
                "checkins_df is not the set these sequences were built from."
            )
        recon = np.array(recon_pois, dtype=np.int64)
        poi_cols = [f"poi_{i}" for i in range(WINDOW)]
        ref = seq_df[poi_cols].to_numpy().astype(str)
        rec = recon.astype(str)
        # seq_df pads as '-1' strings; our recon uses -1 too.
        mism = (ref != rec)
        if mism.any():
            n_bad = int(mism.any(axis=1).sum())
            first = int(np.where(mism.any(axis=1))[0][0])
            raise AssertionError(
                f"Placeid alignment FAILED on {n_bad}/{len(seq_df)} rows. "
                f"First bad row {first}: ref={ref[first].tolist()} rec={rec[first].tolist()}"
            )

    return feat_arr


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Smoke-test feature alignment for a state/engine.")
    ap.add_argument("--state", required=True)
    ap.add_argument("--seq", required=True, help="path to sequences_next.parquet")
    ap.add_argument("--checkins", default=None, help="checkins parquet (default data/checkins/<State>.parquet)")
    args = ap.parse_args()

    seq_df = pd.read_parquet(args.seq)
    ck = args.checkins or str(_root / "data" / "checkins" / f"{args.state.capitalize()}.parquet")
    ck_df = pd.read_parquet(ck)
    fa = build_per_visit_features(seq_df, ck_df, validate=True)
    print(f"OK  feat shape={fa.shape}  F={fa.shape[-1]}  rows={len(seq_df)}  ALIGNMENT VALIDATED")
