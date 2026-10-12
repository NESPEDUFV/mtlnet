"""Drive the full Check2HGI variant sweep on Alabama.

Runs each of {baseline, infonce, gat_time, skip_ln, uncertainty, combined}
× {seeds 42, 43, 44} for `epochs` epochs, then aggregates and prints a table.
"""

from __future__ import annotations

import argparse
import json
import statistics as st
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "src"))
sys.path.insert(0, str(_root / "research"))
sys.path.insert(0, str(_root / "experiments" / "check2hgi_up"))

from run_variant import VARIANTS, run_one  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="Alabama")
    ap.add_argument("--epochs", type=int, default=200)
    ap.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44])
    ap.add_argument("--variants", nargs="+", default=VARIANTS, choices=VARIANTS)
    ap.add_argument("--out_dir", default="docs/results/UP1")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--num_negatives", type=int, default=32)
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--lr", type=float, default=1e-3)
    args = ap.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    t_start = time.time()
    for variant in args.variants:
        for seed in args.seeds:
            print(f"\n{'='*60}\n>>> {variant} seed={seed}\n{'='*60}")
            try:
                r = run_one(
                    variant=variant, seed=seed, state=args.state,
                    epochs=args.epochs, dim=64, heads=4, lr=args.lr,
                    max_norm=0.9, num_negatives=args.num_negatives,
                    temperature=args.temperature, out_dir=out_dir,
                    device=args.device, log_every=max(args.epochs // 4, 1),
                )
                rows.append({
                    "variant": variant, "seed": seed,
                    "f1_mean": r["linear_probe"]["f1_mean"],
                    "f1_std": r["linear_probe"]["f1_std"],
                    "acc_mean": r["linear_probe"]["acc_mean"],
                    "acc_std": r["linear_probe"]["acc_std"],
                    "best_loss": r["best_loss"],
                    "n_params": r["n_params"],
                    "train_s": r["train_time_s"],
                })
            except Exception as e:
                print(f"!!! FAILED {variant} seed={seed}: {e}")
                rows.append({
                    "variant": variant, "seed": seed, "error": repr(e),
                })

    elapsed = time.time() - t_start
    print(f"\n=== sweep done in {elapsed:.1f}s ({elapsed/60:.1f}m) ===\n")

    # Aggregate per-variant
    summary = {}
    for v in args.variants:
        vrows = [r for r in rows if r["variant"] == v and "f1_mean" in r]
        if not vrows:
            summary[v] = {"error": "no successful runs"}; continue
        # mean across seeds (each seed already gives mean across folds)
        f1_means = [r["f1_mean"] for r in vrows]
        acc_means = [r["acc_mean"] for r in vrows]
        summary[v] = {
            "n_seeds": len(vrows),
            "f1_macro_mean_across_seeds": st.mean(f1_means),
            "f1_macro_std_across_seeds": st.stdev(f1_means) if len(f1_means) > 1 else 0.0,
            "acc_mean_across_seeds": st.mean(acc_means),
            "acc_std_across_seeds": st.stdev(acc_means) if len(acc_means) > 1 else 0.0,
            "best_loss_mean": st.mean(r["best_loss"] for r in vrows),
            "n_params": vrows[0]["n_params"],
            "avg_train_s": st.mean(r["train_s"] for r in vrows),
        }

    # Save & print
    summary_path = out_dir / f"summary_{args.state.lower()}_ep{args.epochs}.json"
    with open(summary_path, "w") as f:
        json.dump({
            "config": {
                "state": args.state, "epochs": args.epochs, "seeds": args.seeds,
                "variants": args.variants, "lr": args.lr,
                "num_negatives": args.num_negatives, "temperature": args.temperature,
            },
            "summary": summary,
            "rows": rows,
            "elapsed_s": elapsed,
        }, f, indent=2)
    print(f"\nSummary saved to {summary_path}\n")

    # Print table
    print(f"{'Variant':<14} {'Seeds':<6} {'F1_macro':<22} {'Acc':<22} {'Loss':<10} {'Params':<10}")
    print("-" * 90)
    for v in args.variants:
        s = summary[v]
        if "error" in s:
            print(f"{v:<14} {s['error']}")
            continue
        print(f"{v:<14} {s['n_seeds']:<6} "
              f"{s['f1_macro_mean_across_seeds']:.4f}±{s['f1_macro_std_across_seeds']:.4f}    "
              f"{s['acc_mean_across_seeds']:.4f}±{s['acc_std_across_seeds']:.4f}    "
              f"{s['best_loss_mean']:.4f}    {s['n_params']:<10}")


if __name__ == "__main__":
    main()
