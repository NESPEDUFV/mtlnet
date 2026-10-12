"""Generality probes — fclass linear probe + kNN-overlap with POI2Vec.

Independent of the cat / reg downstream tasks. Runs on frozen POI embeddings
(``poi_embeddings.parquet``) for any substrate. Tests whether the substrate
preserves general POI structure or has overfitted to one downstream task.

Three substrates evaluated by default at AL+AZ:
  canonical c2hgi   — output/check2hgi/<state>/poi_embeddings.parquet
  HGI               — built from output/hgi/<state>/poi2vec_poi_embeddings_<State>.csv
  c2hgi_poi2vec     — output/check2hgi_poi2vec/<state>/poi_embeddings.parquet

Other substrates (Design A, B, C, D outputs) added as they land via the
``--substrates`` flag.

Probes
------
1. fclass linear probe: 5-fold logistic regression on POI embeddings → fclass label.
   Reports macro-F1 mean ± std. HGI's POI2Vec is fclass-clustered by construction;
   anything substantively below HGI here means we lost POI semantic structure.

2. Region-mix regression: linear regression on region embeddings → per-region
   category-fraction vector. Reports R² mean. (Only applies if region_embeddings
   parquet exists for the substrate.)

3. kNN-overlap with HGI POI2Vec: for each substrate, compute Jaccard@10 of
   nearest-POI sets vs HGI's POI2Vec. Tells us whether the substrate's POI
   geometry agrees with HGI's semantic geometry.

Usage::

    python scripts/probe/generality_probes.py --states alabama arizona
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
PAIRED = REPO / "docs" / "studies" / "check2hgi" / "results" / "paired_tests"
PAIRED.mkdir(parents=True, exist_ok=True)


def _load_poi(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return (placeids, emb [N, D]) from a poi_embeddings parquet."""
    df = pd.read_parquet(path)
    if "placeid" not in df.columns:
        raise ValueError(f"{path} missing placeid")
    emb_cols = [c for c in df.columns if c.isdigit() or (c.startswith("reg_") and False)]
    if not emb_cols:
        # check2hgi naming uses '0','1',...
        emb_cols = [c for c in df.columns if c.isdigit()]
    df = df.sort_values("placeid").reset_index(drop=True)
    return df["placeid"].astype(int).to_numpy(), df[emb_cols].to_numpy(dtype=np.float32)


def _load_substrate_poi(state: str, name: str) -> tuple[np.ndarray, np.ndarray]:
    state_lc = state.lower()
    state_cap = state.capitalize()
    if name == "canonical":
        return _load_poi(REPO / f"output/check2hgi/{state_lc}/poi_embeddings.parquet")
    if name == "hgi":
        df = pd.read_csv(REPO / f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state_cap}.csv")
        emb_cols = [str(i) for i in range(64)]
        df = df.sort_values("placeid").reset_index(drop=True)
        return df["placeid"].astype(int).to_numpy(), df[emb_cols].to_numpy(dtype=np.float32)
    if name == "c2hgi_poi2vec":
        return _load_poi(REPO / f"output/check2hgi_poi2vec/{state_lc}/poi_embeddings.parquet")
    if name == "design_e":
        return _load_poi(REPO / f"output/check2hgi_design_e/{state_lc}/poi_embeddings.parquet")
    if name == "design_b":
        return _load_poi(REPO / f"output/check2hgi_design_b/{state_lc}/poi_embeddings.parquet")
    if name == "design_h":
        return _load_poi(REPO / f"output/check2hgi_design_h/{state_lc}/poi_embeddings.parquet")
    if name == "design_d":
        return _load_poi(REPO / f"output/check2hgi_design_d/{state_lc}/poi_embeddings.parquet")
    if name == "design_i":
        return _load_poi(REPO / f"output/check2hgi_design_i/{state_lc}/poi_embeddings.parquet")
    if name == "design_j":
        return _load_poi(REPO / f"output/check2hgi_design_j/{state_lc}/poi_embeddings.parquet")
    if name == "design_m":
        return _load_poi(REPO / f"output/check2hgi_design_m/{state_lc}/poi_embeddings.parquet")
    raise ValueError(f"unknown substrate {name}")


def _load_fclass(state: str) -> dict[int, int]:
    """Return placeid → fclass int."""
    state_cap = state.capitalize()
    pois = pd.read_csv(REPO / f"output/hgi/{state.lower()}/temp/pois.csv")
    return dict(zip(pois["placeid"].astype(int), pois["fclass"].astype(int)))


def fclass_linear_probe(emb: np.ndarray, labels: np.ndarray, seed: int = 42) -> dict:
    """5-fold StratifiedKFold logistic regression on emb -> labels.
    Returns macro-F1 mean ± std and per-fold."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import f1_score

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    f1s = []
    for tr, va in skf.split(emb, labels):
        clf = LogisticRegression(max_iter=2000, C=1.0, n_jobs=-1)
        clf.fit(emb[tr], labels[tr])
        pred = clf.predict(emb[va])
        f1s.append(float(f1_score(labels[va], pred, average="macro", zero_division=0)))
    return {
        "per_fold": f1s,
        "mean": float(np.mean(f1s)),
        "std": float(np.std(f1s, ddof=1)),
    }


def knn_jaccard(emb_a: np.ndarray, emb_b: np.ndarray, k: int = 10) -> float:
    """Mean Jaccard@k of nearest-neighbour sets between two POI matrices.
    emb_a, emb_b are aligned (same row order)."""
    from sklearn.neighbors import NearestNeighbors

    nn_a = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(emb_a)
    nn_b = NearestNeighbors(n_neighbors=k + 1, metric="cosine").fit(emb_b)
    _, idx_a = nn_a.kneighbors(emb_a)
    _, idx_b = nn_b.kneighbors(emb_b)
    # Drop self (first column)
    idx_a = idx_a[:, 1:]
    idx_b = idx_b[:, 1:]
    jacc = []
    for i in range(len(idx_a)):
        sa = set(idx_a[i].tolist())
        sb = set(idx_b[i].tolist())
        jacc.append(len(sa & sb) / len(sa | sb))
    return float(np.mean(jacc))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--states", nargs="+", default=["alabama", "arizona"])
    ap.add_argument("--substrates", nargs="+",
                    default=["canonical", "hgi", "c2hgi_poi2vec"],
                    help="Substrate names registered in _load_substrate_poi")
    args = ap.parse_args()

    out: dict = {}
    for state in args.states:
        print(f"\n=== {state} ===")
        fclass_map = _load_fclass(state)

        # Load all substrates aligned on common placeids
        loaded = {}
        for s in args.substrates:
            try:
                pids, emb = _load_substrate_poi(state, s)
                loaded[s] = (pids, emb)
                print(f"  {s:14s}  {emb.shape}")
            except FileNotFoundError as e:
                print(f"  {s:14s}  MISSING ({e})")

        # Find common placeids across substrates
        common = set(loaded["canonical"][0].tolist())
        for s, (pids, _) in loaded.items():
            common &= set(pids.tolist())
        common = sorted(common)
        print(f"  common placeids: {len(common)}")

        # Align all substrates to common placeids; build label vector
        aligned = {}
        for s, (pids, emb) in loaded.items():
            idx = {int(p): i for i, p in enumerate(pids)}
            sel = [idx[p] for p in common]
            aligned[s] = emb[sel]
        labels = np.array([fclass_map.get(int(p), -1) for p in common], dtype=np.int64)
        valid_mask = labels >= 0
        if not valid_mask.all():
            print(f"  dropping {(~valid_mask).sum()} placeids with no fclass label")
            for s in aligned:
                aligned[s] = aligned[s][valid_mask]
            labels = labels[valid_mask]

        # Probe 1: fclass linear probe
        print("\n  fclass linear probe (5-fold macro-F1):")
        state_results = {"fclass_probe": {}, "knn_jaccard_vs_hgi": {}}
        for s, emb in aligned.items():
            r = fclass_linear_probe(emb, labels)
            state_results["fclass_probe"][s] = r
            print(f"    {s:14s}  F1={r['mean']*100:6.2f} ± {r['std']*100:.2f}")

        # Probe 2: kNN overlap vs HGI
        if "hgi" in aligned:
            print("\n  kNN-Jaccard@10 vs HGI POI2Vec:")
            hgi_emb = aligned["hgi"]
            for s, emb in aligned.items():
                if s == "hgi":
                    state_results["knn_jaccard_vs_hgi"][s] = 1.0
                    print(f"    {s:14s}  1.000 (self)")
                    continue
                j = knn_jaccard(emb, hgi_emb, k=10)
                state_results["knn_jaccard_vs_hgi"][s] = j
                print(f"    {s:14s}  {j:.3f}")

        out[state] = state_results

    out_path = PAIRED / "generality_probes.json"
    out_path.write_text(json.dumps(out, indent=2, default=float))
    print(f"\nwrote {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
