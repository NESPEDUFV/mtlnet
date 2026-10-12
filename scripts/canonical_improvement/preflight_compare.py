"""Compare Stage A (existing embeddings) vs Stage B (regenerated) pre-flight runs.

Reads the most recent two run dirs per state under results/check2hgi/{state}/
that are tagged via the run-dir naming convention, and prints fold-wise +
mean cat F1 and reg top10_acc_indist deltas.

Manual orchestration: pass --stage-a and --stage-b run-dir paths explicitly.
Use --state arizona / --state alabama. Default protocol uses
diagnostic_best_epochs.next_region.per_metric_best.top10_acc_indist and
diagnostic_best_epochs.next_category.per_metric_best.f1 (matching
NORTH_STAR.md v10 v11 protocol).
"""

import argparse
import json
import math
from pathlib import Path


def reg_top10_per_fold(run_dir: Path, fold: int) -> float:
    """Per-fold-best top10_acc_indist for next_region (NORTH_STAR reg protocol)."""
    p = run_dir / "folds" / f"fold{fold}_info.json"
    info = json.loads(p.read_text())
    return float(info["diagnostic_best_epochs"]["next_region"]["per_metric_best"]["top10_acc_indist"]["best_value"])


def cat_f1_per_fold(run_dir: Path, fold: int) -> float:
    """Joint-best epoch's cat F1 (the primary_checkpoint task_metric for next_category)."""
    p = run_dir / "folds" / f"fold{fold}_info.json"
    info = json.loads(p.read_text())
    return float(info["primary_checkpoint"]["task_metrics"]["next_category"]["f1"])


def gather(run_dir: Path, n_folds: int = 5) -> dict:
    cat_f1 = [cat_f1_per_fold(run_dir, f) for f in range(1, n_folds + 1)]
    reg_top10 = [reg_top10_per_fold(run_dir, f) for f in range(1, n_folds + 1)]
    return {
        "cat_f1": cat_f1,
        "reg_top10": reg_top10,
        "cat_mean": sum(cat_f1) / len(cat_f1),
        "reg_mean": sum(reg_top10) / len(reg_top10),
        "cat_std": math.sqrt(sum((x - sum(cat_f1) / len(cat_f1)) ** 2 for x in cat_f1) / (len(cat_f1) - 1)) if len(cat_f1) > 1 else 0.0,
        "reg_std": math.sqrt(sum((x - sum(reg_top10) / len(reg_top10)) ** 2 for x in reg_top10) / (len(reg_top10) - 1)) if len(reg_top10) > 1 else 0.0,
    }


def fmt(values, prec=4):
    return "[" + ", ".join(f"{v:.{prec}f}" for v in values) + "]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage-a", required=True, type=Path, help="Run dir for Stage A (existing emb)")
    ap.add_argument("--stage-b", required=True, type=Path, help="Run dir for Stage B (regen emb)")
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    a = gather(args.stage_a)
    b = gather(args.stage_b)

    print(f"\n=== Pre-flight compare :: state={args.state} ===")
    print(f"Stage A run dir: {args.stage_a}")
    print(f"Stage B run dir: {args.stage_b}")
    print()
    print(f"{'metric':<22} {'Stage A':>14} {'Stage B':>14} {'ΔB-A':>10}")
    print(f"{'cat F1 (mean ± σ)':<22} {a['cat_mean']*100:>8.2f} ± {a['cat_std']*100:>4.2f}  {b['cat_mean']*100:>8.2f} ± {b['cat_std']*100:>4.2f}  {(b['cat_mean']-a['cat_mean'])*100:>+9.2f}")
    print(f"{'reg top10 (mean ± σ)':<22} {a['reg_mean']*100:>8.2f} ± {a['reg_std']*100:>4.2f}  {b['reg_mean']*100:>8.2f} ± {b['reg_std']*100:>4.2f}  {(b['reg_mean']-a['reg_mean'])*100:>+9.2f}")
    print()
    print("Per-fold cat F1:")
    print(f"  Stage A: {fmt(a['cat_f1'])}")
    print(f"  Stage B: {fmt(b['cat_f1'])}")
    print(f"  ΔB-A   : {fmt([bv - av for av, bv in zip(a['cat_f1'], b['cat_f1'])])}")
    print()
    print("Per-fold reg top10_acc_indist:")
    print(f"  Stage A: {fmt(a['reg_top10'])}")
    print(f"  Stage B: {fmt(b['reg_top10'])}")
    print(f"  ΔB-A   : {fmt([bv - av for av, bv in zip(a['reg_top10'], b['reg_top10'])])}")
    print()

    # Gate: |Δmean| <= 1.5 * combined σ on each head -> "within fold σ"
    def within_sigma(am, asd, bm, bsd, k=1.5):
        return abs(bm - am) <= k * math.sqrt((asd ** 2 + bsd ** 2) / 2 + 1e-12)

    cat_ok = within_sigma(a['cat_mean'], a['cat_std'], b['cat_mean'], b['cat_std'])
    reg_ok = within_sigma(a['reg_mean'], a['reg_std'], b['reg_mean'], b['reg_std'])
    verdict = "PASS" if (cat_ok and reg_ok) else "DIVERGENT"
    print(f"Gate (|Δmean| ≤ 1.5 × pooled σ): cat={cat_ok}, reg={reg_ok} → {verdict}")


if __name__ == "__main__":
    main()
