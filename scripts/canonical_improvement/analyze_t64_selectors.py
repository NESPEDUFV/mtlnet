"""Dual-selector analysis for T6.4 — per-task disjoint best + joint_geom_simple.

Reads per-fold ``metrics/fold{1..5}_next_{category,region}_val.csv`` from one or
more MTL run dirs and re-selects each fold's best epoch under TWO selectors:

* **Per-task disjoint best** — cat from cat-best epoch, reg from reg-best epoch.
  Two checkpoints; substrate-capacity framing.
* **joint_geom_simple** — single epoch maximising ``sqrt(cat_f1 * reg_top10)``.
  One checkpoint; deployable-model framing. Penalises head collapse structurally
  because a head dropping to 0 zeros the product. A simpler relative of
  ``joint_geom_lift`` in ``src/training/runners/mtl_cv.py:710`` (which divides
  by per-task majority baselines). We use the simpler form because it does not
  require recomputing majority fractions from raw labels.

The canonical B9 selector (joint best on ``0.5*(cat_f1 + reg_macro_f1)``) is
reported alongside for reference. The substrate-protocol mismatch finding is:

* Under canonical B9 selector, reg_macro_F1 over ~4 700 classes is dominated
  by rare-class noise → blind to reg_top10 collapse → picks late-epoch
  cat-dominated checkpoint.
* Under per-task disjoint, cat and reg both improve over shipping if the
  substrate has the capacity (T6.4 hypothesis).
* Under ``joint_geom_simple``, a single epoch is selected that respects both
  heads' deployment-scale metrics.

See ``docs/studies/mtl-exploration/FUTUREWORK_substrate_aware_mtl_balancing.md``
for the broader MTL-balancing future work this analysis motivates.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
CAT_NAME = "next_category"
REG_NAME = "next_region"


def _load_fold_csvs(run_dir: Path, n_folds: int = 5) -> dict[int, dict[str, pd.DataFrame]]:
    """Return ``{fold: {'cat': df, 'reg': df}}`` keyed by 1-based fold index."""
    out: dict[int, dict[str, pd.DataFrame]] = {}
    for k in range(1, n_folds + 1):
        cat_p = run_dir / "metrics" / f"fold{k}_{CAT_NAME}_val.csv"
        reg_p = run_dir / "metrics" / f"fold{k}_{REG_NAME}_val.csv"
        if not (cat_p.exists() and reg_p.exists()):
            raise FileNotFoundError(f"missing val CSV at fold {k}: {cat_p} / {reg_p}")
        out[k] = {"cat": pd.read_csv(cat_p), "reg": pd.read_csv(reg_p)}
    return out


def _row(df: pd.DataFrame, epoch: int) -> pd.Series:
    sub = df[df["epoch"] == epoch]
    if len(sub) != 1:
        raise ValueError(f"expected 1 row at epoch={epoch}, found {len(sub)}")
    return sub.iloc[0]


def _select_for_fold(cat_df: pd.DataFrame, reg_df: pd.DataFrame) -> dict:
    """Apply the three selectors and return per-selector best epochs + metrics."""
    # Align epoch grids — both heads log per epoch on the val side.
    epochs = sorted(set(cat_df["epoch"].tolist()) & set(reg_df["epoch"].tolist()))
    if not epochs:
        raise ValueError("no overlapping epochs between cat/reg val CSVs")

    cat_by_ep = {int(e): _row(cat_df, e) for e in epochs}
    reg_by_ep = {int(e): _row(reg_df, e) for e in epochs}

    # 1. Per-task disjoint best.
    cat_best_ep = max(epochs, key=lambda e: cat_by_ep[e]["f1"])
    reg_best_ep = max(epochs, key=lambda e: reg_by_ep[e]["top10_acc_indist"])

    # 2. joint_geom_simple = sqrt(cat_f1 * reg_top10).
    def _joint_geom_simple(e: int) -> float:
        cf = float(cat_by_ep[e]["f1"])
        rt = float(reg_by_ep[e]["top10_acc_indist"])
        cf = max(cf, 1e-8)
        rt = max(rt, 1e-8)
        return math.sqrt(cf * rt)

    joint_geom_ep = max(epochs, key=_joint_geom_simple)

    # 3. Canonical B9 joint = 0.5*(cat_f1 + reg_f1).
    def _joint_canonical(e: int) -> float:
        return 0.5 * (float(cat_by_ep[e]["f1"]) + float(reg_by_ep[e]["f1"]))

    joint_canon_ep = max(epochs, key=_joint_canonical)

    def _read(epoch: int) -> dict:
        cr = cat_by_ep[epoch]
        rr = reg_by_ep[epoch]
        return {
            "epoch": int(epoch),
            "cat_f1": float(cr["f1"]),
            "cat_accuracy": float(cr["accuracy"]),
            "reg_top10_indist": float(rr["top10_acc_indist"]),
            "reg_top1_indist": float(rr["top1_acc_indist"]),
            "reg_f1_macro": float(rr["f1"]),
        }

    return {
        "per_task_disjoint": {"cat": _read(cat_best_ep), "reg": _read(reg_best_ep)},
        "joint_geom_simple": _read(joint_geom_ep),
        "joint_canonical_b9": _read(joint_canon_ep),
        "epoch_grid": [int(e) for e in epochs],
    }


def analyze_run(run_dir: Path, n_folds: int = 5) -> dict:
    folds = _load_fold_csvs(run_dir, n_folds=n_folds)
    per_fold = {k: _select_for_fold(v["cat"], v["reg"]) for k, v in folds.items()}

    def _agg(path: list[str], key: str) -> tuple[float, float, list[float]]:
        vals: list[float] = []
        for f in range(1, n_folds + 1):
            x = per_fold[f]
            for p in path:
                x = x[p]
            vals.append(x[key])
        arr = np.array(vals, dtype=np.float64)
        return float(arr.mean()), float(arr.std(ddof=1)), [float(v) for v in vals]

    def _agg_block(path: list[str]) -> dict:
        cat_f1_mean, cat_f1_std, cat_f1_folds = _agg(path, "cat_f1")
        cat_acc_mean, cat_acc_std, _ = _agg(path, "cat_accuracy")
        reg_t10_mean, reg_t10_std, reg_t10_folds = _agg(path, "reg_top10_indist")
        reg_t1_mean, reg_t1_std, _ = _agg(path, "reg_top1_indist")
        reg_f1_mean, reg_f1_std, _ = _agg(path, "reg_f1_macro")
        ep_mean, ep_std, ep_folds = _agg(path, "epoch")
        return {
            "epoch_mean": ep_mean,
            "epoch_std": ep_std,
            "epoch_folds": ep_folds,
            "cat_f1_mean": cat_f1_mean,
            "cat_f1_std": cat_f1_std,
            "cat_f1_folds": cat_f1_folds,
            "cat_acc_mean": cat_acc_mean,
            "cat_acc_std": cat_acc_std,
            "reg_top10_indist_mean": reg_t10_mean,
            "reg_top10_indist_std": reg_t10_std,
            "reg_top10_indist_folds": reg_t10_folds,
            "reg_top1_indist_mean": reg_t1_mean,
            "reg_top1_indist_std": reg_t1_std,
            "reg_f1_macro_mean": reg_f1_mean,
            "reg_f1_macro_std": reg_f1_std,
        }

    summary = {
        "per_task_disjoint": {
            "cat": _agg_block(["per_task_disjoint", "cat"]),
            "reg": _agg_block(["per_task_disjoint", "reg"]),
        },
        "joint_geom_simple": _agg_block(["joint_geom_simple"]),
        "joint_canonical_b9": _agg_block(["joint_canonical_b9"]),
    }
    return {"run_dir": str(run_dir), "per_fold": per_fold, "summary": summary}


def _fmt_pct(mean: float, std: float, decimals: int = 2) -> str:
    return f"{mean*100:.{decimals}f} ± {std*100:.{decimals}f}"


def render_markdown(analyses: dict[str, dict], shipping_ref: dict | None = None) -> str:
    """Render the comparison table. ``analyses`` is keyed by variant tag."""
    rows: list[str] = []
    rows.append("## Dual-selector analysis (single-seed=42, n=5 folds)\n")
    rows.append(
        "_Each variant trained for the full ep=50 horizon. Three selection rules applied per fold:_\n"
    )
    rows.append("- **Per-task disjoint best**: cat from its cat-best epoch, reg from its reg-best epoch (two checkpoints; substrate-capacity framing).")
    rows.append("- **joint_geom_simple**: single epoch maximising `sqrt(cat_f1 * reg_top10_indist)` (one deployable checkpoint).")
    rows.append("- **joint_canonical_b9**: single epoch maximising `0.5*(cat_f1 + reg_macro_f1)` — the current canonical selector. Shown for reference.\n")
    rows.append("### Per-task disjoint best (substrate capacity)\n")
    rows.append("| Variant | cat-best ep | cat F1 | reg-best ep | reg top10 |")
    rows.append("|---|---:|---:|---:|---:|")
    for tag, a in analyses.items():
        cat = a["summary"]["per_task_disjoint"]["cat"]
        reg = a["summary"]["per_task_disjoint"]["reg"]
        rows.append(
            f"| {tag} | {cat['epoch_mean']:.1f} ± {cat['epoch_std']:.1f} | "
            f"{_fmt_pct(cat['cat_f1_mean'], cat['cat_f1_std'])} | "
            f"{reg['epoch_mean']:.1f} ± {reg['epoch_std']:.1f} | "
            f"{_fmt_pct(reg['reg_top10_indist_mean'], reg['reg_top10_indist_std'])} |"
        )

    rows.append("\n### joint_geom_simple = sqrt(cat_f1 * reg_top10_indist) (single deployable checkpoint)\n")
    rows.append("| Variant | selected ep | cat F1 | reg top10 |")
    rows.append("|---|---:|---:|---:|")
    for tag, a in analyses.items():
        s = a["summary"]["joint_geom_simple"]
        rows.append(
            f"| {tag} | {s['epoch_mean']:.1f} ± {s['epoch_std']:.1f} | "
            f"{_fmt_pct(s['cat_f1_mean'], s['cat_f1_std'])} | "
            f"{_fmt_pct(s['reg_top10_indist_mean'], s['reg_top10_indist_std'])} |"
        )

    rows.append("\n### joint_canonical_b9 = 0.5*(cat_f1 + reg_macro_f1) (current production selector)\n")
    rows.append("| Variant | selected ep | cat F1 | reg top10 |")
    rows.append("|---|---:|---:|---:|")
    for tag, a in analyses.items():
        s = a["summary"]["joint_canonical_b9"]
        rows.append(
            f"| {tag} | {s['epoch_mean']:.1f} ± {s['epoch_std']:.1f} | "
            f"{_fmt_pct(s['cat_f1_mean'], s['cat_f1_std'])} | "
            f"{_fmt_pct(s['reg_top10_indist_mean'], s['reg_top10_indist_std'])} |"
        )

    if shipping_ref is not None:
        rows.append("\n### Reference: shipping FL canonical §0.1 (multi-seed n=20)")
        rows.append("- cat F1 = 68.56 ± 0.79")
        rows.append("- reg top10 = 63.27 ± 0.10\n")

    return "\n".join(rows)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--run",
        action="append",
        required=True,
        help="Comma-separated tag:path entry. May be repeated. "
             "Example: --run shipping:results/check2hgi/florida/mtlnet_xxx",
    )
    ap.add_argument("--n-folds", type=int, default=5)
    ap.add_argument(
        "--out-json",
        type=Path,
        default=REPO / "docs" / "results" / "canonical_improvement" / "T6_4_dual_selector_analysis.json",
    )
    ap.add_argument(
        "--out-md",
        type=Path,
        default=REPO / "docs" / "results" / "canonical_improvement" / "T6_4_dual_selector_analysis.md",
    )
    args = ap.parse_args()

    analyses: dict[str, dict] = {}
    for entry in args.run:
        if ":" not in entry:
            raise SystemExit(f"--run expects tag:path, got {entry!r}")
        tag, path = entry.split(":", 1)
        analyses[tag] = analyze_run(Path(path), n_folds=args.n_folds)

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump(analyses, f, indent=2)

    md = render_markdown(analyses, shipping_ref={})
    with open(args.out_md, "w") as f:
        f.write(md)

    print(md)
    print(f"\n[json] {args.out_json}\n[md]   {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
