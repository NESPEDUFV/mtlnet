"""v13 / v14 — reg-path POI-augmentation loaders (graduated from scripts/probe).

These mirror the loaders in ``scripts/probe/build_design_b_poi_pool.py`` and
``scripts/probe/build_design_k_delaunay.py`` so the canonical Check2HGIModule
can build the graduated reg_poi_mode mechanism (poi2vec_residual / delaunay_gcn)
from a single ``check2hgi.py`` invocation.

  * ``load_poi2vec_table`` — frozen 64-d POI2Vec from HGI, remapped to c2hgi
    POI idx (zero rows for unmapped POIs).
  * ``load_delaunay_edges`` — HGI's Delaunay edges remapped to c2hgi POI idx,
    symmetrised. Used only by delaunay_gcn (v14 / Design K).
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import torch

# Repo root: research/embeddings/check2hgi/reg_poi_aug.py -> parents[3]
REPO = Path(__file__).resolve().parents[3]

POI2VEC_DIM = 64


def load_poi2vec_table(state: str, num_pois: int, placeid_to_idx: dict) -> torch.Tensor:
    """Load frozen POI2Vec (64-d) and remap placeid -> c2hgi POI idx.

    Mirrors ``build_design_b_poi_pool.load_poi2vec_table`` /
    ``build_design_k_delaunay.load_poi2vec``. Unmapped POIs stay zero.
    """
    state_lc = state.lower()
    state_cap = state.capitalize()
    csv = REPO / f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state_cap}.csv"
    df = pd.read_csv(csv)
    emb_cols = [str(i) for i in range(POI2VEC_DIM)]
    arr = np.zeros((num_pois, POI2VEC_DIM), dtype=np.float32)
    seen = np.zeros(num_pois, dtype=bool)
    for placeid, vec in zip(df["placeid"].astype(int).tolist(),
                            df[emb_cols].to_numpy(np.float32)):
        idx = placeid_to_idx.get(int(placeid))
        if idx is None:
            continue
        arr[idx] = vec
        seen[idx] = True
    n_unmapped = int((~seen).sum())
    if n_unmapped > 0:
        print(f"  [reg_poi] WARN {n_unmapped} POIs missing from POI2Vec — left zero")
    return torch.from_numpy(arr)


def load_delaunay_edges(state: str, placeid_to_idx: dict, num_pois: int,
                        poi_to_region=None, cross_region_weight: float = 1.0,
                        edge_power: float = 1.0):
    """Load HGI's Delaunay POI-POI edges, remap to c2hgi POI idx, symmetrise.

    Mirrors ``build_design_k_delaunay.load_delaunay_edges`` byte-for-byte.
    HGI's edges.csv has (source, target, weight) where source/target are row
    indices into HGI's pois.csv; map row -> placeid -> c2hgi POI idx.
    """
    state_lc = state.lower()
    pois_path = REPO / "output" / "hgi" / state_lc / "temp" / "pois.csv"
    edges_path = REPO / "output" / "hgi" / state_lc / "temp" / "edges.csv"
    hgi_pois = pd.read_csv(pois_path)
    edges = pd.read_csv(edges_path)

    row_to_c2hgi = {}
    for row_idx, pid in enumerate(hgi_pois["placeid"].tolist()):
        c2_idx = placeid_to_idx.get(int(pid))
        if c2_idx is not None:
            row_to_c2hgi[row_idx] = c2_idx

    src, tgt, w = [], [], []
    n_skip = 0
    for s, t, weight in zip(edges["source"].tolist(), edges["target"].tolist(),
                            edges["weight"].tolist()):
        s_c = row_to_c2hgi.get(int(s))
        t_c = row_to_c2hgi.get(int(t))
        if s_c is None or t_c is None:
            n_skip += 1
            continue
        wv = float(weight) ** edge_power
        if poi_to_region is not None and cross_region_weight != 1.0:
            if int(poi_to_region[s_c]) != int(poi_to_region[t_c]):
                wv *= cross_region_weight
        src.append(s_c); tgt.append(t_c); w.append(wv)
        src.append(t_c); tgt.append(s_c); w.append(wv)

    edge_index = torch.tensor([src, tgt], dtype=torch.int64)
    edge_weight = torch.tensor(w, dtype=torch.float32)
    print(f"  [reg_poi] delaunay state={state} loaded {edge_index.shape[1]} edges "
          f"(skipped {n_skip} unmapped from {len(edges)} raw)")
    return edge_index, edge_weight
