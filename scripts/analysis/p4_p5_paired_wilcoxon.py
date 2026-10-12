"""P4 + P5 paired Wilcoxon analysis (study/check2hgi).

P4: F49 3-way decomposition cells per fold
    - architecture lift: (frozen_λ0 − STL F21c)
    - co-adaptation:     (loss_λ0 − frozen_λ0)
    - cat-supervision:   (Full MTL H3-alt − loss_λ0)

P5: H3-alt vs B3 predecessor per fold (cat F1 + reg Acc@10)

All runs share seed=42 + StratifiedGroupKFold; same fold split → paired Wilcoxon valid.

Outputs:
    docs/results/paired_tests/F49_decomposition_wilcoxon.json
    docs/results/paired_tests/H3alt_vs_B3_wilcoxon.json
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Optional

from scipy import stats

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
DOC_RESULTS = REPO / "docs" / "studies" / "check2hgi" / "results"
PAIRED = DOC_RESULTS / "paired_tests"
PAIRED.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Run paths (from F49_LAMBDA0_DECOMPOSITION_RESULTS.md + F48_H3 docs)
# ---------------------------------------------------------------------------
H3ALT_RUNS = {
    "AL": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1843",
    "AZ": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260425_1853",
    "FL": REPO / "results/check2hgi/florida/mtlnet_lr1.0e-04_bs1024_ep50_20260426_0045",
}

B3_RUNS = {
    "AL": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260424_0241",
    "AZ": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260424_0137",
}

F49_FROZEN = {
    "AL": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260427_1019",
    "AZ": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260427_1049",
    # FL fold-info lives in /tmp/f49_data/ (3853 = frozen)
    "FL": Path("/tmp/f49_data/results/check2hgi/florida/mtlnet_lr1.0e-04_bs1024_ep50_20260427_1853"),
}
F49_LOSSSIDE = {
    "AL": REPO / "results/check2hgi/alabama/mtlnet_lr1.0e-04_bs2048_ep50_20260427_1008",
    "AZ": REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260427_1029",
    "FL": Path("/tmp/f49_data/results/check2hgi/florida/mtlnet_lr1.0e-04_bs1024_ep50_20260427_1541"),
}

STL_F21C_AGG = {
    "AL": DOC_RESULTS / "B3_baselines/stl_getnext_hard_al_5f50ep.json",
    "AZ": DOC_RESULTS / "B3_baselines/stl_getnext_hard_az_5f50ep.json",
    # FL pending — no F21c FL yet (F37 4050 task)
}


def perfold_from_fold_info(rundir: Path, task: str, metric: str) -> Optional[list[float]]:
    """Read fold{i}_info.json files; return per-fold values from diagnostic_best_epochs[task].metrics[metric]."""
    folds_dir = rundir / "folds"
    if not folds_dir.is_dir():
        return None
    info_files = sorted(
        f for f in folds_dir.iterdir() if f.name.startswith("fold") and f.name.endswith("_info.json")
    )
    out: list[float] = []
    for f in info_files:
        d = json.loads(f.read_text())
        diag = d.get("diagnostic_best_epochs", {}).get(task, {}).get("metrics", {})
        if metric not in diag:
            return None
        out.append(diag[metric])
    return out if len(out) >= 2 else None


def perfold_from_stl_f21c(json_path: Path, head: str = "next_getnext_hard", metric: str = "top10_acc") -> Optional[list[float]]:
    if not json_path.exists():
        return None
    d = json.loads(json_path.read_text())
    per_fold = d.get("heads", {}).get(head, {}).get("per_fold")
    if not per_fold:
        return None
    return [pf[metric] for pf in per_fold]


def paired_test(a: list[float], b: list[float], alt: str = "two-sided") -> dict:
    """Paired Wilcoxon signed-rank + paired t-test on deltas (a−b)."""
    deltas = [x - y for x, y in zip(a, b)]
    n = len(deltas)
    out = {
        "n": n,
        "a_mean": sum(a) / n,
        "b_mean": sum(b) / n,
        "delta_mean": sum(deltas) / n,
        "deltas": deltas,
        "n_positive": sum(1 for d in deltas if d > 0),
        "n_negative": sum(1 for d in deltas if d < 0),
        "n_zero": sum(1 for d in deltas if d == 0),
    }
    # Wilcoxon (n=5 too small for Pratt with full ties — use default)
    try:
        w_two = stats.wilcoxon(a, b, alternative="two-sided")
        w_greater = stats.wilcoxon(a, b, alternative="greater")
        w_less = stats.wilcoxon(a, b, alternative="less")
        out["wilcoxon_two_sided"] = {"stat": float(w_two.statistic), "p": float(w_two.pvalue)}
        out["wilcoxon_greater"] = {"stat": float(w_greater.statistic), "p": float(w_greater.pvalue)}
        out["wilcoxon_less"] = {"stat": float(w_less.statistic), "p": float(w_less.pvalue)}
    except Exception as e:
        out["wilcoxon_error"] = str(e)
    # Paired t-test
    try:
        t = stats.ttest_rel(a, b)
        out["paired_t"] = {"stat": float(t.statistic), "p_two_sided": float(t.pvalue)}
    except Exception as e:
        out["paired_t_error"] = str(e)
    return out


# ---------------------------------------------------------------------------
# P4 — F49 decomposition Wilcoxon
# ---------------------------------------------------------------------------

def run_p4() -> dict:
    out: dict = {
        "task": "next_region",
        "metric": "top10_acc_indist (F49 cells); top10_acc (STL F21c)",
        "regime": "H3-alt: --scheduler constant --cat-lr 1e-3 --reg-lr 3e-3 --shared-lr 1e-3; STL: F21c",
        "fold_split": "StratifiedGroupKFold seed=42 (same across all cells; --no-folds-cache)",
        "states": {},
    }
    for state in ("AL", "AZ", "FL"):
        cell: dict = {}
        frozen = perfold_from_fold_info(F49_FROZEN[state], "next_region", "top10_acc_indist")
        loss = perfold_from_fold_info(F49_LOSSSIDE[state], "next_region", "top10_acc_indist")
        h3alt = perfold_from_fold_info(H3ALT_RUNS[state], "next_region", "top10_acc_indist")
        cell["frozen_per_fold"] = frozen
        cell["lossside_per_fold"] = loss
        cell["h3alt_per_fold"] = h3alt
        # STL F21c (only AL+AZ available)
        stl = None
        if state in STL_F21C_AGG:
            stl = perfold_from_stl_f21c(STL_F21C_AGG[state])
        cell["stl_f21c_per_fold"] = stl

        if frozen and loss and len(frozen) == len(loss):
            cell["test_co_adapt_loss_minus_frozen"] = paired_test(loss, frozen, alt="greater")
        if loss and h3alt and len(loss) == len(h3alt):
            cell["test_transfer_h3alt_minus_loss"] = paired_test(h3alt, loss, alt="greater")
        if frozen and h3alt and len(frozen) == len(h3alt):
            cell["test_total_cat_h3alt_minus_frozen"] = paired_test(h3alt, frozen, alt="greater")
        if stl and frozen and len(stl) == len(frozen):
            cell["test_architecture_frozen_minus_stl"] = paired_test(frozen, stl, alt="greater")
        if stl and h3alt and len(stl) == len(h3alt):
            cell["test_full_h3alt_minus_stl"] = paired_test(h3alt, stl, alt="greater")
        out["states"][state] = cell
    return out


# ---------------------------------------------------------------------------
# P5 — H3-alt vs B3 predecessor Wilcoxon
# ---------------------------------------------------------------------------

def run_p5() -> dict:
    out: dict = {
        "comparison": "H3-alt (per-head LR; constant) vs B3 predecessor (OneCycleLR max_lr=3e-3)",
        "fold_split": "StratifiedGroupKFold seed=42 (same across both regimes)",
        "metrics": {},
    }
    # Cat F1 and reg Acc@10
    for metric_label, task, metric in [
        ("cat_f1", "next_category", "f1"),
        ("reg_top10_acc_indist", "next_region", "top10_acc_indist"),
    ]:
        per_state: dict = {}
        for state in ("AL", "AZ"):  # B3 has only AL+AZ at 5f
            h3 = perfold_from_fold_info(H3ALT_RUNS[state], task, metric)
            b3 = perfold_from_fold_info(B3_RUNS[state], task, metric)
            cell: dict = {"h3alt_per_fold": h3, "b3_per_fold": b3}
            if h3 and b3 and len(h3) == len(b3):
                cell["test_h3alt_minus_b3"] = paired_test(h3, b3, alt="greater")
            per_state[state] = cell
        out["metrics"][metric_label] = per_state
    return out


def main() -> None:
    p4 = run_p4()
    p5 = run_p5()
    p4_path = PAIRED / "F49_decomposition_wilcoxon.json"
    p5_path = PAIRED / "H3alt_vs_B3_wilcoxon.json"
    p4_path.write_text(json.dumps(p4, indent=2))
    p5_path.write_text(json.dumps(p5, indent=2))
    print(f"✓ Wrote {p4_path.relative_to(REPO)}")
    print(f"✓ Wrote {p5_path.relative_to(REPO)}")

    # Compact CLI summary
    print("\n=== P4 — F49 decomposition (next_region top10_acc_indist) ===")
    for state, cell in p4["states"].items():
        for label, key in [
            ("co-adapt (loss − frozen)", "test_co_adapt_loss_minus_frozen"),
            ("transfer (full − loss)", "test_transfer_h3alt_minus_loss"),
            ("total cat (full − frozen)", "test_total_cat_h3alt_minus_frozen"),
            ("architecture (frozen − STL)", "test_architecture_frozen_minus_stl"),
            ("full vs STL", "test_full_h3alt_minus_stl"),
        ]:
            t = cell.get(key)
            if not t:
                continue
            ws = t.get("wilcoxon_greater", {})
            print(f"  {state}  {label:30s} Δ={t['delta_mean']*100:+6.2f}pp  W_p_greater={ws.get('p', float('nan')):.4f}  n+/n−={t['n_positive']}/{t['n_negative']}")
    print("\n=== P5 — H3-alt vs B3 ===")
    for metric_label, per_state in p5["metrics"].items():
        for state, cell in per_state.items():
            t = cell.get("test_h3alt_minus_b3")
            if not t:
                continue
            ws = t.get("wilcoxon_greater", {})
            print(f"  {state}  {metric_label:24s}  Δ={t['delta_mean']*100:+6.2f}pp  W_p_greater={ws.get('p', float('nan')):.4f}  n+/n−={t['n_positive']}/{t['n_negative']}")


if __name__ == "__main__":
    main()
