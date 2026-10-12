#!/usr/bin/env python3
"""Probe — HGI on Arizona with POI2Vec encoding CATEGORY instead of FCLASS.

Tests the merge-design briefing's hypothesis that HGI's POI2Vec is essentially
a fclass-level lookup table: all POIs sharing an fclass get an identical vector.
By dropping the granularity from FCLASS (305 unique values on AZ) to CATEGORY
(7 unique values on AZ), we expect:
  - fclass linear probe accuracy collapses (only 7 buckets distinguishable)
  - POI embedding diversity is dramatically reduced
  - Region embeddings keep most of the structure (GCN aggregates over Delaunay)

Outputs land in output/hgi/arizona_category/ (isolated, does not touch canonical).

Usage:
    PYTHONPATH=src python scripts/probe/build_hgi_category_poi2vec.py \\
        [--poi2vec-epochs 100] [--epoch 2000]
"""

from __future__ import annotations

import argparse
import math
import os
import pickle as pkl
import shutil
import sys
import time
from argparse import Namespace
from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Ensure src/ is on the path when invoked as a plain script.
REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "research"))

from configs.paths import IoPaths  # noqa: E402
from embeddings.hgi.poi2vec import POI2Vec  # noqa: E402
import embeddings.hgi.hgi as hgi_mod  # noqa: E402


CANONICAL_STATE = "arizona"
PROBE_STATE = "arizona_category"


def setup_probe_temp_dir() -> Path:
    """Copy canonical AZ temp artifacts and overwrite pois.csv with fclass=category."""
    src_temp = IoPaths.HGI.get_temp_dir(CANONICAL_STATE)
    dst_temp = IoPaths.HGI.get_temp_dir(PROBE_STATE)
    dst_temp.mkdir(parents=True, exist_ok=True)

    # 1. Copy edges.csv unchanged (Delaunay graph topology stays the same).
    shutil.copy(src_temp / "edges.csv", dst_temp / "edges.csv")

    # 2. Build the modified pois.csv: replace 'fclass' values with 'category' values.
    pois = pd.read_csv(src_temp / "pois.csv")
    n_unique_fclass = pois["fclass"].nunique()
    n_unique_category = pois["category"].nunique()
    pois_mod = pois.copy()
    pois_mod["fclass"] = pois_mod["category"]  # override
    pois_mod.to_csv(dst_temp / "pois.csv", index=False)

    print(f"  canonical AZ pois.csv: {len(pois)} POIs, "
          f"{n_unique_fclass} fclass / {n_unique_category} category")
    print(f"  probe pois.csv: fclass <- category ({n_unique_category} buckets)")
    print(f"  avg POIs per category: {len(pois) / n_unique_category:.1f}")

    return dst_temp


def train_poi2vec_at_category(probe_temp: Path, epochs: int) -> Path:
    """Train POI2Vec using the modified pois.csv (fclass=category)."""
    print("\n" + "=" * 80)
    print(f"PHASE A — POI2Vec at CATEGORY granularity ({epochs} epochs, CPU)")
    print("=" * 80)

    poi2vec = POI2Vec(
        edges_file=str(probe_temp / "edges.csv"),
        pois_file=str(probe_temp / "pois.csv"),
        embedding_dim=64,
        device=torch.device("cpu"),
    )
    poi2vec.generate_walks(batch_size=128)
    cat_embeddings = poi2vec.train(epochs=epochs, batch_size=2048, lr=0.05, k=5,
                                   le_lambda=1e-8)
    poi_df = poi2vec.reconstruct_poi_embeddings(cat_embeddings, add_category_label=True)

    # Save POI-level embeddings to a tensor file (the format preprocess_hgi expects).
    poi_emb_path = probe_temp / "poi_embeddings.pt"
    emb_cols = [c for c in poi_df.columns if c.isdigit()]
    embeddings = poi_df[emb_cols].values.astype(np.float32)
    placeids = poi_df["placeid"].tolist()
    torch.save({
        "in_embed.weight": torch.tensor(embeddings, dtype=torch.float32),
        "placeids": placeids,
    }, poi_emb_path)
    print(f"  saved category-POI2Vec embeddings: {poi_emb_path} {embeddings.shape}")
    print(f"  unique POI rows in embedding space: "
          f"{np.unique(embeddings, axis=0).shape[0]} (expected ≈ "
          f"{pd.read_csv(probe_temp / 'pois.csv')['category'].nunique()})")
    return poi_emb_path


def build_probe_pickle(probe_temp: Path, new_poi_emb_path: Path) -> Path:
    """Load canonical AZ gowalla.pt, swap node_features, save to probe temp dir."""
    print("\n" + "=" * 80)
    print("PHASE B — building probe graph pickle (canonical graph + new features)")
    print("=" * 80)

    src_pkl = IoPaths.HGI.get_temp_dir(CANONICAL_STATE) / "gowalla.pt"
    with open(src_pkl, "rb") as f:
        data = pkl.load(f)

    # Sanity: our POI2Vec output is in the SAME row-order as canonical pois.csv,
    # which is exactly the order canonical preprocess_hgi used to build place_id.
    new_emb_blob = torch.load(new_poi_emb_path)
    new_features = new_emb_blob["in_embed.weight"].numpy().astype(np.float32)
    new_placeids = [int(p) for p in new_emb_blob["placeids"]]

    canonical_placeids = [int(p) for p in data["place_id"]]
    if new_placeids != canonical_placeids:
        # Align by placeid just in case (defensive).
        order = {pid: i for i, pid in enumerate(new_placeids)}
        idx = np.array([order[pid] for pid in canonical_placeids], dtype=np.int64)
        new_features = new_features[idx]
        print(f"  aligned {len(canonical_placeids)} POIs by placeid (order differed)")
    else:
        print(f"  POI order matches canonical ({len(canonical_placeids)} POIs)")

    assert new_features.shape == data["node_features"].shape, (
        f"shape mismatch: new {new_features.shape} vs canonical {data['node_features'].shape}"
    )

    data["node_features"] = new_features

    dst_pkl = probe_temp / "gowalla.pt"
    with open(dst_pkl, "wb") as f:
        pkl.dump(data, f)
    print(f"  saved probe pickle: {dst_pkl}")
    return dst_pkl


def train_hgi_on_probe(epoch: int) -> None:
    """Run HGI training on the probe pickle. Outputs land in output/hgi/arizona_category/."""
    print("\n" + "=" * 80)
    print(f"PHASE C — HGI training on category-POI2Vec features ({epoch} epochs, CPU)")
    print("=" * 80)

    args = Namespace(
        dim=64,
        attention_head=4,
        alpha=0.5,
        lr=0.006,
        gamma=1.0,
        max_norm=0.9,
        warmup_period=40,
        epoch=epoch,
        device="cpu",
    )
    hgi_mod.train_hgi(PROBE_STATE, args)


def fclass_linear_probe(probe_state: str, canonical_state: str) -> None:
    """Quick sanity probe: train a logistic regression to predict fclass from POI emb."""
    print("\n" + "=" * 80)
    print("PHASE D — fclass linear probe (briefing's key prediction)")
    print("=" * 80)

    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        print("  sklearn not available; skipping linear probe")
        return

    # Load fclass labels from canonical pois.csv.
    pois = pd.read_csv(IoPaths.HGI.get_temp_dir(canonical_state) / "pois.csv")
    fclass_by_placeid = dict(zip(pois["placeid"].astype(int), pois["fclass"].astype(int)))

    def probe_one(state_name: str, label: str) -> float:
        emb_path = IoPaths.HGI.get_state_dir(state_name) / "embeddings.parquet"
        if not emb_path.exists():
            print(f"  [{label}] missing {emb_path}, skipping")
            return float("nan")
        df = pd.read_parquet(emb_path)
        emb_cols = [c for c in df.columns if c.isdigit()]
        X = df[emb_cols].values.astype(np.float32)
        y = np.array([fclass_by_placeid.get(int(p), -1) for p in df["placeid"]], dtype=np.int64)
        keep = y >= 0
        X, y = X[keep], y[keep]
        # 5-fold CV accuracy, only on classes with >= 2 members for stratification
        counts = pd.Series(y).value_counts()
        valid_classes = set(counts[counts >= 5].index)
        m = np.array([yi in valid_classes for yi in y])
        X, y = X[m], y[m]
        kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        acc_folds = []
        for tr, te in kf.split(X, y):
            sc = StandardScaler().fit(X[tr])
            clf = LogisticRegression(max_iter=2000, n_jobs=-1)
            clf.fit(sc.transform(X[tr]), y[tr])
            acc_folds.append(clf.score(sc.transform(X[te]), y[te]))
        acc = float(np.mean(acc_folds))
        print(f"  [{label}] fclass 5-fold linear probe accuracy = {acc * 100:.2f}%")
        return acc

    acc_canon = probe_one(canonical_state, "canonical HGI (fclass)")
    acc_probe = probe_one(probe_state, "probe HGI (category-as-fclass)")
    if not math.isnan(acc_canon) and not math.isnan(acc_probe):
        print(f"  Δ = {(acc_probe - acc_canon) * 100:+.2f} pp "
              f"({'matches' if abs(acc_probe - acc_canon) < 0.02 else 'differs from'} canonical)")
        print(f"  (briefing prediction: probe should be much lower — only 7 buckets resolvable)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--poi2vec-epochs", type=int, default=100)
    parser.add_argument("--epoch", type=int, default=2000, help="HGI training epochs")
    parser.add_argument("--skip-poi2vec", action="store_true",
                        help="reuse existing probe POI2Vec output (skip Phase A)")
    parser.add_argument("--skip-hgi", action="store_true",
                        help="stop after building the probe pickle (skip Phase C)")
    parser.add_argument("--probe-only", action="store_true",
                        help="just run fclass linear probe on existing outputs")
    args = parser.parse_args()

    t0 = time.time()
    print(f"Probe: HGI on {PROBE_STATE.upper()} with POI2Vec encoding CATEGORY (not fclass)")
    print(f"Canonical state for graph & comparison: {CANONICAL_STATE}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    if args.probe_only:
        fclass_linear_probe(PROBE_STATE, CANONICAL_STATE)
        return

    probe_temp = setup_probe_temp_dir()

    if not args.skip_poi2vec:
        new_emb_path = train_poi2vec_at_category(probe_temp, epochs=args.poi2vec_epochs)
    else:
        new_emb_path = probe_temp / "poi_embeddings.pt"
        print(f"  --skip-poi2vec: reusing {new_emb_path}")

    build_probe_pickle(probe_temp, new_emb_path)

    if not args.skip_hgi:
        train_hgi_on_probe(epoch=args.epoch)
        fclass_linear_probe(PROBE_STATE, CANONICAL_STATE)
    else:
        print("\n--skip-hgi: probe pickle ready; run train_hgi separately.")

    print(f"\nTotal wall time: {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
