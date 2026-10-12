"""K-step Markov over the *category sequence* for next_category.

Apples-to-apples floor for POI-RGNN: both methods see the same 9-step
input window. The Markov side conditions on the last K category IDs
(stupid backoff to K-1, K-2, ..., 1, then global majority) and predicts
the next category.

Outputs Acc@1 + macro-F1 for each K in {1, 3, 5, 7, 9}.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedGroupKFold

_root = Path(__file__).resolve().parents[1]
for p in (str(_root), str(_root / "src")):
    if p not in sys.path:
        sys.path.insert(0, p)

# Use the POI-RGNN ETL output to guarantee the *same* row alignment
# (same dedup, same windows). This is the only way to be sure the
# Markov floor and POI-RGNN see the exact same examples.
from research.baselines.poi_rgnn.etl import (  # noqa: E402
    N_CATEGORIES, WINDOW_SIZE, out_path as etl_out_path,
)

import pandas as pd  # noqa: E402

N_SPLITS = 5
SEED = 42


def _load(state: str):
    df = pd.read_parquet(etl_out_path(state))
    cat_seq = np.stack([df[f"cat_{k}"].to_numpy(np.int64) for k in range(WINDOW_SIZE)], axis=1)
    y = df["target_category"].to_numpy(np.int64)
    uid = df["userid"].astype(str).to_numpy()
    return cat_seq, y, uid


def _markov_k_predict(cat_train, y_train, cat_val, k_max):
    """Build N-gram tables for orders 1..k_max; predict via stupid backoff."""
    tables: list[dict[tuple, Counter]] = [defaultdict(Counter) for _ in range(k_max + 1)]
    for row, y in zip(cat_train, y_train):
        for m in range(1, k_max + 1):
            key = tuple(int(x) for x in row[-m:])
            tables[m][key][int(y)] += 1
    global_top = Counter(y_train).most_common(1)[0][0]

    preds = np.empty(len(cat_val), dtype=np.int64)
    for i, row in enumerate(cat_val):
        chosen = None
        for m in range(k_max, 0, -1):
            key = tuple(int(x) for x in row[-m:])
            ctr = tables[m].get(key)
            if ctr:
                chosen = ctr.most_common(1)[0][0]
                break
        preds[i] = chosen if chosen is not None else global_top
    return preds


def run(state: str) -> dict:
    cat_seq, y, uid = _load(state)
    print(f"[{state}] rows={len(y)}")
    sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)
    Ks = [1, 3, 5, 7, 9]
    fold_metrics = {f"k{k}": {"acc1": [], "f1": []} for k in Ks}

    for fold_idx, (tr, va) in enumerate(sgkf.split(np.zeros(len(y)), y, groups=uid)):
        cat_tr, cat_va = cat_seq[tr], cat_seq[va]
        y_tr, y_va = y[tr], y[va]
        for k in Ks:
            preds = _markov_k_predict(cat_tr, y_tr, cat_va, k_max=k)
            acc = float(np.mean(preds == y_va))
            f1 = f1_score(y_va, preds, average="macro", zero_division=0)
            fold_metrics[f"k{k}"]["acc1"].append(acc)
            fold_metrics[f"k{k}"]["f1"].append(f1)
        msg = " ".join(f"k{k}_F1={fold_metrics[f'k{k}']['f1'][-1]:.4f}" for k in Ks)
        print(f"  fold {fold_idx}: {msg}")

    out = {}
    for k in Ks:
        a = fold_metrics[f"k{k}"]["acc1"]
        f = fold_metrics[f"k{k}"]["f1"]
        out[f"k{k}"] = {
            "acc1_mean": float(np.mean(a) * 100), "acc1_std": float(np.std(a) * 100),
            "macro_f1_mean": float(np.mean(f) * 100), "macro_f1_std": float(np.std(f) * 100),
        }
    print(f"[{state}] AGGREGATE:", json.dumps(out, indent=2))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    args = p.parse_args()
    out = run(args.state)
    out_path = Path("docs/results/P0/simple_baselines") / args.state / "next_category_markov_kstep.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"saved → {out_path}")


if __name__ == "__main__":
    main()
