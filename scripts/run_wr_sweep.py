#!/usr/bin/env python3
"""
w_r sweep for Florida, California, Texas (preceded by Alabama calibration).

Protocol (per research/embeddings/hgi/PLAN_wr_per_state_sweep.md):
  1. Calibration: Alabama at w_r ∈ {0.4, 0.7} (2f15e) — Go/No-Go gate.
  2. If 0.7 ≥ 2σ above 0.4 on Cat F1: sweep target states at {0.4, 0.7, 1.0}.
  3. Snapshot artifacts after each point (shared output path gets overwritten).
  4. Apply decision rule and print recommendations.

Usage:
    cd "/Volumes/Vitor's SSD/ingred"
    source .venv/bin/activate
    PYTHONPATH=src:research python scripts/run_wr_sweep.py

Options (edit constants below or pass via env):
    WR_SWEEP_SKIP_CALIBRATION=1   — skip Alabama calibration (e.g. already done)
    WR_SWEEP_DRY_RUN=1            — print what would run, don't execute
"""

import sys
import os
import json
import shutil
import logging
import pickle as pkl
import subprocess
import argparse
from argparse import Namespace
from copy import copy
from datetime import datetime
from pathlib import Path

# ── Path bootstrap ─────────────────────────────────────────────────────────────
_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))

from configs.paths import Resources, EmbeddingEngine, IoPaths
from configs.model import InputsConfig
from data.inputs.builders import generate_category_input, generate_next_input_from_poi
from embeddings.hgi.hgi import train_hgi
from embeddings.hgi.preprocess import preprocess_hgi
from embeddings.hgi.poi2vec import train_poi2vec

import torch

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("wr_sweep")

# ── Constants ──────────────────────────────────────────────────────────────────

SKIP_CALIBRATION = os.environ.get("WR_SWEEP_SKIP_CALIBRATION", "0") == "1"
DRY_RUN = os.environ.get("WR_SWEEP_DRY_RUN", "0") == "1"

# Sweep grid
WR_GRID = [0.4, 0.7, 1.0]

# States to sweep after calibration (user-requested: Florida, California, Texas)
TARGET_STATES = ["Florida", "California", "Texas"]

SHAPEFILES = {
    "Alabama":    Resources.TL_AL,
    "Florida":    Resources.TL_FL,
    "California": Resources.TL_CA,
    "Texas":      Resources.TL_TX,
}

# MTLnet protocol — 3f25e fallback (2f15e failed calibration: gap=0.0717 < 2σ=0.0762)
FOLDS = 3
EPOCHS = 25

# Base HGI config (paper defaults — do NOT reduce epoch/lr/warmup)
BASE_HGI_CONFIG = Namespace(
    dim=InputsConfig.EMBEDDING_DIM,
    alpha=0.5,
    attention_head=4,
    lr=0.006,
    gamma=1.0,
    max_norm=0.9,
    epoch=2000,
    warmup_period=40,
    poi2vec_epochs=100,
    force_preprocess=True,
    device="cpu",
    shapefile=None,
    cross_region_weight=0.7,
)

# Artifacts root
RESULTS_SAVE = _root / "results_save"


# ── Helpers ────────────────────────────────────────────────────────────────────

def wr_tag(wr: float) -> str:
    """0.4 → 'wr04', 0.7 → 'wr07', 1.0 → 'wr10'"""
    return "wr" + f"{wr:.1f}".replace(".", "")


def snapshot(state: str, wr: float, ts: str) -> Path:
    """Copy HGI output + model inputs to results_save/{state}_{tag}_{ts}/."""
    tag = wr_tag(wr)
    dest = RESULTS_SAVE / f"{state}_{tag}_2f15e_{ts}"
    dest.mkdir(parents=True, exist_ok=True)

    hgi_src = IoPaths.HGI.get_state_dir(state)
    inp_src = hgi_src / "input"
    res_src = IoPaths.get_results_dir(state, EmbeddingEngine.HGI)

    if hgi_src.exists():
        shutil.copytree(hgi_src, dest / "hgi", dirs_exist_ok=True)
        log.info(f"  snapshot: HGI output → {dest / 'hgi'}")
    if inp_src.exists():
        shutil.copytree(inp_src, dest / "inputs", dirs_exist_ok=True)
        log.info(f"  snapshot: inputs   → {dest / 'inputs'}")
    if res_src.exists():
        shutil.copytree(res_src, dest / "mtl_2f15e", dirs_exist_ok=True)
        log.info(f"  snapshot: results  → {dest / 'mtl_2f15e'}")

    return dest


def find_latest_summary(state: str) -> dict | None:
    """Find the most-recently-modified full_summary.json under results/hgi/{state}/."""
    res_dir = IoPaths.get_results_dir(state, EmbeddingEngine.HGI)
    summaries = sorted(res_dir.rglob("full_summary.json"), key=lambda p: p.stat().st_mtime)
    if not summaries:
        return None
    with open(summaries[-1]) as f:
        return json.load(f)


def read_cat_f1(summary: dict) -> tuple[float, float]:
    """Return (mean, std) Cat F1 from a full_summary.json dict."""
    cat = summary.get("category", {}).get("f1", {})
    return float(cat.get("mean", 0.0)), float(cat.get("std", 0.0))


# ── Core pipeline steps ────────────────────────────────────────────────────────

def run_hgi(state: str, wr: float) -> bool:
    """Regenerate HGI embeddings for one (state, w_r) point."""
    if DRY_RUN:
        log.info(f"[DRY] HGI: {state} w_r={wr}")
        return True

    cfg = copy(BASE_HGI_CONFIG)
    cfg.cross_region_weight = wr
    cfg.shapefile = SHAPEFILES[state]

    log.info(f"[1/5] preprocess (no embeddings): {state} w_r={wr}")
    preprocess_hgi(city=state, city_shapefile=str(cfg.shapefile),
                   poi_emb_path=None, cta_file=None, cross_region_weight=wr)

    log.info(f"[2/5] POI2Vec: {state}")
    poi_emb_path = train_poi2vec(city=state, epochs=cfg.poi2vec_epochs,
                                 embedding_dim=cfg.dim,
                                 device="cuda" if torch.cuda.is_available() else "cpu")

    log.info(f"[3/5] preprocess (with embeddings): {state}")
    data = preprocess_hgi(city=state, city_shapefile=str(cfg.shapefile),
                          poi_emb_path=str(poi_emb_path),
                          cta_file=None, cross_region_weight=wr)

    gf = IoPaths.HGI.get_graph_data_file(state)
    gf.parent.mkdir(parents=True, exist_ok=True)
    with open(gf, "wb") as f:
        pkl.dump(data, f)

    log.info(f"[4/5] HGI training: {state}")
    train_hgi(state, cfg)

    log.info(f"[5/5] generating inputs: {state}")
    generate_category_input(state, EmbeddingEngine.HGI)
    generate_next_input_from_poi(state, EmbeddingEngine.HGI)

    return True


def run_mtl_training(state: str) -> bool:
    """Run MTLnet at FOLDS x EPOCHS via the canonical train.py CLI."""
    cmd = [
        sys.executable, str(_root / "scripts" / "train.py"),
        "--task", "mtl",
        "--state", state.lower(),
        "--engine", "hgi",
        "--folds", str(FOLDS),
        "--epochs", str(EPOCHS),
    ]
    env = {**os.environ, "PYTHONPATH": f"{_root / 'src'}:{_root / 'research'}"}

    if DRY_RUN:
        log.info(f"[DRY] train: {' '.join(cmd)}")
        return True

    log.info(f"Running MTLnet: {state} {FOLDS}f{EPOCHS}e")
    result = subprocess.run(cmd, env=env, cwd=str(_root))
    return result.returncode == 0


def run_sweep_point(state: str, wr: float) -> tuple[float, float] | None:
    """
    Full pipeline for one (state, w_r) point.
    Returns (cat_f1_mean, cat_f1_std) or None on failure.
    """
    ts = datetime.now().strftime("%Y%m%dT%H%M")
    tag = wr_tag(wr)
    log.info(f"\n{'='*60}")
    log.info(f"  SWEEP POINT: {state}  w_r={wr}  ({tag})")
    log.info(f"{'='*60}")

    try:
        ok = run_hgi(state, wr)
        if not ok:
            log.error(f"HGI failed: {state} w_r={wr}")
            return None

        ok = run_mtl_training(state)
        if not ok:
            log.error(f"MTLnet failed: {state} w_r={wr}")
            return None

        if not DRY_RUN:
            snapshot(state, wr, ts)

        if DRY_RUN:
            return (0.5 + wr * 0.1, 0.01)  # fake for dry run

        summary = find_latest_summary(state)
        if summary is None:
            log.error(f"No summary found for {state}")
            return None

        mean_f1, std_f1 = read_cat_f1(summary)
        log.info(f"  → Cat F1: {mean_f1:.4f} ± {std_f1:.4f}")
        return mean_f1, std_f1

    except Exception as e:
        log.error(f"Exception at {state} w_r={wr}: {e}", exc_info=True)
        return None


# ── Decision rule ──────────────────────────────────────────────────────────────

def apply_decision_rule(state: str, results: dict[float, tuple[float, float]]) -> float | None:
    """
    Decision rule from the plan:
    1. Pin to w_r with highest Cat F1 if best - second_best ≥ 1σ of second_best.
    2. If inconclusive (all within 1σ): return None (keep density default).
    """
    valid = {wr: (m, s) for wr, (m, s) in results.items() if m > 0}
    if not valid:
        return None

    ranked = sorted(valid.items(), key=lambda x: x[1][0], reverse=True)
    best_wr, (best_mean, best_std) = ranked[0]

    if len(ranked) < 2:
        return best_wr

    _, (second_mean, second_std) = ranked[1]
    gap = best_mean - second_mean
    threshold = second_std  # 1σ of second-best

    if gap >= threshold:
        log.info(f"  [DECISION] {state}: pin to w_r={best_wr} "
                 f"(gap={gap:.4f} ≥ 1σ={threshold:.4f})")
        return best_wr
    else:
        log.info(f"  [DECISION] {state}: INCONCLUSIVE "
                 f"(gap={gap:.4f} < 1σ={threshold:.4f}) — keep density default")
        return None


# ── Calibration ────────────────────────────────────────────────────────────────

def run_calibration() -> bool:
    """
    Alabama Go/No-Go gate: w_r=0.7 must be ≥ 2σ above w_r=0.4 on Cat F1.
    Returns True if calibration passes (proceed with sweep).
    """
    log.info("\n" + "="*60)
    log.info("  CALIBRATION: Alabama w_r ∈ {0.4, 0.7}")
    log.info("="*60)

    cal_results = {}
    for wr in [0.4, 0.7]:
        res = run_sweep_point("Alabama", wr)
        if res is None:
            log.error("Calibration aborted: pipeline failure")
            return False
        cal_results[wr] = res

    m04, s04 = cal_results[0.4]
    m07, s07 = cal_results[0.7]
    gap = m07 - m04
    threshold = 2 * s04  # 2σ of the lower point

    log.info(f"\n  Calibration results:")
    log.info(f"    w_r=0.4: Cat F1 = {m04:.4f} ± {s04:.4f}")
    log.info(f"    w_r=0.7: Cat F1 = {m07:.4f} ± {s07:.4f}")
    log.info(f"    gap = {gap:.4f}, required ≥ 2σ(0.4) = {threshold:.4f}")

    if gap >= threshold:
        log.info("  ✓ CALIBRATION PASSED — proceeding with state sweeps")
        return True
    else:
        log.warning("  ✗ CALIBRATION FAILED — 2f15e protocol too noisy")
        log.warning("    Recommendation: fall back to 3f25e (edit FOLDS=3, EPOCHS=25)")
        return False


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="w_r sweep for HGI embeddings")
    parser.add_argument(
        "--states", nargs="+", metavar="STATE",
        help="States to sweep (default: Florida California Texas). "
             "Pass one or more to run a subset, e.g. --states Florida California",
    )
    parser.add_argument(
        "--skip-calibration", action="store_true",
        help="Skip Alabama calibration step (use when already validated)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would run without executing",
    )
    parser.add_argument(
        "--wr-grid", nargs="+", type=float, metavar="WR",
        help="w_r values to sweep (default: 0.4 0.7 1.0). "
             "E.g. --wr-grid 0.5 0.9",
    )
    args = parser.parse_args()

    # CLI args override env vars
    global DRY_RUN, SKIP_CALIBRATION, WR_GRID
    if args.dry_run:
        DRY_RUN = True
    if args.skip_calibration:
        SKIP_CALIBRATION = True
    if args.wr_grid:
        WR_GRID = args.wr_grid

    target_states = args.states if args.states else TARGET_STATES

    log.info(f"w_r sweep  |  target states: {target_states}")
    log.info(f"Protocol: {FOLDS}f{EPOCHS}e  |  grid: {WR_GRID}")
    if DRY_RUN:
        log.info("DRY RUN — nothing will actually execute")

    # Step 1: Calibration
    if SKIP_CALIBRATION:
        log.info("Skipping calibration (--skip-calibration)")
    else:
        passed = run_calibration()
        if not passed:
            log.error("Sweep aborted at calibration gate.")
            sys.exit(1)

    # Step 2: Sweep target states
    all_results: dict[str, dict[float, tuple[float, float]]] = {}
    decisions: dict[str, float | None] = {}

    for state in target_states:
        state_results = {}
        for wr in WR_GRID:
            res = run_sweep_point(state, wr)
            if res is not None:
                state_results[wr] = res
            else:
                log.warning(f"  {state} w_r={wr} failed — skipping point")

        all_results[state] = state_results
        decisions[state] = apply_decision_rule(state, state_results)

    # Step 3: Print summary table
    log.info("\n" + "="*60)
    log.info("  SWEEP RESULTS SUMMARY")
    log.info("="*60)
    log.info(f"{'State':<12} {'w_r':<6} {'Cat F1 mean':>12} {'± std':>8}  {'Decision'}")
    log.info("-"*60)

    for state in target_states:
        best_wr = decisions[state]
        for wr in WR_GRID:
            if wr not in all_results.get(state, {}):
                log.info(f"{state:<12} {wr:<6.1f} {'FAILED':>12}")
                continue
            mean_f1, std_f1 = all_results[state][wr]
            marker = " ← BEST" if wr == best_wr else ""
            log.info(f"{state:<12} {wr:<6.1f} {mean_f1:>12.4f} {f'±{std_f1:.4f}':>8}{marker}")

    # Step 4: Recommendations for hgi.pipe.py
    log.info("\n" + "="*60)
    log.info("  RECOMMENDED CROSS_REGION_WEIGHT_PER_STATE updates")
    log.info("="*60)
    for state in target_states:
        best = decisions[state]
        if best is not None:
            log.info(f"  '{state}': {best},  # swept {datetime.now().strftime('%Y-%m-%d')}")
        else:
            log.info(f"  # '{state}': inconclusive — keep current density default")

    log.info("\nDone.")


if __name__ == "__main__":
    main()
