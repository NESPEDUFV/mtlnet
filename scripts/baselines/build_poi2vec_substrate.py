#!/usr/bin/env python
"""FAITHFUL POI2Vec (Feng et al., AAAI 2017; ref github.com/yongqyu/POI2Vec) — build a
STANDALONE per-POI 64-d probe-engine substrate that plugs under the matched champion
heads (cat=next_gru, reg=next_stan_flow_dualtower) via train.py --engine, exactly like
build_geotree_skipgram_substrate.py / build_overlap_probe_engine.py.

This is the class-(A) SC-substrate-column FAITHFUL POI2Vec baseline. It implements the
four defining POI2Vec mechanisms RIGHT (the geotree_skipgram baseline gets all four
wrong): (1) FIXED recursive rectangular midpoint tree over the state bbox to theta;
(2) OVERLAP-AREA phi; (3) CBOW forward + hierarchical softmax + USER term; (4) tables
poi_embed/user_embed/node_vec, EXPORT ONLY poi_embed. See poi2vec_lib/model.py +
README_poi2vec.md (incl. DIM=64 matched-protocol deviation + the loss-form note).

LEAK-SAFE per-fold protocol (HARD requirement) — VERBATIM from the geotree template:
  POI2Vec is PRETRAINED on the FOLD'S TRAIN PORTION ONLY. We reproduce the trainer's
  user-disjoint split bit-identically with StratifiedGroupKFold(userid) over
  load_next_data(state, CHECK2HGI) (same algorithm/groups/y/seed as
  FoldCreator._create_check2hgi_mtl_folds @ folds.py:1162 and
  compute_region_transition._build_per_fold), take train_idx, derive the TRAIN-USER
  set, and build CBOW examples ONLY from check-ins of train users. We assert val users
  are disjoint from train users before training.

  Because train.py reads ONE engine dir, this script emits into a SCRATCH OUTPUT_DIR
  (zero-enum escape hatch: PROBE_ENGINE=CHECK2HGI + scratch OUTPUT_DIR) and you run
  train.py --folds 1 against it.

SUBSTRATE ROW-ALIGNMENT (emit block VERBATIM from the geotree template):
  Reconstruct the check-in-level embeddings.parquet by LEFT-JOIN of the per-POI POI2Vec
  table onto the check2hgi embeddings frame on placeid, then run the canonical
  generate_next_input_from_checkins + build_next_region_for so next/next_region/sequences
  are byte-compatible + row-aligned with the champion pipeline (asserts mirror it).

REQUIRED HARDENING: a hard guard at the TOP of main(), before any write, refuses to
clobber the FROZEN check2hgi substrate (embeddings + next + next_region dirs) unless
OUTPUT_DIR is a scratch dir.

Usage (smoke, leak-safe single fold, into a scratch OUTPUT_DIR):
  OUTPUT_DIR=/tmp/bl_poi2vec PYTHONPATH=src .venv/bin/python \
    scripts/baselines/build_poi2vec_substrate.py alabama --seed 0 --fold 0 \
    --epochs 2 --theta 0.05 --route-count 4 --context-window 9 --device cpu
"""
import argparse
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
from poi2vec_lib import POI2VecAAAI, build_midpoint_tree, build_poi_routes  # noqa: E402

# Zero-enum escape hatch: reuse the allow-listed CHECK2HGI engine, emit into a SCRATCH
# OUTPUT_DIR, and run train.py --engine check2hgi pointed at the scratch dir. For the
# scored run, register a dedicated EmbeddingEngine member (deferred to the main agent's
# consolidated commit) and emit here.
PROBE_ENGINE = EmbeddingEngine.CHECK2HGI


def _frozen_check2hgi_root() -> Path:
    """Absolute path of the REAL (frozen) check2hgi output root, regardless of the
    current OUTPUT_DIR override. Repo-root/output/check2hgi."""
    repo_root = Path(__file__).resolve().parent.parent.parent
    return (repo_root / "output" / "check2hgi").resolve()


def assert_not_clobbering_frozen(dst_dir: Path):
    """REQUIRED HARDENING: refuse to write over the frozen check2hgi substrate.

    When PROBE_ENGINE==CHECK2HGI and OUTPUT_DIR is not a scratch dir, the emit paths
    would point AT output/check2hgi/<state>/. Assert the destination embeddings / next /
    next_region dirs are NOT the frozen ones. A 'scratch' OUTPUT_DIR is anything whose
    resolved path is not the repo's output/ tree.
    """
    frozen_root = _frozen_check2hgi_root()
    dst_resolved = dst_dir.resolve()
    # The three things the builder writes under dst_dir.
    targets = [
        IoPaths.get_embedd(state_for_guard, PROBE_ENGINE).resolve(),
        IoPaths.get_next(state_for_guard, PROBE_ENGINE).resolve(),
        IoPaths.get_next_region(state_for_guard, PROBE_ENGINE).resolve(),
    ]
    frozen_state_dir = (frozen_root / state_for_guard).resolve()
    for t in targets:
        # If any write target lives inside the frozen check2hgi/<state> tree, refuse.
        try:
            t.relative_to(frozen_state_dir)
            inside_frozen = True
        except ValueError:
            inside_frozen = False
        assert not inside_frozen, (
            f"REFUSING TO CLOBBER FROZEN check2hgi substrate: write target {t} is "
            f"inside {frozen_state_dir}. Use a scratch OUTPUT_DIR "
            f"(e.g. OUTPUT_DIR=/tmp/bl_poi2vec) — current OUTPUT_DIR={OUTPUT_DIR}."
        )
    # Also assert dst_dir itself is not the frozen state dir.
    assert dst_resolved != frozen_state_dir, (
        f"REFUSING TO CLOBBER: dst_dir {dst_resolved} == frozen {frozen_state_dir}"
    )


# module-global the guard reads (set in main before the guard call)
state_for_guard = "alabama"


def reproduce_fold_train_idx(state: str, seed: int, n_splits: int, fold: int):
    """Bit-identical to FoldCreator._create_check2hgi_mtl_folds @ folds.py:1162 /
    compute_region_transition._build_per_fold: StratifiedGroupKFold(userid).
    VERBATIM from build_geotree_skipgram_substrate.py."""
    from sklearn.model_selection import StratifiedGroupKFold

    X, y_cat, userids, _ = load_next_data(state, EmbeddingEngine.CHECK2HGI)
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for fi, (train_idx, val_idx) in enumerate(sgkf.split(X, y_cat, groups=userids)):
        if fi == fold:
            return train_idx, val_idx, userids
    raise ValueError(f"fold {fold} out of range for n_splits={n_splits}")


def build_cbow_examples(seq_df: pd.DataFrame, placeid_to_idx: dict,
                        userid_to_idx: dict, train_userids: set,
                        context_window: int, max_examples: int,
                        rng: np.random.Generator):
    """Build CBOW (context POIs, target POI, user) examples from TRAIN-USER sequences.

    Replaces the geotree template's build_skipgram_pairs. Each sequences_next row is a
    window poi_0..poi_8 + target_poi + userid. We slide a forward CBOW window over the
    non-pad POIs of each row: for each position t, the CONTEXT is the preceding up-to
    ``context_window`` POIs and the TARGET is the POI at t. (Forward/causal — matches
    the paper's "predict future visitor" framing.)

    LEAK-SAFE: rows whose userid is not in train_userids are dropped here.

    Returns:
        ctx_idx:  int64 [N, context_window] padded POI indices (pad = -1)
        ctx_len:  int64 [N] real context length per example
        tgt_idx:  int64 [N] target POI index
        usr_idx:  int64 [N] user index (in user_embed space)
    """
    poi_cols = [f"poi_{i}" for i in range(InputsConfig.SLIDE_WINDOW)] + ["target_poi"]
    mask = seq_df["userid"].astype(int).isin(train_userids)
    sub = seq_df.loc[mask, poi_cols + ["userid"]]

    ctx_rows: list[np.ndarray] = []
    ctx_lens: list[int] = []
    tgts: list[int] = []
    usrs: list[int] = []
    W = context_window
    for row in sub.itertuples(index=False):
        vals = row[:-1]
        uid = int(row[-1])
        uidx = userid_to_idx.get(uid)
        if uidx is None:
            continue
        toks = []
        for v in vals:
            try:
                pid = int(v)
            except (ValueError, TypeError):
                continue
            if pid < 0:
                continue
            pidx = placeid_to_idx.get(pid)
            if pidx is not None:
                toks.append(pidx)
        L = len(toks)
        # forward CBOW: target at t, context = preceding window (t-W .. t-1)
        for t in range(1, L):
            lo = max(0, t - W)
            ctx = toks[lo:t]
            if not ctx:
                continue
            padded = np.full(W, -1, dtype=np.int64)
            padded[:len(ctx)] = np.asarray(ctx, dtype=np.int64)
            ctx_rows.append(padded)
            ctx_lens.append(len(ctx))
            tgts.append(toks[t])
            usrs.append(uidx)

    if not ctx_rows:
        return (np.zeros((0, W), np.int64), np.zeros(0, np.int64),
                np.zeros(0, np.int64), np.zeros(0, np.int64))
    ctx_idx = np.stack(ctx_rows, axis=0)
    ctx_len = np.asarray(ctx_lens, dtype=np.int64)
    tgt_idx = np.asarray(tgts, dtype=np.int64)
    usr_idx = np.asarray(usrs, dtype=np.int64)
    if max_examples and len(tgt_idx) > max_examples:
        sel = rng.choice(len(tgt_idx), size=max_examples, replace=False)
        ctx_idx, ctx_len = ctx_idx[sel], ctx_len[sel]
        tgt_idx, usr_idx = tgt_idx[sel], usr_idx[sel]
    return ctx_idx, ctx_len, tgt_idx, usr_idx


def train_poi2vec(ctx_idx, ctx_len, tgt_idx, usr_idx, n_poi, n_user, poi_xy,
                  bbox, theta, route_count, user_dim, embed_dim, epochs,
                  batch_size, lr, n_neg_user, loss_form, device):
    print(f"  building FIXED midpoint tree (theta={theta}, bbox={tuple(round(b,4) for b in bbox)})...")
    tree = build_midpoint_tree(bbox, theta=theta)
    print(f"  tree: n_internal={tree.n_internal} n_leaf={tree.n_leaf}")
    print(f"  computing overlap-area phi (route_count={route_count}) for {n_poi} POIs...")
    routes = build_poi_routes(poi_xy, tree, theta=theta, route_count=route_count)
    avg_leaves = float(np.mean([len(r[0]) for r in routes]))
    print(f"  avg routed leaves/POI={avg_leaves:.3f}")

    model = POI2VecAAAI(n_poi, n_user, tree, routes, embed_dim=embed_dim,
                        route_count=route_count, n_neg_user=n_neg_user,
                        loss_form=loss_form).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)

    ctx = torch.from_numpy(ctx_idx)                # [N,W]
    mask = torch.from_numpy((ctx_idx >= 0))        # [N,W] bool
    tgt = torch.from_numpy(tgt_idx)
    usr = torch.from_numpy(usr_idx)
    n = len(tgt_idx)
    print(f"  training POI2VecAAAI ({loss_form} loss): {n:,} CBOW examples, "
          f"{epochs} epochs, bs={batch_size}, lr={lr}, neg_user={n_neg_user}, device={device}")
    model.train()
    for ep in range(epochs):
        perm = torch.randperm(n)
        # Accumulate on-device — NO per-batch .item() (it forces a CPU<->GPU sync
        # that serializes MPS/CUDA). Canonical: src/training/runners/mtl_cv.py:818.
        tot = torch.zeros((), device=device)
        nb = 0
        t0 = time.time()
        for s in range(0, n, batch_size):
            bi = perm[s:s + batch_size]
            cb = ctx[bi].to(device)
            mb = mask[bi].to(device)
            tb = tgt[bi].to(device)
            ub = usr[bi].to(device)
            opt.zero_grad(set_to_none=True)
            loss = model.forward_nll(cb, mb, tb, ub)
            loss.backward()
            opt.step()
            tot += loss.detach()
            nb += 1
        print(f"    epoch {ep+1}/{epochs}: loss={(tot/max(nb,1)).item():.4f} ({time.time()-t0:.1f}s)")
    return model.export_table()


def main():
    global state_for_guard
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--embed-dim", type=int, default=64, help="MATCHED to board (paper:200)")
    ap.add_argument("--user-dim", type=int, default=64, help="user latent dim (matched to embed-dim)")
    ap.add_argument("--batch-size", type=int, default=1024)
    ap.add_argument("--lr", type=float, default=0.025)
    ap.add_argument("--context-window", type=int, default=9)
    ap.add_argument("--theta", type=float, default=0.05, help="leaf cell size (degrees)")
    ap.add_argument("--route-count", type=int, default=4, help="max leaves per POI (top by overlap area)")
    ap.add_argument("--n-neg-user", type=int, default=5, help="negative-sampled user softmax k")
    ap.add_argument("--loss-form", choices=["mixture", "noisy_or"], default="mixture",
                    help="mixture=stable -log(sum phi*pr_user*pr_path); noisy_or=paper exact")
    ap.add_argument("--max-examples", type=int, default=0, help="0 = use all CBOW examples")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--all-data", action="store_true",
                    help="LEAKY: pretrain on ALL users (smoke only, never scored).")
    ap.add_argument("--stride", type=int, default=None,
                    help="window stride for next.parquet (None=non-overlap default; P3 uses 1).")
    args = ap.parse_args()

    state = args.state.lower()
    state_for_guard = state
    if args.user_dim != args.embed_dim:
        print(f"  NOTE: --user-dim {args.user_dim} != --embed-dim {args.embed_dim}; the "
              f"model uses a single shared dim. Using {args.embed_dim}.")
    device = torch.device(args.device)
    rng = np.random.default_rng(args.seed)

    if args.all_data:
        tag = f"ALLDATA(leaky-smoke) seed={args.seed}"
    else:
        tag = f"seed={args.seed} fold={args.fold}"
    dst_dir = OUTPUT_DIR / PROBE_ENGINE.value / state
    print(f"=== build FAITHFUL POI2Vec (AAAI'17) substrate :: {state} :: {tag} ===")
    print(f"    OUTPUT_DIR={OUTPUT_DIR}  (engine dir={dst_dir})")

    # ---- REQUIRED HARDENING: refuse to clobber the frozen check2hgi substrate. ----
    assert_not_clobbering_frozen(dst_dir)
    print("  guard OK: not writing into the frozen check2hgi substrate.")

    # 1. Leak-safe fold split -> train-user set. (VERBATIM from geotree template.)
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
        assert val_userids.isdisjoint(train_userids), "LEAK: val users overlap train users!"
        print(f"  fold {args.fold}: train_users={len(train_userids)} "
              f"val_users={len(val_userids)} (disjoint OK)")

    # 2. POI universe + coordinates + user index map.
    from data.inputs.region_sequence import _load_graph_maps
    placeid_to_idx, _poi_to_region = _load_graph_maps(state)
    n_poi = max(placeid_to_idx.values()) + 1
    checkins = IoPaths.load_city(state)
    coord = (checkins.groupby("placeid")[["longitude", "latitude"]].mean())
    poi_xy = np.full((n_poi, 2), np.nan, dtype=np.float64)
    have = 0
    for pid, idx in placeid_to_idx.items():
        if pid in coord.index:
            poi_xy[idx] = coord.loc[pid, ["longitude", "latitude"]].to_numpy()
            have += 1
    # bbox over filled coords (DATA-INDEPENDENT-shape tree; bbox is geometry, not labels)
    fin = np.isfinite(poi_xy).all(axis=1)
    lon = poi_xy[fin, 0]
    lat = poi_xy[fin, 1]
    bbox = (float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max()))
    print(f"  POI universe n_poi={n_poi}, coords filled={have}, bbox={tuple(round(b,4) for b in bbox)}")

    # user index map: load_next_data returns RAW userids; build a contiguous map.
    all_uids = np.unique(userids.astype(np.int64))
    userid_to_idx = {int(u): i for i, u in enumerate(all_uids)}
    n_user = len(all_uids)
    print(f"  n_user={n_user} (userid->idx map built; raw userids from load_next_data)")

    # 3. CBOW examples from TRAIN-USER sequences ONLY.
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, EmbeddingEngine.CHECK2HGI))
    ctx_idx, ctx_len, tgt_idx, usr_idx = build_cbow_examples(
        seq_df, placeid_to_idx, userid_to_idx, train_userids,
        context_window=args.context_window, max_examples=args.max_examples, rng=rng)
    print(f"  CBOW examples (train-only)={len(tgt_idx):,}")
    if len(tgt_idx) == 0:
        raise RuntimeError("no CBOW examples — check train_userids / sequences.")

    # 4. Train POI2Vec -> per-POI latent table (EXPORT ONLY poi_embed).
    poi_table = train_poi2vec(
        ctx_idx, ctx_len, tgt_idx, usr_idx, n_poi, n_user, poi_xy, bbox,
        args.theta, args.route_count, args.user_dim, args.embed_dim, args.epochs,
        args.batch_size, args.lr, args.n_neg_user, args.loss_form, device)
    print(f"  POI2Vec poi_embed table shape={poi_table.shape}")

    # ===== EMIT BLOCK — VERBATIM from build_geotree_skipgram_substrate.py =====
    # 5. Reconstruct CHECK-IN-LEVEL embeddings.parquet aligned to check2hgi row order
    #    (LEFT JOIN per-POI table onto check2hgi embeddings frame on placeid).
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
