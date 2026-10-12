#!/usr/bin/env python
"""Build the CTLE (B1) probe-engine substrate, LEAK-SAFE per fold.

Baseline B1 — CTLE (Lin et al., AAAI 2021, Logan-Lin/CTLE): the single most
important baseline (the *contextualization* control). CTLE pre-trains a
contextual, time-aware PER-VISIT (check-in-level) location embedding via a
bidirectional Transformer with MLM + Masked-Hour (MH) pretext objectives. We
emit that 64-d per-visit embedding as a substrate column and route it under the
FROZEN matched champion heads (cat=next_gru, reg=next_stan_flow_dualtower) via
``train.py --engine``. This is the class-(A) SC-SUBSTRATE-COLUMN pattern, mirror
of ``scripts/mtl_improvement/build_overlap_probe_engine.py``.

LEAK-SAFETY (HARD REQUIREMENT)
------------------------------
CTLE's MLM+MH is pre-trained on the FOLD'S TRAIN PORTION ONLY:
  1. Reproduce the EXACT board fold split bit-for-bit:
       X, y_cat, userids, _ = load_next_data(state, CHECK2HGI)
       sgkf = StratifiedGroupKFold(5, shuffle=True, random_state=seed)
       for f,(train_idx,val_idx) in enumerate(sgkf.split(X, y_cat, groups=userids))
     (identical algorithm/groups/y/seed to FoldCreator._create_check2hgi_mtl_folds
      and compute_region_transition._build_per_fold).
  2. train_userids = set(userids[train_idx]); pretrain CTLE only on the check-in
     trajectories of those users (user-disjoint, matching the fold).
  3. Emit the substrate into output/check2hgi_ctle/<state>/ for the BUILT fold,
     and run train.py with --folds 1 against it, so val users never influenced
     the substrate. We ALSO assert
       set(userids[val_idx]).isdisjoint(train_userids)
     before pretraining (cheapest proof of the contract). A CTLE_FOLD.txt marker
     records which (seed, fold) the dir is leak-clean for.

P3 SCORED-RUN DRIVER (n=20, NOT run here)
-----------------------------------------
The board scores 5 folds x 4 seeds. Because CTLE's train set differs per fold,
a single emitted dir is leak-clean for exactly ONE fold. The scored driver loops
seeds x folds: for each (seed, fold) it (a) builds this fold's substrate into
output/check2hgi_ctle/<state>/, (b) ensures a matching per-fold log_T exists at
the trainer's n_splits, (c) runs train.py with --folds 1 reading fold-0 of a
split rotated so the target fold is in slot 0 (or builds a per-fold engine value
to keep the real 5-split). The smoke below builds + runs fold 0 directly, which
IS leak-clean (fold 0 == slot 0 of the canonical 5-split).

The contextual embedding for EVERY row (train + val) is produced by running the
*train-pretrained, frozen* encoder over each user's full trajectory in
inference mode. Val rows get embeddings from a model that never saw them — no
transductive advantage (CTLE is inductive: the encoder generalises to unseen
users' trajectories). This matches CTLE's downstream-adaptation step.

ROW-ALIGNMENT
-------------
The emitted ``embeddings.parquet`` keeps the EXACT metadata columns + row order
of the frozen check2hgi substrate (userid, placeid, category, datetime) and only
replaces the 64 numeric embedding columns with CTLE contextual vectors. The
downstream builders (``generate_next_input_from_checkins`` + ``build_next_region_for``)
then produce next/next_region/sequences that row-align by construction (same
sort key ['userid','datetime']).

Usage:
  # tiny smoke (AL, fold 0, seed 0, 2 pretrain epochs):
  PYTHONPATH=src .venv/bin/python scripts/baselines/build_ctle_substrate.py \
      --state alabama --seed 0 --fold 0 --pretrain-epochs 2 --smoke

  # full per-fold build for one (state, seed):
  PYTHONPATH=src .venv/bin/python scripts/baselines/build_ctle_substrate.py \
      --state alabama --seed 0   # builds all 5 folds
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

# ensure src on path when invoked without PYTHONPATH=src
_SRC = Path(__file__).resolve().parents[2] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR  # noqa: E402
from data.folds import load_next_data  # noqa: E402
from data.inputs.builders import generate_next_input_from_checkins  # noqa: E402

# repo-local import of the CTLE model lib
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ctle_lib.ctle_model import (  # noqa: E402
    CTLE, CTLEConfig, N_SPECIAL, PAD_ID, build_mlm_mh_batch,
)

# The probe-engine. The single shared-file edit allowed by the integration
# contract: EmbeddingEngine.CHECK2HGI_CTLE appended at the END of the enum
# (paths.py) + added to get_next_region `supported`, builders._CHECKIN_LEVEL_ENGINES,
# and folds._MTL_C2HGI_ALLOWED_ENGINES. Documented [ENUM-MERGE] for sequential merge.
CTLE_ENGINE = EmbeddingEngine.CHECK2HGI_CTLE
CHECK2HGI = EmbeddingEngine.CHECK2HGI


# ---------------------------------------------------------------------------
# Fold split — bit-identical to the board (see module docstring step 1).
# ---------------------------------------------------------------------------
def get_fold_indices(state: str, seed: int, fold: int, split_engine: str = "check2hgi"):
    """Return (train_idx, val_idx, userids) for ONE fold of the board split.

    [2026-10-01] ``split_engine`` picks the rows the split is computed on. The default, ``check2hgi``
    (canonical stride-9 rows), is what the June cells used. But the CTLE cells are SCORED by
    ``train.py --only-fold`` on the engine's own stride-1 rows (= ``check2hgi_dk_ovl``), whose folds differ:
    74-82 % (AL) / 78-82 % (AZ) of each scored fold's validation users were on the pre-training side.
    Pass ``--split-engine check2hgi_dk_ovl`` so pre-training excludes exactly the scored fold's users.
    ``load_next_data`` returns int64 userids, i.e. the same groups ``train.py`` uses.

    Bit-identical to FoldCreator._create_check2hgi_mtl_folds /
    compute_region_transition._build_per_fold (same X/y_cat/groups/seed).
    """
    X, y_cat, userids, _ = load_next_data(state, EmbeddingEngine(split_engine))
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    splits = list(sgkf.split(X, y_cat, groups=userids))
    train_idx, val_idx = splits[fold]
    return train_idx, val_idx, userids


# ---------------------------------------------------------------------------
# Trajectory construction from the frozen check2hgi check-in table.
# ---------------------------------------------------------------------------
def _load_checkins(state: str) -> pd.DataFrame:
    """Load the per-check-in metadata frame (sorted ['userid','datetime']).

    This is the SAME embeddings.parquet the downstream builder consumes; we read
    only its metadata (userid, placeid, category, datetime) — the 64 numeric
    columns are about to be REPLACED by CTLE contextual vectors.
    """
    df = IoPaths.load_embedd(state, CHECK2HGI)
    df = df.sort_values(["userid", "datetime"]).reset_index(drop=True)
    return df


def _build_vocab(df: pd.DataFrame):
    """Map distinct placeid -> contiguous loc id starting at N_SPECIAL.

    Vocab built over ALL placeids (the location universe is not user-private;
    CTLE's vocab is the full POI set). Leak-safety is enforced by training the
    *encoder weights* on train-user trajectories only — not by hiding location
    ids, which are public POI identities.
    """
    uniq = sorted(df["placeid"].astype(np.int64).unique().tolist())
    placeid_to_loc = {pid: i + N_SPECIAL for i, pid in enumerate(uniq)}
    vocab_size = len(uniq) + N_SPECIAL
    return placeid_to_loc, vocab_size


def _user_trajectories(df: pd.DataFrame, placeid_to_loc: dict, max_len: int):
    """Group into per-user (loc_id_seq, hour_seq, row_index_seq) lists.

    Long trajectories are chunked into windows of <= max_len (CTLE encodes a
    trajectory window). Returns a list of dicts with the global row indices so
    we can scatter contextual outputs back into the full per-check-in table.
    """
    df = df.reset_index(drop=True)
    hours = pd.to_datetime(df["datetime"]).dt.hour.to_numpy(np.int64)
    locs = df["placeid"].astype(np.int64).map(placeid_to_loc).to_numpy(np.int64)
    out = []
    for uid, sub in df.groupby("userid", sort=False):
        idx = sub.index.to_numpy()
        for start in range(0, len(idx), max_len):
            chunk = idx[start:start + max_len]
            out.append({
                "rows": chunk,
                "locs": locs[chunk],
                "hours": hours[chunk],
                "userid": int(uid),
            })
    return out


def _collate(trajs, max_len: int):
    """Pad a list of trajectory dicts to [B, max_len] tensors."""
    B = len(trajs)
    loc = np.full((B, max_len), PAD_ID, dtype=np.int64)
    hr = np.zeros((B, max_len), dtype=np.int64)
    rows = np.full((B, max_len), -1, dtype=np.int64)
    for i, t in enumerate(trajs):
        L = len(t["locs"])
        loc[i, :L] = t["locs"]
        hr[i, :L] = t["hours"]
        rows[i, :L] = t["rows"]
    return (torch.from_numpy(loc), torch.from_numpy(hr).float(),
            torch.from_numpy(hr), torch.from_numpy(rows))


# ---------------------------------------------------------------------------
# Pretrain (train-users only) + emit contextual embeddings for ALL rows.
# ---------------------------------------------------------------------------
def pretrain_and_embed(state, seed, fold, df, train_userids, val_userids,
                       embed_dim=64, max_len=64, pretrain_epochs=10,
                       batch_size=256, lr=1e-3, device=None, smoke=False):
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"  # Apple GPU: CTLE transformer pretrain is ~CPU-bound otherwise
        else:
            device = "cpu"
    placeid_to_loc, vocab_size = _build_vocab(df)
    cfg = CTLEConfig(vocab_size=vocab_size, embed_dim=embed_dim,
                     max_len=max_len,
                     n_layers=(2 if smoke else 4),
                     n_heads=(4 if smoke else 8))
    model = CTLE(cfg).to(device)

    all_trajs = _user_trajectories(df, placeid_to_loc, max_len)
    # LEAK-SAFE: pretrain ONLY on train-user trajectories.
    train_trajs = [t for t in all_trajs if t["userid"] in train_userids]
    assert train_trajs, "no train trajectories — check fold/user filtering"
    # contract proof: train + val users are disjoint
    assert set(t["userid"] for t in train_trajs).isdisjoint(val_userids), \
        "LEAK: a val user appears in the pretrain corpus"

    gen = torch.Generator(device=device).manual_seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)

    print(f"  CTLE pretrain: vocab={vocab_size} train_trajs={len(train_trajs)} "
          f"(of {len(all_trajs)} total) device={device} epochs={pretrain_epochs}")
    model.train()
    order = np.arange(len(train_trajs))
    rng = np.random.default_rng(seed)
    for ep in range(pretrain_epochs):
        rng.shuffle(order)
        # Accumulate on-device — NO per-batch .item() (each .item() forces a
        # CPU<->GPU sync that serializes the MPS/CUDA pipeline). Canonical pattern:
        # src/training/runners/mtl_cv.py:818. We sync once per epoch for the log.
        tot = torch.zeros((), device=device)
        mlm_t = torch.zeros((), device=device)
        mh_t = torch.zeros((), device=device)
        nb = 0
        for bs in range(0, len(order), batch_size):
            batch = [train_trajs[j] for j in order[bs:bs + batch_size]]
            loc, hr_f, hr_i, _rows = _collate(batch, max_len)
            loc, hr_f, hr_i = loc.to(device), hr_f.to(device), hr_i.to(device)
            masked, mlm_tgt, mh_tgt, _sel = build_mlm_mh_batch(
                loc, hr_i, vocab_size, cfg.mask_ratio, gen)
            total, mlm_l, mh_l = model(masked, hr_f, mlm_tgt, mh_tgt, _sel)
            opt.zero_grad(set_to_none=True)
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            tot += total.detach(); mlm_t += mlm_l.detach(); mh_t += mh_l.detach(); nb += 1
        print(f"    epoch {ep+1}/{pretrain_epochs}  loss={(tot/nb).item():.4f} "
              f"mlm={(mlm_t/nb).item():.4f} mh={(mh_t/nb).item():.4f}")

    # ---- emit: run frozen encoder over ALL trajectories (no masking) ----
    model.eval()
    out_emb = np.zeros((len(df), embed_dim), dtype=np.float32)
    with torch.no_grad():
        for bs in range(0, len(all_trajs), batch_size):
            batch = all_trajs[bs:bs + batch_size]
            loc, hr_f, _hr_i, rows = _collate(batch, max_len)
            loc, hr_f = loc.to(device), hr_f.to(device)
            ctx = model.encode(loc, hr_f).cpu().numpy()  # [B, L, D]
            rows_np = rows.numpy()
            for b in range(len(batch)):
                valid = rows_np[b] >= 0
                out_emb[rows_np[b][valid]] = ctx[b][valid]
    return out_emb, vocab_size


# ---------------------------------------------------------------------------
# next_region build (engine-aware) — adapted from build_overlap_probe_engine.py.
# ---------------------------------------------------------------------------
def build_next_region_for(state: str, engine: EmbeddingEngine):
    from data.inputs.region_sequence import _load_graph_maps
    next_df = IoPaths.load_next(state, engine)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    assert len(next_df) == len(seq_df), (len(next_df), len(seq_df))
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1
    tgt = seq_df["target_poi"].astype(np.int64).to_numpy()
    poi_idx = pd.Series(tgt).map(placeid_to_idx).to_numpy(dtype=np.float64)
    poi_idx_i = np.where(np.isnan(poi_idx), -1, poi_idx).astype(np.int64)
    region_idx = np.where(poi_idx_i >= 0, poi_to_region[np.clip(poi_idx_i, 0, None)], -1)
    poi_cols = [f"poi_{i}" for i in range(9)]
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
    dst = IoPaths.get_input_dir(state, engine) / "next_region.parquet"
    dst.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dst, index=False)
    print(f"  next_region -> {dst} (rows={len(out)}, n_regions={n_regions}, "
          f"pad={(last_region < 0).mean()*100:.1f}%)")


def _symlink(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        dst.unlink()
    if src.exists():
        dst.symlink_to(src.resolve())


def build_one_fold(state, seed, fold, args):
    """Build a leak-safe CTLE substrate for ONE (state, seed, fold).

    Emits into the standard probe-engine layout
    ``output/check2hgi_ctle/<state>/`` (overridable via OUTPUT_DIR env). The
    CTLE encoder is pre-trained on fold-``fold`` TRAIN users only; every row's
    contextual embedding then comes from that frozen train-only encoder (val
    rows included — CTLE is inductive, no transductive leak).

    Because IoPaths routes a single dir per (engine, state), this dir is
    SPECIFIC TO ``fold``. The matched-head run for this fold must be launched
    with ``--fold-only <fold>`` semantics: in practice the smoke/P3 driver
    builds fold ``fold``, then runs ``train.py --folds 1`` after rotating that
    fold to position 0 (see ``--rotate-to-fold0``); for the smoke we build +
    run fold 0 directly. The leak-clean granularity mirrors the champion's own
    per-fold seeded log_T (``region_transition_log_seed{S}_fold{N}.pt``).
    """
    state = state.lower()
    train_idx, val_idx, userids = get_fold_indices(state, seed, fold, args.split_engine)
    train_userids = set(int(u) for u in userids[train_idx])
    val_userids = set(int(u) for u in userids[val_idx])
    print(f"[fold {fold} seed {seed}] train_users={len(train_userids)} "
          f"val_users={len(val_userids)} "
          f"disjoint={train_userids.isdisjoint(val_userids)}")
    assert train_userids.isdisjoint(val_userids), "fold split is not user-disjoint!"

    df = _load_checkins(state)
    ctx_emb, vocab = pretrain_and_embed(
        state, seed, fold, df, train_userids, val_userids,
        embed_dim=64, max_len=args.max_len,
        pretrain_epochs=args.pretrain_epochs,
        batch_size=args.batch_size, lr=args.lr, smoke=args.smoke,
        device=args.device,
    )

    # write substrate embeddings.parquet (metadata cols + CTLE ctx cols).
    # Same row set + order as the frozen check2hgi embeddings.parquet (sorted
    # ['userid','datetime']) -> downstream next/next_region row-align by const.
    sub_dir = OUTPUT_DIR / CTLE_ENGINE.value / state
    sub_dir.mkdir(parents=True, exist_ok=True)
    meta_cols = [c for c in df.columns if not c.isdigit()]
    emb_df = df[meta_cols].copy().reset_index(drop=True)
    for i in range(64):
        emb_df[str(i)] = ctx_emb[:, i]
    emb_path = sub_dir / "embeddings.parquet"
    emb_df.to_parquet(emb_path, index=False)
    print(f"  embeddings.parquet -> {emb_path} (rows={len(emb_df)}, vocab={vocab})")

    # region_embeddings.parquet: symlink from frozen check2hgi (shared geo
    # partition; CTLE re-embeds check-ins, not regions).
    _symlink(OUTPUT_DIR / CHECK2HGI.value / state / "region_embeddings.parquet",
             sub_dir / "region_embeddings.parquet")

    # downstream inputs: next.parquet + sequences_next.parquet + next_region.parquet
    # WINDOWING: CTLE has no windowing of its own to inherit (the §3d handoff
    # assumption was wrong); thread --stride explicitly like the other 3 builders.
    # --stride 1 -> gated overlap (emit_tail auto-off via _resolve_emit_tail);
    # min_seq stays the global 5 (a proven no-op at stride-1: a full 9+1 window
    # already needs >=10 check-ins). The contextual embeddings.parquet is
    # windowing-INDEPENDENT (one ctx vector per check-in row) -> stays 113,846.
    print(f"  building downstream inputs (next + sequences + next_region, stride={args.stride})...")
    generate_next_input_from_checkins(state, CTLE_ENGINE, stride=args.stride)
    build_next_region_for(state, CTLE_ENGINE)
    n = len(IoPaths.load_next(state, CTLE_ENGINE))
    nr = len(IoPaths.load_next_region(state, CTLE_ENGINE))
    print(f"  fold {fold}: next rows={n} next_region rows={nr} aligned={n == nr}")
    assert n == nr, "row-alignment broken: len(next) != len(next_region)"
    # fold-marker so the driver / audit knows which fold this dir is leak-clean for
    (sub_dir / "CTLE_FOLD.txt").write_text(
        f"state={state} seed={seed} fold={fold} vocab={vocab}\n"
        f"pretrain_epochs={args.pretrain_epochs} smoke={args.smoke}\n"
        f"split_engine={args.split_engine} n_val_users={len(val_userids)} "
        f"val_users_sha256={__import__('hashlib').sha256(np.sort(np.fromiter(val_userids, dtype=np.int64)).tobytes()).hexdigest()}\n"
        f"LEAK-SAFE: encoder pretrained on fold-{fold} TRAIN users only.\n"
    )
    return sub_dir


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--fold", type=int, default=0,
                    help="fold idx 0..4 to build a leak-clean substrate for")
    ap.add_argument("--pretrain-epochs", type=int, default=10)
    ap.add_argument("--batch-size", type=int, default=256)
    ap.add_argument("--max-len", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--split-engine", default="check2hgi",
                    help="engine whose rows define the fold split (default check2hgi = the June behaviour). "
                         "Use check2hgi_dk_ovl to match the rows train.py scores the CTLE cells on.")
    ap.add_argument("--stride", type=int, default=None,
                    help="window stride for next/next_region (None=stride-9 "
                         "non-overlap default; pass 1 for the P3 gated-overlap "
                         "board build, matching the other 3 baseline builders).")
    ap.add_argument("--device", default=None,
                    help="cuda / mps / cpu. Default: auto (cuda > mps > cpu). On a "
                         "Mac, mps (Apple GPU) is FAR faster than cpu for the "
                         "transformer pretrain. Embeddings are device-tolerant inputs.")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny config (2 layers/4 heads); use with --fold 0 "
                         "--pretrain-epochs 2 for a fast plumbing check")
    args = ap.parse_args()

    sub_dir = build_one_fold(args.state, args.seed, args.fold, args)
    print(f"DONE -> {sub_dir}")


if __name__ == "__main__":
    main()
