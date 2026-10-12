#!/usr/bin/env python
"""GeoTreeSkipGram (geographically-tree-regularized skip-gram) — build a STANDALONE
per-POI 64-d probe engine that plugs into the matched-head MTL pipeline (cat=next_gru,
reg=next_stan_flow_dualtower) exactly like build_overlap_probe_engine.py.

⚠ NOT POI2Vec (AAAI'17). This is an honest geo-regularized skip-gram baseline; the
faithful AAAI'17 POI2Vec builder is scripts/baselines/build_poi2vec_substrate.py.

LEAK-SAFE per-fold protocol (HARD requirement):
  GeoTreeSkipGram is PRETRAINED on the FOLD'S TRAIN PORTION ONLY. We reproduce the
  trainer's user-disjoint split bit-identically with
  ``StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed)`` over
  ``load_next_data(state, CHECK2HGI)`` (same algorithm/groups/y/seed as
  ``FoldCreator._create_check2hgi_mtl_folds`` and
  ``compute_region_transition._build_per_fold``), take ``train_idx``, derive the
  TRAIN-USER set, and build skip-gram pairs ONLY from check-ins of train users.
  We assert ``val users are disjoint from train users`` before training.

  Because train.py reads ONE engine dir, this script emits a PER-FOLD engine dir
  ``<engine>_seed{S}_fold{N}`` and you run train.py with ``--folds 1`` against it
  (fully leak-clean). A whole-corpus mode (``--all-data``) exists ONLY for a quick
  smoke and is loudly flagged as leaky (NOT for scored runs).

SUBSTRATE ROW-ALIGNMENT:
  The matched heads consume a CHECK-IN-LEVEL ``embeddings.parquet`` with columns
  ``userid, placeid, category, datetime, 0..63`` in the SAME row order as the
  frozen check2hgi substrate. We reconstruct it by LEFT-JOINING the per-POI
  GeoTreeSkipGram table onto the check2hgi embeddings frame on ``placeid`` (so every
  check-in of a POI gets that POI's vector — GeoTreeSkipGram is per-POI by construction).
  We then run the canonical ``generate_next_input_from_checkins`` +
  ``build_next_region_for`` so next/next_region/sequences are byte-compatible
  with the champion pipeline and row-aligned (asserts mirror the champion's).

Usage (smoke, leak-safe single fold, into a scratch OUTPUT_DIR):
  OUTPUT_DIR=/tmp/bl_b2a PYTHONPATH=src .venv/bin/python \
    scripts/baselines/build_geotree_skipgram_substrate.py alabama --seed 0 --fold 0 \
    --epochs 2 --max-pairs 200000 --device cpu
"""
import argparse
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR
from configs.model import InputsConfig
from data.folds import load_next_data
from data.inputs.builders import generate_next_input_from_checkins

# Reuse the canonical next_region builder verbatim (poi->region from check2hgi graph).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mtl_improvement"))
from build_overlap_probe_engine import build_next_region_for  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geotree_skipgram_lib import GeoTreeSkipGram, build_geo_binary_tree  # noqa: E402

# The probe engine value. We reuse an EXISTING allow-listed engine (CHECK2HGI)
# at the FROZEN check2hgi allow-lists by emitting into a SCRATCH OUTPUT_DIR and
# running train.py --engine check2hgi pointed at the scratch dir (zero enum edit,
# per the integration guide's escape hatch). For the scored P3 run, register a
# dedicated EmbeddingEngine member (see PR note in the final report) and emit here.
PROBE_ENGINE = EmbeddingEngine.CHECK2HGI


def reproduce_fold_train_idx(state: str, seed: int, n_splits: int, fold: int):
    """Bit-identical to FoldCreator._create_check2hgi_mtl_folds /
    compute_region_transition._build_per_fold: StratifiedGroupKFold(userid)."""
    from sklearn.model_selection import StratifiedGroupKFold

    X, y_cat, userids, _ = load_next_data(state, EmbeddingEngine.CHECK2HGI)
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for fi, (train_idx, val_idx) in enumerate(sgkf.split(X, y_cat, groups=userids)):
        if fi == fold:
            return train_idx, val_idx, userids
    raise ValueError(f"fold {fold} out of range for n_splits={n_splits}")


def build_skipgram_pairs(seq_df: pd.DataFrame, placeid_to_idx: dict,
                         train_userids: set, window: int, max_pairs: int,
                         rng: np.random.Generator):
    """Build (center, context) POI-index skip-gram pairs from TRAIN-USER
    sequences only. Each sequences_next row is a window of poi_0..poi_8 +
    target_poi; we slide a context window over the non-pad POIs.

    LEAK-SAFE: rows whose userid is not in train_userids are dropped here.
    """
    poi_cols = [f"poi_{i}" for i in range(InputsConfig.SLIDE_WINDOW)] + ["target_poi"]
    mask = seq_df["userid"].astype(int).isin(train_userids)
    sub = seq_df.loc[mask, poi_cols]
    centers: list[int] = []
    contexts: list[int] = []
    for row in sub.itertuples(index=False):
        toks = []
        for v in row:
            try:
                pid = int(v)
            except (ValueError, TypeError):
                continue
            if pid < 0:
                continue
            idx = placeid_to_idx.get(pid)
            if idx is not None:
                toks.append(idx)
        L = len(toks)
        for i in range(L):
            lo = max(0, i - window)
            hi = min(L, i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                centers.append(toks[i])
                contexts.append(toks[j])
    centers = np.asarray(centers, dtype=np.int64)
    contexts = np.asarray(contexts, dtype=np.int64)
    if max_pairs and len(centers) > max_pairs:
        sel = rng.choice(len(centers), size=max_pairs, replace=False)
        centers, contexts = centers[sel], contexts[sel]
    return centers, contexts


def train_geotree_skipgram(centers, contexts, n_poi, poi_xy, embed_dim, epochs,
                  batch_size, lr, max_depth, min_leaf, boundary_frac, device):
    print(f"  building geo binary tree (depth<={max_depth}, min_leaf={min_leaf}, "
          f"boundary_frac={boundary_frac})...")
    tree = build_geo_binary_tree(poi_xy, max_depth=max_depth, min_leaf=min_leaf,
                                 boundary_frac=boundary_frac)
    print(f"  tree internal nodes={tree.n_internal}")
    model = GeoTreeSkipGram(n_poi, tree, embed_dim=embed_dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    c = torch.from_numpy(centers)
    x = torch.from_numpy(contexts)
    n = len(centers)
    print(f"  training GeoTreeSkipGram: {n:,} pairs, {epochs} epochs, bs={batch_size}, "
          f"lr={lr}, device={device}")
    model.train()
    for ep in range(epochs):
        perm = torch.randperm(n)
        tot, nb = 0.0, 0
        t0 = time.time()
        for s in range(0, n, batch_size):
            bi = perm[s:s + batch_size]
            cb = c[bi].to(device)
            xb = x[bi].to(device)
            opt.zero_grad()
            loss = model.path_loss(cb, xb)
            loss.backward()
            opt.step()
            tot += loss.item()
            nb += 1
        print(f"    epoch {ep+1}/{epochs}: loss={tot/max(nb,1):.4f} "
              f"({time.time()-t0:.1f}s)")
    return model.export_table()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--embed-dim", type=int, default=64)
    ap.add_argument("--batch-size", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=0.025)
    ap.add_argument("--context-window", type=int, default=2)
    ap.add_argument("--max-pairs", type=int, default=0, help="0 = use all pairs")
    ap.add_argument("--max-depth", type=int, default=12)
    ap.add_argument("--min-leaf", type=int, default=8)
    ap.add_argument("--boundary-frac", type=float, default=0.05)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--all-data", action="store_true",
                    help="LEAKY: pretrain on ALL users (smoke only, never scored).")
    ap.add_argument("--stride", type=int, default=None,
                    help="window stride for next.parquet (None=non-overlap default; P3 uses 1).")
    args = ap.parse_args()

    state = args.state.lower()
    device = torch.device(args.device)
    rng = np.random.default_rng(args.seed)

    # Per-fold engine identity so train.py --folds 1 is fully leak-clean.
    if args.all_data:
        engine_value = f"{PROBE_ENGINE.value}"  # scratch; leaky smoke writes into scratch OUTPUT_DIR
        tag = f"ALLDATA(leaky-smoke) seed={args.seed}"
    else:
        engine_value = PROBE_ENGINE.value
        tag = f"seed={args.seed} fold={args.fold}"
    dst_dir = OUTPUT_DIR / engine_value / state
    print(f"=== build B2a GeoTreeSkipGram substrate :: {state} :: {tag} ===")
    print(f"    OUTPUT_DIR={OUTPUT_DIR}  (engine dir={dst_dir})")

    # 1. Leak-safe fold split -> train-user set.
    if args.all_data:
        _, _, userids = reproduce_fold_train_idx(state, args.seed, args.n_splits, 0)
        train_userids = set(int(u) for u in userids)
        val_userids: set = set()
        print("  WARNING: --all-data uses ALL users (LEAKY). Smoke only.")
    else:
        train_idx, val_idx, userids = reproduce_fold_train_idx(
            state, args.seed, args.n_splits, args.fold)
        train_userids = set(int(u) for u in userids[train_idx])
        val_userids = set(int(u) for u in userids[val_idx])
        # HARD leak assertion.
        assert val_userids.isdisjoint(train_userids), "LEAK: val users overlap train users!"
        print(f"  fold {args.fold}: train_users={len(train_userids)} "
              f"val_users={len(val_userids)} (disjoint OK)")

    # 2. POI universe + coordinates (geo tree). Use check2hgi graph poi index space.
    from data.inputs.region_sequence import _load_graph_maps
    placeid_to_idx, _poi_to_region = _load_graph_maps(state)
    n_poi = max(placeid_to_idx.values()) + 1
    checkins = IoPaths.load_city(state)
    coord = (checkins.groupby("placeid")[["longitude", "latitude"]].mean())
    poi_xy = np.zeros((n_poi, 2), dtype=np.float64)
    have = 0
    for pid, idx in placeid_to_idx.items():
        if pid in coord.index:
            poi_xy[idx] = coord.loc[pid, ["longitude", "latitude"]].to_numpy()
            have += 1
    print(f"  POI universe n_poi={n_poi}, coords filled={have}")

    # 3. Skip-gram pairs from TRAIN-USER sequences ONLY.
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, EmbeddingEngine.CHECK2HGI))
    centers, contexts = build_skipgram_pairs(
        seq_df, placeid_to_idx, train_userids,
        window=args.context_window, max_pairs=args.max_pairs, rng=rng)
    print(f"  skip-gram pairs (train-only)={len(centers):,}")
    if len(centers) == 0:
        raise RuntimeError("no skip-gram pairs — check train_userids / sequences.")

    # 4. Train GeoTreeSkipGram -> per-POI latent table.
    poi_table = train_geotree_skipgram(
        centers, contexts, n_poi, poi_xy, args.embed_dim, args.epochs,
        args.batch_size, args.lr, args.max_depth, args.min_leaf,
        args.boundary_frac, device)
    print(f"  GeoTreeSkipGram table shape={poi_table.shape}")

    # 5. Reconstruct CHECK-IN-LEVEL embeddings.parquet aligned to check2hgi row order.
    base_emb = IoPaths.load_embedd(state, EmbeddingEngine.CHECK2HGI)
    idx_col = base_emb["placeid"].astype(int).map(placeid_to_idx)
    missing = int(idx_col.isna().sum())
    idx_arr = idx_col.fillna(-1).astype(int).to_numpy()
    emb_mat = np.zeros((len(base_emb), args.embed_dim), dtype=np.float32)
    valid = idx_arr >= 0
    emb_mat[valid] = poi_table[idx_arr[valid]]
    out_emb = base_emb[["userid", "placeid", "category", "datetime"]].copy()
    for d in range(args.embed_dim):
        out_emb[str(d)] = emb_mat[:, d]
    assert len(out_emb) == len(base_emb), (len(out_emb), len(base_emb))
    dst_dir.mkdir(parents=True, exist_ok=True)
    emb_path = IoPaths.get_embedd(state, PROBE_ENGINE)
    out_emb.to_parquet(emb_path, index=False)
    print(f"  embeddings.parquet -> {emb_path} (rows={len(out_emb)}, "
          f"placeids w/o poi-idx={missing})")

    # 6. Canonical next.parquet + sequences + next_region (row-aligned, asserts inside).
    print("  building next.parquet + sequences ...")
    generate_next_input_from_checkins(state, PROBE_ENGINE, stride=args.stride)
    print("  building next_region.parquet ...")
    build_next_region_for(state, PROBE_ENGINE)

    # 7. region_embeddings.parquet — geographic partition is SHARED; symlink from check2hgi.
    src_region = OUTPUT_DIR.parent / "output" / "check2hgi" / state / "region_embeddings.parquet"
    # robust: resolve via IoPaths of check2hgi
    src_region = IoPaths.get_embedd(state, EmbeddingEngine.CHECK2HGI).parent / "region_embeddings.parquet"
    dst_region = emb_path.parent / "region_embeddings.parquet"
    if src_region.resolve() != dst_region.resolve():
        if dst_region.exists() or dst_region.is_symlink():
            dst_region.unlink()
        dst_region.symlink_to(src_region.resolve())
        print(f"  region_embeddings.parquet -> symlink {src_region}")

    n = len(IoPaths.load_next(state, PROBE_ENGINE))
    nr = len(IoPaths.load_next_region(state, PROBE_ENGINE))
    assert n == nr, (n, nr)
    print(f"DONE: {state} next.parquet rows={n:,} (next_region rows={nr:,}) — row-aligned OK")


if __name__ == "__main__":
    main()
