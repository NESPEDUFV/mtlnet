"""F50 Tier 1 — quick post-run comparison printer.

Given a Tier-1 result JSON (e.g. F50_T1_2_HSM_FL or F50_T1_3_FAMO_FL),
compares against:
  - flat STL `next_getnext_hard` per state (B3_baselines)
  - MTL H3-alt champion per state (existing `mtlnet_*` runs)

For STL HSM: compares HSM vs flat STL (acceptance: HSM ≥ flat within σ).
For MTL with HSM/FAMO/AlignedMTL: compares to MTL H3-alt champion +
matched-head STL ceiling (acceptance: closes ≥ 3 pp of architectural gap).

Pairing: same StratifiedGroupKFold seed=42 across all cells → fold-i paired.

Usage:
    python scripts/analysis/f50_t1_compare.py --variant stl_hsm --state florida
    python scripts/analysis/f50_t1_compare.py --variant mtl_hsm --state florida
    python scripts/analysis/f50_t1_compare.py --variant mtl_famo --state florida
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from itertools import product

REPO = Path(__file__).resolve().parents[2]


# Path templates
STL_FLAT_PATH = REPO / "docs/results/B3_baselines/stl_getnext_hard_{state_short}_5f50ep.json"

STL_HSM_PATH = REPO / "docs/results/P1/region_head_{state}_region_5f_50ep_F50_T1_2_HSM_{state_upper}_5f50ep.json"

MTL_H3ALT_PATHS = {
    "florida": REPO / "results/check2hgi/florida/mtlnet_lr1.0e-04_bs1024_ep50_20260426_0045",
    "alabama": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1843",
    "arizona": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1853",
}

STATE_SHORT = {"florida": "fl", "alabama": "al", "arizona": "az"}


def load_stl_flat(state: str) -> list[float]:
    """STL flat next_getnext_hard per-fold top10_acc."""
    p = Path(str(STL_FLAT_PATH).format(state_short=STATE_SHORT[state]))
    with open(p) as f:
        d = json.load(f)
    folds = d["heads"]["next_getnext_hard"]["per_fold"]
    return [fold["top10_acc"] for fold in folds]


def load_stl_hsm(state: str, tag: str = None) -> dict:
    """STL HSM result JSON (output of p1_region_head_ablation.py)."""
    if tag is None:
        tag = f"F50_T1_2_HSM_{STATE_SHORT[state].upper()}_5f50ep"
    candidates = list(REPO.glob(f"docs/results/P1/region_head_{state}_region_5f_50ep_{tag}.json"))
    if not candidates:
        candidates = list(REPO.glob(f"docs/results/P1/region_head_{state}_*HSM*.json"))
    if not candidates:
        raise FileNotFoundError(f"No STL HSM result found for {state} with tag {tag}")
    with open(candidates[0]) as f:
        return json.load(f)


def load_mtl_h3alt_per_fold(state: str) -> dict:
    """MTL H3-alt champion per-fold top10_acc_indist + cat F1."""
    folds_dir = MTL_H3ALT_PATHS[state] / "folds"
    cat_f1, reg_top10_indist = [], []
    for i in range(1, 6):
        with open(folds_dir / f"fold{i}_info.json") as f:
            d = json.load(f)
        cat_f1.append(d["diagnostic_best_epochs"]["next_category"]["metrics"]["f1"])
        reg_top10_indist.append(d["diagnostic_best_epochs"]["next_region"]["metrics"]["top10_acc_indist"])
    return {"cat_f1": cat_f1, "reg_top10_indist": reg_top10_indist}


# Pure-python paired Wilcoxon (reused from f50_delta_m.py)
def signed_rank_w_plus(deltas):
    nz = [d for d in deltas if d != 0]
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


def exact_p(w_plus, n, alternative="greater"):
    if n == 0:
        return 1.0
    counts = {}
    total = 0
    for signs in product([0, 1], repeat=n):
        w = sum(r for r, s in zip(range(1, n+1), signs) if s == 1)
        counts[w] = counts.get(w, 0) + 1
        total += 1
    if alternative == "greater":
        return sum(c for w, c in counts.items() if w >= w_plus) / total
    elif alternative == "less":
        return sum(c for w, c in counts.items() if w <= w_plus) / total
    pg = sum(c for w, c in counts.items() if w >= w_plus) / total
    pl = sum(c for w, c in counts.items() if w <= w_plus) / total
    return min(1.0, 2 * min(pg, pl))


def stats(values):
    n = len(values)
    if n == 0:
        return (0.0, 0.0)
    m = sum(values) / n
    var = sum((v - m) ** 2 for v in values) / (n - 1) if n > 1 else 0.0
    return m, math.sqrt(var)


def paired_compare(a, b, label_a, label_b):
    deltas = [x - y for x, y in zip(a, b)]
    n = len(deltas)
    n_pos = sum(1 for d in deltas if d > 0)
    n_neg = sum(1 for d in deltas if d < 0)
    w_plus, n_nz = signed_rank_w_plus(deltas)
    p_g = exact_p(w_plus, n_nz, "greater")
    p_t = exact_p(w_plus, n_nz, "two-sided")
    a_m, a_s = stats(a)
    b_m, b_s = stats(b)
    d_m, d_s = stats(deltas)
    print(f"  {label_a:30s}: {a_m*100:6.2f} ± {a_s*100:5.2f}  per-fold: {[f'{v*100:.2f}' for v in a]}")
    print(f"  {label_b:30s}: {b_m*100:6.2f} ± {b_s*100:5.2f}  per-fold: {[f'{v*100:.2f}' for v in b]}")
    print(f"  Δ ({label_a} − {label_b}):  {d_m*100:+.2f} ± {d_s*100:.2f} pp  n+/n−={n_pos}/{n_neg}  W_p_greater={p_g:.4f}  W_p_two_sided={p_t:.4f}")


def cmd_stl_hsm(state: str) -> None:
    print(f"=== F50 T1.2 STL HSM vs flat STL (state={state}) ===\n")
    flat = load_stl_flat(state)
    hsm_json = load_stl_hsm(state)
    # The p1_region_head_ablation.py JSON has per-head per-fold structure
    head_key = "next_getnext_hard_hsm"
    if "heads" not in hsm_json or head_key not in hsm_json["heads"]:
        print(f"FATAL: heads.{head_key} not in result JSON. heads keys={list(hsm_json.get('heads', {}).keys())}")
        sys.exit(1)
    hsm_folds = hsm_json["heads"][head_key]["per_fold"]
    hsm_top10 = [fold["top10_acc"] for fold in hsm_folds]
    paired_compare(hsm_top10, flat, "STL HSM top10_acc", "STL flat top10_acc")
    hsm_mean, _ = stats(hsm_top10)
    flat_mean, _ = stats(flat)
    print()
    if hsm_mean >= flat_mean - 0.01:
        print(f"✓ ACCEPTANCE: STL HSM ({hsm_mean*100:.2f}%) ≥ STL flat ({flat_mean*100:.2f}%) within 1 pp.")
        print(f"  Architecture preserved at the head level → proceed to MTL run with HSM.")
    else:
        print(f"✗ STL HSM ({hsm_mean*100:.2f}%) < STL flat ({flat_mean*100:.2f}%) by {(flat_mean - hsm_mean)*100:.2f} pp.")
        print(f"  HSM head architecture costs reg accuracy at the STL level. MTL run probably wasted.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=["stl_hsm", "mtl_hsm", "mtl_famo", "mtl_aligned"])
    parser.add_argument("--state", required=True)
    args = parser.parse_args()
    if args.variant == "stl_hsm":
        cmd_stl_hsm(args.state)
    else:
        # MTL variants: compare against MTL H3-alt + matched-head STL ceiling
        # Implementation deferred until those JSONs exist.
        print(f"variant {args.variant} not yet implemented; will add once T1 results land.")


if __name__ == "__main__":
    main()
