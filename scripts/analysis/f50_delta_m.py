"""F50 Tier 0 — Joint Δm computation with paired Wilcoxon.

Computes the MTL-survey-standard Δm (Maninis CVPR 2019 / Vandenhende TPAMI 2021)
across AL+AZ+FL on the H3-alt champion vs matched-head STL ceilings.

Δm = (1/T) · Σ_t (-1)^l_t · (M_{m,t} - M_{b,t}) / M_{b,t}    (× 100%)

Both tasks are higher-is-better (l_t = 0).

Pairing: all runs use --no-folds-cache + seed=42 → identical StratifiedGroupKFold
splits across cells → fold-i-of-A is paired with fold-i-of-B.

Metric-definition caveat:
  - MTL fold_info reports `top10_acc_indist` (in-distribution only).
  - STL B3_baselines reports `top10_acc` (full distribution).
  - These are NOT apples-to-apples (~0.7-1 pp drift at AL, ~0.6-1.1 pp at FL per F49 docs).

Therefore PRIMARY Δm uses cat F1 + reg MRR (clean, both files share the same
non-_indist definition). SECONDARY uses top5_acc (also clean). top10 reported
with explicit caveat as a sanity check against the F49 results doc.

Output: docs/results/paired_tests/F50_T0_delta_m.json + console.
"""
from __future__ import annotations

import json
import math
from itertools import product
from pathlib import Path
from typing import Sequence

REPO = Path(__file__).resolve().parents[2]

# --- run paths (per F50 plan) --------------------------------------------------

MTL_PATHS = {
    "AL": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1843/folds",
    "AZ": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1853/folds",
    "FL": REPO / "results/check2hgi/florida/mtlnet_lr1.0e-04_bs1024_ep50_20260426_0045/folds",
}

STL_CAT_PATHS = {
    # AL/AZ: phase1_perfold aggregated JSON (key fold_{0..4} -> {f1, accuracy, mrr})
    "AL": ("phase1_aggregated",
           REPO / "docs/results/phase1_perfold/AL_check2hgi_cat_gru_5f50ep.json"),
    "AZ": ("phase1_aggregated",
           REPO / "docs/results/phase1_perfold/AZ_check2hgi_cat_gru_5f50ep.json"),
    # FL: F37 P1 (2026-04-28 09:31) — single-task run, fold_info per-fold dirs
    "FL": ("fold_info",
           REPO / "results/check2hgi/florida/next_lr1.0e-04_bs2048_ep50_20260428_0931/folds"),
}

STL_REG_PATHS = {
    "AL": REPO / "docs/results/B3_baselines/stl_getnext_hard_al_5f50ep.json",
    "AZ": REPO / "docs/results/B3_baselines/stl_getnext_hard_az_5f50ep.json",
    "FL": REPO / "docs/results/B3_baselines/stl_getnext_hard_fl_5f50ep.json",
}

OUT_JSON = REPO / "docs/results/paired_tests/F50_T0_delta_m.json"

# ------------------------------------------------------------------------------
# Per-fold extractors
# ------------------------------------------------------------------------------

def extract_mtl(state: str) -> dict[str, list[float]]:
    """MTL H3-alt: read fold_info.json × 5, per-task-best-epoch metrics."""
    folds_dir = MTL_PATHS[state]
    cat_f1, reg_mrr, reg_top10_indist, reg_top5 = [], [], [], []
    for i in range(1, 6):
        with open(folds_dir / f"fold{i}_info.json") as f:
            d = json.load(f)
        cm = d["diagnostic_best_epochs"]["next_category"]["metrics"]
        rm = d["diagnostic_best_epochs"]["next_region"]["metrics"]
        cat_f1.append(cm["f1"])
        reg_mrr.append(rm["mrr"])
        reg_top10_indist.append(rm["top10_acc_indist"])
        reg_top5.append(rm["top5_acc"])
    return {
        "cat_f1": cat_f1,
        "reg_mrr": reg_mrr,
        "reg_top10_indist": reg_top10_indist,
        "reg_top5": reg_top5,
    }


def extract_stl_cat(state: str) -> dict[str, list[float]]:
    """STL `next_gru` cat: AL/AZ from phase1 aggregated JSON, FL from F37 P1 fold_info."""
    kind, path = STL_CAT_PATHS[state]
    cat_f1, cat_mrr = [], []
    if kind == "phase1_aggregated":
        with open(path) as f:
            d = json.load(f)
        for i in range(5):
            entry = d[f"fold_{i}"]
            cat_f1.append(entry["f1"])
            cat_mrr.append(entry.get("mrr"))
    elif kind == "fold_info":
        for i in range(1, 6):
            with open(path / f"fold{i}_info.json") as f:
                d = json.load(f)
            m = d["diagnostic_best_epochs"]["next"]["metrics"]
            cat_f1.append(m["f1"])
            cat_mrr.append(m.get("mrr"))
    else:
        raise ValueError(f"Unknown STL_CAT kind: {kind}")
    return {"cat_f1": cat_f1, "cat_mrr": cat_mrr}


def extract_stl_reg(state: str) -> dict[str, list[float]]:
    """STL `next_getnext_hard` reg: aggregated JSON → heads.next_getnext_hard.per_fold[0..4]."""
    with open(STL_REG_PATHS[state]) as f:
        d = json.load(f)
    folds = d["heads"]["next_getnext_hard"]["per_fold"]
    return {
        "reg_mrr": [fold["mrr"] for fold in folds],
        "reg_top10": [fold["top10_acc"] for fold in folds],     # NOTE: full-distribution
        "reg_top5": [fold["top5_acc"] for fold in folds],
    }


# ------------------------------------------------------------------------------
# Wilcoxon signed-rank (exact, n ≤ 25) — pure Python; reused from p4_p5
# ------------------------------------------------------------------------------

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


def exact_p(w_plus: float, n: int, alternative: str = "greater") -> float:
    if n == 0:
        return 1.0
    counts: dict[float, int] = {}
    total = 0
    for signs in product([0, 1], repeat=n):
        w = sum(r for r, s in zip(range(1, n+1), signs) if s == 1)
        counts[w] = counts.get(w, 0) + 1
        total += 1
    if alternative == "greater":
        return sum(c for w, c in counts.items() if w >= w_plus) / total
    elif alternative == "less":
        return sum(c for w, c in counts.items() if w <= w_plus) / total
    else:
        pg = sum(c for w, c in counts.items() if w >= w_plus) / total
        pl = sum(c for w, c in counts.items() if w <= w_plus) / total
        return min(1.0, 2 * min(pg, pl))


def stats(values: Sequence[float]) -> dict[str, float]:
    n = len(values)
    if n == 0:
        return {"n": 0, "mean": float("nan"), "std": float("nan")}
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    return {"n": n, "mean": m, "std": math.sqrt(var)}


def paired_test(a: Sequence[float], b: Sequence[float]) -> dict:
    """One-sided (greater) + two-sided paired Wilcoxon. a > b ↔ MTL > STL."""
    deltas = [x - y for x, y in zip(a, b)]
    n = len(deltas)
    n_pos = sum(1 for d in deltas if d > 0)
    n_neg = sum(1 for d in deltas if d < 0)
    w_plus, n_nz = signed_rank_w_plus(deltas)
    return {
        "deltas": deltas,
        "n": n,
        "n_paired_nonzero": n_nz,
        "delta_mean": sum(deltas) / n,
        "n_positive": n_pos,
        "n_negative": n_neg,
        "wilcoxon_W_plus": w_plus,
        "wilcoxon_p_greater": exact_p(w_plus, n_nz, "greater"),
        "wilcoxon_p_less": exact_p(w_plus, n_nz, "less"),
        "wilcoxon_p_two_sided": exact_p(w_plus, n_nz, "two-sided"),
        "a_summary": stats(a),
        "b_summary": stats(b),
    }


# ------------------------------------------------------------------------------
# Δm computation
# ------------------------------------------------------------------------------

def relative_delta(m_m: list[float], m_b: list[float]) -> list[float]:
    """Δ_t per fold: (m_m - m_b) / m_b   (relative, NOT yet × 100)."""
    return [(mm - mb) / mb for mm, mb in zip(m_m, m_b)]


def per_fold_delta_m(deltas_cat: list[float], deltas_reg: list[float]) -> list[float]:
    """Δm_i = mean of relative-Δs across tasks (T=2)."""
    return [(c + r) / 2 for c, r in zip(deltas_cat, deltas_reg)]


# ------------------------------------------------------------------------------
# Driver
# ------------------------------------------------------------------------------

def run() -> None:
    out: dict = {
        "analysis": "F50 Tier 0 — joint Δm + paired Wilcoxon",
        "spec": (
            "Δm = (1/T) · Σ_t (-1)^l_t · (M_m - M_b) / M_b ; both tasks higher-is-better. "
            "Pairing: --no-folds-cache + seed=42 + StratifiedGroupKFold. "
            "Primary: cat F1 + reg MRR (clean). Secondary: cat F1 + reg top5_acc (clean). "
            "Tertiary: cat F1 + reg top10 — METRIC MISMATCH (MTL=top10_acc_indist vs STL=top10_acc full-dist), reported with caveat."
        ),
        "states": {},
    }

    for state in ("AL", "AZ", "FL"):
        mtl = extract_mtl(state)
        stl_cat = extract_stl_cat(state)
        stl_reg = extract_stl_reg(state)

        # absolute means for sanity
        means_check = {
            "MTL_cat_f1_mean": stats(mtl["cat_f1"])["mean"],
            "MTL_reg_top10_indist_mean": stats(mtl["reg_top10_indist"])["mean"],
            "MTL_reg_mrr_mean": stats(mtl["reg_mrr"])["mean"],
            "STL_cat_f1_mean": stats(stl_cat["cat_f1"])["mean"],
            "STL_reg_top10_mean": stats(stl_reg["reg_top10"])["mean"],
            "STL_reg_mrr_mean": stats(stl_reg["reg_mrr"])["mean"],
        }

        # per-fold relative deltas
        d_cat_f1 = relative_delta(mtl["cat_f1"], stl_cat["cat_f1"])
        d_reg_mrr = relative_delta(mtl["reg_mrr"], stl_reg["reg_mrr"])
        d_reg_top10 = relative_delta(mtl["reg_top10_indist"], stl_reg["reg_top10"])  # mismatched
        d_reg_top5 = relative_delta(mtl["reg_top5"], stl_reg["reg_top5"])

        # per-fold Δm
        dm_mrr = per_fold_delta_m(d_cat_f1, d_reg_mrr)
        dm_top10 = per_fold_delta_m(d_cat_f1, d_reg_top10)
        dm_top5 = per_fold_delta_m(d_cat_f1, d_reg_top5)

        # paired Wilcoxon: delta from zero ↔ MTL > STL (positive Δm)
        wmrr = paired_test([2 * dm for dm in dm_mrr], [0.0] * len(dm_mrr))  # equivalent to test against zero
        # Simpler: test whether dm > 0 by running paired_test against zeros directly
        wmrr_vs_zero = paired_test(dm_mrr, [0.0] * len(dm_mrr))
        wtop10_vs_zero = paired_test(dm_top10, [0.0] * len(dm_top10))
        wtop5_vs_zero = paired_test(dm_top5, [0.0] * len(dm_top5))

        # Also: Pareto-domination check per fold
        pareto_dom_mrr = sum(1 for c, r in zip(d_cat_f1, d_reg_mrr) if c > 0 and r > 0)
        pareto_dom_top10 = sum(1 for c, r in zip(d_cat_f1, d_reg_top10) if c > 0 and r > 0)
        pareto_neg_mrr = sum(1 for c, r in zip(d_cat_f1, d_reg_mrr) if c < 0 and r < 0)
        pareto_neg_top10 = sum(1 for c, r in zip(d_cat_f1, d_reg_top10) if c < 0 and r < 0)

        out["states"][state] = {
            "absolute_means_sanity": means_check,
            "per_fold": {
                "MTL_cat_f1": mtl["cat_f1"],
                "STL_cat_f1": stl_cat["cat_f1"],
                "MTL_reg_top10_indist": mtl["reg_top10_indist"],
                "STL_reg_top10": stl_reg["reg_top10"],
                "MTL_reg_mrr": mtl["reg_mrr"],
                "STL_reg_mrr": stl_reg["reg_mrr"],
                "MTL_reg_top5": mtl["reg_top5"],
                "STL_reg_top5": stl_reg["reg_top5"],
            },
            "per_fold_relative_deltas": {
                "delta_cat_f1": d_cat_f1,
                "delta_reg_mrr": d_reg_mrr,
                "delta_reg_top10_MISMATCHED": d_reg_top10,
                "delta_reg_top5": d_reg_top5,
            },
            "per_fold_delta_m": {
                "primary_mrr":   dm_mrr,
                "secondary_top5": dm_top5,
                "tertiary_top10_MISMATCHED": dm_top10,
            },
            "delta_m_summary": {
                "primary_mrr":   {**stats(dm_mrr),   "wilcoxon": wmrr_vs_zero},
                "secondary_top5":{**stats(dm_top5),  "wilcoxon": wtop5_vs_zero},
                "tertiary_top10_MISMATCHED": {**stats(dm_top10), "wilcoxon": wtop10_vs_zero},
            },
            "pareto_per_fold": {
                "n_pareto_dominate_mtl_mrr": pareto_dom_mrr,
                "n_pareto_dominate_mtl_top10": pareto_dom_top10,
                "n_pareto_dominated_by_stl_mrr": pareto_neg_mrr,
                "n_pareto_dominated_by_stl_top10": pareto_neg_top10,
            },
        }

        # Console output
        print(f"=== {state} (n_regions = {{'AL': 1109, 'AZ': 1547, 'FL': 4702}}[state]) ===")
        print(f"  MTL cat F1:    {means_check['MTL_cat_f1_mean']*100:6.2f}%")
        print(f"  STL cat F1:    {means_check['STL_cat_f1_mean']*100:6.2f}%")
        print(f"  MTL reg MRR:   {means_check['MTL_reg_mrr_mean']*100:6.2f}%")
        print(f"  STL reg MRR:   {means_check['STL_reg_mrr_mean']*100:6.2f}%")
        print(f"  MTL reg top10_indist: {means_check['MTL_reg_top10_indist_mean']*100:6.2f}%")
        print(f"  STL reg top10:        {means_check['STL_reg_top10_mean']*100:6.2f}%  (full-dist)")
        print()
        for label, dm, w in [
            ("PRIMARY  (cat F1 + reg MRR)         ", dm_mrr, wmrr_vs_zero),
            ("SECONDARY(cat F1 + reg top5_acc)    ", dm_top5, wtop5_vs_zero),
            ("TERTIARY (cat F1 + reg top10) MISMATCH", dm_top10, wtop10_vs_zero),
        ]:
            mean_pct = stats(dm)['mean'] * 100
            std_pct = stats(dm)['std'] * 100
            print(
                f"  {label}: Δm = {mean_pct:+6.2f}% ± {std_pct:5.2f}%  "
                f"n+/n−={w['n_positive']}/{w['n_negative']}  "
                f"W_p_greater={w['wilcoxon_p_greater']:.4f}  "
                f"W_p_two_sided={w['wilcoxon_p_two_sided']:.4f}"
            )
        print()

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n✓ wrote {OUT_JSON}")


if __name__ == "__main__":
    run()
