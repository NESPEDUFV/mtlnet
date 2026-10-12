#!/usr/bin/env python3
"""
poi2vec_epochs ablation for HGI embeddings — Alabama, next head only.

Protocol:
  1. Fixed: state=Alabama, w_r=0.7 (swept-optimal), task=next, 3f25e.
  2. Sweep poi2vec_epochs ∈ {25, 50, 75, 100, 150, 200}.
  3. Each point uses an isolated city alias (Alabama_ep25, etc.) so parallel
     workers never clobber each other's output/hgi/ or results/ directories.
  4. Checkin symlinks are created once and cleaned up on exit.
  5. MAX_WORKERS controls parallelism; use 2 or 3 depending on RAM.

Usage:
    cd "/Volumes/Vitor's SSD/ingred"
    source .venv/bin/activate
    HGI_NUM_THREADS=4 PYTHONPATH=src:research python scripts/run_poi2vec_ablation.py
    HGI_NUM_THREADS=4 PYTHONPATH=src:research python scripts/run_poi2vec_ablation.py --workers 2
    HGI_NUM_THREADS=4 PYTHONPATH=src:research python scripts/run_poi2vec_ablation.py --grid 25 50 75 --workers 3
"""

import argparse
import atexit
import json
import logging
import os
import pickle as pkl
import shutil
import subprocess
import sys
from argparse import Namespace
from concurrent.futures import ProcessPoolExecutor, as_completed
from copy import copy
from datetime import datetime
from pathlib import Path

# ── Path bootstrap ─────────────────────────────────────────────────────────────
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

import torch

from configs.model import InputsConfig
from configs.paths import DATA_ROOT, EmbeddingEngine, IoPaths, Resources
from data.inputs.builders import generate_next_input_from_poi
from embeddings.hgi.hgi import train_hgi
from embeddings.hgi.poi2vec import train_poi2vec
from embeddings.hgi.preprocess import preprocess_hgi

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("poi2vec_ablation")

# ── Constants ──────────────────────────────────────────────────────────────────
STATE = "Alabama"
SHAPEFILE = Resources.TL_AL
WR = 0.7
FOLDS = 3
EPOCHS = 25
TASK = "next"
MAX_WORKERS = 3

DEFAULT_GRID = [25, 50, 75, 100, 150, 200]

BASE_HGI_CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    alpha=0.5,
    attention_head=4,
    lr=0.006,
    gamma=1.0,
    max_norm=0.9,
    epoch=2000,
    warmup_period=40,
    force_preprocess=True,
    device="cpu",
    shapefile=SHAPEFILE,
    cross_region_weight=WR,
)

RESULTS_SAVE = _root / "results_save"
DRY_RUN = False

# Track created symlinks for cleanup
_CREATED_SYMLINKS: list[Path] = []


# ── Isolation helpers ──────────────────────────────────────────────────────────

def city_alias(epochs: int) -> str:
    """Alabama + ep suffix → isolated output dirs per ablation point."""
    return f"Alabama_ep{epochs}"


def ensure_checkin_symlink(epochs: int) -> None:
    """
    Create data/checkins/Alabama_ep{N}.parquet → Alabama.parquet symlink
    so IoPaths.load_city(city_alias) resolves to the real checkin data.
    """
    src = DATA_ROOT / "checkins" / "Alabama.parquet"
    dst = DATA_ROOT / "checkins" / f"Alabama_ep{epochs}.parquet"
    if not dst.exists():
        dst.symlink_to(src)
        _CREATED_SYMLINKS.append(dst)


def cleanup_symlinks() -> None:
    for p in _CREATED_SYMLINKS:
        try:
            p.unlink(missing_ok=True)
        except Exception:
            pass


# ── Helpers ────────────────────────────────────────────────────────────────────

def ep_tag(epochs: int) -> str:
    return f"ep{epochs}"


def snapshot_point(epochs: int, ts: str) -> Path:
    tag = ep_tag(epochs)
    alias = city_alias(epochs)
    dest = RESULTS_SAVE / f"{STATE}_poi2vec_{tag}_3f25e_{ts}"
    dest.mkdir(parents=True, exist_ok=True)

    hgi_src = IoPaths.HGI.get_state_dir(alias)
    inp_src = hgi_src / "input"
    res_src = IoPaths.get_results_dir(alias, EmbeddingEngine.HGI)

    if hgi_src.exists():
        shutil.copytree(hgi_src, dest / "hgi", dirs_exist_ok=True)
        log.info(f"  snapshot: HGI output → {dest / 'hgi'}")
    if inp_src.exists():
        shutil.copytree(inp_src, dest / "inputs", dirs_exist_ok=True)
        log.info(f"  snapshot: inputs     → {dest / 'inputs'}")
    if res_src.exists():
        shutil.copytree(res_src, dest / "results", dirs_exist_ok=True)
        log.info(f"  snapshot: results    → {dest / 'results'}")
    return dest


def find_latest_summary(epochs: int) -> dict | None:
    alias = city_alias(epochs)
    res_dir = IoPaths.get_results_dir(alias, EmbeddingEngine.HGI)
    summaries = sorted(res_dir.rglob("full_summary.json"), key=lambda p: p.stat().st_mtime)
    if not summaries:
        return None
    with open(summaries[-1]) as f:
        return json.load(f)


def read_next_f1(summary: dict) -> tuple[float, float]:
    nxt = summary.get("next", {}).get("f1", {})
    return float(nxt.get("mean", 0.0)), float(nxt.get("std", 0.0))


# ── Per-point pipeline (runs in worker process) ────────────────────────────────

def run_point(poi2vec_epochs: int) -> tuple[float, float] | None:
    """
    Full isolated pipeline for one poi2vec_epochs value.
    Each point uses city_alias as city name → separate output/hgi/ and results/ dirs.
    Returns (next_f1_mean, next_f1_std) or None on failure.
    """
    # Re-bootstrap path in subprocess
    sys.path.insert(0, str(_root / "src"))
    sys.path.insert(0, str(_root / "research"))

    import logging as _logging
    _logging.basicConfig(
        level=_logging.INFO,
        format="%(asctime)s  %(levelname)-7s  [ep%(poi2vec_epochs)s] %(message)s"
              .replace("%(poi2vec_epochs)s", str(poi2vec_epochs)),
        datefmt="%H:%M:%S",
        force=True,
    )
    _log = _logging.getLogger(f"ablation.ep{poi2vec_epochs}")

    alias = city_alias(poi2vec_epochs)
    ts = datetime.now().strftime("%Y%m%dT%H%M")

    _log.info(f"START: {alias}  poi2vec_epochs={poi2vec_epochs}")

    if DRY_RUN:
        return (0.5 + poi2vec_epochs / 1000, 0.01)

    try:
        cfg = copy(BASE_HGI_CONFIG)
        cfg.poi2vec_epochs = poi2vec_epochs

        # Step 1: Delaunay graph (w_r fixed, but each alias needs its own temp dir)
        _log.info(f"[1/5] preprocess (no embeddings): {alias}")
        preprocess_hgi(
            city=alias,
            city_shapefile=str(SHAPEFILE),
            poi_emb_path=None,
            cta_file=None,
            cross_region_weight=WR,
        )

        # Step 2: POI2Vec
        _log.info(f"[2/5] POI2Vec: {alias}  epochs={poi2vec_epochs}")
        poi_emb_path = train_poi2vec(
            city=alias,
            epochs=poi2vec_epochs,
            embedding_dim=cfg.dim,
            device="cuda" if torch.cuda.is_available() else "cpu",
        )

        # Step 3: Preprocess with embeddings
        _log.info(f"[3/5] preprocess (with embeddings): {alias}")
        data = preprocess_hgi(
            city=alias,
            city_shapefile=str(SHAPEFILE),
            poi_emb_path=str(poi_emb_path),
            cta_file=None,
            cross_region_weight=WR,
        )
        gf = IoPaths.HGI.get_graph_data_file(alias)
        gf.parent.mkdir(parents=True, exist_ok=True)
        with open(gf, "wb") as f:
            pkl.dump(data, f)

        # Step 4: HGI training
        _log.info(f"[4/5] HGI training: {alias}")
        cfg.shapefile = SHAPEFILE
        train_hgi(alias, cfg)

        # Step 5: Generate inputs (next only)
        _log.info(f"[5/5] generating inputs: {alias}")
        generate_next_input_from_poi(alias, EmbeddingEngine.HGI)

        # Step 6: Train next head
        _log.info(f"[6/6] next-head training: {alias} {FOLDS}f{EPOCHS}e")
        cmd = [
            sys.executable, str(_root / "scripts" / "train.py"),
            "--task", TASK,
            "--state", alias.lower(),
            "--engine", "hgi",
            "--folds", str(FOLDS),
            "--epochs", str(EPOCHS),
        ]
        env = {**os.environ, "PYTHONPATH": f"{_root / 'src'}:{_root / 'research'}"}
        result = subprocess.run(cmd, env=env, cwd=str(_root))
        if result.returncode != 0:
            _log.error(f"Next-head training failed: {alias}")
            return None

        snapshot_point(poi2vec_epochs, ts)

        summary = find_latest_summary(poi2vec_epochs)
        if summary is None:
            _log.error(f"No summary found: {alias}")
            return None

        mean_f1, std_f1 = read_next_f1(summary)
        _log.info(f"  → Next F1: {mean_f1:.4f} ± {std_f1:.4f}")
        return mean_f1, std_f1

    except Exception as e:
        import traceback
        _logging.getLogger(f"ablation.ep{poi2vec_epochs}").error(
            f"Exception: {e}\n{traceback.format_exc()}"
        )
        return None


# ── Decision rule ──────────────────────────────────────────────────────────────

def apply_decision(results: dict[int, tuple[float, float]]) -> int | None:
    valid = {ep: (m, s) for ep, (m, s) in results.items() if m > 0}
    if not valid:
        return None
    ranked = sorted(valid.items(), key=lambda x: x[1][0], reverse=True)
    best_ep, (best_mean, _) = ranked[0]
    if len(ranked) < 2:
        return best_ep
    _, (second_mean, second_std) = ranked[1]
    gap = best_mean - second_mean
    if gap >= second_std:
        log.info(f"  [DECISION] pin to poi2vec_epochs={best_ep} "
                 f"(gap={gap:.4f} ≥ 1σ={second_std:.4f})")
        return best_ep
    log.info(f"  [DECISION] INCONCLUSIVE (gap={gap:.4f} < 1σ={second_std:.4f}) "
             "— keep default (100)")
    return None


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="poi2vec_epochs ablation — Alabama, next head, parallel workers"
    )
    parser.add_argument("--grid", nargs="+", type=int, metavar="EP",
                        help=f"poi2vec epoch values (default: {DEFAULT_GRID})")
    parser.add_argument("--workers", type=int, default=MAX_WORKERS,
                        help="Parallel workers (default: 3; use 2 if RAM-constrained)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    global DRY_RUN
    DRY_RUN = args.dry_run
    grid = args.grid or DEFAULT_GRID
    workers = args.workers

    log.info(f"poi2vec ablation  |  state={STATE}  task={TASK}  w_r={WR}")
    log.info(f"Protocol: {FOLDS}f{EPOCHS}e  |  grid: {grid}  |  workers: {workers}")
    if DRY_RUN:
        log.info("DRY RUN — nothing will execute")

    # Create checkin symlinks once (main process only)
    if not DRY_RUN:
        atexit.register(cleanup_symlinks)
        for ep in grid:
            ensure_checkin_symlink(ep)
        log.info(f"Checkin symlinks ready for {len(grid)} aliases")

    # Run points in parallel (MAX_WORKERS at a time)
    results: dict[int, tuple[float, float]] = {}

    if workers == 1 or DRY_RUN:
        for ep in grid:
            res = run_point(ep)
            if res is not None:
                results[ep] = res
                log.info(f"  ep{ep}: Next F1 = {res[0]:.4f} ± {res[1]:.4f}")
            else:
                log.warning(f"  ep{ep}: FAILED — skipping")
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(run_point, ep): ep for ep in grid}
            for future in as_completed(futures):
                ep = futures[future]
                try:
                    res = future.result()
                except Exception as e:
                    log.error(f"  ep{ep} raised: {e}")
                    res = None
                if res is not None:
                    results[ep] = res
                    log.info(f"  ep{ep} done: Next F1 = {res[0]:.4f} ± {res[1]:.4f}")
                else:
                    log.warning(f"  ep{ep}: FAILED")

    # Summary
    log.info("\n" + "="*60)
    log.info("  ABLATION RESULTS SUMMARY")
    log.info("="*60)
    log.info(f"{'poi2vec_epochs':<16} {'Next F1 mean':>14} {'± std':>8}  Decision")
    log.info("-"*60)

    best_ep = apply_decision(results)
    for ep in sorted(grid):
        if ep not in results:
            log.info(f"{ep:<16} {'FAILED':>14}")
            continue
        mean_f1, std_f1 = results[ep]
        marker = " ← BEST" if ep == best_ep else ""
        log.info(f"{ep:<16} {mean_f1:>14.4f} {f'±{std_f1:.4f}':>8}{marker}")

    log.info("\n" + "="*60)
    log.info("  RECOMMENDATION")
    log.info("="*60)
    if best_ep is not None:
        log.info(f"  Set poi2vec_epochs={best_ep} in BASE_HGI_CONFIG and hgi.pipe.py CONFIG")
    else:
        log.info("  Inconclusive — keep poi2vec_epochs=100")
    log.info("\nDone.")


if __name__ == "__main__":
    main()
