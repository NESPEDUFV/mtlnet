"""Build output/hgi/<state>/input/next.parquet (cat task input) for the HGI MTL counterfactual.

Row-aligned to canonical c2hgi next.parquet (same sequences, same labels). Only the
576 embedding columns are swapped to HGI POI-level embeddings (placeid -> 64-dim, looked
up through canonical c2hgi sequences poi_0..poi_8). next_category + userid are taken
verbatim from canonical c2hgi next.parquet (substrate-independent labels).

Padding: c2hgi sequences use -1 for missing positions -> zero embedding (matches the
canonical convert_sequences_to_poi_embeddings get_zero_embedding behaviour).
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
from configs.paths import EmbeddingEngine, IoPaths  # noqa: E402

WINDOW = 9
EMB_DIM = 64


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    state = args.state

    seq_p = IoPaths.CHECK2HGI.get_temp_dir(state) / "sequences_next.parquet"
    hgi_emb_p = IoPaths.get_embedd(state, EmbeddingEngine.HGI)
    c2_next_p = IoPaths.get_next(state, EmbeddingEngine.CHECK2HGI)
    out_p = IoPaths.get_next(state, EmbeddingEngine.HGI)
    out_p.parent.mkdir(parents=True, exist_ok=True)

    print(f"[build_hgi_next_cat] state={state}")
    print(f"  seq:     {seq_p}")
    print(f"  hgi emb: {hgi_emb_p}")
    print(f"  c2 next: {c2_next_p}")
    print(f"  out:     {out_p}")

    seq = pd.read_parquet(seq_p)
    print(f"  sequences: {seq.shape}")

    emb_df = pd.read_parquet(hgi_emb_p)
    num_cols = [c for c in emb_df.columns if c.isdigit()]
    assert len(num_cols) == EMB_DIM, f"expected {EMB_DIM} emb cols, got {len(num_cols)}"
    # placeid -> 64-dim vector lookup
    placeids = emb_df["placeid"].astype(str).tolist()
    emb_mat = emb_df[num_cols].to_numpy(dtype=np.float32)  # [n_pois, 64]
    pid_to_row = {p: i for i, p in enumerate(placeids)}
    print(f"  hgi emb matrix: {emb_mat.shape}  n_placeids={len(pid_to_row)}")

    poi_cols = [f"poi_{k}" for k in range(WINDOW)]
    n = len(seq)
    out_emb = np.zeros((n, WINDOW, EMB_DIM), dtype=np.float32)
    miss = 0
    for k, col in enumerate(poi_cols):
        pids = seq[col].astype(str).to_numpy()
        for i, p in enumerate(pids):
            r = pid_to_row.get(p)
            if r is not None:
                out_emb[i, k] = emb_mat[r]
            elif p not in ("-1", "-1.0"):
                miss += 1
    if miss:
        print(f"  WARN: {miss} non-pad placeid lookups missed -> left as zero embedding")
    out_emb = out_emb.reshape(n, WINDOW * EMB_DIM)

    out = pd.DataFrame(out_emb, columns=[str(i) for i in range(WINDOW * EMB_DIM)])
    # Trust canonical c2hgi authoritative labels (substrate-independent), row-aligned.
    c2 = pd.read_parquet(c2_next_p, columns=["next_category", "userid"])
    if len(c2) != len(out):
        raise RuntimeError(f"row-count mismatch: c2hgi next={len(c2)} vs ours={len(out)}")
    # sanity: userid order must match sequences
    if not (seq["userid"].astype(str).reset_index(drop=True)
            == c2["userid"].astype(str).reset_index(drop=True)).all():
        raise RuntimeError("userid order mismatch between sequences_next and c2hgi next.parquet")
    out["next_category"] = c2["next_category"].values
    out["userid"] = c2["userid"].values

    out.to_parquet(out_p, index=False)
    print(f"  wrote {out_p}  shape={out.shape}")
    # quick non-degeneracy check
    arr = out[[str(i) for i in range(WINDOW * EMB_DIM)]].to_numpy()
    print(f"  emb stats: nan={np.isnan(arr).any()} min={arr.min():.4f} max={arr.max():.4f} "
          f"mean={arr.mean():.4f} frac_zero_rows={(np.abs(arr).sum(1)==0).mean():.4f}")


if __name__ == "__main__":
    main()
