"""Build a POI-mean → region-mean readout from canonical Check2HGI check-in embeddings.

Diagnostic for the per-visit-noise hypothesis on next-region: if post-hoc pooling
the existing check-in embeddings into region vectors closes most of the C2HGI→HGI
reg gap, the per-visit variance in the canonical region encoder is the load-bearing
factor and an engine-level dual-readout intervention is justified. If it doesn't,
the gap lies in the POI2Region weights / training signal — pooling won't help.

Pipeline
--------
1. Load ``output/check2hgi/<state>/embeddings.parquet`` (per-check-in, 64-dim).
2. POI-mean by ``placeid``, mapped to dense ``poi_idx`` via the graph pickle.
3. Region-mean by ``poi_to_region``.
4. Save ``output/check2hgi/<state>/region_embeddings_postpool.parquet`` with
   ``region_id`` + ``reg_0 .. reg_63`` columns (matching the canonical schema so
   ``_load_region_embeddings`` picks up ``reg_*`` columns transparently).

Usage::

    python scripts/probe/build_check2hgi_postpool_region.py --state alabama
    python scripts/probe/build_check2hgi_postpool_region.py --state arizona
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

EMB_DIM = 64


def build_postpool_region(state: str) -> Path:
    base = Path("output/check2hgi") / state
    checkin_path = base / "embeddings.parquet"
    graph_path = base / "temp" / "checkin_graph.pt"
    out_path = base / "region_embeddings_postpool.parquet"

    df = pd.read_parquet(checkin_path)
    emb_cols = [str(i) for i in range(EMB_DIM)]
    missing = [c for c in emb_cols if c not in df.columns]
    if missing:
        raise RuntimeError(f"embeddings.parquet missing cols {missing[:5]}...")

    with open(graph_path, "rb") as f:
        g = pickle.load(f)
    placeid_to_idx: dict = g["placeid_to_idx"]
    poi_to_region = np.asarray(g["poi_to_region"], dtype=np.int64)
    num_pois = int(g["num_pois"])
    num_regions = int(g["num_regions"])

    poi_means = (
        df.groupby("placeid", sort=True)[emb_cols].mean()
    )

    poi_arr = np.zeros((num_pois, EMB_DIM), dtype=np.float64)
    poi_seen = np.zeros(num_pois, dtype=bool)
    for placeid, row in zip(poi_means.index.to_numpy(), poi_means.to_numpy()):
        idx = placeid_to_idx.get(int(placeid))
        if idx is None:
            continue
        poi_arr[idx] = row
        poi_seen[idx] = True

    region_sum = np.zeros((num_regions, EMB_DIM), dtype=np.float64)
    region_cnt = np.zeros(num_regions, dtype=np.int64)
    for poi_idx in range(num_pois):
        if not poi_seen[poi_idx]:
            continue
        r = int(poi_to_region[poi_idx])
        region_sum[r] += poi_arr[poi_idx]
        region_cnt[r] += 1
    region_arr = np.zeros_like(region_sum, dtype=np.float32)
    nz = region_cnt > 0
    region_arr[nz] = (region_sum[nz] / region_cnt[nz, None]).astype(np.float32)

    out = pd.DataFrame({"region_id": np.arange(num_regions, dtype=np.int64)})
    for i in range(EMB_DIM):
        out[f"reg_{i}"] = region_arr[:, i]

    out.to_parquet(out_path)

    n_empty = int((~nz).sum())
    print(
        f"[{state}] checkins={len(df)} pois_seen={int(poi_seen.sum())}/{num_pois} "
        f"regions_with_pois={int(nz.sum())}/{num_regions} (empty={n_empty}) "
        f"-> {out_path}"
    )
    return out_path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True, help="State name (e.g. alabama)")
    args = ap.parse_args()
    build_postpool_region(args.state.lower())


if __name__ == "__main__":
    main()
