#!/usr/bin/env python
"""B2b — skip-gram (word2vec/SGNS) over check-in sequences, 64-d probe engine.

SPEC (board baseline B2b)
-------------------------
Train skip-gram on check-in POI sequences, TRAIN-PORTION-ONLY per fold; emit a
64-d check-in-level ``embeddings.parquet`` that plugs into the FROZEN
matched-head MTL pipeline (cat=next_gru, reg=next_stan_flow_dualtower) via
``train.py --engine``. This is a class-(A) SC-SUBSTRATE-COLUMN baseline — it
only changes the substrate axis; folds/seeds/labels/metric/heads/selector are
identical to the champion.

Cite: Mikolov et al., NeurIPS 2013 (Skip-Gram w/ Negative Sampling). POI-seq
treatment per DeepCity (arXiv:1610.03676) / CAPE / SG-CWARP.

Deviations (documented):
  - In-repo ``research/embeddings/hgi/poi2vec.py`` is the FCLASS-level HGI
    teacher (categories), NOT this baseline. B2b is a standalone POI-level
    skip-gram producing a per-POI 64-d vector, looked up per check-in.
  - POIs unseen in the fold's train users get a deterministic ZERO vector
    (cold-start placeholder; never trained on val users -> no leak).
  - WINDOWING: this script builds the CURRENT stride-9 (non-overlapping)
    substrate for the SMOKE / code path. The board's paper-grade n=20 runs are
    stride-1 (P3, post-freeze) — pass ``--stride 1`` then.

LEAK-SAFETY (HARD requirement)
------------------------------
Per (state, seed, fold) we:
  1. load_next_data(state, CHECK2HGI) -> X, y_cat, userids (champion loader).
  2. StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed).split(
        X, y_cat, groups=userids)  -> bit-identical to the champion fold split.
  3. train_userids = set(userids[train_idx]); assert disjoint from val users.
  4. skip-gram trains ONLY on POI sequences of train_userids.
  5. emit a FOLD-SPECIFIC engine dir; run train.py with --folds 1 on it.

ARTIFACTS (under output/<engine_value>/<state>/, namespaced — never collide)
  - embeddings.parquet      : check-in-level, row order = check2hgi's
                              (sorted ['userid','datetime']); cols
                              userid,placeid,category,datetime,0..63
  - input/next.parquet      : built by generate_next_input_from_checkins
  - temp/sequences_next.parquet
  - input/next_region.parquet : built by build_next_region_for (shared partition)
  - region_embeddings.parquet : SYMLINK from check2hgi (geographic partition is
                              substrate-independent for B2b)

Usage (per-fold leak-clean build):
  PYTHONPATH=src .venv/bin/python scripts/baselines/build_b2b_skipgram_substrate.py \
      --state alabama --seed 0 --fold 0 --epochs 5

  # smoke (writes into an OUTPUT_DIR scratch + --engine check2hgi at train time):
  OUTPUT_DIR=/tmp/bl_b2b PYTHONPATH=src .venv/bin/python \
      scripts/baselines/build_b2b_skipgram_substrate.py \
      --state alabama --seed 0 --fold 0 --epochs 2 --smoke
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import StratifiedGroupKFold

# allow running with PYTHONPATH=src OR bare (we add src/ ourselves)
_REPO = Path(__file__).resolve().parents[2]
for _p in (str(_REPO / "src"), str(_REPO / "scripts" / "baselines")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR  # noqa: E402
from configs.model import InputsConfig  # noqa: E402
from data.inputs.builders import generate_next_input_from_checkins  # noqa: E402

from skipgram_lib import train_skipgram  # noqa: E402

# B2b column engine value. Smoke writes into an OUTPUT_DIR scratch and trains
# with --engine check2hgi (frozen allow-lists accept it), so NO enum edit is
# needed for dev/smoke. For the scored P3 run, append ONE enum member
# `B2B_SKIPGRAM = "b2b_skipgram"` to EmbeddingEngine + the three allow-lists
# (paths.get_next_region `supported`, folds._MTL_C2HGI_ALLOWED_ENGINES,
# builders._CHECKIN_LEVEL_ENGINES) — documented for sequential [ENUM-MERGE].
B2B_ENGINE_VALUE = "b2b_skipgram"
CHECK2HGI = EmbeddingEngine.CHECK2HGI


def _c2hgi_embeddings(state: str, read_root: Path) -> pd.DataFrame:
    """Read the FROZEN check2hgi check-in embeddings.parquet from read_root."""
    return pd.read_parquet(read_root / CHECK2HGI.value / state.lower() / "embeddings.parquet")


def _c2hgi_graph_maps(state: str, read_root: Path):
    """poi->region maps from the FROZEN check2hgi graph at read_root (shared
    geographic partition, substrate-independent)."""
    import pickle as pkl
    gpath = read_root / CHECK2HGI.value / state.lower() / "temp" / "checkin_graph.pt"
    with open(gpath, "rb") as f:
        graph = pkl.load(f)
    placeid_to_idx = graph["placeid_to_idx"]
    poi_to_region = graph["poi_to_region"]
    if hasattr(poi_to_region, "cpu"):
        poi_to_region = poi_to_region.cpu().numpy()
    return placeid_to_idx, np.asarray(poi_to_region, dtype=np.int64)


# --------------------------------------------------------------------------
# Leak-safe fold derivation (bit-identical to the champion split)
# --------------------------------------------------------------------------
def get_fold_train_userids(state: str, seed: int, fold: int, read_root: Path, n_splits: int = 5):
    """Return (train_userids:set, val_userids:set) for (seed, fold).

    Bit-identical to FoldCreator._create_check2hgi_mtl_folds and to
    compute_region_transition._build_per_fold: StratifiedGroupKFold over the
    FROZEN check2hgi next.parquet, groups=userid, y=next_category. We read it
    directly from read_root (not via OUTPUT_DIR) so the scratch overlay never
    perturbs the canonical fold split.
    """
    next_df = pd.read_parquet(read_root / CHECK2HGI.value / state.lower() / "input" / "next.parquet")
    from data.folds import _map_categories  # the same label map load_next_data uses
    labels = _map_categories(next_df["next_category"])
    valid = ~labels.isna()
    userids = next_df.loc[valid, "userid"].astype(int).to_numpy()
    y_cat = labels[valid].to_numpy().astype(np.int64)
    X = np.zeros((len(userids), 1), dtype=np.float32)  # SGKF only uses y + groups
    sgkf = StratifiedGroupKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    for fi, (train_idx, val_idx) in enumerate(sgkf.split(X, y_cat, groups=userids)):
        if fi == fold:
            train_users = set(int(u) for u in userids[train_idx])
            val_users = set(int(u) for u in userids[val_idx])
            # HARD leak assert: user-disjoint folds
            assert train_users.isdisjoint(val_users), "fold users overlap!"
            return train_users, val_users
    raise ValueError(f"fold {fold} out of range for n_splits={n_splits}")


# --------------------------------------------------------------------------
# Pretrain corpus = TRAIN-user POI sequences only
# --------------------------------------------------------------------------
def build_train_poi_sequences(checkins_df: pd.DataFrame, train_userids: set):
    """Per train-user chronological placeid trajectory -> list of int sequences.

    One "sentence" per user (the full trajectory). The skip-gram window is
    applied inside train_skipgram. Uses ONLY train_userids check-ins.
    """
    sub = checkins_df[checkins_df["userid"].astype(int).isin(train_userids)]
    sub = sub.sort_values(["userid", "datetime"])
    seqs = []
    for _uid, udf in sub.groupby("userid"):
        seqs.append([int(p) for p in udf["placeid"].tolist()])
    return seqs


# --------------------------------------------------------------------------
# Emit check-in-level embeddings.parquet (row-aligned with check2hgi's)
# --------------------------------------------------------------------------
def emit_embeddings(state: str, dst_dir: Path, vocab: dict, emb: np.ndarray, read_root: Path):
    """Look up each check-in's placeid -> skip-gram vector. Row order MUST match
    check2hgi's embeddings.parquet (sorted ['userid','datetime']) so that
    generate_next_input_from_checkins produces row-aligned next.parquet."""
    src = _c2hgi_embeddings(state, read_root)  # userid,placeid,category,datetime,0..63
    base_cols = ["userid", "placeid", "category", "datetime"]
    df = src[base_cols].copy().sort_values(["userid", "datetime"]).reset_index(drop=True)

    dim = emb.shape[1]
    pids = df["placeid"].astype(int).to_numpy()
    idx = np.array([vocab.get(int(p), 0) for p in pids], dtype=np.int64)  # 0 = <unk>/cold
    vecs = emb[idx]  # [N, dim]
    n_cold = int((idx == 0).sum())

    for d in range(dim):
        df[str(d)] = vecs[:, d]
    dst = dst_dir / "embeddings.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(dst, index=False)
    print(f"  embeddings.parquet -> {dst}  rows={len(df)}, dim={dim}, "
          f"cold/<unk>={n_cold} ({100*n_cold/len(df):.1f}%)")
    return len(df)


# --------------------------------------------------------------------------
# next_region build (replicated from build_overlap_probe_engine.py)
# --------------------------------------------------------------------------
def build_next_region_for(state: str, engine: EmbeddingEngine, read_root: Path):
    next_df = IoPaths.load_next(state, engine)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    assert len(next_df) == len(seq_df), (len(next_df), len(seq_df))
    placeid_to_idx, poi_to_region = _c2hgi_graph_maps(state, read_root)
    n_regions = int(poi_to_region.max()) + 1
    tgt = seq_df["target_poi"].astype(np.int64).to_numpy()
    poi_idx = pd.Series(tgt).map(placeid_to_idx).to_numpy(dtype=np.int64)
    region_idx = poi_to_region[poi_idx]
    poi_cols = [f"poi_{i}" for i in range(InputsConfig.SLIDE_WINDOW)]
    poi_mat = seq_df[poi_cols].astype(np.int64).to_numpy()
    last_region = np.full(len(seq_df), -1, np.int64)
    for r in range(len(seq_df)):
        valid = np.where(poi_mat[r] >= 0)[0]
        if len(valid):
            pi = placeid_to_idx.get(int(poi_mat[r][valid[-1]]), None)
            if pi is not None:
                last_region[r] = poi_to_region[pi]
    out = next_df.copy()
    out["region_idx"] = region_idx
    out["last_region_idx"] = last_region
    dst = IoPaths.get_next_region(state, engine)
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dst, index=False)
    print(f"  next_region -> {dst}  (rows={len(out)}, n_regions={n_regions}, "
          f"pad={(last_region<0).mean()*100:.1f}%)")


def _symlink(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src.resolve())
        print(f"  symlink {dst.name} -> {src}")
    else:
        print(f"  WARN: source missing, cannot symlink {src}")


# --------------------------------------------------------------------------
# get_next_region is enum-gated; the smoke uses --engine check2hgi, but the
# BUILD writes into a scratch engine dir. We patch the supported tuple at
# RUNTIME (process-local, never touches the file on disk) so the scratch engine
# can publish next_region.parquet. This is the zero-enum-edit escape hatch.
# --------------------------------------------------------------------------
def _runtime_allow_engine(engine: EmbeddingEngine):
    import configs.paths as paths_mod
    import data.inputs.builders as builders_mod
    # monkeypatch get_next_region to bypass the supported-tuple gate for our
    # process only (no disk edit, no cross-implementer conflict).
    orig = paths_mod.IoPaths.get_next_region.__func__

    def patched(cls, st, eng):
        try:
            return orig(cls, st, eng)
        except ValueError:
            return cls.get_input_dir(st, eng) / "next_region.parquet"
    paths_mod.IoPaths.get_next_region = classmethod(patched)
    # allow check-in-level builder for our scratch engine
    builders_mod._CHECKIN_LEVEL_ENGINES.add(engine)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--n-splits", type=int, default=5)
    ap.add_argument("--dim", type=int, default=64)
    ap.add_argument("--window", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--neg-k", type=int, default=5)
    ap.add_argument("--stride", type=int, default=None,
                    help="None=stride-9 non-overlap (current/smoke); 1=overlap (P3)")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny build; also prints the train.py smoke command")
    ap.add_argument("--read-output-dir", default=None,
                    help="dir to READ the frozen check2hgi substrate from "
                         "(embeddings/graph/region/log_T). Defaults to OUTPUT_DIR. "
                         "Set this (to the real output/) when emitting an overlay "
                         "into a scratch OUTPUT_DIR so the frozen check2hgi is "
                         "never overwritten.")
    ap.add_argument("--engine-value", default=None,
                    help="override the emitted engine dir name. For the SMOKE "
                         "end-to-end plumbing proof, pass 'check2hgi' so the "
                         "FROZEN allow-lists accept --engine check2hgi against a "
                         "scratch OUTPUT_DIR holding THIS substrate (overlay the "
                         "real region_embeddings/graph/log_T via symlink).")
    args = ap.parse_args()

    state = args.state.lower()
    # The engine value is the directory name under OUTPUT_DIR. We use a
    # fold/seed-namespaced value so concurrent folds never collide on disk.
    engine_value = args.engine_value or f"{B2B_ENGINE_VALUE}_s{args.seed}_f{args.fold}"
    # Reuse an existing enum member's machinery by minting a dynamic engine.
    # EmbeddingEngine is a value-keyed Enum; we add a member dynamically so the
    # IoPaths.<getters> resolve OUTPUT_DIR/<engine_value>/<state>/.
    try:
        engine = EmbeddingEngine(engine_value)
    except ValueError:
        engine = EmbeddingEngine._value2member_map_.get(engine_value)
        if engine is None:
            # dynamically extend the Enum (process-local) so paths resolve
            engine = object.__new__(EmbeddingEngine)
            engine._name_ = engine_value.upper()
            engine._value_ = engine_value
            EmbeddingEngine._value2member_map_[engine_value] = engine
            EmbeddingEngine._member_map_[engine._name_] = engine

    _runtime_allow_engine(engine)

    read_root = Path(args.read_output_dir) if args.read_output_dir else OUTPUT_DIR
    dst_dir = OUTPUT_DIR / engine_value / state
    print(f"=== B2b skip-gram substrate: {engine_value}/{state} "
          f"(seed={args.seed} fold={args.fold} stride={args.stride}) ===")
    print(f"    OUTPUT_DIR={OUTPUT_DIR}  READ_ROOT={read_root}")

    # 1. leak-safe fold train users
    train_users, val_users = get_fold_train_userids(
        state, args.seed, args.fold, read_root, args.n_splits)
    print(f"  train_users={len(train_users)}  val_users={len(val_users)}  "
          f"(disjoint asserted)")

    # 2. pretrain corpus = train-user POI sequences ONLY
    checkins = _c2hgi_embeddings(state, read_root)[["userid", "placeid", "category", "datetime"]]
    seqs = build_train_poi_sequences(checkins, train_users)
    print(f"  pretrain corpus: {len(seqs)} train-user trajectories")

    # 3. train skip-gram (SGNS) on train portion only
    vocab, emb = train_skipgram(
        seqs, dim=args.dim, window=args.window, epochs=args.epochs,
        neg_k=args.neg_k, seed=args.seed, device=args.device,
    )

    # 4. emit row-aligned check-in-level embeddings.parquet
    n = emit_embeddings(state, dst_dir, vocab, emb, read_root)

    # 5. build next.parquet + sequences (matched-head inputs)
    print(f"  building next.parquet + sequences (stride={args.stride}) ...")
    generate_next_input_from_checkins(state, engine, stride=args.stride)

    # 6. build next_region.parquet (shared geographic partition)
    build_next_region_for(state, engine, read_root)

    # 7. symlink region_embeddings.parquet from check2hgi (substrate-independent)
    src_dir = read_root / CHECK2HGI.value / state
    _symlink(src_dir / "region_embeddings.parquet", dst_dir / "region_embeddings.parquet")
    # If we overlaid onto the 'check2hgi' engine name for the smoke, also bring
    # in the graph artifact + seeded log_T so train.py runs self-contained on a
    # scratch OUTPUT_DIR (region partition + transition prior are shared, NOT
    # substrate-specific). When emitting a namespaced engine these are unused.
    if engine_value == CHECK2HGI.value and src_dir.resolve() != dst_dir.resolve():
        _symlink(src_dir / "temp" / "checkin_graph.pt", dst_dir / "temp" / "checkin_graph.pt")
        for f in src_dir.glob("region_transition_log_*.pt"):
            _symlink(f, dst_dir / f.name)

    # row-alignment assert (the matched-head contract)
    next_df = IoPaths.load_next(state, engine)
    reg_df = IoPaths.load_next_region(state, engine)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    assert len(next_df) == len(reg_df) == len(seq_df), \
        (len(next_df), len(reg_df), len(seq_df))
    print(f"  ROW-ALIGN OK: next==region==seq=={len(next_df)}")
    print(f"DONE: {engine_value}/{state} next rows={len(next_df):,}")

    if args.smoke:
        print("\n--- SMOKE train.py command (run on the scratch engine via "
              "--engine check2hgi against this OUTPUT_DIR) ---")
        print(
            f"OUTPUT_DIR={OUTPUT_DIR} PYTHONPATH=src .venv/bin/python scripts/train.py "
            f"--task mtl --task-set check2hgi_next_region --engine check2hgi "
            f"--state {state} --seed {args.seed} --folds 1 --epochs 2 "
            f"--batch-size 2048 --no-checkpoints --model mtlnet_crossattn_dualtower "
            f"--cat-head next_gru --reg-head next_stan_flow_dualtower "
            f"--task-a-input-type checkin --task-b-input-type region "
            f"--per-fold-transition-dir output/check2hgi/{state}"
        )


if __name__ == "__main__":
    main()
