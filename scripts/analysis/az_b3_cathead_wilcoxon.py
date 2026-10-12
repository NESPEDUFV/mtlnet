"""F27 validation Wilcoxon: B3 (next_mtl default cat-head) vs B3 (next_gru cat-head) on AZ, 5 folds."""
import json
from pathlib import Path
from scipy.stats import wilcoxon


OLD = Path("/Volumes/Vitor's SSD/ingred/.claude/worktrees/check2hgi-mtl/results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260423_0339")
NEW = Path("/Volumes/Vitor's SSD/ingred/.claude/worktrees/check2hgi-mtl/results/check2hgi/arizona/mtlnet_lr1.0e-04_bs2048_ep50_20260424_0137")


def load(run_dir: Path, fold: int, task: str, metric: str) -> float:
    info = json.loads((run_dir / "folds" / f"fold{fold}_info.json").read_text())
    return info["diagnostic_best_epochs"][task]["metrics"][metric]


def report(label: str, old_vals: list[float], new_vals: list[float]) -> None:
    deltas = [n - o for o, n in zip(old_vals, new_vals)]
    print(f"\n=== {label}  (NEW_gru − OLD_next_mtl) ===")
    print(f"{'':14s} {'fold1':>8s} {'fold2':>8s} {'fold3':>8s} {'fold4':>8s} {'fold5':>8s} {'mean':>9s}")
    print(f"{'OLD (mtl)':14s} " + " ".join(f"{v*100:7.3f}" for v in old_vals) + f"  {sum(old_vals)/5*100:7.3f}")
    print(f"{'NEW (gru)':14s} " + " ".join(f"{v*100:7.3f}" for v in new_vals) + f"  {sum(new_vals)/5*100:7.3f}")
    print(f"{'Δ (gru − mtl)':14s} " + " ".join(f"{d*100:+7.3f}" for d in deltas) + f"  {sum(deltas)/5*100:+7.3f}")
    try:
        stat, p_two = wilcoxon(deltas, alternative="two-sided")
        _, p_greater = wilcoxon(deltas, alternative="greater")
        positive = sum(1 for d in deltas if d > 0)
        print(f"\nWilcoxon: W={stat:.1f}  p_two={p_two:.4f}  p_greater={p_greater:.4f}  ({positive}/5 deltas positive)")
    except ValueError as e:
        print(f"\nWilcoxon error: {e}")


for task, metric, label in [
    ("next_category", "f1", "CAT F1"),
    ("next_category", "accuracy", "CAT Acc@1"),
    ("next_region", "top10_acc_indist", "REG Acc@10_indist"),
    ("next_region", "top5_acc_indist", "REG Acc@5_indist"),
    ("next_region", "mrr_indist", "REG MRR_indist"),
    ("next_region", "f1", "REG macro-F1"),
]:
    old_vals = [load(OLD, f, task, metric) for f in range(1, 6)]
    new_vals = [load(NEW, f, task, metric) for f in range(1, 6)]
    report(label, old_vals, new_vals)
