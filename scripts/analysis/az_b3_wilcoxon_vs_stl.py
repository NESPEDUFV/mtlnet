"""AZ paired Wilcoxon: B3 MTL (hard + static cat=0.75) vs STL baselines.

Tests at n=5 folds on Arizona:
  1. B3 cat F1 vs STL Check2HGI cat F1 (STL next_ pipeline)
  2. B3 reg Acc@10_indist vs STL STAN reg Acc@10 (P1 archived summary with per-fold)

Per-fold extraction from different schemas:
  MTL runs: fold_info.json.diagnostic_best_epochs.<task>.metrics.<metric>
  STL cat runs: fold_info.json.diagnostic_best_epochs.next.metrics.<metric>
  STL STAN P1 summary: heads.next_stan.per_fold[i].<metric>
"""
from __future__ import annotations

import json
from pathlib import Path

from scipy.stats import wilcoxon  # type: ignore


REPO = Path("/Volumes/Vitor's SSD/ingred/.claude/worktrees/check2hgi-mtl")
B3_AZ = REPO / "results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260423_0339"
STL_CAT_AZ = REPO / "results/check2hgi/arizona/next_lr1.0e-04_bs1024_ep50_20260419_0302"
STL_STAN_AZ_SUMMARY = REPO / "docs/results/P1/region_head_arizona_region_5f_50ep_STAN_az_5f50ep.json"


def load_mtl(run_dir: Path, fold: int, task: str, metric: str) -> float:
    info = json.loads((run_dir / "folds" / f"fold{fold}_info.json").read_text())
    return info["diagnostic_best_epochs"][task]["metrics"][metric]


def load_stl_next(run_dir: Path, fold: int, metric: str) -> float:
    info = json.loads((run_dir / "folds" / f"fold{fold}_info.json").read_text())
    return info["diagnostic_best_epochs"]["next"]["metrics"][metric]


def load_stl_stan_perfold(summary_path: Path, metric: str) -> list[float]:
    d = json.loads(summary_path.read_text())
    return [fold[metric] for fold in d["heads"]["next_stan"]["per_fold"]]


def report(label: str, stl_vals: list[float], mtl_vals: list[float]) -> None:
    deltas = [m - s for s, m in zip(stl_vals, mtl_vals)]
    print("=" * 90)
    print(f"{label}  (MTL_B3 − STL)")
    print("=" * 90)
    print(f"{'':14s} {'fold1':>8s} {'fold2':>8s} {'fold3':>8s} {'fold4':>8s} {'fold5':>8s} {'mean':>9s}")
    print(f"{'STL':14s} " + " ".join(f"{v*100:7.3f}" for v in stl_vals) + f"  {sum(stl_vals)/5*100:7.3f}")
    print(f"{'B3 MTL':14s} " + " ".join(f"{v*100:7.3f}" for v in mtl_vals) + f"  {sum(mtl_vals)/5*100:7.3f}")
    print(f"{'Δ (B3 − STL)':14s} " + " ".join(f"{d*100:+7.3f}" for d in deltas) + f"  {sum(deltas)/5*100:+7.3f}")
    try:
        stat, p_two = wilcoxon(deltas, alternative="two-sided")
        _, p_greater = wilcoxon(deltas, alternative="greater")
        positive = sum(1 for d in deltas if d > 0)
        print(f"\nWilcoxon: W={stat:.1f}  p_two={p_two:.4f}  p_greater={p_greater:.4f}  ({positive}/5 deltas positive)\n")
    except ValueError as e:
        print(f"\nWilcoxon error: {e}\n")


def main() -> None:
    print(f"B3 AZ:       {B3_AZ.name}")
    print(f"STL cat AZ:  {STL_CAT_AZ.name}")
    print(f"STL STAN AZ: {STL_STAN_AZ_SUMMARY.name}")
    print()

    # Comparison 1 — cat F1
    b3_cat = [load_mtl(B3_AZ, f, "next_category", "f1") for f in range(1, 6)]
    stl_cat = [load_stl_next(STL_CAT_AZ, f, "f1") for f in range(1, 6)]
    report("CAT F1 (B3 MTL vs STL Check2HGI cat)", stl_cat, b3_cat)

    # Comparison 2 — reg Acc@10
    b3_reg = [load_mtl(B3_AZ, f, "next_region", "top10_acc_indist") for f in range(1, 6)]
    stl_stan_reg = load_stl_stan_perfold(STL_STAN_AZ_SUMMARY, "top10_acc")
    report("REG Acc@10 (B3 MTL indist vs STL STAN)", stl_stan_reg, b3_reg)

    # Comparison 3 — reg MRR
    b3_mrr = [load_mtl(B3_AZ, f, "next_region", "mrr_indist") for f in range(1, 6)]
    stl_stan_mrr = load_stl_stan_perfold(STL_STAN_AZ_SUMMARY, "mrr")
    report("REG MRR (B3 MTL indist vs STL STAN)", stl_stan_mrr, b3_mrr)

    # Comparison 4 — reg macro-F1
    b3_f1 = [load_mtl(B3_AZ, f, "next_region", "f1") for f in range(1, 6)]
    stl_stan_f1 = load_stl_stan_perfold(STL_STAN_AZ_SUMMARY, "f1")
    report("REG macro-F1 (B3 MTL vs STL STAN)", stl_stan_f1, b3_f1)


if __name__ == "__main__":
    main()
