"""Anchor baselines: linear probe on raw input features (no encoder),
and a 'majority' floor. These anchor the variant comparison: if a variant's
probe F1 is barely above raw-feature F1, the encoder isn't doing much.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pickle

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))
sys.path.insert(0, str(_root / "experiments" / "check2hgi_up"))

from run_variant import build_eval_pairs, linear_probe_cv  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="Alabama")
    ap.add_argument("--out_dir", default="docs/results/UP1")
    args = ap.parse_args()

    p = _root / "output" / "check2hgi" / args.state.lower() / "temp" / "checkin_graph.pt"
    with open(p, "rb") as f:
        cd = pickle.load(f)
    metadata = cd["metadata"]
    raw_feats = cd["node_features"].astype(np.float32)  # [N_checkins, F]
    print(f"raw features shape: {raw_feats.shape}")

    # Anchor 1: identity raw features
    X, y, groups, _ = build_eval_pairs(metadata, raw_feats)
    t0 = time.time()
    probe_raw = linear_probe_cv(X, y, groups, k=5, seed=42)
    print(f"raw-features:  f1={probe_raw['f1_mean']:.4f}±{probe_raw['f1_std']:.4f}  "
          f"acc={probe_raw['acc_mean']:.4f}±{probe_raw['acc_std']:.4f}  ({time.time()-t0:.1f}s)")

    # Anchor 2: majority class — predicted label = mode of training set per fold
    from sklearn.model_selection import GroupKFold
    from sklearn.metrics import f1_score, accuracy_score
    folds = list(GroupKFold(n_splits=5).split(X, y, groups=groups))
    f1s, accs = [], []
    for tr, te in folds:
        most = np.bincount(y[tr]).argmax()
        pred = np.full_like(y[te], most)
        f1s.append(float(f1_score(y[te], pred, average="macro")))
        accs.append(float(accuracy_score(y[te], pred)))
    probe_maj = {
        "f1_mean": float(np.mean(f1s)), "f1_std": float(np.std(f1s)),
        "acc_mean": float(np.mean(accs)), "acc_std": float(np.std(accs)),
        "f1_per_fold": f1s, "acc_per_fold": accs,
    }
    print(f"majority:      f1={probe_maj['f1_mean']:.4f}±{probe_maj['f1_std']:.4f}  "
          f"acc={probe_maj['acc_mean']:.4f}±{probe_maj['acc_std']:.4f}")

    out_dir = Path(args.out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"anchors_{args.state.lower()}.json", "w") as f:
        json.dump({
            "state": args.state,
            "raw_features": probe_raw,
            "majority": probe_maj,
            "raw_feature_dim": int(raw_feats.shape[1]),
        }, f, indent=2)
    print(f"saved anchors to {out_dir}/anchors_{args.state.lower()}.json")


if __name__ == "__main__":
    main()
