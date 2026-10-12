"""F50 D5 — encoder trajectory plot.

Loads the per-fold diagnostics CSVs from the H3-alt and B9 D5 runs and plots
side-by-side Frobenius drift-from-init for `next_encoder` (reg-side) and
`category_encoder` (cat-side) across epochs. The smoking-gun comparison:
under joint training, the reg-side drift saturates earlier than cat-side,
paralleling reg-best at ~ep 5 vs cat-best at ~ep 16.

Output: docs/findings/figs/f50_d5_encoder_trajectory.png

Usage:
    python scripts/analysis/f50_d5_encoder_traj_plot.py \\
        --h3alt-run results/check2hgi/florida/<h3alt_run_dir> \\
        --b9-run results/check2hgi/florida/<b9_run_dir> \\
        --output docs/findings/figs/f50_d5_encoder_trajectory.png
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def load_fold_diagnostics(run_dir: Path, fold: int = 1) -> pd.DataFrame:
    csv = run_dir / "diagnostics" / f"fold{fold}_diagnostics.csv"
    if not csv.exists():
        raise FileNotFoundError(f"missing: {csv}")
    return pd.read_csv(csv)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--h3alt-run", type=Path, required=True)
    ap.add_argument("--b9-run", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--fold", type=int, default=1)
    args = ap.parse_args()

    h3 = load_fold_diagnostics(args.h3alt_run, fold=args.fold)
    b9 = load_fold_diagnostics(args.b9_run, fold=args.fold)

    needed = {
        "reg_encoder_drift_from_init", "cat_encoder_drift_from_init",
        "reg_encoder_l2norm", "cat_encoder_l2norm",
        "head_alpha",
    }
    missing_h3 = needed - set(h3.columns)
    missing_b9 = needed - set(b9.columns)
    if missing_h3 or missing_b9:
        print(f"WARN: missing cols — h3alt:{missing_h3} b9:{missing_b9}")

    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

    # Top-left: Frobenius drift from init (reg vs cat) under H3-alt
    ax = axes[0, 0]
    ax.plot(h3["epoch"], h3["reg_encoder_drift_from_init"], "o-", color="C3", label="reg encoder")
    ax.plot(h3["epoch"], h3["cat_encoder_drift_from_init"], "o-", color="C0", label="cat encoder")
    ax.set_title("H3-alt baseline (no P4)")
    ax.set_ylabel("‖θ(t) − θ(0)‖₂  (Frobenius drift from init)")
    ax.legend()
    ax.grid(alpha=0.3)

    # Top-right: same under B9 champion
    ax = axes[0, 1]
    ax.plot(b9["epoch"], b9["reg_encoder_drift_from_init"], "o-", color="C3", label="reg encoder")
    ax.plot(b9["epoch"], b9["cat_encoder_drift_from_init"], "o-", color="C0", label="cat encoder")
    ax.set_title("B9 champion (P4 + Cosine + α-no-WD)")
    ax.set_ylabel("‖θ(t) − θ(0)‖₂")
    ax.legend()
    ax.grid(alpha=0.3)

    # Bottom-left: step-drift (per-epoch deltas) for both encoders, both runs
    ax = axes[1, 0]
    if "reg_encoder_step_drift" in h3.columns:
        ax.plot(h3["epoch"], h3["reg_encoder_step_drift"], "-", color="C3", label="reg (H3-alt)", alpha=0.6)
        ax.plot(h3["epoch"], h3["cat_encoder_step_drift"], "-", color="C0", label="cat (H3-alt)", alpha=0.6)
    if "reg_encoder_step_drift" in b9.columns:
        ax.plot(b9["epoch"], b9["reg_encoder_step_drift"], "--", color="C3", label="reg (B9)")
        ax.plot(b9["epoch"], b9["cat_encoder_step_drift"], "--", color="C0", label="cat (B9)")
    ax.set_title("Per-epoch step drift  ‖θ(t) − θ(t−1)‖₂")
    ax.set_xlabel("epoch")
    ax.set_ylabel("step drift")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)

    # Bottom-right: head alpha trajectory under both runs
    ax = axes[1, 1]
    if "head_alpha" in h3.columns:
        ax.plot(h3["epoch"], h3["head_alpha"], "o-", color="C2", label="H3-alt")
    if "head_alpha" in b9.columns:
        ax.plot(b9["epoch"], b9["head_alpha"], "o--", color="C4", label="B9")
    ax.set_title("Head α trajectory (graph prior amplifier)")
    ax.set_xlabel("epoch")
    ax.set_ylabel("α")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.suptitle(
        "F50 D5 — encoder weight-trajectory diagnostic (FL fold 1, leak-free)",
        fontsize=13, y=0.995,
    )
    fig.tight_layout()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, dpi=140, bbox_inches="tight")
    print(f"wrote {args.output}")

    # Print headline saturation epochs.
    def saturation_epoch(series: pd.Series, ref_epoch: int = 5, tol: float = 0.10) -> int:
        """First epoch e ≥ ref_epoch where step_drift drops below tol × max."""
        if series is None or len(series) == 0:
            return -1
        peak = series.max()
        for e_idx, val in enumerate(series):
            if e_idx >= ref_epoch and val < tol * peak:
                return e_idx + 1  # 1-indexed
        return len(series)

    if "reg_encoder_step_drift" in h3.columns:
        print(f"\nH3-alt saturation epochs (10% of peak step-drift):")
        print(f"  reg encoder: ep {saturation_epoch(h3['reg_encoder_step_drift'])}")
        print(f"  cat encoder: ep {saturation_epoch(h3['cat_encoder_step_drift'])}")
    if "reg_encoder_step_drift" in b9.columns:
        print(f"\nB9 saturation epochs:")
        print(f"  reg encoder: ep {saturation_epoch(b9['reg_encoder_step_drift'])}")
        print(f"  cat encoder: ep {saturation_epoch(b9['cat_encoder_step_drift'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
