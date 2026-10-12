"""Capture per-fold cat F1 + reg top10_acc_indist + leak-probe for one T1.3 grid point."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import StratifiedKFold


def leak_probe(state: str) -> dict:
    """Re-run T1.1 protocol on the current canonical Check2HGI for this state."""
    p = Path(f"/home/vitor.oliveira/PoiMtlNet/output/check2hgi/{state}/input/next.parquet")
    if not p.exists():
        return {"error": f"missing {p}"}
    df = pd.read_parquet(p)
    last_cols = [str(i) for i in range(8 * 64, 9 * 64)]
    X = df[last_cols].to_numpy(np.float32)
    y_raw = df["next_category"]
    y = pd.Categorical(y_raw).codes if y_raw.dtype == object else y_raw.to_numpy()
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1s = []
    for tr, va in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0)
        clf.fit(X[tr], y[tr])
        f1s.append(f1_score(y[va], clf.predict(X[va]), average="macro", zero_division=0))
    return {
        "f1_mean_pct": float(np.mean(f1s) * 100),
        "f1_std_pct": float(np.std(f1s, ddof=1) * 100),
    }


def gather_run(run_dir: Path, n_folds: int = 5) -> dict:
    cat_f1, reg_top10 = [], []
    for fold in range(1, n_folds + 1):
        p = run_dir / "folds" / f"fold{fold}_info.json"
        info = json.loads(p.read_text())
        cat_f1.append(float(info["primary_checkpoint"]["task_metrics"]["next_category"]["f1"]))
        reg_top10.append(float(info["diagnostic_best_epochs"]["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"]))
    return {
        "cat_f1_per_fold": cat_f1,
        "reg_top10_per_fold": reg_top10,
        "cat_f1_mean_pct": float(np.mean(cat_f1) * 100),
        "cat_f1_std_pct": float(np.std(cat_f1, ddof=1) * 100),
        "reg_top10_mean_pct": float(np.mean(reg_top10) * 100),
        "reg_top10_std_pct": float(np.std(reg_top10, ddof=1) * 100),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--c2p", type=float, required=True)
    ap.add_argument("--p2r", type=float, required=True)
    ap.add_argument("--r2c", type=float, required=True)
    ap.add_argument("--al-run", type=Path, required=True)
    ap.add_argument("--az-run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    record = {
        "tag": args.tag,
        "alpha": {"c2p": args.c2p, "p2r": args.p2r, "r2c": args.r2c},
        "al": {
            "run_dir": str(args.al_run),
            **gather_run(args.al_run),
            "leak_probe": leak_probe("alabama"),
        },
        "az": {
            "run_dir": str(args.az_run),
            **gather_run(args.az_run),
            "leak_probe": leak_probe("arizona"),
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(record, indent=2))
    print(f"[T1-3-record] wrote {args.out}")
    print(f"  AL: cat F1={record['al']['cat_f1_mean_pct']:.2f}±{record['al']['cat_f1_std_pct']:.2f}  reg={record['al']['reg_top10_mean_pct']:.2f}±{record['al']['reg_top10_std_pct']:.2f}  leak={record['al']['leak_probe'].get('f1_mean_pct','?'):.2f}")
    print(f"  AZ: cat F1={record['az']['cat_f1_mean_pct']:.2f}±{record['az']['cat_f1_std_pct']:.2f}  reg={record['az']['reg_top10_mean_pct']:.2f}±{record['az']['reg_top10_std_pct']:.2f}  leak={record['az']['leak_probe'].get('f1_mean_pct','?'):.2f}")


if __name__ == "__main__":
    main()
