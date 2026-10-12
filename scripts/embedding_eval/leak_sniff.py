"""Leak-sniff gate for next-cat substrates (advisor-recommended, 2026-06-01).

The forward-temporal category leak (GAT self-loops / R-GCN root-weight letting the
NEXT check-in's category one-hot bleed into the current node) is invisible to the
POI-pooled L1 probe but shows up as a **per-step** signal: a linear probe on the
SINGLE last window-slot embedding should only recover the *last-visited* category's
autocorrelation ceiling (~the clean control). If a substrate's per-step probe beats
the clean control, its embedding carries FUTURE information => leak.

Gate: per-step next-cat F1 (last 64-d slot -> next_category, GroupKFold-by-user) vs
the control engine. flag if  perstep_F1 > control_perstep_F1 + margin.

Run on the harvested input/next.parquet (window of 9x64 + next_category + userid).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import GroupKFold

from configs.globals import CATEGORIES_MAP
from configs.paths import EmbeddingEngine, IoPaths

_CAT = {v: k for k, v in CATEGORIES_MAP.items()}


def _probe(X, y, groups, n_folds=5, standardize=True):
    """Macro-F1 of a torch linear softmax probe (GPU), GroupKFold-by-user, mean over folds.
    standardize=False keeps raw scale (needed to catch scale-amplification leaks)."""
    import torch, torch.nn.functional as F
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    C = int(y.max()) + 1
    f1s = []
    for tr, te in GroupKFold(n_folds).split(X, y, groups):
        if standardize:
            mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-6
        else:
            mu, sd = 0.0, 1.0
        xtr = torch.from_numpy(((X[tr] - mu) / sd).astype(np.float32)).to(dev)
        ytr = torch.from_numpy(y[tr]).long().to(dev)
        xte = torch.from_numpy(((X[te] - mu) / sd).astype(np.float32)).to(dev)
        clf = torch.nn.Linear(X.shape[1], C).to(dev)
        opt = torch.optim.AdamW(clf.parameters(), lr=1e-2)
        for _ in range(200):
            opt.zero_grad(); F.cross_entropy(clf(xtr), ytr).backward(); opt.step()
        with torch.no_grad():
            pred = clf(xte).argmax(1).cpu().numpy()
        f1s.append(f1_score(y[te], pred, average="macro", zero_division=0))
    return float(np.mean(f1s)), float(np.std(f1s))


def sniff(state: str, engines: list[str], control: str = "check2hgi_gcn_ctrl", margin: float = 0.03):
    rows = {}
    D = None
    for name in engines:
        df = IoPaths.load_next(state, EmbeddingEngine(name))
        num = [c for c in df.columns if str(c).isdigit()]
        if D is None:
            D = len(num) // 9  # per-step embedding dim
        X = df[num].to_numpy(np.float32)
        last = X[:, -D:]                       # last window slot (most recent check-in)
        full = X                               # all 9 steps (legit sequence reference)
        y = df["next_category"].map(_CAT).to_numpy()
        g = df["userid"].astype(str).to_numpy()
        ps_m, ps_s = _probe(last, y, g, standardize=True)
        raw_m, _ = _probe(last, y, g, standardize=False)   # raw scale → catches amplification leaks
        rows[name] = dict(perstep=ps_m, perstep_sd=ps_s, perstep_raw=raw_m)
        print(f"  {name:26s} per-step(std)={ps_m:.4f}±{ps_s:.4f}  per-step(raw)={raw_m:.4f}", flush=True)

    ceil = rows[control]["perstep"]; ceil_raw = rows[control]["perstep_raw"]
    print(f"\n[{state}] control ceilings: std={ceil:.4f} raw={ceil_raw:.4f}  (LEAK if std OR raw > ctrl+{margin})")
    print(f"{'engine':26s} {'std':>8s} {'raw':>8s} {'VERDICT':>8s}")
    out = []
    for name, r in rows.items():
        d_std = r["perstep"] - ceil; d_raw = r["perstep_raw"] - ceil_raw
        verdict = "LEAK" if (d_std > margin or d_raw > margin) else "clean"
        out.append({"state": state, "engine": name, **r,
                    "delta_std": d_std, "delta_raw": d_raw, "verdict": verdict})
        print(f"{name:26s} {r['perstep']:>8.4f} {r['perstep_raw']:>8.4f} {verdict:>8s}")
    return out


def main():
    ap = argparse.ArgumentParser(description="next-cat forward-leak sniff gate")
    ap.add_argument("--engines", nargs="+", required=True)
    ap.add_argument("--state", default="florida")
    ap.add_argument("--control", default="check2hgi_gcn_ctrl")
    ap.add_argument("--margin", type=float, default=0.03)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    print(f"### leak-sniff (per-step next-cat probe) — {args.state}")
    rows = sniff(args.state, args.engines, control=args.control, margin=args.margin)
    if args.out:
        pd.DataFrame(rows).to_csv(args.out, index=False)
        print(f"[written] {args.out}")


if __name__ == "__main__":
    main()
