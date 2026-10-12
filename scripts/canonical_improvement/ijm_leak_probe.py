"""IJM-masked leak probe — runs standard + user-grouped 5-fold logreg on the
slot-8 embedding column of `next.parquet`. The standard probe (StratifiedKFold)
allows the same user to appear in both train and val splits; the IJM-masked
variant (StratifiedGroupKFold by userid) prevents user-level info bleed.

Used for the T3.2 ResLN leak-claim guard (advisor C18 mitigation, task #67):
if the standard leak F1 drops sharply under user-held-out splits, the original
+2.24 pp leak drift was inflated by user-level correlations rather than
encoder-internal structural leakage.

Usage:
    python scripts/ijm_leak_probe.py --next-parquet PATH [--out PATH]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold


def _probe(X, y, splitter, name, groups=None):
    f1s = []
    if groups is None:
        iterator = splitter.split(X, y)
    else:
        iterator = splitter.split(X, y, groups=groups)
    for fold, (tr, va) in enumerate(iterator):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[tr], y[tr])
        pred = clf.predict(X[va])
        f1 = f1_score(y[va], pred, average="macro", zero_division=0)
        f1s.append(f1)
        print(f"  [{name}] fold {fold+1}/5: f1={f1*100:.2f}  "
              f"train_users={len(np.unique(groups[tr])) if groups is not None else 'n/a'}  "
              f"val_users={len(np.unique(groups[va])) if groups is not None else 'n/a'}")
    return {
        "f1_mean_pct": float(np.mean(f1s) * 100),
        "f1_std_pct": float(np.std(f1s, ddof=1) * 100),
        "f1_per_fold_pct": [float(f * 100) for f in f1s],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--next-parquet", required=True,
                    help="path to {state}/input/next.parquet (must have "
                         "embedding cols '0'..'575', 'next_category', 'userid')")
    ap.add_argument("--out", default=None,
                    help="output JSON path (default: alongside input as ijm_leak_probe.json)")
    args = ap.parse_args()

    in_path = Path(args.next_parquet)
    if not in_path.exists():
        raise FileNotFoundError(f"missing {in_path}")
    out_path = Path(args.out) if args.out else in_path.parent / "ijm_leak_probe.json"

    print(f"[IJM] loading {in_path}")
    df = pd.read_parquet(in_path)
    last_cols = [str(i) for i in range(8 * 64, 9 * 64)]
    X = df[last_cols].to_numpy(np.float32)
    y_raw = df["next_category"]
    y = pd.Categorical(y_raw).codes if y_raw.dtype == object else y_raw.to_numpy()
    groups = df["userid"].to_numpy()
    print(f"[IJM]   rows: {len(df):,}  n_users: {len(np.unique(groups)):,}  "
          f"n_classes: {len(np.unique(y))}")

    print("[IJM] standard probe (StratifiedKFold, random samples)")
    sk = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    sk_res = _probe(X, y, sk, "SK", groups=groups)
    print(f"[IJM]   StratifiedKFold      cat F1: {sk_res['f1_mean_pct']:.2f} ± {sk_res['f1_std_pct']:.2f}")

    print("[IJM] user-held-out probe (StratifiedGroupKFold by userid)")
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    sgkf_res = _probe(X, y, sgkf, "SGKF", groups=groups)
    print(f"[IJM]   StratifiedGroupKFold cat F1: {sgkf_res['f1_mean_pct']:.2f} ± {sgkf_res['f1_std_pct']:.2f}")

    drift = sk_res["f1_mean_pct"] - sgkf_res["f1_mean_pct"]
    print(f"[IJM]   user-level leak drift (SK − SGKF) = {drift:+.2f} pp")
    print(f"[IJM]     interpretation: drift > +3 pp ⇒ standard probe was user-level leaky")
    print(f"[IJM]                     drift ≤ +2 pp ⇒ original leak claim is structurally honest")

    payload = {
        "source": str(in_path),
        "n_rows": int(len(df)),
        "n_users": int(len(np.unique(groups))),
        "n_classes": int(len(np.unique(y))),
        "stratified_kfold": sk_res,
        "stratified_group_kfold": sgkf_res,
        "user_leak_drift_pp": float(drift),
    }
    out_path.write_text(json.dumps(payload, indent=2))
    print(f"[IJM] saved {out_path}")


if __name__ == "__main__":
    main()
