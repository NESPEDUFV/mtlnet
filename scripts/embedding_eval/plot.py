"""Standalone plot generator for the embedding-eval ladder.

Reads a finished run's ``metrics_long.csv`` for the bar charts, and reloads the
embedding tables for the 2D PCA scatters. Kept separate from run.py so plots can
be regenerated without recomputing metrics.

Example:
    python scripts/embedding_eval/plot.py \
        --results-dir docs/results/embedding_eval/fl_poi \
        --engines hgi check2hgi check2hgi_resln_design_b \
        --state florida --granularity poi --tasks cat reg
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent
for p in (_root, _root / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pandas as pd

from configs.paths import EmbeddingEngine

from scripts.embedding_eval.labels import load_item_table
from scripts.embedding_eval.plots import bar_metric, scatter_2d

# the L0/L1 metrics worth a headline image (the "possible algorithms" view)
BAR_METRICS = [
    ("knn10_acc", "L0 kNN-LOO accuracy (cosine, k=10)"),
    ("knn10_macro_f1", "L0 kNN-LOO macro-F1"),
    ("silhouette", "L0 silhouette (cosine)"),
    ("sep_ratio", "L0 centroid separability ratio"),
    ("accuracy", "L1 linear-probe accuracy"),
]


def main() -> None:
    ap = argparse.ArgumentParser(description="Plots for the embedding-eval ladder")
    ap.add_argument("--results-dir", required=True, help="dir containing metrics_long.csv")
    ap.add_argument("--engines", nargs="+", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--granularity", default="poi", choices=["poi", "checkin"])
    ap.add_argument("--tasks", nargs="+", default=["cat", "reg"], choices=["cat", "reg", "poi"])
    ap.add_argument("--max-items", type=int, default=8000, help="points per scatter")
    ap.add_argument("--out", default=None, help="defaults to <results-dir>/plots")
    args = ap.parse_args()

    rdir = _root / args.results_dir
    out = Path(args.out) if args.out else rdir / "plots"
    out.mkdir(parents=True, exist_ok=True)

    # ---- bar charts from the long metrics frame ----
    df = pd.read_csv(rdir / "metrics_long.csv")
    made = []
    for metric, title in BAR_METRICS:
        if bar_metric(df, metric, out / f"bar_{metric}.png", title=f"{title} — {args.state}"):
            made.append(f"bar_{metric}.png")

    # ---- 2D PCA scatters per engine x task (reload embeddings) ----
    for name in args.engines:
        tab = load_item_table(args.state, EmbeddingEngine(name), granularity=args.granularity)
        for task in args.tasks:
            mask = tab.valid_mask(task)
            ok = scatter_2d(
                tab.emb[mask], tab.labels(task)[mask],
                out / f"pca_{name}_{task}.png",
                title=f"PCA-2D — {name} / {args.state} — coloured by {task}",
                max_points=args.max_items,
            )
            if ok:
                made.append(f"pca_{name}_{task}.png")

    print(f"[plots] wrote {len(made)} images to {out}")
    for m in made:
        print(f"  - {m}")


if __name__ == "__main__":
    main()
