"""T0.0 — Freeze the fold partition + record a hashed manifest (mtl_improvement study).

The frozen partition is the IMMUTABLE shared artifact every tier reuses. It is
derived from the SAME code path the trainer + per-fold log_T builder use
(`scripts/compute_region_transition.py::_build_per_fold` ==
`FoldCreator._create_mtl_folds_with_isolation`):

    StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed)
        .split(X_next, y_next, groups=userid)   # via data.folds.load_next_data(CHECK2HGI)

so the manifest is provenance-matched (advisor #1), NOT a re-implementation. The
seeded per-fold log_T on disk (`region_transition_log_seed{S}_fold{N}.pt`) was
built from this exact split, so this partition IS the operative one.

Modes:
    --write   materialize docs/results/mtl_improvement/frozen_folds/{state}_seed{S}.json
              (per-fold train/val userid lists + per-fold + partition hashes)
    --check   recompute the split and HARD-FAIL if the partition hash drifts from
              the frozen manifest (sklearn / data / loader drift guard). Use as a
              preflight before any run that relies on the frozen folds.

Usage::
    .venv/bin/python scripts/mtl_improvement/freeze_folds.py --write \
        --state alabama --state arizona --state florida --seed 0 1 7 100 42
    .venv/bin/python scripts/mtl_improvement/freeze_folds.py --check \
        --state alabama --seed 42
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

import sklearn
from sklearn.model_selection import StratifiedGroupKFold

from configs.paths import EmbeddingEngine
from data.folds import load_next_data

MANIFEST_DIR = REPO / "docs" / "results" / "mtl_improvement" / "frozen_folds"


def _hash_userids(userids) -> str:
    """Order-independent hash of an integer userid set."""
    s = ",".join(str(u) for u in sorted(int(u) for u in userids))
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def _derive_partition(state: str, n_splits: int, seed: int) -> dict:
    """Reproduce the trainer / log_T split EXACTLY (provenance-matched)."""
    X_next, y_next, userids, _ = load_next_data(state, EmbeddingEngine.CHECK2HGI)
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    folds = []
    for fold_idx, (train_idx, val_idx) in enumerate(
        sgkf.split(X_next, y_next, groups=userids), start=1
    ):
        train_u = sorted(int(u) for u in set(userids[train_idx]))
        val_u = sorted(int(u) for u in set(userids[val_idx]))
        folds.append({
            "fold": fold_idx,
            "n_train_rows": int(len(train_idx)),
            "n_val_rows": int(len(val_idx)),
            "n_train_users": len(train_u),
            "n_val_users": len(val_u),
            "train_userid_hash": _hash_userids(train_u),
            "val_userid_hash": _hash_userids(val_u),
            "val_userids": val_u,
            "train_userids": train_u,
        })
    # Partition hash = hash over each fold's val-userid hash (order = fold order).
    part = hashlib.sha256(
        "|".join(f["val_userid_hash"] for f in folds).encode()
    ).hexdigest()[:16]
    return {
        "state": state,
        "seed": int(seed),
        "n_splits": int(n_splits),
        "engine": "check2hgi",
        "loader": "data.folds.load_next_data",
        "split": "StratifiedGroupKFold(shuffle=True, random_state=seed, groups=userid, y=next_category)",
        "sklearn_version": sklearn.__version__,
        "n_samples": int(len(y_next)),
        "n_users": int(len(set(int(u) for u in userids))),
        "partition_hash": part,
        "folds": folds,
    }


def _manifest_path(state: str, seed: int) -> Path:
    return MANIFEST_DIR / f"{state}_seed{seed}.json"


def cmd_write(states, seeds, n_splits):
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    for state in states:
        for seed in seeds:
            man = _derive_partition(state, n_splits, seed)
            p = _manifest_path(state, seed)
            p.write_text(json.dumps(man, indent=2))
            print(f"[write] {p.relative_to(REPO)}  partition_hash={man['partition_hash']}  "
                  f"n_samples={man['n_samples']} n_users={man['n_users']}")


def cmd_check(states, seeds, n_splits):
    bad = 0
    for state in states:
        for seed in seeds:
            p = _manifest_path(state, seed)
            if not p.exists():
                print(f"[check] MISSING manifest {p.relative_to(REPO)} — run --write first")
                bad += 1
                continue
            frozen = json.loads(p.read_text())
            live = _derive_partition(state, n_splits, seed)
            ok = frozen["partition_hash"] == live["partition_hash"]
            tag = "OK " if ok else "DRIFT"
            print(f"[check] {tag} {state} seed={seed}  frozen={frozen['partition_hash']} "
                  f"live={live['partition_hash']}  (sklearn frozen={frozen.get('sklearn_version')} "
                  f"live={live['sklearn_version']})")
            if not ok:
                bad += 1
    if bad:
        print(f"[check] FAIL — {bad} partition(s) drifted or missing")
        sys.exit(1)
    print("[check] all partitions match the frozen manifest")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", action="append", required=True, dest="states")
    ap.add_argument("--seed", type=int, nargs="+", required=True, dest="seeds")
    ap.add_argument("--n-splits", type=int, default=5)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args()
    if args.write:
        cmd_write(args.states, args.seeds, args.n_splits)
    else:
        cmd_check(args.states, args.seeds, args.n_splits)


if __name__ == "__main__":
    main()
