"""Build output/hgi/<state>/input/next_region.parquet for the MTL+HGI counterfactual.

Inputs:
  - output/check2hgi/<state>/temp/sequences_next.parquet  (poi_0..poi_8, target_poi, userid)
  - output/check2hgi/<state>/temp/checkin_graph.pt        (poi_to_region, region_to_idx)
  - output/hgi/<state>/region_embeddings.parquet           (region_id, reg_0..reg_63)

Output:
  - output/hgi/<state>/input/next_region.parquet           (576 emb cols + userid + region_idx + last_region_idx)

The region label space (region_id, region_idx) is substrate-independent —
derived from poi_to_region. Only the embedding lookup changes per substrate.
"""

from __future__ import annotations

import argparse
import os
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

WINDOW = 9
EMB_DIM = 64


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    out_root = Path(os.environ.get("OUTPUT_DIR", Path(__file__).resolve().parents[2] / "output"))
    c2_temp = out_root / "check2hgi" / args.state / "temp"
    hgi_root = out_root / "hgi" / args.state

    seq_p = c2_temp / "sequences_next.parquet"
    graph_p = c2_temp / "checkin_graph.pt"
    hgi_reg_p = hgi_root / "region_embeddings.parquet"
    out_p = hgi_root / "input" / "next_region.parquet"
    out_p.parent.mkdir(parents=True, exist_ok=True)

    print(f"[build_hgi_next_region] state={args.state}")
    print(f"  seq:    {seq_p}")
    print(f"  graph:  {graph_p}")
    print(f"  hgi reg:{hgi_reg_p}")
    print(f"  out:    {out_p}")

    seq = pd.read_parquet(seq_p)
    print(f"  sequences: {seq.shape}")

    with open(graph_p, "rb") as f:
        cd = pickle.load(f)
    poi_to_region = cd["poi_to_region"]  # tensor [n_pois], indexed by POI idx
    if isinstance(poi_to_region, torch.Tensor):
        poi_to_region = poi_to_region.cpu().numpy()
    poi_to_region = np.asarray(poi_to_region, dtype=np.int64)
    n_regions = int(cd["num_regions"])
    placeid_to_idx = cd["placeid_to_idx"]  # dict: raw placeid → POI idx (0..n_pois-1)
    print(f"  poi_to_region: {poi_to_region.shape}  n_regions={n_regions}  "
          f"placeid_to_idx: {len(placeid_to_idx)} entries")

    # Build region embedding matrix indexed by region_id (0..n_regions-1)
    reg_df = pd.read_parquet(hgi_reg_p)
    reg_cols = [f"reg_{i}" for i in range(EMB_DIM)]
    reg_emb = np.zeros((n_regions, EMB_DIM), dtype=np.float32)
    for _, row in reg_df.iterrows():
        rid = int(row["region_id"])
        if 0 <= rid < n_regions:
            reg_emb[rid] = np.asarray([row[c] for c in reg_cols], dtype=np.float32)
    print(f"  hgi reg_emb matrix: {reg_emb.shape}")

    # Resolve region IDs per window position: placeid → POI idx → region idx.
    # sequences_next.parquet stores raw placeids (as strings or ints).
    poi_cols = [f"poi_{k}" for k in range(WINDOW)]
    target_col = "target_poi"

    def to_poi_idx(series):
        return series.astype(np.int64).map(lambda p: placeid_to_idx.get(int(p), -1)).to_numpy()

    poi_idx_mat = np.stack([to_poi_idx(seq[c]) for c in poi_cols], axis=1)  # [N, 9]
    target_poi_idx = to_poi_idx(seq[target_col])                            # [N]
    pois = poi_idx_mat
    target_pois = target_poi_idx

    n_unmapped = int((pois < 0).sum() + (target_pois < 0).sum())
    if n_unmapped:
        print(f"  WARN: {n_unmapped} placeid lookups missed; clipping to 0.")

    def lookup(pids):
        safe = np.clip(pids, 0, len(poi_to_region) - 1)
        return poi_to_region[safe]

    regions = lookup(pois)                # [N, 9]
    target_regions = lookup(target_pois)  # [N]
    last_region = regions[:, -1]          # [N]

    # Build embedding matrix per row: stack 9 × 64-dim region embeddings
    embs = reg_emb[regions]               # [N, 9, 64]
    embs = embs.reshape(len(seq), WINDOW * EMB_DIM)

    out = pd.DataFrame(embs, columns=[str(i) for i in range(WINDOW * EMB_DIM)])
    # Trust check2hgi's authoritative labels (substrate-independent; correctly
    # handles pad/missing placeids that our naive lookup mishandles).
    c2_p = out_root / "check2hgi" / args.state / "input" / "next_region.parquet"
    c2 = pd.read_parquet(c2_p, columns=["userid", "region_idx", "last_region_idx"])
    if len(c2) != len(out):
        raise RuntimeError(f"row-count mismatch: check2hgi={len(c2)} vs ours={len(out)}")
    out["userid"] = c2["userid"].values
    out["region_idx"] = c2["region_idx"].astype(np.int32).values
    out["last_region_idx"] = c2["last_region_idx"].astype(np.int32).values

    out.to_parquet(out_p, index=False)
    print(f"  wrote {out_p}  shape={out.shape}")


if __name__ == "__main__":
    main()
