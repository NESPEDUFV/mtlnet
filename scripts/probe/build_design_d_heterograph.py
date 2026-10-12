"""Design D — Heterogeneous CHECKIN+POI graph encoder for Check2HGI.

Two node types, four edge types:

  CHECKIN[N_checkins]  features = canonical 11-dim (cat_onehot + temporal)
  POI[N_pois]          features = POI2Vec(64) — frozen per-POI semantics

  (CHECKIN -[seq]→     CHECKIN)   user trajectory, weight = exp(-Δt/τ)
  (CHECKIN -[visits]→  POI)       membership; weight = 1
  (POI     -[visited]→ CHECKIN)   reverse for bidir flow
  (POI     -[spatial]→ POI)       Delaunay (loaded from HGI's edges.csv)

Encoder (PyG HeteroConv): typed conv per edge type, summed per destination.
Two layers, hidden 64.

Loss boundaries (5):
  L_c2c   per-visit contrastive (CHECKIN ↔ CHECKIN, dropout-corrupted)
  L_c2p   check-in ↔ POI (membership)
  L_p2p   POI ↔ POI (spatial — bridges Delaunay neighbours)
  L_p2r   POI ↔ Region (PMA + GCN, like HGI)
  L_r2c   Region ↔ City

Critical property: encoder weights are typed per edge — gradient from L_p2p
only updates the spatial-conv params and POI embeddings, never the
sequence-conv params that drive cat. This is the structural escape from
the cat-vs-reg trade-off.

This file is preprocessing-only (Stage 1). Builds and saves a HeteroData
pickle to ``output/check2hgi_design_d/<state>/temp/heterograph.pt``.
Training is Stage 2 (separate file: build_design_d_train.py — TBD).

Usage::

    python scripts/probe/build_design_d_heterograph.py --state alabama
"""

from __future__ import annotations

import argparse
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch_geometric.data import HeteroData

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))


POI2VEC_DIM = 64


def build_heterograph(state: str) -> Path:
    state_lc = state.lower()
    state_cap = state.capitalize()
    out_dir = REPO / "output" / "check2hgi_design_d" / state_lc / "temp"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "heterograph.pt"

    # --- Load canonical c2hgi graph (check-in side) ---
    c2hgi_graph = REPO / f"output/check2hgi/{state_lc}/temp/checkin_graph.pt"
    with open(c2hgi_graph, "rb") as f:
        c2 = pickle.load(f)

    num_checkins = int(c2["num_checkins"])
    num_pois = int(c2["num_pois"])
    num_regions = int(c2["num_regions"])
    placeid_to_idx = c2["placeid_to_idx"]

    print(f"[{state_lc}] from c2hgi: checkins={num_checkins} pois={num_pois} regions={num_regions}")

    # --- Load HGI POI2Vec features (POI nodes input) ---
    p2v_csv = REPO / f"output/hgi/{state_lc}/poi2vec_poi_embeddings_{state_cap}.csv"
    p2v_df = pd.read_csv(p2v_csv)
    emb_cols = [str(i) for i in range(POI2VEC_DIM)]
    poi2vec_arr = np.zeros((num_pois, POI2VEC_DIM), dtype=np.float32)
    seen = np.zeros(num_pois, dtype=bool)
    for placeid, vec in zip(p2v_df["placeid"].astype(int).tolist(), p2v_df[emb_cols].to_numpy(np.float32)):
        idx = placeid_to_idx.get(placeid)
        if idx is None:
            continue
        poi2vec_arr[idx] = vec
        seen[idx] = True
    n_unseen = int((~seen).sum())
    if n_unseen > 0:
        print(f"  WARN {n_unseen}/{num_pois} POIs unseen in POI2Vec (zero-init)")

    # --- Load HGI Delaunay edges (POI-POI) ---
    delaunay_csv = REPO / f"output/hgi/{state_lc}/temp/edges.csv"
    de_df = pd.read_csv(delaunay_csv)
    # source/target are POI INDICES into HGI's pois.csv ordering — must remap to c2hgi's.
    hgi_pois_csv = REPO / f"output/hgi/{state_lc}/temp/pois.csv"
    hgi_pois = pd.read_csv(hgi_pois_csv)
    # HGI's row index → placeid → c2hgi poi_idx
    hgi_to_c2 = {}
    for hgi_idx, placeid in enumerate(hgi_pois["placeid"].astype(int).tolist()):
        c2_idx = placeid_to_idx.get(placeid)
        if c2_idx is not None:
            hgi_to_c2[hgi_idx] = c2_idx

    src_remap, tgt_remap, w_remap = [], [], []
    for s, t, w in zip(de_df["source"].astype(int), de_df["target"].astype(int),
                        de_df["weight"].astype(np.float32)):
        cs, ct = hgi_to_c2.get(int(s)), hgi_to_c2.get(int(t))
        if cs is None or ct is None:
            continue
        src_remap.append(cs); tgt_remap.append(ct); w_remap.append(w)
    spatial_edge_index = torch.tensor([src_remap, tgt_remap], dtype=torch.int64)
    spatial_edge_weight = torch.tensor(w_remap, dtype=torch.float32)
    print(f"  spatial edges: {spatial_edge_index.shape[1]} (POI-POI Delaunay, c2hgi-indexed)")

    # --- Build HeteroData ---
    h = HeteroData()
    h["checkin"].x = torch.tensor(c2["node_features"], dtype=torch.float32)
    h["poi"].x = torch.tensor(poi2vec_arr, dtype=torch.float32)

    # CHECKIN -[seq]-> CHECKIN
    seq_edge_index = torch.tensor(c2["edge_index"], dtype=torch.int64)
    seq_edge_weight = torch.tensor(c2["edge_weight"], dtype=torch.float32)
    h["checkin", "seq", "checkin"].edge_index = seq_edge_index
    h["checkin", "seq", "checkin"].edge_attr = seq_edge_weight

    # CHECKIN -[visits]-> POI
    checkin_to_poi = torch.tensor(c2["checkin_to_poi"], dtype=torch.int64)
    visits_src = torch.arange(num_checkins, dtype=torch.int64)
    visits_index = torch.stack([visits_src, checkin_to_poi], dim=0)
    h["checkin", "visits", "poi"].edge_index = visits_index

    # POI -[visited]-> CHECKIN  (reverse of visits)
    h["poi", "visited", "checkin"].edge_index = torch.stack([checkin_to_poi, visits_src], dim=0)

    # POI -[spatial]-> POI
    h["poi", "spatial", "poi"].edge_index = spatial_edge_index
    h["poi", "spatial", "poi"].edge_attr = spatial_edge_weight

    # Region-side metadata for downstream POI2Region (not in graph; passed separately)
    extras = {
        "poi_to_region": np.asarray(c2["poi_to_region"], dtype=np.int64),
        "region_adjacency": np.asarray(c2["region_adjacency"], dtype=np.int64),
        "region_area": np.asarray(c2["region_area"], dtype=np.float32),
        "coarse_region_similarity": np.asarray(c2["coarse_region_similarity"], dtype=np.float32),
        "num_pois": num_pois,
        "num_regions": num_regions,
        "placeid_to_idx": placeid_to_idx,
        "metadata": c2["metadata"],
    }

    payload = {"hetero": h, "extras": extras}
    with open(out_path, "wb") as f:
        pickle.dump(payload, f)

    print(f"  wrote {out_path}")
    print(f"    nodes: checkin={num_checkins}, poi={num_pois}")
    print(f"    edges: seq={seq_edge_index.shape[1]}, visits={visits_index.shape[1]}, "
          f"spatial={spatial_edge_index.shape[1]}")
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    build_heterograph(args.state.lower())


if __name__ == "__main__":
    main()
