"""Wilcoxon analysis for §0.1 architectural-Δ: MTL B9 vs STL ceiling (CA + TX).

Comparison:
  - MTL B9  vs  STL cat next_gru    → Δ_cat F1
  - MTL B9  vs  STL reg next_getnext_hard → Δ_reg Acc@10

Seeds: {0,1,7,100}  Folds: 5  n=20 per state per metric.

Output: docs/findings/ARCH_DELTA_WILCOXON.json
"""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from scipy.stats import wilcoxon
from statistics import mean

MIN_EPOCH = 5
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/findings/ARCH_DELTA_WILCOXON.json"

SEEDS = [0, 1, 7, 100]

# ── MTL B9 dirs ───────────────────────────────────────────────────────────────
CA_MTL_B9 = {
    0:   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_175905_48470",
    1:   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_191305_330675",
    7:   "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_202334_391773",
    100: "results/check2hgi/california/mtlnet_lr1.0e-04_bs2048_ep50_20260501_213249_394079",
}
TX_MTL_B9 = {
    0:   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260501_224154_395464",
    1:   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_001027_400101",
    7:   "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_013938_403692",
    100: "results/check2hgi/texas/mtlnet_lr1.0e-04_bs2048_ep50_20260502_030814_406999",
}

# ── STL cat dirs (new CA/TX runs, timestamp order = seed order 0,1,7,100) ────
CA_STL_CAT = {
    0:   "results/check2hgi/california/next_lr1.0e-04_bs2048_ep50_20260502_045010_411555",
    1:   "results/check2hgi/california/next_lr1.0e-04_bs2048_ep50_20260502_045010_411556",
    7:   "results/check2hgi/california/next_lr1.0e-04_bs2048_ep50_20260502_050210_412465",
    100: "results/check2hgi/california/next_lr1.0e-04_bs2048_ep50_20260502_050540_412800",
}
TX_STL_CAT = {
    0:   "results/check2hgi/texas/next_lr1.0e-04_bs2048_ep50_20260502_045011_411554",
    1:   "results/check2hgi/texas/next_lr1.0e-04_bs2048_ep50_20260502_045011_411557",
    7:   "results/check2hgi/texas/next_lr1.0e-04_bs2048_ep50_20260502_050211_412466",
    100: "results/check2hgi/texas/next_lr1.0e-04_bs2048_ep50_20260502_050541_412801",
}

# ── STL reg JSONs ─────────────────────────────────────────────────────────────
P1_DIR = ROOT / "docs/results/P1"
CA_STL_REG = {
    s: P1_DIR / f"region_head_california_region_5f_50ep_paper_close_california_stl_reg_seed{s}.json"
    for s in SEEDS
}
TX_STL_REG = {
    s: P1_DIR / f"region_head_texas_region_5f_50ep_paper_close_texas_stl_reg_seed{s}.json"
    for s in SEEDS
}


def per_fold_best_csv(run_dir: Path, task_fname: str, metric: str) -> list[float]:
    vals = []
    for fold in range(1, 6):
        csv = run_dir / "metrics" / f"fold{fold}_{task_fname}_val.csv"
        df = pd.read_csv(csv)
        sub = df[df["epoch"] >= MIN_EPOCH]
        vals.append(float(sub[metric].max()))
    return vals


def per_fold_from_p1_json(json_path: Path, head: str = "next_getnext_hard") -> list[float]:
    d = json.loads(json_path.read_text())
    return [fold["top10_acc"] for fold in d["heads"][head]["per_fold"]]


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


output = {}

for state_label, mtl_dirs, stl_cat_dirs, stl_reg_paths in [
    ("california", CA_MTL_B9, CA_STL_CAT, CA_STL_REG),
    ("texas",      TX_MTL_B9, TX_STL_CAT, TX_STL_REG),
]:
    print(f"\n{'='*60}")
    print(f"STATE: {state_label.upper()}")
    print(f"{'='*60}")

    mtl_reg_pool, stl_reg_pool = [], []
    mtl_cat_pool, stl_cat_pool = [], []

    for seed in SEEDS:
        mtl_dir = ROOT / mtl_dirs[seed]
        stl_cat_dir = ROOT / stl_cat_dirs[seed]

        # MTL: reg = next_region top10_acc_indist, cat = next_category f1
        mtl_reg = per_fold_best_csv(mtl_dir, "next_region", "top10_acc_indist")
        mtl_cat = per_fold_best_csv(mtl_dir, "next_category", "f1")
        stl_cat = per_fold_best_csv(stl_cat_dir, "next", "f1")
        stl_reg = per_fold_from_p1_json(stl_reg_paths[seed])

        print(f"  seed={seed}  MTL_reg={[round(x*100,2) for x in mtl_reg]}")
        print(f"           STL_reg={[round(x*100,2) for x in stl_reg]}")
        print(f"           MTL_cat={[round(x*100,2) for x in mtl_cat]}")
        print(f"           STL_cat={[round(x*100,2) for x in stl_cat]}")

        mtl_reg_pool.extend(mtl_reg)
        stl_reg_pool.extend(stl_reg)
        mtl_cat_pool.extend(mtl_cat)
        stl_cat_pool.extend(stl_cat)

    w_reg = run_wilcoxon(mtl_reg_pool, stl_reg_pool)
    w_cat = run_wilcoxon(mtl_cat_pool, stl_cat_pool)

    print(f"\n  REG Wilcoxon (MTL vs STL): Δ={w_reg['delta_pp']:+.4f} pp  p={w_reg['p_two_sided']:.4g}  n={w_reg['n_pairs']}")
    print(f"  CAT Wilcoxon (MTL vs STL): Δ={w_cat['delta_pp']:+.4f} pp  p={w_cat['p_two_sided']:.4g}  n={w_cat['n_pairs']}")

    output[state_label] = {
        "description": "MTL B9 vs STL ceiling (cat=next_gru, reg=next_getnext_hard), seeds {0,1,7,100}, n=20",
        "reg_wilcoxon_mtl_vs_stl": w_reg,
        "cat_wilcoxon_mtl_vs_stl": w_cat,
    }

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(output, indent=2))
print(f"\nSaved → {OUT}")
