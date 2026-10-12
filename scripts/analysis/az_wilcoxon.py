"""F1 — Paired Wilcoxon signed-rank test, AZ soft (B-M9b) vs AZ hard (B-M9d).

Extracts per-fold `top10_acc_indist` and `mrr_indist` from both runs' fold_info.json
files, computes fold-wise deltas, reports Wilcoxon signed-rank statistic + p-value.
"""
import json
import os
from pathlib import Path

try:
    from scipy.stats import wilcoxon
except ImportError as exc:
    raise SystemExit("scipy required: activate /Volumes/Vitor's SSD/ingred/.venv") from exc

S = Path(os.environ["S"])
SOFT = S / "mtlnet_lr1.0e-04_bs2048_ep50_20260421_1158"
HARD = S / "mtlnet_lr1.0e-04_bs2048_ep50_20260422_1815"

METRICS = [
    ("next_region", "top10_acc_indist", "reg Acc@10_indist"),
    ("next_region", "top5_acc_indist", "reg Acc@5_indist"),
    ("next_region", "mrr_indist", "reg MRR_indist"),
    ("next_region", "f1", "reg macro-F1"),
    ("next_category", "f1", "cat macro-F1"),
    ("next_category", "accuracy", "cat Acc@1"),
]

def load_fold(run_dir: Path, fold: int, task: str, metric: str) -> float:
    info = json.loads((run_dir / "folds" / f"fold{fold}_info.json").read_text())
    return info["diagnostic_best_epochs"][task]["metrics"][metric]

print(f"Run dirs:\n  SOFT: {SOFT.name}\n  HARD: {HARD.name}\n")

print(f"{'Metric':<22s} | {'fold1':>6s} {'fold2':>6s} {'fold3':>6s} {'fold4':>6s} {'fold5':>6s} | {'Δ mean':>8s} | Wilcoxon")
print("-" * 110)

rows = []
for task, metric, label in METRICS:
    soft_vals = [load_fold(SOFT, f, task, metric) for f in range(1, 6)]
    hard_vals = [load_fold(HARD, f, task, metric) for f in range(1, 6)]
    deltas = [h - s for s, h in zip(soft_vals, hard_vals)]
    delta_mean = sum(deltas) / len(deltas)
    try:
        # One-sided: does hard > soft?
        stat, p_two = wilcoxon(deltas, alternative="two-sided")
        _, p_greater = wilcoxon(deltas, alternative="greater")
    except ValueError as e:
        stat = float("nan")
        p_two = p_greater = float("nan")
        note = f" ({e})"
    else:
        note = ""
    print(
        f"{label:<22s} | "
        f"{soft_vals[0]*100:5.2f}→{hard_vals[0]*100:<5.2f} "
        f"{soft_vals[1]*100:5.2f}→{hard_vals[1]*100:<5.2f} "
        f"{soft_vals[2]*100:5.2f}→{hard_vals[2]*100:<5.2f} "
        f"{soft_vals[3]*100:5.2f}→{hard_vals[3]*100:<5.2f} "
        f"{soft_vals[4]*100:5.2f}→{hard_vals[4]*100:<5.2f} | "
        f"{delta_mean*100:+7.2f}pp | "
        f"W={stat:.1f}, p_two={p_two:.4f}, p_greater={p_greater:.4f}{note}"
    )
    rows.append((label, soft_vals, hard_vals, deltas, delta_mean, stat, p_two, p_greater))

# Emit markdown-ready summary
md = ["# F1 — AZ paired Wilcoxon signed-rank test (B-M9b soft vs B-M9d hard)",
      "",
      f"**Run dirs:** `{SOFT.name}` (soft) · `{HARD.name}` (hard)",
      "**Test:** Wilcoxon signed-rank on fold-wise deltas (Δ = hard − soft), 5 paired folds.",
      "**Selection epoch per metric:** `diagnostic_best_epochs` (best per-task validation epoch per fold).",
      "",
      "## Per-metric results",
      "",
      "| Metric | soft folds (%) | hard folds (%) | Δ mean (pp) | Wilcoxon W | p (two-sided) | p (H₁: hard > soft) |",
      "|---|---|---|---:|---:|---:|---:|",
]
for label, sv, hv, d, dm, stat, p_two, p_greater in rows:
    sv_str = ", ".join(f"{v*100:.2f}" for v in sv)
    hv_str = ", ".join(f"{v*100:.2f}" for v in hv)
    md.append(
        f"| {label} | {sv_str} | {hv_str} | {dm*100:+.2f} | {stat:.1f} | {p_two:.4f} | {p_greater:.4f} |"
    )
print("\n" + "\n".join(md))
