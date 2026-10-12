"""Substrate-only linear probe (Leg I of SUBSTRATE_COMPARISON_PLAN).

Loads the cat-task `next.parquet` for a given (state, engine), extracts
the last-position embedding of each 9-window sequence, and runs a
user-disjoint K-fold logistic regression. Reports per-fold + summary
macro-F1 / Acc@1. No sequence model, no attention — substrate quality
direct.

Usage::

    python scripts/probe/substrate_linear_probe.py \\
        --state alabama --engine check2hgi --window-pos last

Output: docs/results/probe/<state>_<engine>_<pos>.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

_root = Path(__file__).resolve().parents[2]
if str(_root / "src") not in sys.path:
    sys.path.insert(0, str(_root / "src"))
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

EMB_DIM = 64
WINDOW = 9


def _load_next(state: str, engine: str) -> pd.DataFrame:
    out_root = Path(__import__("os").environ.get("OUTPUT_DIR", _root / "output"))
    p = out_root / engine / state / "input" / "next.parquet"
    if not p.exists():
        raise FileNotFoundError(f"next.parquet not found at {p}")
    df = pd.read_parquet(p)
    return df


def _extract_window(df: pd.DataFrame, pos: str) -> np.ndarray:
    """Extract a single 64-dim slice from each row's 9*64 = 576 emb cols."""
    emb_cols = [str(i) for i in range(WINDOW * EMB_DIM)]
    arr = df[emb_cols].to_numpy(dtype=np.float32)
    arr = arr.reshape(len(df), WINDOW, EMB_DIM)  # [N, 9, 64]
    if pos == "last":
        return arr[:, -1, :]
    if pos == "mean":
        # Mean over non-pad positions (pad = -1 sentinel; treat any all-(-1) slot as pad)
        mask = ~(arr == -1.0).all(axis=-1)  # [N, 9]
        weights = mask.astype(np.float32)
        weights = weights / np.clip(weights.sum(axis=1, keepdims=True), 1.0, None)
        return (arr * weights[..., None]).sum(axis=1)
    if pos == "first":
        return arr[:, 0, :]
    raise ValueError(f"unknown --window-pos {pos!r}")


def _build_xy(df: pd.DataFrame, pos: str):
    X = _extract_window(df, pos)
    cats = sorted(df["next_category"].unique())
    cat_to_id = {c: i for i, c in enumerate(cats)}
    y = df["next_category"].map(cat_to_id).to_numpy(np.int64)
    groups = df["userid"].astype(str).to_numpy()
    return X, y, groups, cat_to_id


def linear_probe_cv(X, y, groups, k=5, seed=42):
    folds = list(GroupKFold(n_splits=k).split(X, y, groups=groups))
    f1s, accs = [], []
    for tr, te in folds:
        clf = Pipeline([
            ("scaler", StandardScaler()),
            ("lr", LogisticRegression(max_iter=1000, C=1.0, n_jobs=1,
                                      solver="lbfgs", random_state=seed)),
        ])
        clf.fit(X[tr], y[tr])
        pred = clf.predict(X[te])
        f1s.append(float(f1_score(y[te], pred, average="macro")))
        accs.append(float(accuracy_score(y[te], pred)))
    return {
        "f1_per_fold": f1s, "acc_per_fold": accs,
        "f1_mean": float(np.mean(f1s)), "f1_std": float(np.std(f1s)),
        "acc_mean": float(np.mean(accs)), "acc_std": float(np.std(accs)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    ap.add_argument("--engine", required=True, choices=["check2hgi", "hgi", "check2hgi_pooled"])
    ap.add_argument("--window-pos", default="last", choices=["last", "mean", "first"])
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out-dir", default=None,
                    help="default: docs/results/probe/")
    args = ap.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else (
        _root / "docs" / "studies" / "check2hgi" / "results" / "probe"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    df = _load_next(args.state, args.engine)
    X, y, groups, cat_to_id = _build_xy(df, args.window_pos)
    print(f"[probe] state={args.state} engine={args.engine} pos={args.window_pos} "
          f"X={X.shape} y={y.shape} n_users={len(set(groups))} n_classes={len(cat_to_id)}")

    res = linear_probe_cv(X, y, groups, k=args.folds, seed=args.seed)
    res.update(dict(
        state=args.state, engine=args.engine, window_pos=args.window_pos,
        folds=args.folds, seed=args.seed,
        n_rows=int(len(df)), n_users=int(len(set(groups))),
        n_classes=int(len(cat_to_id)), cat_to_id=cat_to_id,
        elapsed_sec=round(time.time() - t0, 2),
    ))
    print(f"[probe] f1_macro={res['f1_mean']:.4f}±{res['f1_std']:.4f}  "
          f"acc={res['acc_mean']:.4f}±{res['acc_std']:.4f}  ({res['elapsed_sec']:.1f}s)")

    fname = f"{args.state}_{args.engine}_{args.window_pos}.json"
    out = out_dir / fname
    with open(out, "w") as f:
        json.dump(res, f, indent=2)
    print(f"[probe] saved → {out}")


if __name__ == "__main__":
    main()
