"""Freeze CV fold indices once per (task, state, engine) combination.

Writes a deterministic `fold_indices_{task}.pt` under
`output/{engine}/{state}/folds/` plus a companion `.meta.json` that records
the sklearn version, input parquet SHA-256 signatures, and fold sizes.

Why this exists
---------------
Every ablation test in P1-P6 is a paired comparison against other tests on
the same (state, engine). Paired statistical tests (Wilcoxon signed-rank,
paired-t) require byte-identical train/val splits across the models being
compared (Dietterich 1998; Raschka 2018). `StratifiedGroupKFold` is
deterministic given a fixed `random_state`, but splits can drift silently
across sklearn versions or if the input parquet is regenerated. Freezing
indices once and loading them everywhere removes both risks.

See the study phases/P0_preparation.md §P0.8 for the methodological
rationale.

Usage
-----
    # One (state, engine, task):
    python scripts/study/freeze_folds.py --state alabama --engine fusion --task mtl

    # Minimum P0.8 set (AL + AZ × {dgi, hgi, fusion} × mtl):
    python scripts/study/freeze_folds.py --default-set

    # Re-freeze even if cache already exists:
    python scripts/study/freeze_folds.py --state alabama --engine fusion --task mtl --force

After freezing, `scripts/train.py` auto-loads the canonical cache. No
further action is required on downstream test configs.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Make src importable when invoked directly
_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (_REPO_ROOT, _REPO_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import sklearn
import torch
from configs.experiment import DatasetSignature
from configs.paths import EmbeddingEngine, IoPaths
from data.folds import FoldCreator, TaskType

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
logger = logging.getLogger("freeze_folds")

STUDY_ROLLUP_PATH = _REPO_ROOT / "docs" / "studies" / "fusion" / "results" / "P0" / "folds" / "frozen.json"

_TASK_TYPES: dict[str, TaskType] = {
    "mtl": TaskType.MTL,
    "category": TaskType.CATEGORY,
    "next": TaskType.NEXT,
}

# P0.8 default coverage — the minimum set required to unblock P1.
_DEFAULT_SET: list[tuple[str, str, str]] = [
    ("alabama", "dgi", "mtl"),
    ("alabama", "hgi", "mtl"),
    ("alabama", "fusion", "mtl"),
    ("arizona", "dgi", "mtl"),
    ("arizona", "hgi", "mtl"),
    ("arizona", "fusion", "mtl"),
]


def _input_signatures(state: str, engine: EmbeddingEngine, task: str) -> dict[str, dict]:
    """SHA-256 of the input parquets this task depends on."""
    sigs: dict[str, dict] = {}
    if task in ("mtl", "category"):
        cat = IoPaths.get_category(state, engine)
        if cat.exists():
            sigs["category.parquet"] = dataclasses.asdict(DatasetSignature.from_path(cat))
    if task in ("mtl", "next"):
        nxt = IoPaths.get_next(state, engine)
        if nxt.exists():
            sigs["next.parquet"] = dataclasses.asdict(DatasetSignature.from_path(nxt))
    return sigs


def _serialize_folds(creator: FoldCreator) -> dict[str, Any]:
    """Match the format produced by src/data/folds.py::save_folds, but
    without the timestamped filename (we want a stable path)."""
    return {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "config": creator._config.__dict__,
        "task_tensors": {
            t.value: {"x": td.x, "y": td.y}
            for t, td in creator._task_tensors.items()
        },
        "fold_indices": {
            t.value: [
                {"fold_idx": idx.fold_idx, "train": idx.train_indices, "val": idx.val_indices}
                for idx in indices
            ]
            for t, indices in creator._fold_indices.items()
        },
    }


def freeze_one(state: str, engine_name: str, task: str, seed: int, force: bool) -> dict:
    """Freeze folds for one (state, engine, task). Returns manifest entry."""
    engine = EmbeddingEngine(engine_name)
    task_type = _TASK_TYPES[task]

    folds_dir = IoPaths.get_folds_dir(state, engine)
    folds_dir.mkdir(parents=True, exist_ok=True)
    fold_file = folds_dir / f"fold_indices_{task}.pt"
    meta_file = folds_dir / f"fold_indices_{task}.meta.json"

    if fold_file.exists() and not force:
        logger.info("[skip] %s already frozen at %s (pass --force to overwrite)", task, fold_file)
        existing_meta = json.loads(meta_file.read_text()) if meta_file.exists() else {}
        return {"status": "skipped", "state": state, "engine": engine_name, "task": task,
                "fold_file": str(fold_file), "meta": existing_meta}

    logger.info("[freeze] state=%s engine=%s task=%s seed=%d", state, engine_name, task, seed)
    sigs = _input_signatures(state, engine, task)
    if task in ("mtl", "category") and "category.parquet" not in sigs:
        raise SystemExit(f"missing category.parquet for {state}/{engine_name}")
    if task in ("mtl", "next") and "next.parquet" not in sigs:
        raise SystemExit(f"missing next.parquet for {state}/{engine_name}")

    # NOTE: we pass a batch_size here just to satisfy FoldCreator; downstream
    # runs override it via rebuild_dataloaders(batch_size=...).
    creator = FoldCreator(
        task_type=task_type,
        n_splits=5,
        batch_size=2048,
        seed=seed,
        use_weighted_sampling=False,
    )
    creator.create_folds(state, engine)

    save_dict = _serialize_folds(creator)
    torch.save(save_dict, fold_file)

    fold_sizes = {
        t_name: [
            {"fold_idx": entry["fold_idx"], "train": int(len(entry["train"])), "val": int(len(entry["val"]))}
            for entry in entries
        ]
        for t_name, entries in save_dict["fold_indices"].items()
    }

    # Store repo-relative paths in signatures so the meta is portable.
    rel_sigs = {}
    for name, sig in sigs.items():
        sig = dict(sig)
        try:
            sig["path"] = Path(sig["path"]).resolve().relative_to(_REPO_ROOT).as_posix()
        except ValueError:
            pass  # path outside repo, leave as-is
        rel_sigs[name] = sig

    meta = {
        "schema_version": 1,
        "state": state,
        "engine": engine_name,
        "task": task,
        "seed": seed,
        "n_splits": 5,
        "sklearn_version": sklearn.__version__,
        "torch_version": torch.__version__,
        "created_at": save_dict["created_at"],
        "inputs_signatures": rel_sigs,
        "fold_sizes": fold_sizes,
        "fold_file": fold_file.name,
    }
    meta_file.write_text(json.dumps(meta, indent=2, default=str))

    logger.info("[freeze] wrote %s (%.1f MB) + %s", fold_file,
                fold_file.stat().st_size / 1e6, meta_file.name)
    rel_fold = fold_file.resolve().relative_to(_REPO_ROOT).as_posix()
    return {"status": "frozen", "state": state, "engine": engine_name, "task": task,
            "fold_file": rel_fold, "meta": meta}


def _update_rollup(results: list[dict]) -> Path:
    STUDY_ROLLUP_PATH.parent.mkdir(parents=True, exist_ok=True)
    existing: dict[str, dict] = {}
    if STUDY_ROLLUP_PATH.exists():
        try:
            existing = {r["key"]: r for r in json.loads(STUDY_ROLLUP_PATH.read_text())["entries"]}
        except (json.JSONDecodeError, KeyError):
            existing = {}
    for r in results:
        key = f"{r['state']}/{r['engine']}/{r['task']}"
        existing[key] = {"key": key, **r}
    rollup = {
        "schema_version": 1,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "entries": sorted(existing.values(), key=lambda e: e["key"]),
    }
    STUDY_ROLLUP_PATH.write_text(json.dumps(rollup, indent=2, default=str))
    return STUDY_ROLLUP_PATH


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="freeze_folds", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--state", type=str, default=None, help="e.g. alabama, arizona, florida")
    p.add_argument("--engine", type=str, default=None, help="e.g. fusion, hgi, dgi")
    p.add_argument("--task", type=str, default="mtl", choices=sorted(_TASK_TYPES.keys()))
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--force", action="store_true", help="Overwrite existing cache")
    p.add_argument("--default-set", action="store_true",
                   help="Freeze the P0.8 minimum: AL+AZ × {dgi,hgi,fusion} × mtl")
    args = p.parse_args(argv)

    if args.default_set:
        jobs = _DEFAULT_SET
    else:
        if args.state is None or args.engine is None:
            p.error("--state and --engine are required unless --default-set is given")
        jobs = [(args.state, args.engine, args.task)]

    results: list[dict] = []
    failed: list[tuple[str, str, str, str]] = []
    for state, engine, task in jobs:
        try:
            results.append(freeze_one(state, engine, task, args.seed, args.force))
        except SystemExit as exc:
            failed.append((state, engine, task, str(exc)))
            logger.error("[fail] %s/%s/%s: %s", state, engine, task, exc)

    rollup_path = _update_rollup(results)
    logger.info("[rollup] %s", rollup_path)

    n_ok = sum(1 for r in results if r["status"] == "frozen")
    n_skip = sum(1 for r in results if r["status"] == "skipped")
    logger.info("Done. frozen=%d skipped=%d failed=%d", n_ok, n_skip, len(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
