"""P4 + P5 paired Wilcoxon analysis (no scipy — pure Python).

This file is for offline computation while the SSD volume is read-locked.

P4: F49 3-way decomposition cells per fold (AL+AZ+FL n=5 paired)
P5: H3-alt vs B3 predecessor per fold (AL+AZ n=5 paired)

Per-fold values were extracted earlier from:
- AL/AZ MTL runs: results/check2hgi/{state}/mtlnet_*/folds/fold{i}_info.json
                  → diagnostic_best_epochs.next_region.metrics.top10_acc_indist
- FL F49 runs: /tmp/f49_data/.../folds + metrics
- STL F21c: docs/results/B3_baselines/stl_getnext_hard_{al,az}_5f50ep.json

Pairing assumption: all runs use --no-folds-cache + seed=42 → identical
StratifiedGroupKFold splits → fold-i-of-A is paired with fold-i-of-B.

Output: /tmp/check2hgi_drafts/p4_p5_wilcoxon_results.json + console summary.
"""
from __future__ import annotations

import json
import math
from itertools import product
from pathlib import Path
from typing import Sequence

OUT_DIR = Path("/tmp/check2hgi_drafts")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Per-fold values (extracted in this session from fold{i}_info.json)
# Metric: next_region.top10_acc_indist at diagnostic_best_epochs.next_region
# (per-task best epoch — the metric reg head was optimised against)
# ---------------------------------------------------------------------------

PERFOLD = {
    # F49 cells (AL+AZ from SSD; FL from /tmp val CSV at primary checkpoint epoch)
    "AL_frozen":   [0.7700, 0.7051, 0.7462, 0.7693, 0.7353],
    "AL_lossside": [0.7700, 0.7043, 0.7467, 0.7697, 0.7344],
    "AL_h3alt":    [0.7728, 0.7271, 0.7495, 0.7673, 0.7312],

    "AZ_frozen":   [0.6479, 0.6493, 0.6500, 0.5934, 0.6096],
    "AZ_lossside": [0.6477, 0.6479, 0.6484, 0.6030, 0.6290],
    "AZ_h3alt":    [0.6475, 0.6456, 0.6542, 0.6156, 0.6189],

    # FL F49 from /tmp val CSV (primary-checkpoint epoch lookup; mean ≈ archived)
    "FL_frozen":   [0.4975, 0.5142, 0.7893, 0.7662, 0.7469],
    "FL_lossside": [0.7054, 0.5191, 0.7112, 0.7662, 0.7932],
    "FL_h3alt":    [0.7401, 0.7438, 0.7311, 0.7191, 0.7486],

    # H3-alt cat F1 per-fold (also AL+AZ B3) — for P5
    "AL_h3alt_cat":[0.4017708898, 0.3849932551, 0.4245955646, 0.4240056574, 0.4026218355],  # from phase1_perfold AL_check2hgi_cat_gru_5f50ep (matches H3-alt cat numbers!)
    # NOTE: for P5 we need the actual H3-alt MTL cat F1 + B3 cat F1.
}

# ---------------------------------------------------------------------------
# B3 + H3-alt MTL cat-F1 + reg-Acc@10 per-fold (for P5)
# These were not all extracted in this session. Mark as PENDING — needs SSD access.
# ---------------------------------------------------------------------------
PERFOLD_PENDING = {
    "P5 AL B3 cat F1":   "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260424_0241/folds/fold{i}_info.json → diagnostic_best_epochs.next_category.metrics.f1",
    "P5 AL B3 reg Acc@10":"same dir → diagnostic_best_epochs.next_region.metrics.top10_acc_indist",
    "P5 AZ B3 cat F1":   "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260424_0137/folds/fold{i}_info.json → diagnostic_best_epochs.next_category.metrics.f1",
    "P5 AZ B3 reg Acc@10":"same dir → diagnostic_best_epochs.next_region.metrics.top10_acc_indist",
    "P5 AL/AZ H3-alt cat F1": "results/check2hgi/{alabama,arizona}/mtlnet_lr1.0e-04_bs2048_ep50_20260425_18{43,53}/folds/fold{i}_info.json → ...next_category.metrics.f1",
    "P5 AL/AZ H3-alt reg Acc@10": "same dirs → next_region.metrics.top10_acc_indist (subset already in PERFOLD as AL_h3alt / AZ_h3alt)",
}

# ---------------------------------------------------------------------------
# STL F21c per-fold reg Acc@10 — only AL fold1 was inspected this session.
# Full file: docs/results/B3_baselines/stl_getnext_hard_{al,az}_5f50ep.json
# Format: heads.next_getnext_hard.per_fold[i].top10_acc
# AL fold1 confirmed = 0.7077; need folds 2-5 + AZ all 5 → SSD read needed.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Wilcoxon signed-rank (exact, n ≤ 25) — pure Python
# ---------------------------------------------------------------------------

def signed_rank_stat(a: Sequence[float], b: Sequence[float]) -> tuple[float, list[float]]:
    """Returns (W+, deltas). Discards zero deltas (Pratt-equivalent for our purposes)."""
    deltas = [x - y for x, y in zip(a, b)]
    nz = [d for d in deltas if d != 0.0]
    abs_ranks = sorted(range(len(nz)), key=lambda i: abs(nz[i]))
    # Average ranks for ties (rare in float data)
    rank_of = [0.0] * len(nz)
    i = 0
    while i < len(nz):
        j = i
        while j + 1 < len(nz) and abs(nz[abs_ranks[j+1]]) == abs(nz[abs_ranks[i]]):
            j += 1
        avg = (i + j + 2) / 2  # ranks are 1-indexed
        for k in range(i, j+1):
            rank_of[abs_ranks[k]] = avg
        i = j + 1
    w_plus = sum(rank_of[i] for i in range(len(nz)) if nz[i] > 0)
    return w_plus, deltas


def exact_p_value(w_plus: float, n: int, alternative: str = "greater") -> float:
    """Exact two-sided / one-sided p-value for n ≤ 25 via enumeration over 2^n sign patterns.
    Assumes no zeros (enforced by signed_rank_stat returning non-zero ranks)."""
    if n == 0:
        return 1.0
    # Each rank from 1..n can be + or -; compute distribution of W+
    # We approximate ties as 0 (n is small, ties improbable in float data)
    ranks = list(range(1, n+1))
    counts = {}
    total = 0
    for signs in product([0, 1], repeat=n):
        w = sum(r for r, s in zip(ranks, signs) if s == 1)
        counts[w] = counts.get(w, 0) + 1
        total += 1
    # one-sided p
    if alternative == "greater":
        return sum(c for w, c in counts.items() if w >= w_plus) / total
    elif alternative == "less":
        return sum(c for w, c in counts.items() if w <= w_plus) / total
    else:  # two-sided
        # standard convention: 2 * min(p_greater, p_less), capped at 1
        pg = sum(c for w, c in counts.items() if w >= w_plus) / total
        pl = sum(c for w, c in counts.items() if w <= w_plus) / total
        return min(1.0, 2 * min(pg, pl))


def paired_t_p(deltas: Sequence[float]) -> tuple[float, float]:
    """Returns (t-stat, two-sided p) for paired t-test — exact under normality.
    Approximates p via t distribution; n=5 → df=4. Use scipy if available."""
    n = len(deltas)
    m = sum(deltas) / n
    var = sum((d - m)**2 for d in deltas) / (n - 1) if n > 1 else 0.0
    se = math.sqrt(var / n) if n > 0 else 0.0
    if se == 0:
        return float('inf') if m != 0 else 0.0, 0.0 if m != 0 else 1.0
    t_stat = m / se
    # 2-sided p from Student's t with df = n-1, computed via incomplete beta
    df = n - 1
    x = df / (df + t_stat**2)
    # Regularised incomplete beta I_x(df/2, 1/2) — series approximation good enough for our n
    # Use simple approximation: p ≈ 2 * (1 - cdf_t(|t|, df))
    # Lentz continued-fraction for incomplete beta, simplified
    def betacf(a, b, x):
        MAX = 200; EPS = 1e-12
        qab = a + b; qap = a + 1; qam = a - 1
        c = 1.0; d = 1.0 - qab * x / qap
        if abs(d) < EPS: d = EPS
        d = 1.0 / d; h = d
        for m in range(1, MAX):
            m2 = 2*m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < EPS: d = EPS
            c = 1.0 + aa / c
            if abs(c) < EPS: c = EPS
            d = 1.0 / d; h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            if abs(d) < EPS: d = EPS
            c = 1.0 + aa / c
            if abs(c) < EPS: c = EPS
            d = 1.0 / d
            delta = d * c; h *= delta
            if abs(delta - 1.0) < EPS: break
        return h
    a = df / 2.0; b = 0.5
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                  + a * math.log(x) + b * math.log(1 - x))
    if x < (a + 1) / (a + b + 2):
        ix = bt * betacf(a, b, x) / a
    else:
        ix = 1 - bt * betacf(b, a, 1 - x) / b
    p_two = ix
    return t_stat, p_two


def paired_test(a: Sequence[float], b: Sequence[float]) -> dict:
    if len(a) != len(b):
        return {"error": f"unequal lengths {len(a)} vs {len(b)}"}
    deltas = [x - y for x, y in zip(a, b)]
    n = len(a)
    nz = [d for d in deltas if d != 0]
    n_nz = len(nz)
    w_plus, _ = signed_rank_stat(a, b)
    p_greater = exact_p_value(w_plus, n_nz, "greater")
    p_less = exact_p_value(w_plus, n_nz, "less")
    p_two = exact_p_value(w_plus, n_nz, "two-sided")
    t_stat, t_p = paired_t_p(deltas)
    return {
        "n": n,
        "n_paired_nonzero": n_nz,
        "a_mean": sum(a) / n,
        "b_mean": sum(b) / n,
        "delta_mean": sum(deltas) / n,
        "delta_mean_pp": sum(deltas) / n * 100,
        "deltas": deltas,
        "n_positive": sum(1 for d in deltas if d > 0),
        "n_negative": sum(1 for d in deltas if d < 0),
        "n_zero": sum(1 for d in deltas if d == 0),
        "wilcoxon_W_plus": w_plus,
        "wilcoxon_p_greater": p_greater,
        "wilcoxon_p_less": p_less,
        "wilcoxon_p_two_sided": p_two,
        "paired_t_stat": t_stat,
        "paired_t_p_two_sided": t_p,
    }


def fmt(t: dict) -> str:
    if "error" in t:
        return t["error"]
    return (
        f"Δ={t['delta_mean_pp']:+6.2f}pp  "
        f"n+/n−={t['n_positive']}/{t['n_negative']}  "
        f"W+={t['wilcoxon_W_plus']:.1f}  "
        f"W_p_greater={t['wilcoxon_p_greater']:.4f}  "
        f"t_p_two={t['paired_t_p_two_sided']:.4f}"
    )


def run() -> None:
    out: dict = {
        "analysis": "P4 + P5 paired Wilcoxon (offline, no scipy)",
        "metric": "next_region.top10_acc_indist",
        "fold_split": "StratifiedGroupKFold seed=42 (--no-folds-cache; same across all cells)",
        "note": "P4 only uses values extractable from fold{i}_info.json or val CSV. "
                "P5 (H3-alt vs B3) requires per-fold extraction not done in this session — "
                "see PERFOLD_PENDING for paths needed.",
        "P4_F49_decomposition": {},
        "P5_H3alt_vs_B3": {
            "status": "PENDING — extraction blocked by SSD permission lock; paths in PERFOLD_PENDING",
            "needed_paths": PERFOLD_PENDING,
        },
    }

    print("=== P4 — F49 decomposition (next_region top10_acc_indist) ===\n")
    for state in ("AL", "AZ", "FL"):
        frozen = PERFOLD[f"{state}_frozen"]
        loss   = PERFOLD[f"{state}_lossside"]
        h3alt  = PERFOLD[f"{state}_h3alt"]
        cell = {
            "frozen_per_fold": frozen,
            "lossside_per_fold": loss,
            "h3alt_per_fold": h3alt,
            "co_adapt (loss − frozen)": paired_test(loss, frozen),
            "transfer (full − loss)": paired_test(h3alt, loss),
            "total_cat (full − frozen)": paired_test(h3alt, frozen),
        }
        out["P4_F49_decomposition"][state] = cell
        print(f"--- {state} ---")
        for label, key in [
            ("co-adapt (loss − frozen)", "co_adapt (loss − frozen)"),
            ("transfer (full − loss)", "transfer (full − loss)"),
            ("total cat (full − frozen)", "total_cat (full − frozen)"),
        ]:
            print(f"  {label:30s}  {fmt(cell[key])}")
        print()

    out_path = OUT_DIR / "p4_p5_wilcoxon_results.json"
    out_path.write_text(json.dumps(out, indent=2, default=str))
    print(f"\n✓ wrote {out_path}")


if __name__ == "__main__":
    run()
