"""One-shot: compute macro-F1 for next_category floors (majority + markov_1step + top_k_popular).

The original ``compute_simple_baselines.py`` only stored Acc/MRR. This script
recreates the same StratifiedGroupKFold protocol, runs the floors, and
prints / writes their macro-F1 (top-1 prediction).

Usage::

    PYTHONPATH=src DATA_ROOT=... OUTPUT_DIR=... \\
        python scripts/compute_next_cat_floor_f1.py --state alabama
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
_src = str(_root / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from configs.paths import EmbeddingEngine, IoPaths  # noqa: E402
from configs.model import InputsConfig  # noqa: E402

SLIDE_WINDOW = InputsConfig.SLIDE_WINDOW
N_SPLITS = 5
SEED = 42


def _load(state: str):
    engine = EmbeddingEngine.CHECK2HGI
    next_df = IoPaths.load_next(state, engine)
    userids = next_df["userid"].astype(str).to_numpy()
    from configs.globals import CATEGORIES_MAP
    inv = {v: k for k, v in CATEGORIES_MAP.items()}
    y = next_df["next_category"].map(inv).to_numpy(dtype=np.int64)

    seq_path = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    import pandas as pd
    seq_df = pd.read_parquet(seq_path)
    import pickle as pkl
    with open(IoPaths.CHECK2HGI.get_graph_data_file(state), "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]

    last_col = f"poi_{SLIDE_WINDOW - 1}"
    last_pois_raw = seq_df[last_col].astype(np.int64).to_numpy()
    window_last_pois = np.array(
        [placeid_to_idx.get(int(pid), -1) for pid in last_pois_raw],
        dtype=np.int64,
    )
    return y, userids, window_last_pois


def _markov_top1(lp_train, y_train, lp_val):
    transition = defaultdict(Counter)
    for lp, y in zip(lp_train, y_train):
        if lp >= 0:
            transition[int(lp)][int(y)] += 1
    global_top = Counter(y_train).most_common(1)[0][0]
    preds = []
    for lp in lp_val:
        if int(lp) in transition:
            preds.append(transition[int(lp)].most_common(1)[0][0])
        else:
            preds.append(global_top)
    return np.array(preds, dtype=np.int64)


def run(state: str) -> dict:
    y, uids, lp = _load(state)
    sgkf = StratifiedGroupKFold(n_splits=N_SPLITS, shuffle=True, random_state=SEED)

    fold_f1 = {"majority": [], "top_k_popular_top1": [], "markov_1step": []}
    for fold_idx, (tr, va) in enumerate(sgkf.split(np.zeros(len(y)), y, groups=uids)):
        y_tr, y_va = y[tr], y[va]
        lp_tr, lp_va = lp[tr], lp[va]

        # Majority: predict the train majority class for every val sample.
        maj = Counter(y_tr).most_common(1)[0][0]
        f1_maj = f1_score(y_va, np.full_like(y_va, maj), average="macro", zero_division=0)
        fold_f1["majority"].append(f1_maj)

        # Top-K popular: top-1 prediction is identical to majority.
        fold_f1["top_k_popular_top1"].append(f1_maj)

        # Markov-1step: argmax of P(next | last_poi).
        preds = _markov_top1(lp_tr, y_tr, lp_va)
        f1_mk = f1_score(y_va, preds, average="macro", zero_division=0)
        fold_f1["markov_1step"].append(f1_mk)

        print(f"[{state}] fold {fold_idx}: majority_F1={f1_maj:.4f} markov_F1={f1_mk:.4f}")

    out = {}
    for k, v in fold_f1.items():
        out[f"{k}_f1_mean"] = float(np.mean(v) * 100)
        out[f"{k}_f1_std"] = float(np.std(v) * 100)
    print(f"[{state}] AGGREGATE:", out)
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--state", required=True)
    args = p.parse_args()
    out = run(args.state)
    out_path = Path("docs/results/P0/simple_baselines") / args.state / "next_category_f1.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"saved → {out_path}")


if __name__ == "__main__":
    main()
