"""F50 Tier 0 — leak-free Δm scoreboard (CH22 refresh, 2026-05-01).

Re-extracts the joint Δm metric (Maninis CVPR 2019 / Vandenhende TPAMI 2021)
across all 5 states under leak-free per-fold log_T (seed=42 baseline). Supersedes
``f50_delta_m.py``, which read the pre-F44/F50 leaky run dirs and is now
historical.

Δm = (1/T) · Σ_t (-1)^l_t · (M_m - M_b) / M_b   (× 100%)

Both tasks are higher-is-better (l_t = 0). Pairing: leak-free MTL B9 fold-i
matched with leak-free STL ceiling fold-i at the same seed (=42) — fold splits
coincide because both arms share `StratifiedGroupKFold(seed=42)` under
sklearn 1.8.0.

PRIMARY:   cat F1 + reg MRR     (clean across MTL/STL)
SECONDARY: cat F1 + reg Acc@10  (also clean — `acc10` in STL pf, `acc10` in MTL pf)

Source files (all under `docs/results/phase1_perfold/`):
  MTL B9 cat: <ST>_check2hgi_mtl_cat_pf.json   (fold_N.f1)
  MTL B9 reg: <ST>_check2hgi_mtl_reg_pf.json   (fold_N.{acc10, mrr})
  STL cat:    <ST>_check2hgi_cat_gru_5f50ep.json (fold_N.f1)
  STL reg:    <ST>_check2hgi_reg_gethard_pf_5f50ep.json (fold_N.{acc10, mrr})

Outputs:
  docs/results/paired_tests/F50_T0_delta_m_leakfree.json
"""
from __future__ import annotations

import json
import math
from itertools import product
from pathlib import Path
from typing import Sequence

REPO = Path(__file__).resolve().parents[2]
PFD = REPO / "docs/results/phase1_perfold"
OUT = REPO / "docs/results/paired_tests/F50_T0_delta_m_leakfree.json"

STATES = ("AL", "AZ", "FL", "CA", "TX")


def load_pf(filename: str) -> list[dict]:
    """Return a list of fold dicts, ordered fold_0..fold_4."""
    d = json.load((PFD / filename).open())
    return [d[f"fold_{i}"] for i in range(5)]


def extract_state(state: str) -> dict[str, list[float]]:
    mtl_cat = load_pf(f"{state}_check2hgi_mtl_cat_pf.json")
    mtl_reg = load_pf(f"{state}_check2hgi_mtl_reg_pf.json")
    stl_cat = load_pf(f"{state}_check2hgi_cat_gru_5f50ep.json")
    stl_reg = load_pf(f"{state}_check2hgi_reg_gethard_pf_5f50ep.json")
    return {
        "mtl_cat_f1":  [f["f1"]    for f in mtl_cat],
        "mtl_reg_acc10": [f["acc10"] for f in mtl_reg],
        "mtl_reg_mrr": [f["mrr"]   for f in mtl_reg],
        "stl_cat_f1":  [f["f1"]    for f in stl_cat],
        "stl_reg_acc10": [f["acc10"] if "acc10" in f else f["top10_acc"] for f in stl_reg],
        "stl_reg_mrr": [f["mrr"]   for f in stl_reg],
    }


# --- Wilcoxon signed-rank exact (n ≤ 25) -------------------------------------

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


def stats(values: Sequence[float]) -> dict:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "std": float("nan")}
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    return {"n": n, "mean": m, "std": math.sqrt(var)}


def paired_against_zero(deltas: Sequence[float]) -> dict:
    n = len(deltas)
    n_pos = sum(1 for d in deltas if d > 0)
    n_neg = sum(1 for d in deltas if d < 0)
    w_plus, n_nz = signed_rank_w_plus(deltas)
    return {
        "n": n,
        "n_paired_nonzero": n_nz,
        "delta_mean": sum(deltas) / n,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "wilcoxon_W_plus": w_plus,
        "wilcoxon_p_greater": exact_p(w_plus, n_nz, "greater"),
        "wilcoxon_p_less": exact_p(w_plus, n_nz, "less"),
        "wilcoxon_p_two_sided": exact_p(w_plus, n_nz, "two-sided"),
    }


def relative(m_m: list[float], m_b: list[float]) -> list[float]:
    return [(mm - mb) / mb for mm, mb in zip(m_m, m_b)]


def per_fold_delta_m(d_cat: list[float], d_reg: list[float]) -> list[float]:
    return [(c + r) / 2 for c, r in zip(d_cat, d_reg)]


def run() -> None:
    out = {
        "analysis": "F50 Tier 0 leak-free — joint Δm + paired Wilcoxon (CH22 refresh)",
        "spec": (
            "Δm = (1/T) · Σ_t (M_m - M_b) / M_b ; both tasks higher-is-better. "
            "Pairing: per-fold paired across MTL B9 vs STL at seed=42 leak-free. "
            "PRIMARY = cat F1 + reg MRR ; SECONDARY = cat F1 + reg Acc@10 . "
            "All inputs are leak-free per-fold log_T (Phase 3 / paper-closure 2026-05-01)."
        ),
        "source_files": {
            "mtl_cat":  "phase1_perfold/<ST>_check2hgi_mtl_cat_pf.json",
            "mtl_reg":  "phase1_perfold/<ST>_check2hgi_mtl_reg_pf.json",
            "stl_cat":  "phase1_perfold/<ST>_check2hgi_cat_gru_5f50ep.json",
            "stl_reg":  "phase1_perfold/<ST>_check2hgi_reg_gethard_pf_5f50ep.json",
        },
        "states": {},
    }

    print(f"{'State':<5} {'metric':<10} {'Δm(%)':>8} {'σ':>6} {'n+/n−':>6} {'W+':>4} {'p>':>9} {'p2s':>9}")
    print("-" * 70)

    for st in STATES:
        e = extract_state(st)

        means = {
            "mtl_cat_f1_mean":     stats(e["mtl_cat_f1"])["mean"],
            "mtl_reg_acc10_mean":  stats(e["mtl_reg_acc10"])["mean"],
            "mtl_reg_mrr_mean":    stats(e["mtl_reg_mrr"])["mean"],
            "stl_cat_f1_mean":     stats(e["stl_cat_f1"])["mean"],
            "stl_reg_acc10_mean":  stats(e["stl_reg_acc10"])["mean"],
            "stl_reg_mrr_mean":    stats(e["stl_reg_mrr"])["mean"],
        }

        d_cat_f1   = relative(e["mtl_cat_f1"],    e["stl_cat_f1"])
        d_reg_mrr  = relative(e["mtl_reg_mrr"],   e["stl_reg_mrr"])
        d_reg_a10  = relative(e["mtl_reg_acc10"], e["stl_reg_acc10"])

        dm_primary   = per_fold_delta_m(d_cat_f1, d_reg_mrr)
        dm_secondary = per_fold_delta_m(d_cat_f1, d_reg_a10)

        # Wilcoxon: test Δm > 0 (MTL Pareto-positive)
        w_primary   = paired_against_zero(dm_primary)
        w_secondary = paired_against_zero(dm_secondary)

        # Per-task signed Wilcoxon for context
        w_cat = paired_against_zero(d_cat_f1)
        w_mrr = paired_against_zero(d_reg_mrr)
        w_a10 = paired_against_zero(d_reg_a10)

        out["states"][st] = {
            "n_folds": 5,
            "seed": 42,
            "absolute_means": means,
            "per_fold_relative_deltas": {
                "cat_f1":      d_cat_f1,
                "reg_mrr":     d_reg_mrr,
                "reg_acc10":   d_reg_a10,
            },
            "delta_m_primary_mrr": {
                "per_fold": dm_primary,
                "mean_pct": stats(dm_primary)["mean"] * 100,
                "std_pct":  stats(dm_primary)["std"] * 100,
                "wilcoxon": {
                    "W_plus": w_primary["wilcoxon_W_plus"],
                    "p_greater": w_primary["wilcoxon_p_greater"],
                    "p_two_sided": w_primary["wilcoxon_p_two_sided"],
                    "n_pos_n_neg": [w_primary["n_positive"], w_primary["n_negative"]],
                },
            },
            "delta_m_secondary_acc10": {
                "per_fold": dm_secondary,
                "mean_pct": stats(dm_secondary)["mean"] * 100,
                "std_pct":  stats(dm_secondary)["std"] * 100,
                "wilcoxon": {
                    "W_plus": w_secondary["wilcoxon_W_plus"],
                    "p_greater": w_secondary["wilcoxon_p_greater"],
                    "p_two_sided": w_secondary["wilcoxon_p_two_sided"],
                    "n_pos_n_neg": [w_secondary["n_positive"], w_secondary["n_negative"]],
                },
            },
            "per_task_wilcoxon": {
                "cat_f1": {
                    "delta_mean_pct": stats(d_cat_f1)["mean"] * 100,
                    "p_greater": w_cat["wilcoxon_p_greater"],
                    "p_two_sided": w_cat["wilcoxon_p_two_sided"],
                    "n_pos_n_neg": [w_cat["n_positive"], w_cat["n_negative"]],
                },
                "reg_mrr": {
                    "delta_mean_pct": stats(d_reg_mrr)["mean"] * 100,
                    "p_greater": w_mrr["wilcoxon_p_greater"],
                    "p_two_sided": w_mrr["wilcoxon_p_two_sided"],
                    "n_pos_n_neg": [w_mrr["n_positive"], w_mrr["n_negative"]],
                },
                "reg_acc10": {
                    "delta_mean_pct": stats(d_reg_a10)["mean"] * 100,
                    "p_greater": w_a10["wilcoxon_p_greater"],
                    "p_two_sided": w_a10["wilcoxon_p_two_sided"],
                    "n_pos_n_neg": [w_a10["n_positive"], w_a10["n_negative"]],
                },
            },
        }

        for label, dm, w in (("Δm-MRR", dm_primary, w_primary),
                             ("Δm-A10", dm_secondary, w_secondary)):
            print(f"{st:<5} {label:<10} {stats(dm)['mean']*100:+8.2f} "
                  f"{stats(dm)['std']*100:6.2f} "
                  f"{w['n_positive']}/{w['n_negative']:>1}    "
                  f"{w['wilcoxon_W_plus']:>4.1f}  "
                  f"{w['wilcoxon_p_greater']:.4f}   "
                  f"{w['wilcoxon_p_two_sided']:.4f}")

    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nSaved → {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    run()
