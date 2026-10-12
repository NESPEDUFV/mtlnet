"""Freeze one fold's exact train/validation indices and user lists, once, for every arm to share.

Every paired comparison in this study must run on identical rows. Recomputing the split inside
each script would make that a hope rather than a guarantee, so the split is computed once here and
written to a JSON that carries hashes of both index arrays. Downstream scripts load it and assert
the hashes.

The split reproduces the reported harness: StratifiedGroupKFold(n_splits=5, shuffle=True,
random_state=seed) over the windowed rows of the engine being trained, grouped by user and
stratified by the next-category label (src/data/folds.py:1159 and :1247). Fold numbering is
0-indexed here; the reported logs number folds from 1, so fold 0 here is "fold1" there.

Usage:
    PYTHONPATH=src .venv/bin/python scripts/integrity_v2/freeze_split.py \
        --state alabama --seed 0 --fold 0 \
        --out docs/results/check2hgi_integrity_v2/alabama/split_seed0_fold0.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedGroupKFold

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from configs.paths import EmbeddingEngine, IoPaths  # noqa: E402


def _sha(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument("--engine", default="check2hgi_dk_ovl",
                    help="the windowing the reported runs use")
    ap.add_argument("--out", required=True)
    ap.add_argument("--group-dtype", choices=("str", "int"), default="str",
                    help="dtype of the userid groups passed to StratifiedGroupKFold. 'str' (default, "
                         "unchanged) is what the integrity_v2 study used. 'int' reproduces train.py's "
                         "FoldCreator, which passes the int64 userids from load_next_data: SGKF sorts the "
                         "groups, string order is not integer order, and the two partitions differ "
                         "(measured 2026-10-01, AL/AZ seed 0: 0 of 5 folds equal). Use 'int' for any "
                         "split that must equal the delivered folds.")
    args = ap.parse_args()

    engine = EmbeddingEngine(args.engine)
    nxt = IoPaths.load_next(args.state, engine)
    y = nxt["next_category"].to_numpy()
    groups = (nxt["userid"].astype(str).to_numpy() if args.group_dtype == "str"
              else nxt["userid"].astype(np.int64).to_numpy())

    sgkf = StratifiedGroupKFold(n_splits=args.n_folds, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(np.zeros(len(y)), y, groups=groups))
    train_idx, val_idx = splits[args.fold]
    train_idx = np.sort(train_idx); val_idx = np.sort(val_idx)

    tr_u = np.unique(groups[train_idx]); va_u = np.unique(groups[val_idx])
    assert np.intersect1d(tr_u, va_u).size == 0, "split is not user-disjoint"

    # the graph stores userid as int; carry both so consumers cannot mismatch dtype
    out = {
        "study": "check2hgi_integrity_v2",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "revision": subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                                   capture_output=True, text=True).stdout.strip(),
        "command": " ".join(sys.argv),
        "state": args.state, "seed": args.seed, "fold": args.fold, "n_folds": args.n_folds,
        "engine": args.engine,
        "splitter": "StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed), group=userid, stratify=next_category",
        "group_dtype": args.group_dtype,
        "fold_indexing": "0-indexed here; reported logs number the same fold as fold1",
        "n_rows_total": int(len(y)),
        "n_train_rows": int(train_idx.size), "n_val_rows": int(val_idx.size),
        "n_train_users": int(tr_u.size), "n_val_users": int(va_u.size),
        "train_idx_sha256": _sha(train_idx), "val_idx_sha256": _sha(val_idx),
        "train_users": sorted(int(u) for u in tr_u),
        "val_users": sorted(int(u) for u in va_u),
        "train_idx": train_idx.tolist(), "val_idx": val_idx.tolist(),
    }
    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out))
    print(f"[split] {args.state} seed={args.seed} fold={args.fold}: "
          f"train {train_idx.size} rows / {tr_u.size} users, "
          f"val {val_idx.size} rows / {va_u.size} users -> {outp}")


if __name__ == "__main__":
    main()
