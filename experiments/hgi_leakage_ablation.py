"""HGI leakage ablation driver.

Runs four arms sequentially on Alabama, 1 fold, seed 42, HGI-only:
    baseline           : le_lambda=1e-8, hard_neg_prob=0.25 (current defaults)
    A_no_hierarchy     : le_lambda=0.0,  hard_neg_prob=0.25
    B_uniform_negs     : le_lambda=1e-8, hard_neg_prob=0.0
    AB_both            : le_lambda=0.0,  hard_neg_prob=0.0

Each arm:
  1. Rebuilds POI2Vec → HGI → category/next inputs with arm-specific flags.
  2. Archives the resulting embeddings.parquet to
     docs/archive/fusion-study/results/P0/leakage_ablation/alabama/<arm>/.
  3. Runs scripts/train.py with --folds-path pinned to the frozen
     alabama/hgi fold indices so paired comparison survives across arms.
  4. Captures the MTL results directory produced by that run.

Usage:
    python scripts/hgi_leakage_ablation.py [--arms baseline,A,B,AB]
"""

from __future__ import annotations

import argparse
import json
import os
import pickle as pkl
import shutil
import subprocess
import sys
import traceback
from argparse import Namespace
from datetime import datetime
from pathlib import Path

# Resolve repo root and add src/ + research/ to sys.path so we can import
# the HGI pipeline functions directly (mirrors pipelines/embedding/hgi.pipe.py).
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
RESEARCH = ROOT / "research"
for _p in (SRC, RESEARCH):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from configs.model import InputsConfig  # noqa: E402
from configs.paths import EmbeddingEngine, IoPaths, Resources  # noqa: E402
from data.inputs.builders import (  # noqa: E402
    generate_category_input,
    generate_next_input_from_poi,
)
from embeddings.hgi.hgi import train_hgi  # noqa: E402
from embeddings.hgi.poi2vec import train_poi2vec  # noqa: E402
from embeddings.hgi.preprocess import preprocess_hgi  # noqa: E402

STATE = "Alabama"
STATE_LOWER = "alabama"
SEED = 42
FOLDS = 1

_STATE_RESOURCES = {
    "Alabama": "TL_AL",
    "Arizona": "TL_AZ",
    "California": "TL_CA",
    "Florida": "TL_FL",
    "Georgia": "TL_GA",
    "Texas": "TL_TX",
}


def _configure_state(state: str) -> None:
    """Reconfigure module-level paths for a different state.

    Called after CLI parsing so --state can override the hardcoded Alabama
    default. Mutates STATE, STATE_LOWER, ARCHIVE_ROOT, FROZEN_FOLDS,
    HGI_CONFIG.shapefile in place.
    """
    global STATE, STATE_LOWER, ARCHIVE_ROOT, FROZEN_FOLDS, HGI_CONFIG
    STATE = state
    STATE_LOWER = state.lower()
    ARCHIVE_ROOT = ROOT / f"docs/archive/fusion-study/results/P0/leakage_ablation/{STATE_LOWER}"
    FROZEN_FOLDS = ROOT / f"output/hgi/{STATE_LOWER}/folds/fold_indices_mtl.pt"
    HGI_CONFIG.shapefile = str(getattr(Resources, _STATE_RESOURCES[state]))


ARCHIVE_ROOT = ROOT / "docs/archive/fusion-study/results/P0/leakage_ablation/alabama"
FROZEN_FOLDS = ROOT / "output/hgi/alabama/folds/fold_indices_mtl.pt"

ARMS = [
    {"name": "baseline",       "le_lambda": 1e-8, "hard_neg_prob": 0.25, "shuffle_fclass_seed": None},
    {"name": "A_no_hierarchy", "le_lambda": 0.0,  "hard_neg_prob": 0.25, "shuffle_fclass_seed": None},
    {"name": "B_uniform_negs", "le_lambda": 1e-8, "hard_neg_prob": 0.0,  "shuffle_fclass_seed": None},
    {"name": "AB_both",        "le_lambda": 0.0,  "hard_neg_prob": 0.0,  "shuffle_fclass_seed": None},
    # Arm C: break the fclass→category deterministic lookup. fclass is
    # permuted across POIs; category stays intact. Tests whether the
    # Category task is actually learning spatial structure or just
    # performing an fclass lookup.
    {"name": "C_fclass_shuffle", "le_lambda": 1e-8, "hard_neg_prob": 0.25, "shuffle_fclass_seed": SEED},
]

HGI_CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,         # 64
    alpha=0.5,
    attention_head=4,
    lr=0.006,
    gamma=1.0,
    max_norm=0.9,
    epoch=2000,
    warmup_period=40,
    poi2vec_epochs=100,
    force_preprocess=True,
    cross_region_weight=0.7,
    device="cpu",
    shapefile=str(Resources.TL_AL),
)


def _seed_everything(seed: int) -> None:
    import random

    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def _results_dir() -> Path:
    return ROOT / "results" / "hgi" / STATE_LOWER


def _snapshot_results_dir() -> set[str]:
    rd = _results_dir()
    if not rd.exists():
        return set()
    return {p.name for p in rd.iterdir() if p.is_dir()}


def run_embedding_arm(arm: dict) -> None:
    _seed_everything(SEED)
    shuffle_seed = arm.get("shuffle_fclass_seed")

    # Phase 3a: Delaunay graph (no embeddings yet)
    preprocess_hgi(
        city=STATE,
        city_shapefile=HGI_CONFIG.shapefile,
        poi_emb_path=None,
        cross_region_weight=HGI_CONFIG.cross_region_weight,
        shuffle_fclass_seed=shuffle_seed,
    )

    # Phase 3b-d: POI2Vec with arm-specific le_lambda
    poi_emb_path = train_poi2vec(
        city=STATE,
        epochs=HGI_CONFIG.poi2vec_epochs,
        embedding_dim=HGI_CONFIG.dim,
        device="cpu",
        le_lambda=arm["le_lambda"],
    )

    # Phase 4: rebuild graph with POI2Vec features.
    # CRUCIAL: pass the same shuffle_fclass_seed so Phase 4's
    # coarse_region_similarity uses the same shuffled fclass as Phase 3a
    # (and as POI2Vec saw via pois.csv). Otherwise Phase 4 re-reads the
    # raw parquet and rebuilds region similarity on UNshuffled fclass,
    # leaking the real category geography back in.
    data = preprocess_hgi(
        city=STATE,
        city_shapefile=HGI_CONFIG.shapefile,
        poi_emb_path=str(poi_emb_path),
        cross_region_weight=HGI_CONFIG.cross_region_weight,
        shuffle_fclass_seed=shuffle_seed,
    )
    graph_data_file = IoPaths.HGI.get_graph_data_file(STATE)
    graph_data_file.parent.mkdir(parents=True, exist_ok=True)
    with open(graph_data_file, "wb") as f:
        pkl.dump(data, f)

    # Phase 5: HGI training with arm-specific hard_neg_prob
    hgi_args = Namespace(**{**vars(HGI_CONFIG), "hard_neg_prob": arm["hard_neg_prob"]})
    train_hgi(STATE, hgi_args)

    # Downstream inputs (category + next)
    generate_category_input(STATE, EmbeddingEngine.HGI)
    generate_next_input_from_poi(STATE, EmbeddingEngine.HGI)


def archive_embeddings(arm_name: str) -> Path:
    arm_dir = ARCHIVE_ROOT / arm_name
    arm_dir.mkdir(parents=True, exist_ok=True)
    src = IoPaths.get_embedd(STATE, EmbeddingEngine.HGI)
    dst = arm_dir / "embeddings.parquet"
    shutil.copy2(src, dst)
    # Also archive POI2Vec fclass embeddings for post-hoc analysis
    fclass_src = IoPaths.HGI.get_output_dir(STATE) / f"poi2vec_fclass_embeddings_{STATE}.pt"
    if fclass_src.exists():
        shutil.copy2(fclass_src, arm_dir / fclass_src.name)
    return arm_dir


def run_mtl_arm(arm: dict, arm_dir: Path) -> tuple[int, Path | None]:
    # IMPORTANT: do NOT pass --folds-path. The frozen file at
    # output/hgi/alabama/folds/fold_indices_mtl.pt bakes in the feature
    # tensors from the pre-ablation embeddings, which would silently short-
    # circuit the ablation. Use --no-folds-cache so train.py rebuilds
    # dataloaders from the current input parquets. Fold indices remain
    # identical across arms: StratifiedGroupKFold(seed=42) over userids,
    # and input row ordering is embedding-independent.
    before = _snapshot_results_dir()

    cmd = [
        sys.executable, str(ROOT / "scripts/train.py"),
        "--task", "mtl",
        "--state", STATE_LOWER,
        "--engine", "hgi",
        "--model", "mtlnet_dselectk",
        "--model-param", "num_experts=4",
        "--model-param", "num_selectors=2",
        "--model-param", "temperature=0.5",
        "--mtl-loss", "aligned_mtl",
        "--gradient-accumulation-steps", "1",
        "--embedding-dim", "64",
        "--seed", str(SEED),
        "--folds", str(FOLDS),
        "--no-folds-cache",
    ]

    log_path = arm_dir / "mtl_training.log"
    with open(log_path, "w") as f:
        f.write(f"CMD: {' '.join(cmd)}\n")
        f.write(f"CWD: {ROOT}\n\n")
        f.flush()
        proc = subprocess.run(cmd, cwd=str(ROOT), stdout=f, stderr=subprocess.STDOUT)

    after = _snapshot_results_dir()
    new_dirs = sorted(after - before)
    if not new_dirs:
        return proc.returncode, None

    # Take the latest new directory (scripts/train.py names with timestamp)
    latest = max(new_dirs)
    result_src = _results_dir() / latest
    result_dst = arm_dir / "mtl_results"
    if result_dst.exists():
        shutil.rmtree(result_dst)
    shutil.copytree(result_src, result_dst)
    return proc.returncode, result_dst


def summarize_arm(arm_name: str, arm_dir: Path) -> dict:
    """Pull joint/category/next F1 from the fold summary CSV or JSON."""
    result_dir = arm_dir / "mtl_results"
    summary = {"arm": arm_name}
    if not result_dir.exists():
        summary["error"] = "no mtl_results directory"
        return summary

    # Look for a summary JSON (MLHistory typically writes one)
    for candidate in ("summary.json", "fold_summary.json", "metrics.json"):
        p = result_dir / candidate
        if p.exists():
            try:
                summary["summary_file"] = str(p.relative_to(ROOT))
                summary["summary"] = json.loads(p.read_text())
                break
            except Exception as exc:
                summary["summary_file_error"] = str(exc)

    # Look for fold CSVs
    csvs = sorted(result_dir.glob("*.csv"))
    if csvs:
        summary["csv_files"] = [str(p.relative_to(ROOT)) for p in csvs]

    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--arms",
        default="baseline,A_no_hierarchy,B_uniform_negs,AB_both",
        help="Comma-separated arm names to run.",
    )
    ap.add_argument("--skip-embedding", action="store_true",
                    help="Skip embedding training; only run MTL. Useful for re-summarizing.")
    ap.add_argument("--restore-from-archive", action="store_true",
                    help="Before the MTL step, copy each arm's archived embeddings.parquet "
                         "back to the canonical HGI output path and regenerate the MTL "
                         "inputs. Implies --skip-embedding. Used when the embedding step "
                         "already completed but the MTL step needs to rerun.")
    ap.add_argument("--state", default="Alabama", choices=list(_STATE_RESOURCES.keys()),
                    help="State to run the ablation on. Resources + shapefile are "
                         "resolved from configs.paths.Resources.")
    args = ap.parse_args()

    _configure_state(args.state)

    requested = set(args.arms.split(","))
    selected_arms = [a for a in ARMS if a["name"] in requested]
    if not selected_arms:
        sys.exit(f"No matching arms. Available: {[a['name'] for a in ARMS]}")

    ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
    print(f"State: {STATE} (archive: {ARCHIVE_ROOT.relative_to(ROOT)})", flush=True)

    run_log = []
    t_start = datetime.now()

    for arm in selected_arms:
        print(f"\n{'=' * 80}\nARM: {arm['name']}\n"
              f"  le_lambda={arm['le_lambda']}, hard_neg_prob={arm['hard_neg_prob']}\n"
              f"{'=' * 80}", flush=True)
        t0 = datetime.now()
        entry = {"arm": arm["name"], "start": t0.isoformat(), **arm}
        try:
            if args.restore_from_archive:
                # Copy arm's archived embeddings back to canonical, then
                # regenerate MTL inputs so they pick up the arm's values.
                arm_dir = ARCHIVE_ROOT / arm["name"]
                src = arm_dir / "embeddings.parquet"
                if not src.exists():
                    raise FileNotFoundError(f"no archived embeddings at {src}")
                dst = IoPaths.get_embedd(STATE, EmbeddingEngine.HGI)
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"  restored canonical <- {src.relative_to(ROOT)}", flush=True)
                generate_category_input(STATE, EmbeddingEngine.HGI)
                generate_next_input_from_poi(STATE, EmbeddingEngine.HGI)
            elif not args.skip_embedding:
                run_embedding_arm(arm)
                archive_embeddings(arm["name"])
            arm_dir = ARCHIVE_ROOT / arm["name"]
            rc, result_dst = run_mtl_arm(arm, arm_dir)
            entry["mtl_return_code"] = rc
            entry["mtl_results"] = str(result_dst.relative_to(ROOT)) if result_dst else None
            entry.update(summarize_arm(arm["name"], arm_dir))
        except Exception as exc:
            entry["error"] = str(exc)
            entry["traceback"] = traceback.format_exc()
            print(f"  FAILED: {exc}", flush=True)
        t1 = datetime.now()
        entry["end"] = t1.isoformat()
        entry["wall_seconds"] = (t1 - t0).total_seconds()
        run_log.append(entry)
        print(f"  wall={t1 - t0}", flush=True)

    t_end = datetime.now()
    run_log_path = ARCHIVE_ROOT / "run_log.json"
    run_log_path.write_text(json.dumps({
        "started": t_start.isoformat(),
        "ended": t_end.isoformat(),
        "total_wall_seconds": (t_end - t_start).total_seconds(),
        "seed": SEED,
        "folds": FOLDS,
        "state": STATE,
        "frozen_folds": str(FROZEN_FOLDS.relative_to(ROOT)),
        "arms": run_log,
    }, indent=2, default=str))
    print(f"\nRun log: {run_log_path}", flush=True)


if __name__ == "__main__":
    main()
