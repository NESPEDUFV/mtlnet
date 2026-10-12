#!/usr/bin/env python3
"""Collect metrics.json from each variant + the two existing 100-epoch references
and print a single comparison table. Reads output/hgi/arizona{,_category,_cat*}/metrics.json.

For arizona (canonical fclass, 100ep) and arizona_category (cat-only, 100ep) — where
no metrics.json exists — we recompute the linear probes + embedding stats on the fly.

Usage:
    PYTHONPATH=src:research python scripts/probe/summarize_hgi_category_variants.py \\
        [--write-md docs/studies/hgi_category_injection/INDEX.md]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "research"))

from configs.paths import IoPaths  # noqa: E402

# Reuse the probes from the build script.
sys.path.insert(0, str(REPO_ROOT / "scripts" / "probe"))
from build_hgi_category_variants import fclass_linear_probe, embedding_stats  # noqa: E402


CANDIDATES = [
    ("arizona",         "canonical (fclass, 100ep)"),
    ("arizona_category","category-only (cat-as-fclass, 100ep)"),
    ("arizona_catbaseline", "baseline (fclass, matched ep)"),
    ("arizona_cata",    "A — separate cat table + λ"),
    ("arizona_catb",    "B — concat + PCA"),
    ("arizona_catc",    "C — additive joint skip-gram"),
]


def collect_one(state: str, label: str) -> dict | None:
    metrics_path = IoPaths.HGI.get_state_dir(state) / "metrics.json"
    emb_path = IoPaths.HGI.get_state_dir(state) / "embeddings.parquet"
    if not emb_path.exists():
        return None
    if metrics_path.exists():
        with open(metrics_path) as f:
            m = json.load(f)
    else:
        m = {}
        m.update(embedding_stats(state))
        m["fclass_probe"] = fclass_linear_probe(state, "fclass")
        m["category_probe"] = fclass_linear_probe(state, "category", min_per_class=10)
    m["state"] = state
    m["label"] = label
    return m


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-md", type=str, default=None)
    args = ap.parse_args()

    rows = []
    for state, label in CANDIDATES:
        m = collect_one(state, label)
        if m is None:
            print(f"  [skip] {state}: no embeddings.parquet yet")
            continue
        rows.append(m)

    df = pd.DataFrame(rows)
    cols_order = [
        "label", "poi2vec_epochs", "hgi_epochs",
        "fclass_probe", "category_probe",
        "poi_norm_mean", "poi_dim_std_mean",
        "poi_unique_rows", "region_norm_mean",
        "wall_time_min",
    ]
    cols = [c for c in cols_order if c in df.columns]
    df_show = df[cols].copy()
    for c in ["fclass_probe", "category_probe"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].apply(lambda v: f"{v*100:.2f}%" if pd.notna(v) else "n/a")
    for c in ["poi_norm_mean", "poi_dim_std_mean", "region_norm_mean", "wall_time_min"]:
        if c in df_show.columns:
            df_show[c] = df_show[c].apply(lambda v: f"{v:.3f}" if pd.notna(v) else "n/a")

    print("\n" + "=" * 100)
    print("HGI POI2Vec category-injection variants — AZ comparison")
    print("=" * 100)
    print(df_show.to_string(index=False))

    if args.write_md:
        md_lines = [
            "# HGI POI2Vec — category-injection experiments on Arizona",
            "",
            "Compares canonical HGI (POI2Vec at fclass granularity) against three",
            "variants that try to bake the *category* label into the POI embedding,",
            "plus the existing category-only ablation as a sanity floor.",
            "",
            "All variants reuse canonical AZ's Delaunay graph (edges.csv) and HGI",
            "training protocol (2000 epochs, alpha=0.5, lr=0.006, warmup=40,",
            "cross_region_weight=0.7, CPU). They differ only in how POI2Vec is",
            "trained and how POI embeddings are reconstructed.",
            "",
            "## Variants",
            "",
            "- **canonical (100ep)** — existing `output/hgi/arizona/`, POI2Vec at",
            "  fclass (305 buckets), `le_lambda=1e-8` (hierarchical L2 effectively off).",
            "- **category-only (100ep)** — earlier ablation. POI2Vec at category",
            "  (7 buckets) only — the briefing-confirming hypothesis test.",
            "- **baseline (matched-ep)** — canonical fclass POI2Vec re-run at",
            "  matched epoch budget, so A/B/C have an apples-to-apples reference.",
            "- **A** — fix the latent indexing bug in `EmbeddingModel`: give CATEGORY",
            "  its own `nn.Embedding(num_cat, D)` table. Raise `le_lambda` from 1e-8",
            "  to 0.1 so the hierarchical L2 actually does work. POI emb stays fclass-only.",
            "- **B** — train POI2Vec twice (fclass + category), concat → 128-dim,",
            "  PCA → 64-dim.",
            "- **C** — single joint skip-gram with two embedding tables (fclass + category),",
            "  POI emb = fclass_emb[f] + γ·cat_emb[c] (γ=0.5).",
            "",
            "## Results",
            "",
            df_show.to_markdown(index=False),
            "",
            "## Interpretation hooks",
            "",
            "- **fclass linear probe** — measures how much fclass-discriminability",
            "  survives in the final HGI POI embedding. Canonical sets the ceiling;",
            "  category-only sets the floor (~13 %).",
            "- **category linear probe** — measures how cleanly category is encoded.",
            "  A useful variant should raise this without dropping fclass probe.",
            "- **POI norm / std** — collapsed manifold indicates the underlying",
            "  POI2Vec output had too little diversity (vocab too small or one signal dominated).",
            "",
            "Generated by `scripts/probe/summarize_hgi_category_variants.py`.",
        ]
        out_path = Path(args.write_md)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(md_lines))
        print(f"\nWrote markdown summary → {out_path}")


if __name__ == "__main__":
    main()
