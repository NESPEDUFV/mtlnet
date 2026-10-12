"""Design A — late-fusion concat substrate (c2hgi check-in + HGI POI per step).

Per the merge design ladder. Builds an artefact directory under
``output/c2hgi_hgi_concat/<state>/`` containing:

  embeddings.parquet         per-check-in [c2hgi(64), hgi_poi(64)] = 128-dim
  region_embeddings.parquet  unchanged HGI region embeddings (cat-stable consumer)
  input/next.parquet         per-step concat for cat task (9×128 + meta)
  input/next_region.parquet  per-step concat for reg task (9×128 + meta)

The downstream pipeline reads these as if it were a single 128-dim engine.
No training step — this is pure feature concatenation.

Usage::

    python scripts/probe/build_design_a_concat.py --state alabama
    python scripts/probe/build_design_a_concat.py --state arizona
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import numpy as np
import pandas as pd

EMB_DIM = 64
SLIDE = 9
PAD = -1


def load_hgi_poi_embeddings(state: str) -> tuple[np.ndarray, dict]:
    """Return (poi_emb [N_pois, 64], placeid_to_idx) keyed to canonical c2hgi
    POI ordering — so check-in lookups translate cleanly through the existing
    placeid_to_idx map.
    """
    state_lc = state.lower()
    state_cap = state.capitalize()

    # HGI's POI embeddings live as poi2vec_poi_embeddings_<State>.csv (per-placeid).
    # Use that as the canonical HGI POI source — it's what HGI feeds into POIEncoder
    # as input. (HGI's own embeddings.parquet is post-encoder; we want the input view.)
    hgi_csv = Path("output/hgi") / state_lc / f"poi2vec_poi_embeddings_{state_cap}.csv"
    df = pd.read_csv(hgi_csv)
    emb_cols = [str(i) for i in range(EMB_DIM)]
    placeid_to_hgi = {int(p): df[emb_cols].iloc[i].to_numpy(dtype=np.float32)
                      for i, p in enumerate(df["placeid"].astype(int).tolist())}

    return placeid_to_hgi


def build_concat_next(state: str) -> None:
    state_lc = state.lower()
    base = Path("output/c2hgi_hgi_concat") / state_lc
    base.mkdir(parents=True, exist_ok=True)
    (base / "input").mkdir(parents=True, exist_ok=True)
    (base / "temp").mkdir(parents=True, exist_ok=True)

    # ── Inputs ─────────────────────────────────────────────────────────────
    c2hgi_next = pd.read_parquet(f"output/check2hgi/{state_lc}/input/next.parquet")
    seq = pd.read_parquet(f"output/check2hgi/{state_lc}/temp/sequences_next.parquet")
    placeid_to_hgi = load_hgi_poi_embeddings(state)

    n_rows = len(c2hgi_next)
    assert len(seq) == n_rows, f"row mismatch: c2hgi_next={n_rows} seq={len(seq)}"

    c2hgi_emb_cols = [str(i) for i in range(SLIDE * EMB_DIM)]  # 0..575
    c2hgi_arr = c2hgi_next[c2hgi_emb_cols].to_numpy(dtype=np.float32)
    c2hgi_arr = c2hgi_arr.reshape(n_rows, SLIDE, EMB_DIM)  # [N, 9, 64]

    # Build per-step HGI POI embeddings via placeid lookup
    hgi_arr = np.zeros((n_rows, SLIDE, EMB_DIM), dtype=np.float32)
    n_unmapped = 0
    for s in range(SLIDE):
        col = f"poi_{s}"
        placeids = seq[col].astype(str).to_numpy()
        for i, p_str in enumerate(placeids):
            if p_str == "-1" or p_str == "nan":
                continue  # padding stays zero
            try:
                p = int(p_str)
            except ValueError:
                continue
            v = placeid_to_hgi.get(p)
            if v is None:
                n_unmapped += 1
                continue
            hgi_arr[i, s] = v

    if n_unmapped > 0:
        print(f"[{state_lc}] {n_unmapped} placeids not in HGI POI2Vec table — left zero")

    # Concat per step
    fused = np.concatenate([c2hgi_arr, hgi_arr], axis=-1)  # [N, 9, 128]
    fused_flat = fused.reshape(n_rows, SLIDE * 2 * EMB_DIM)

    # ── next.parquet (cat task) ────────────────────────────────────────────
    out_next = pd.DataFrame(fused_flat, columns=[str(i) for i in range(fused_flat.shape[1])])
    out_next["next_category"] = c2hgi_next["next_category"].values
    out_next["userid"] = c2hgi_next["userid"].values
    out_next.to_parquet(base / "input" / "next.parquet", index=False)
    print(f"[{state_lc}] wrote next.parquet shape={fused_flat.shape} (per-step dim=128)")

    # ── next_region.parquet (reg task) ─────────────────────────────────────
    c2hgi_reg = pd.read_parquet(f"output/check2hgi/{state_lc}/input/next_region.parquet")
    assert len(c2hgi_reg) == n_rows, "next_region row mismatch"
    out_reg = pd.DataFrame(fused_flat, columns=[str(i) for i in range(fused_flat.shape[1])])
    out_reg["userid"] = c2hgi_reg["userid"].values
    out_reg["region_idx"] = c2hgi_reg["region_idx"].values
    if "last_region_idx" in c2hgi_reg.columns:
        out_reg["last_region_idx"] = c2hgi_reg["last_region_idx"].values
    out_reg.to_parquet(base / "input" / "next_region.parquet", index=False)
    print(f"[{state_lc}] wrote next_region.parquet shape={fused_flat.shape}")

    # ── sequences_next + graph (mirror canonical for downstream lookups) ───
    import shutil
    src_seq = Path(f"output/check2hgi/{state_lc}/temp/sequences_next.parquet")
    src_graph = Path(f"output/check2hgi/{state_lc}/temp/checkin_graph.pt")
    shutil.copy(src_seq, base / "temp" / "sequences_next.parquet")
    if src_graph.exists():
        shutil.copy(src_graph, base / "temp" / "checkin_graph.pt")

    # ── per-fold log_T (substrate-independent — symlink) ───────────────────
    for f in range(1, 6):
        src = Path(f"output/check2hgi/{state_lc}/region_transition_log_seed42_fold{f}.pt")
        dst = base / f"region_transition_log_seed42_fold{f}.pt"
        if src.exists() and not dst.exists():
            dst.symlink_to(src.resolve())

    print(f"[{state_lc}] artifact tree ready under {base}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", required=True)
    args = ap.parse_args()
    build_concat_next(args.state.lower())


if __name__ == "__main__":
    main()
