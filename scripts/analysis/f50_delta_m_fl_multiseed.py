"""F50 Tier 0 — FL multi-seed Δm extension (CH22 tightening, 2026-05-01).

Pools 5 seeds × 5 folds = 25 paired Δm samples at Florida using:
  - MTL B9 per-seed run dirs from F51 paper-grade folder.
  - STL reg per-seed JSONs (paper_close + c4_clean for seed=42).
  - STL cat seed=42 single-seed (no multi-seed FL STL cat exists; we use
    seed=42 STL cat as a fixed per-fold baseline for cat-side relative Δ
    across seeds — defensible approximation: STL cat is leak-free by
    construction (no log_T) and F51 shows STL is essentially seed-deterministic
    on the partition-difficulty axis at FL).

Driver outputs:
  docs/results/paired_tests/F50_T0_delta_m_FL_multiseed.json
"""
from __future__ import annotations

import json, math, statistics
from itertools import product
from pathlib import Path
from typing import Sequence

import pandas as pd

REPO = Path(__file__).resolve().parents[2]
F51 = Path("/Volumes/Vitor's SSD/drive/results/f51_paper_grade_runs")
P1  = REPO / "docs/results/P1"
PFD = REPO / "docs/results/phase1_perfold"
OUT = REPO / "docs/results/paired_tests/F50_T0_delta_m_FL_multiseed.json"

# Seed → MTL run dir (B9). Mapped by matching against F51_multi_seed_results.json.
B9_DIRS = {
    42:  F51 / "mtlnet_lr1.0e-04_bs2048_ep50_20260429_1813",
    0:   F51 / "mtlnet_lr1.0e-04_bs2048_ep50_20260430_0547",
    1:   F51 / "mtlnet_lr1.0e-04_bs2048_ep50_20260430_0605",
    7:   F51 / "mtlnet_lr1.0e-04_bs2048_ep50_20260430_0623",
    100: F51 / "mtlnet_lr1.0e-04_bs2048_ep50_20260430_0641",
}

# Seed → STL reg per-fold JSON (paper_close + c4_clean for seed=42).
STL_REG_FILES = {
    42:  P1 / "region_head_florida_region_5f_50ep_c4_clean.json",
    0:   P1 / "region_head_florida_region_5f_50ep_paper_close_fl_stl_reg_seed0_retry.json",
    1:   P1 / "region_head_florida_region_5f_50ep_paper_close_fl_stl_reg_seed1_retry.json",
    7:   P1 / "region_head_florida_region_5f_50ep_paper_close_fl_stl_reg_seed7_retry.json",
    100: P1 / "region_head_florida_region_5f_50ep_paper_close_fl_stl_reg_seed100_retry.json",
}

# STL cat seed=42 only — fixed per-fold baseline for cat side.
STL_CAT_FILE = PFD / "FL_check2hgi_cat_gru_5f50ep.json"


def per_fold_max(run_dir: Path, task: str, metric: str, min_epoch: int = 5) -> list[float]:
    out = []
    for f in (1, 2, 3, 4, 5):
        df = pd.read_csv(run_dir / "metrics" / f"fold{f}_{task}_val.csv")
        sub = df[df["epoch"] >= min_epoch]
        out.append(float(sub[metric].max()))
    return out


# ---------- Wilcoxon -----------

def signed_rank_w_plus(deltas: Sequence[float]) -> tuple[float, int]:
    nz = [d for d in deltas if d != 0.0]
    n = len(nz)
    abs_idx = sorted(range(n), key=lambda i: abs(nz[i]))
    rank_of = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(nz[abs_idx[j+1]]) == abs(nz[abs_idx[i]]):
            j += 1
        avg = (i + j + 2) / 2
        for k in range(i, j+1):
            rank_of[abs_idx[k]] = avg
        i = j + 1
    return sum(rank_of[i] for i in range(n) if nz[i] > 0), n


def exact_p(w_plus: float, n: int, alt: str = "greater") -> float:
    if n == 0:
        return 1.0
    if n > 25:
        # Normal approximation for large n
        mu = n * (n + 1) / 4
        sigma = math.sqrt(n * (n + 1) * (2 * n + 1) / 24)
        z = (w_plus - mu) / sigma
        from math import erf, sqrt
        cdf = 0.5 * (1 + erf(z / sqrt(2)))
        if alt == "greater": return 1 - cdf
        if alt == "less": return cdf
        return min(1.0, 2 * min(cdf, 1 - cdf))
    counts: dict[float, int] = {}
    total = 0
    for signs in product([0, 1], repeat=n):
        w = sum(r for r, s in zip(range(1, n+1), signs) if s == 1)
        counts[w] = counts.get(w, 0) + 1
        total += 1
    if alt == "greater":
        return sum(c for w, c in counts.items() if w >= w_plus) / total
    if alt == "less":
        return sum(c for w, c in counts.items() if w <= w_plus) / total
    pg = sum(c for w, c in counts.items() if w >= w_plus) / total
    pl = sum(c for w, c in counts.items() if w <= w_plus) / total
    return min(1.0, 2 * min(pg, pl))


def paired_against_zero(deltas: Sequence[float]) -> dict:
    n = len(deltas)
    n_pos = sum(1 for d in deltas if d > 0)
    n_neg = sum(1 for d in deltas if d < 0)
    w_plus, n_nz = signed_rank_w_plus(deltas)
    return {
        "n": n,
        "n_paired_nonzero": n_nz,
        "delta_mean": sum(deltas) / n,
        "delta_std": statistics.stdev(deltas) if n > 1 else 0.0,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "wilcoxon_W_plus": w_plus,
        "wilcoxon_p_greater": exact_p(w_plus, n_nz, "greater"),
        "wilcoxon_p_less": exact_p(w_plus, n_nz, "less"),
        "wilcoxon_p_two_sided": exact_p(w_plus, n_nz, "two-sided"),
    }


# ---------- Driver ---------

def run() -> None:
    # STL cat per-fold (seed=42 only; fixed baseline)
    stl_cat_data = json.load(STL_CAT_FILE.open())
    stl_cat_per_fold = [stl_cat_data[f"fold_{i}"]["f1"] for i in range(5)]

    print(f"STL cat seed=42 per-fold F1: {[round(v,4) for v in stl_cat_per_fold]}")
    print(f"  mean = {statistics.mean(stl_cat_per_fold):.4f}\n")

    rows = []
    pooled_dm_mrr, pooled_dm_a10 = [], []
    pooled_d_cat, pooled_d_mrr, pooled_d_a10 = [], [], []

    print(f"{'seed':>4}  {'mtl_cat':>7}  {'stl_cat':>7}  {'r_cat%':>7}  "
          f"{'mtl_mrr':>7}  {'stl_mrr':>7}  {'r_mrr%':>7}  "
          f"{'mtl_a10':>7}  {'stl_a10':>7}  {'r_a10%':>7}  "
          f"{'Δm_mrr%':>8}  {'Δm_a10%':>8}")
    print("-" * 130)

    for seed in (42, 0, 1, 7, 100):
        # MTL per-fold
        mtl_cat = per_fold_max(B9_DIRS[seed], "next_category", "f1")
        mtl_mrr = per_fold_max(B9_DIRS[seed], "next_region", "mrr_indist")
        mtl_a10 = per_fold_max(B9_DIRS[seed], "next_region", "top10_acc_indist")

        # STL reg per-fold (matched-seed)
        stl_reg_data = json.load(STL_REG_FILES[seed].open())
        stl_pf = stl_reg_data["heads"]["next_getnext_hard"]["per_fold"]
        stl_mrr = [pf["mrr"] for pf in stl_pf]
        stl_a10 = [pf["top10_acc"] for pf in stl_pf]

        # STL cat per-fold = seed=42 fixed baseline
        # For seed=42 this is true matched-fold paired; for other seeds it's a defensible
        # approximation since STL cat is essentially seed-deterministic at FL.
        stl_cat = stl_cat_per_fold

        # Per-fold relative Δ
        d_cat = [(m - s) / s for m, s in zip(mtl_cat, stl_cat)]
        d_mrr = [(m - s) / s for m, s in zip(mtl_mrr, stl_mrr)]
        d_a10 = [(m - s) / s for m, s in zip(mtl_a10, stl_a10)]

        dm_mrr = [(c + r) / 2 for c, r in zip(d_cat, d_mrr)]
        dm_a10 = [(c + r) / 2 for c, r in zip(d_cat, d_a10)]

        pooled_dm_mrr.extend(dm_mrr)
        pooled_dm_a10.extend(dm_a10)
        pooled_d_cat.extend(d_cat)
        pooled_d_mrr.extend(d_mrr)
        pooled_d_a10.extend(d_a10)

        print(f"{seed:>4}  {statistics.mean(mtl_cat):.4f}   {statistics.mean(stl_cat):.4f}   "
              f"{statistics.mean(d_cat)*100:+6.2f}   "
              f"{statistics.mean(mtl_mrr):.4f}   {statistics.mean(stl_mrr):.4f}   "
              f"{statistics.mean(d_mrr)*100:+6.2f}   "
              f"{statistics.mean(mtl_a10):.4f}   {statistics.mean(stl_a10):.4f}   "
              f"{statistics.mean(d_a10)*100:+6.2f}   "
              f"{statistics.mean(dm_mrr)*100:+7.2f}   "
              f"{statistics.mean(dm_a10)*100:+7.2f}")

        rows.append({
            "seed": seed,
            "mtl_dir": B9_DIRS[seed].name,
            "stl_reg_file": STL_REG_FILES[seed].name,
            "absolute_means": {
                "mtl_cat_f1": statistics.mean(mtl_cat),
                "mtl_reg_mrr": statistics.mean(mtl_mrr),
                "mtl_reg_acc10_indist": statistics.mean(mtl_a10),
                "stl_cat_f1": statistics.mean(stl_cat),
                "stl_reg_mrr": statistics.mean(stl_mrr),
                "stl_reg_acc10": statistics.mean(stl_a10),
            },
            "per_fold_relative": {
                "cat_f1": d_cat, "reg_mrr": d_mrr, "reg_acc10": d_a10,
            },
            "delta_m_per_fold": {
                "primary_mrr": dm_mrr,
                "secondary_acc10": dm_a10,
            },
            "per_seed_5fold_wilcoxon": {
                "delta_m_mrr_p_greater": exact_p(*signed_rank_w_plus(dm_mrr), "greater"),
                "delta_m_acc10_p_greater": exact_p(*signed_rank_w_plus(dm_a10), "greater"),
                "n_pos_mrr": sum(1 for d in dm_mrr if d > 0),
                "n_pos_a10": sum(1 for d in dm_a10 if d > 0),
            },
        })

    print("-" * 130)
    print("\n=== Pooled multi-seed paired Wilcoxon (n=25) ===\n")
    pdm_mrr = paired_against_zero(pooled_dm_mrr)
    pdm_a10 = paired_against_zero(pooled_dm_a10)
    pcat = paired_against_zero(pooled_d_cat)
    pmrr = paired_against_zero(pooled_d_mrr)
    pa10 = paired_against_zero(pooled_d_a10)

    print(f"{'metric':<14} {'mean(%)':>8} {'σ':>6} {'n+/n−':>8} {'p_>':>10} {'p_2s':>10}")
    print("-" * 70)
    for label, w in [("Δm-MRR", pdm_mrr), ("Δm-Acc@10", pdm_a10),
                     ("rel cat F1", pcat), ("rel reg MRR", pmrr), ("rel reg Acc@10", pa10)]:
        print(f"{label:<14} {w['delta_mean']*100:+8.3f} "
              f"{w['delta_std']*100:6.3f} "
              f"{w['n_positive']:>3}/{w['n_negative']:<3} "
              f"{w['wilcoxon_p_greater']:.3e} "
              f"{w['wilcoxon_p_two_sided']:.3e}")

    out = {
        "analysis": "F50 Tier 0 leak-free FL multi-seed — Δm extension (CH22 tightening)",
        "spec": (
            "5 seeds × 5 folds = 25 paired samples. Reg side (MRR + Acc@10): "
            "matched-seed paired (5 STL reg files at seeds {42,0,1,7,100}). "
            "Cat side (F1): seed=42 STL cat is matched-fold paired; for other seeds "
            "STL cat is the seed=42 fixed baseline (defensible approximation; STL cat "
            "is seed-deterministic at FL per F51, leak-free by construction)."
        ),
        "n_seeds": 5, "n_folds_per_seed": 5, "n_paired_total": 25,
        "per_seed_rows": rows,
        "pooled_wilcoxon": {
            "delta_m_primary_mrr": {
                "mean_pct": pdm_mrr["delta_mean"] * 100,
                "std_pct": pdm_mrr["delta_std"] * 100,
                "n_positive": pdm_mrr["n_positive"],
                "n_negative": pdm_mrr["n_negative"],
                "wilcoxon_W_plus": pdm_mrr["wilcoxon_W_plus"],
                "p_greater": pdm_mrr["wilcoxon_p_greater"],
                "p_two_sided": pdm_mrr["wilcoxon_p_two_sided"],
            },
            "delta_m_secondary_acc10": {
                "mean_pct": pdm_a10["delta_mean"] * 100,
                "std_pct": pdm_a10["delta_std"] * 100,
                "n_positive": pdm_a10["n_positive"],
                "n_negative": pdm_a10["n_negative"],
                "wilcoxon_W_plus": pdm_a10["wilcoxon_W_plus"],
                "p_greater": pdm_a10["wilcoxon_p_greater"],
                "p_two_sided": pdm_a10["wilcoxon_p_two_sided"],
            },
            "per_task_rel_cat_f1": {
                "mean_pct": pcat["delta_mean"] * 100,
                "n_pos_n_neg": [pcat["n_positive"], pcat["n_negative"]],
                "p_greater": pcat["wilcoxon_p_greater"],
                "p_two_sided": pcat["wilcoxon_p_two_sided"],
            },
            "per_task_rel_reg_mrr": {
                "mean_pct": pmrr["delta_mean"] * 100,
                "n_pos_n_neg": [pmrr["n_positive"], pmrr["n_negative"]],
                "p_greater": pmrr["wilcoxon_p_greater"],
                "p_two_sided": pmrr["wilcoxon_p_two_sided"],
            },
            "per_task_rel_reg_acc10": {
                "mean_pct": pa10["delta_mean"] * 100,
                "n_pos_n_neg": [pa10["n_positive"], pa10["n_negative"]],
                "p_greater": pa10["wilcoxon_p_greater"],
                "p_two_sided": pa10["wilcoxon_p_two_sided"],
            },
        },
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nSaved → {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    run()
