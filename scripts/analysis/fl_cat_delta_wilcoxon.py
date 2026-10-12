"""Wilcoxon analysis for §0.1 FL cat-side n=5 → n=20 upgrade.

Comparison: MTL B9 (mtlnet_crossattn) vs STL cat next_gru, Florida, seeds {0,1,7,100}.
Seeds {0,1,7,100} × 5 folds = n=20 paired Δs. Closes the last n=5 ceiling in §0.1.

STL cat next_gru dirs (Gap 2, already done):
  seed 0: results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48444
  seed 1: results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48455
  seed 7: results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48469
  seed100: results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175853_48438

MTL B9 dirs: auto-discovered from results/check2hgi/florida/mtlnet_lr* (4 newest by seed).

Output: docs/findings/FL_CAT_DELTA_WILCOXON.json
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import pandas as pd
from scipy.stats import wilcoxon
from statistics import mean

MIN_EPOCH = 5
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/findings/FL_CAT_DELTA_WILCOXON.json"

SEEDS = [0, 1, 7, 100]

# STL cat dirs (Gap 2, fixed)
FL_STL_CAT = {
    0:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48444",
    1:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48455",
    7:   "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175852_48469",
    100: "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260501_175853_48438",
}

# MTL B9 dirs: 2026-05-02 relaunch with canonical recipe (cat next_gru + reg next_getnext_hard)
FL_MTL_B9 = {
    0:   "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260502_162244_127432",
    1:   "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260502_162244_127433",
    7:   "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260502_162244_127434",
    100: "results/check2hgi/florida/mtlnet_lr1.0e-04_bs2048_ep50_20260502_162244_127435",
}

def find_mtl_dir(seed: int) -> Path:
    return ROOT / FL_MTL_B9[seed]


def per_fold_best_csv(run_dir: Path, task_fname: str, metric: str) -> list[float]:
    vals = []
    for fold in range(1, 6):
        csv = run_dir / "metrics" / f"fold{fold}_{task_fname}_val.csv"
        df = pd.read_csv(csv)
        sub = df[df["epoch"] >= MIN_EPOCH]
        vals.append(float(sub[metric].max()))
    return vals


def run_wilcoxon(a: list[float], b: list[float]) -> dict:
    diffs = [x - y for x, y in zip(a, b)]
    delta = mean(a) - mean(b)
    try:
        _, p_two = wilcoxon(diffs, alternative="two-sided")
        _, p_gt  = wilcoxon(diffs, alternative="greater")
    except Exception:
        p_two, p_gt = float("nan"), float("nan")
    return {
        "n_pairs": len(diffs),
        "mean_a": round(mean(a) * 100, 4),
        "mean_b": round(mean(b) * 100, 4),
        "delta_pp": round(delta * 100, 4),
        "p_two_sided": round(p_two, 6),
        "p_greater": round(p_gt, 6),
        "n_positive": sum(1 for d in diffs if d > 0),
        "n_negative": sum(1 for d in diffs if d < 0),
        "values_a": [round(x * 100, 4) for x in a],
        "values_b": [round(x * 100, 4) for x in b],
    }


mtl_cat_pool, stl_cat_pool = [], []
mtl_dirs = {}

for seed in SEEDS:
    mtl_dir = find_mtl_dir(seed)
    mtl_dirs[seed] = str(mtl_dir.relative_to(ROOT))
    stl_dir = ROOT / FL_STL_CAT[seed]

    mtl_cat = per_fold_best_csv(mtl_dir, "next_category", "f1")
    stl_cat = per_fold_best_csv(stl_dir, "next", "f1")

    print(f"  seed={seed}  MTL={[round(x*100,2) for x in mtl_cat]}")
    print(f"           STL={[round(x*100,2) for x in stl_cat]}")

    mtl_cat_pool.extend(mtl_cat)
    stl_cat_pool.extend(stl_cat)

w = run_wilcoxon(mtl_cat_pool, stl_cat_pool)
print(f"\nFL CAT Wilcoxon (MTL vs STL): Δ={w['delta_pp']:+.4f} pp  p={w['p_two_sided']:.4g}  n={w['n_pairs']}")
print(f"  MTL mean={w['mean_a']:.4f}%  STL mean={w['mean_b']:.4f}%  n+={w['n_positive']} n-={w['n_negative']}")

output = {
    "description": "FL §0.1 cat-Δ Wilcoxon: MTL B9 (mtlnet_crossattn) vs STL next_gru, seeds {0,1,7,100}, n=20",
    "mtl_dirs": mtl_dirs,
    "stl_dirs": FL_STL_CAT,
    "cat_wilcoxon_mtl_vs_stl": w,
}

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2))
print(f"\nSaved → {OUT}")
