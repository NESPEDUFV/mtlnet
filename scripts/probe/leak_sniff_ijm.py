"""Leak sniff test on I/J/M check-in embeddings.

Mechanically the cat path is byte-identical to canonical c2hgi (encoder
unchanged + .detach() before residual), so the last-step linear probe on
checkin embeddings should match canonical's ~31% (AL) / ~34% (AZ).
Anything elevated means an unexpected leak path.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score

REPO = Path(__file__).resolve().parents[2]


def last_step_probe(emb_parquet: Path) -> tuple[float, float]:
    df = pd.read_parquet(emb_parquet)
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    last = df.groupby("userid").tail(1)
    last = last[last["category"].notna()]
    emb_cols = [c for c in last.columns if c.isdigit()]
    X = last[emb_cols].to_numpy(np.float32)
    cat_codes = pd.Categorical(last["category"]).codes
    y = cat_codes.astype(int)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1s = []
    for tr, va in skf.split(X, y):
        clf = LogisticRegression(max_iter=2000, C=1.0, n_jobs=-1)
        clf.fit(X[tr], y[tr])
        f1s.append(f1_score(y[va], clf.predict(X[va]), average="macro", zero_division=0))
    return float(np.mean(f1s) * 100), float(np.std(f1s, ddof=1) * 100)


def main():
    designs = ["check2hgi", "check2hgi_design_b", "check2hgi_design_h",
               "check2hgi_design_d", "check2hgi_design_i", "check2hgi_design_j",
               "check2hgi_design_m"]
    import sys as _sys
    states = _sys.argv[1:] if len(_sys.argv) > 1 else ["alabama", "arizona"]
    headers = "  ".join([f"{s[:2].upper():>14s}" for s in states])
    print(f"{'design':28s}  {headers}")
    print("-" * 64)
    for d in designs:
        cells = []
        for s in states:
            p = REPO / "output" / d / s / "embeddings.parquet"
            if not p.exists():
                cells.append("MISSING        "); continue
            mean, std = last_step_probe(p)
            cells.append(f"{mean:5.2f} ± {std:4.2f}")
        row = "  ".join([f"{c:>14s}" for c in cells])
        print(f"{d:28s}  {row}")


if __name__ == "__main__":
    main()
