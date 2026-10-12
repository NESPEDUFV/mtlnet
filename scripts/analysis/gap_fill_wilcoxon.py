"""Wilcoxon analysis for H100 camera-ready gap-fill runs (2026-05-01 PM).

Two analyses:

A) Gap 2 — STL cat next_gru multi-seed (AL/AZ/FL, seeds {0,1,7,100}):
   Paired Wilcoxon: MTL B9 cat F1  vs  STL next_gru cat F1
   Updates the §0.1 Δ_cat column with multi-seed STL ceiling.

B) Gap 1 CA — MTL multi-seed B9 vs H3-alt (CA, seeds {0,1,7,100}):
   Paired Wilcoxon: B9 reg Acc@10 vs H3-alt reg Acc@10
                    B9 cat F1    vs H3-alt cat F1
   Updates §0.4 recipe-selection table CA row.

Extraction methodology: per-fold max metric for epoch >= 5 (F51 canonical).
Output: docs/findings/GAP_FILL_WILCOXON.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy.stats import wilcoxon
from statistics import mean, stdev

MIN_EPOCH = 5
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/findings/GAP_FILL_WILCOXON.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def per_fold_best_from_dir(run_dir: Path, task_fname: str, metric: str) -> list[float]:
    vals = []
    for fold in range(1, 6):
        csv = run_dir / "metrics" / f"fold{fold}_{task_fname}_val.csv"
        if not csv.exists():
            return []
        df = pd.read_csv(csv)
        if metric not in df.columns:
            return []
        sub = df[df["epoch"] >= MIN_EPOCH]
        if sub.empty:
            return []
        vals.append(float(sub[metric].max()))
    return vals


def per_fold_best_from_phase1_json(json_path: Path, metric: str) -> list[float]:
    d = json.loads(json_path.read_text())
    return [d[f"fold_{i}"][metric] for i in range(5)]


def run_wilcoxon(a: list[float], b: list[float]) -> dict:
    diffs = [x - y for x, y in zip(a, b)]
    n = len(diffs)
    delta = mean(a) - mean(b)
    try:
        _, p_two = wilcoxon(diffs, alternative="two-sided")
        _, p_gt  = wilcoxon(diffs, alternative="greater")
    except Exception:
        p_two, p_gt = float("nan"), float("nan")
    n_pos = sum(1 for d in diffs if d > 0)
    n_neg = sum(1 for d in diffs if d < 0)
    return {
        "n_pairs": n,
        "mean_a": round(mean(a) * 100, 4),
        "mean_b": round(mean(b) * 100, 4),
        "delta_pp": round(delta * 100, 4),
        "p_two_sided": round(p_two, 6),
        "p_greater": round(p_gt, 6),
        "n_positive": n_pos,
        "n_negative": n_neg,
        "values_a": [round(x * 100, 4) for x in a],
        "values_b": [round(x * 100, 4) for x in b],
    }


def pool_seeds(seed_fold_lists: list[list[float]]) -> list[float]:
    """Flatten [[f1..f5], [f1..f5], ...] → single pooled list."""
    return [v for lst in seed_fold_lists for v in lst]

# ── CA MTL dir mapping (from timestamp alignment with master log) ─────────────
CA_MTL_DIRS = {
    ("b9",    0):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_175905_48470",
    ("h3alt", 0):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_183635_182272",
    ("b9",    1):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_191305_330675",
    ("h3alt", 1):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_194725_390548",
    ("b9",    7):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_202334_391773",
    ("h3alt", 7):   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_205702_393048",
    ("b9",    100): "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_213249_394079",
    ("h3alt", 100): "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_220626_394753",
}

# Gap 2 STL cat dirs (today's runs, timestamp order = seed order 0,1,7,100)
GAP2_STL_CAT_SEED_ORDER = [0, 1, 7, 100]
GAP2_STL_CAT_DIRS = {
    "alabama": {
        0:   "results/check2hgi/alabama/next_lr1.0e-04_bs2048_ep50_20260501_175846_48350",
        1:   "results/check2hgi/alabama/next_lr1.0e-04_bs2048_ep50_20260501_175846_48359",
        7:   "results/check2hgi/alabama/next_lr1.0e-04_bs2048_ep50_20260501_175846_48372",
        100: "results/check2hgi/alabama/next_lr1.0e-04_bs2048_ep50_20260501_175846_48381",
    },
    "arizona": {
        0:   "results/check2hgi/arizona/next_lr1.0e-04_bs2048_ep50_20260501_175847_48394",
        1:   "results/check2hgi/arizona/next_lr1.0e-04_bs2048_ep50_20260501_175847_48405",
        7:   "results/check2hgi/arizona/next_lr1.0e-04_bs2048_ep50_20260501_175847_48416",
        100: "results/check2hgi/arizona/next_lr1.0e-04_bs2048_ep50_20260501_175847_48423",
    },
    "florida": {
        0:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48444",
        1:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48455",
        7:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48469",
        100: "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175853_48438",
    },
}

# AL/AZ MTL B9 dirs (from prior paper_closure_wilcoxon.py)
AL_AZ_MTL_B9_DIRS = {
    ("alabama", 0):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411673",
    ("alabama", 1):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411676",
    ("alabama", 7):   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411691",
    ("alabama", 100): "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260501_014904_411706",
    ("arizona", 0):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015206_412194",
    ("arizona", 1):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015208_412291",
    ("arizona", 7):   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015209_412306",
    ("arizona", 100): "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260501_015209_412356",
}

# FL MTL B9 seed=42 (single seed, from prior session)
FL_MTL_B9_SEED42_DIR = "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260501_052359_421824"

# TX MTL dirs — seeds {0,1,7,100} × {b9, h3alt}; timestamp-aligned from master log
# Old seed=42 dirs (_20260501_023224_413998 and _20260501_031509_414897) excluded.
TX_MTL_DIRS = {
    ("b9",    0):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260501_224154_395464",
    ("h3alt", 0):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260501_232445_397950",
    ("b9",    1):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_001027_400101",
    ("h3alt", 1):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_005342_401803",
    ("b9",    7):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_013938_403692",
    ("h3alt", 7):   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_022233_405231",
    ("b9",    100): "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_030814_406999",
    ("h3alt", 100): "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_035106_408627",
}

# ── Analysis A: Gap 2 — MTL B9 cat vs new multi-seed STL cat ─────────────────

print("=" * 60)
print("A) Gap 2 — MTL B9 cat F1 vs multi-seed STL next_gru cat F1")
print("   States: AL, AZ, FL   Seeds: {0,1,7,100}")
print("=" * 60)

results_a = {}

for state in ("alabama", "arizona", "florida"):
    print(f"\n--- {state.upper()} ---")

    # STL cat: pool across 4 seeds from today's runs
    stl_cat_pooled = []
    for seed in GAP2_STL_CAT_SEED_ORDER:
        d = ROOT / GAP2_STL_CAT_DIRS[state][seed]
        folds = per_fold_best_from_dir(d, "next", "f1")
        if not folds:
            print(f"  STL cat seed={seed}: no data at {d}")
        else:
            stl_cat_pooled.append(folds)
            print(f"  STL cat seed={seed}: {[round(f*100,2) for f in folds]} mean={mean(folds)*100:.2f}%")

    # MTL B9 cat: AL/AZ from prior paper_closure session; FL single seed=42
    if state in ("alabama", "arizona"):
        mtl_b9_pooled = []
        for seed in [0, 1, 7, 100]:
            d = ROOT / AL_AZ_MTL_B9_DIRS[(state, seed)]
            folds = per_fold_best_from_dir(d, "next_category", "f1")
            if not folds:
                folds = per_fold_best_from_dir(d, "category", "f1")
            if folds:
                mtl_b9_pooled.append(folds)
                print(f"  MTL B9 cat seed={seed}: {[round(f*100,2) for f in folds]} mean={mean(folds)*100:.2f}%")
    else:  # florida — single seed=42
        d = ROOT / FL_MTL_B9_SEED42_DIR
        folds = per_fold_best_from_dir(d, "next_category", "f1")
        if not folds:
            folds = per_fold_best_from_dir(d, "category", "f1")
        mtl_b9_pooled = [folds] if folds else []
        if folds:
            print(f"  MTL B9 cat seed=42: {[round(f*100,2) for f in folds]} mean={mean(folds)*100:.2f}%")

    if stl_cat_pooled and mtl_b9_pooled:
        # Pair seed-by-seed (use matching seeds where available, else pool all)
        n_seeds = min(len(stl_cat_pooled), len(mtl_b9_pooled))
        stl_flat = pool_seeds(stl_cat_pooled[:n_seeds])
        mtl_flat = pool_seeds(mtl_b9_pooled[:n_seeds])
        w = run_wilcoxon(mtl_flat, stl_flat)
        w["note"] = f"MTL B9 cat vs STL next_gru cat, {n_seeds} seeds × 5 folds"
        results_a[state] = w
        print(f"  Δ_cat = MTL − STL = {w['delta_pp']:+.2f} pp  p_two={w['p_two_sided']:.4f}  n={w['n_pairs']}")
    else:
        print(f"  MISSING DATA — skipping {state}")

# ── Analysis B: Gap 1 CA — B9 vs H3-alt ──────────────────────────────────────

print("\n" + "=" * 60)
print("B) Gap 1 CA — B9 vs H3-alt, seeds {0,1,7,100}")
print("=" * 60)

b9_reg, h3_reg, b9_cat, h3_cat = [], [], [], []

for seed in [0, 1, 7, 100]:
    for recipe, store_reg, store_cat in [("b9", b9_reg, b9_cat), ("h3alt", h3_reg, h3_cat)]:
        d = ROOT / CA_MTL_DIRS[(recipe, seed)]
        reg = per_fold_best_from_dir(d, "next_region", "top10_acc_indist")
        if not reg:
            reg = per_fold_best_from_dir(d, "region", "top10_acc_indist")
        cat = per_fold_best_from_dir(d, "next_category", "f1")
        if not cat:
            cat = per_fold_best_from_dir(d, "category", "f1")
        if reg:
            store_reg.append(reg)
            print(f"  CA {recipe} seed={seed} reg: {[round(v*100,2) for v in reg]} mean={mean(reg)*100:.2f}%")
        else:
            print(f"  CA {recipe} seed={seed} reg: NO DATA")
        if cat:
            store_cat.append(cat)
            print(f"  CA {recipe} seed={seed} cat: {[round(v*100,2) for v in cat]} mean={mean(cat)*100:.2f}%")

results_b = {"california": {}}
if b9_reg and h3_reg:
    n_seeds = min(len(b9_reg), len(h3_reg))
    w_reg = run_wilcoxon(pool_seeds(b9_reg[:n_seeds]), pool_seeds(h3_reg[:n_seeds]))
    w_reg["note"] = f"CA B9 vs H3-alt reg Acc@10, {n_seeds} seeds × 5 folds"
    results_b["california"]["reg"] = w_reg
    print(f"\nCA reg Δ = B9 − H3-alt = {w_reg['delta_pp']:+.2f} pp  p_two={w_reg['p_two_sided']:.4f}  n={w_reg['n_pairs']}")

if b9_cat and h3_cat:
    n_seeds = min(len(b9_cat), len(h3_cat))
    w_cat = run_wilcoxon(pool_seeds(b9_cat[:n_seeds]), pool_seeds(h3_cat[:n_seeds]))
    w_cat["note"] = f"CA B9 vs H3-alt cat F1, {n_seeds} seeds × 5 folds"
    results_b["california"]["cat"] = w_cat
    print(f"CA cat Δ = B9 − H3-alt = {w_cat['delta_pp']:+.2f} pp  p_two={w_cat['p_two_sided']:.4f}  n={w_cat['n_pairs']}")

# ── Analysis C: TX — B9 vs H3-alt, seeds {0,1,7,100} ─────────────────────────

print("\n" + "=" * 60)
print("C) Gap 1 TX — B9 vs H3-alt, seeds {0,1,7,100}")
print("=" * 60)

tx_b9_reg, tx_h3_reg, tx_b9_cat, tx_h3_cat = [], [], [], []

for seed in [0, 1, 7, 100]:
    for recipe, store_reg, store_cat in [("b9", tx_b9_reg, tx_b9_cat), ("h3alt", tx_h3_reg, tx_h3_cat)]:
        d = ROOT / TX_MTL_DIRS[(recipe, seed)]
        reg = per_fold_best_from_dir(d, "next_region", "top10_acc_indist")
        if not reg:
            reg = per_fold_best_from_dir(d, "region", "top10_acc_indist")
        cat = per_fold_best_from_dir(d, "next_category", "f1")
        if not cat:
            cat = per_fold_best_from_dir(d, "category", "f1")
        if reg:
            store_reg.append(reg)
            print(f"  TX {recipe} seed={seed} reg: {[round(v*100,2) for v in reg]} mean={mean(reg)*100:.2f}%")
        else:
            print(f"  TX {recipe} seed={seed} reg: NO DATA")
        if cat:
            store_cat.append(cat)
            print(f"  TX {recipe} seed={seed} cat: {[round(v*100,2) for v in cat]} mean={mean(cat)*100:.2f}%")

results_c = {"texas": {}}
if tx_b9_reg and tx_h3_reg:
    n_seeds = min(len(tx_b9_reg), len(tx_h3_reg))
    w_reg = run_wilcoxon(pool_seeds(tx_b9_reg[:n_seeds]), pool_seeds(tx_h3_reg[:n_seeds]))
    w_reg["note"] = f"TX B9 vs H3-alt reg Acc@10, {n_seeds} seeds × 5 folds"
    results_c["texas"]["reg"] = w_reg
    print(f"\nTX reg Δ = B9 − H3-alt = {w_reg['delta_pp']:+.2f} pp  p_two={w_reg['p_two_sided']:.4f}  n={w_reg['n_pairs']}")

if tx_b9_cat and tx_h3_cat:
    n_seeds = min(len(tx_b9_cat), len(tx_h3_cat))
    w_cat = run_wilcoxon(pool_seeds(tx_b9_cat[:n_seeds]), pool_seeds(tx_h3_cat[:n_seeds]))
    w_cat["note"] = f"TX B9 vs H3-alt cat F1, {n_seeds} seeds × 5 folds"
    results_c["texas"]["cat"] = w_cat
    print(f"TX cat Δ = B9 − H3-alt = {w_cat['delta_pp']:+.2f} pp  p_two={w_cat['p_two_sided']:.4f}  n={w_cat['n_pairs']}")

# ── Save ──────────────────────────────────────────────────────────────────────
out = {
    "generated": "2026-05-02T05:xx:xxZ",
    "description": "Gap-fill Wilcoxon: (A) MTL B9 cat vs multi-seed STL next_gru for AL/AZ/FL; (B) CA B9 vs H3-alt multi-seed; (C) TX B9 vs H3-alt multi-seed",
    "gap2_mtl_b9_vs_stl_cat": results_a,
    "gap1_ca_b9_vs_h3alt": results_b,
    "gap1_tx_b9_vs_h3alt": results_c,
}
OUT.write_text(json.dumps(out, indent=2))
print(f"\nSaved → {OUT}")
