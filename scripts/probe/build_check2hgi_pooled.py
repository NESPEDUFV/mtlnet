"""C4 mechanism counterfactual — build POI-averaged Check2HGI inputs.

For each (userid, placeid, datetime) check-in, the canonical Check2HGI
embedding is contextual (per-visit). This script replaces every row's
embedding with the *mean across all check-ins at the same placeid*,
killing per-visit variation while preserving every other property
(POI-level identity, distribution, dimensionality).

If per-visit variation is the mechanism behind CH16's substrate lift,
substituting these pooled embeddings into the cat STL pipeline should
collapse F1 toward HGI-level (~25 % at AL under matched-head). If F1
stays at canonical Check2HGI level (~40 %), the mechanism is the
embedding training signal itself, not per-visit context.

Outputs:
  output/check2hgi_pooled/<state>/embeddings.parquet   — pooled per-checkin (rows aligned to source)
  output/check2hgi_pooled/<state>/input/next.parquet   — cat task input with pooled emb sequences
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

EMB_DIM = 64
WINDOW = 9


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()

    out_root = Path(os.environ.get("OUTPUT_DIR", Path(__file__).resolve().parents[2] / "output"))
    src_emb_p = out_root / "check2hgi" / args.state / "embeddings.parquet"
    src_next_p = out_root / "check2hgi" / args.state / "input" / "next.parquet"
    src_seq_p = out_root / "check2hgi" / args.state / "temp" / "sequences_next.parquet"

    dst_root = out_root / "check2hgi_pooled" / args.state
    dst_emb_p = dst_root / "embeddings.parquet"
    dst_next_p = dst_root / "input" / "next.parquet"
    dst_emb_p.parent.mkdir(parents=True, exist_ok=True)
    dst_next_p.parent.mkdir(parents=True, exist_ok=True)

    print(f"[c2_pooled] state={args.state}")
    print(f"  src emb: {src_emb_p}")
    print(f"  src nxt: {src_next_p}")
    print(f"  src seq: {src_seq_p}")
    print(f"  dst emb: {dst_emb_p}")
    print(f"  dst nxt: {dst_next_p}")

    emb = pd.read_parquet(src_emb_p)
    print(f"  emb: {emb.shape}")

    # Mean-pool per placeid across all check-ins
    emb_cols = [str(i) for i in range(EMB_DIM)]
    poi_mean = emb.groupby("placeid")[emb_cols].mean().reset_index()
    poi_mean_lookup = poi_mean.set_index("placeid")[emb_cols].to_numpy(dtype=np.float32)
    placeid_to_pos = {pid: i for i, pid in enumerate(poi_mean["placeid"].values)}
    print(f"  pooled per-POI: {poi_mean.shape}")

    # Write the rebuilt embeddings.parquet (same row alignment, but values are POI-pooled)
    emb_pooled_arr = np.zeros((len(emb), EMB_DIM), dtype=np.float32)
    for i, pid in enumerate(emb["placeid"].values):
        pos = placeid_to_pos.get(pid)
        if pos is not None:
            emb_pooled_arr[i] = poi_mean_lookup[pos]
    emb_out = emb[["userid", "placeid", "category", "datetime"]].copy()
    for k, c in enumerate(emb_cols):
        emb_out[c] = emb_pooled_arr[:, k]
    emb_out.to_parquet(dst_emb_p, index=False)
    print(f"  wrote pooled embeddings: {dst_emb_p}  shape={emb_out.shape}")

    # Rebuild next.parquet: 9-window sequence from sequences_next, looking up
    # POI-pooled embedding per placeid.
    seq = pd.read_parquet(src_seq_p)
    print(f"  sequences_next: {seq.shape}")
    poi_cols = [f"poi_{k}" for k in range(WINDOW)]
    seq_pids = seq[poi_cols].astype(np.int64).to_numpy()  # [N, 9]

    out_emb = np.zeros((len(seq), WINDOW, EMB_DIM), dtype=np.float32)
    n_missing = 0
    for k in range(WINDOW):
        for i, pid in enumerate(seq_pids[:, k]):
            pos = placeid_to_pos.get(int(pid))
            if pos is None:
                n_missing += 1
                continue
            out_emb[i, k] = poi_mean_lookup[pos]
    if n_missing:
        print(f"  WARN: {n_missing} placeid lookups missed (pad/-1 or unknown POIs)")

    out_emb = out_emb.reshape(len(seq), WINDOW * EMB_DIM)
    next_cols = [str(i) for i in range(WINDOW * EMB_DIM)]
    next_df = pd.DataFrame(out_emb, columns=next_cols)

    # Carry next_category + userid from canonical next.parquet (row-aligned with sequences_next).
    src_next = pd.read_parquet(src_next_p, columns=["next_category", "userid"])
    if len(src_next) != len(next_df):
        raise RuntimeError(f"row count mismatch: src_next={len(src_next)} vs new={len(next_df)}")
    next_df["next_category"] = src_next["next_category"].values
    next_df["userid"] = src_next["userid"].values
    next_df.to_parquet(dst_next_p, index=False)
    print(f"  wrote pooled next.parquet: {dst_next_p}  shape={next_df.shape}")


if __name__ == "__main__":
    main()
