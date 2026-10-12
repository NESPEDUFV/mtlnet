#!/usr/bin/env python
"""B1-E2E — CTLE (Lin et al., AAAI 2021) — NATIVE end-to-end baseline trainer.

Paper: Yan Lin, Huaiyu Wan, Shengnan Guo, Youfang Lin.
"Pre-training Context and Time Aware Location Embeddings from Spatial-Temporal
Trajectories for User Next Location Prediction." AAAI 2021.
Code: https://github.com/Logan-Lin/CTLE

================================================================================
WHAT THIS IS (vs build_ctle_substrate.py)
================================================================================
``build_ctle_substrate.py`` (class-A) emits a FROZEN 64-d CTLE column and routes
it under the champion heads via ``train.py --engine``. THIS driver is the
**class-(B) NATIVE-E2E** variant: it keeps CTLE's native contextual Transformer
(``ctle_lib/ctle_model.py``: MLM + Masked-Hour pretext) as the *body*, and adds a
next-REGION head (n_regions classes) + a next-CATEGORY head (7 root classes) on
the CTLE contextual output, **fine-tuned jointly END-TO-END** (the encoder is NOT
frozen during the supervised stage). It mirrors the structure of
``scripts/baselines/flashback_e2e.py`` (its own self-contained driver) and reuses
the shared board machinery exactly the way ``b3_hmt_grn.py`` does.

================================================================================
ALIGNMENT TO THE GATED STRIDE-1 OVERLAP BASE (the board base)
================================================================================
Unlike ``flashback_e2e.py`` (which reads canonical stride-9 CHECK2HGI), this
driver aligns to the **GATED STRIDE-1 OVERLAP engine** ``check2hgi_dk_ovl``:

  output/check2hgi_dk_ovl/<state>/input/{next.parquet,next_region.parquet}
  = 96,326 rows for alabama (stride=1, emit_tail=False, MIN_SEQUENCE_LENGTH=10).

Provenance (next_build_provenance.json): stride=1, window_size=9, emit_tail=False,
min_sequence_length=10. We do NOT consume the dk substrate's 64-d numeric columns
(this is a NATIVE baseline that learns its own location embeddings end-to-end); we
consume the dk_ovl ROW SET + LABELS:
  * fold split / category labels: ``load_next_data(state, CHECK2HGI_DK_OVL)`` ->
    (X, y_cat, userids) over the 96,326 dk_ovl rows.
  * region labels: ``next_region.parquet['region_idx']`` (row-aligned).

The per-row 9-step PLACEID windows + HOUR windows that CTLE actually encodes are
reconstructed by REPLAYING ``data.inputs.core.generate_sequences`` with the EXACT
dk_ovl params (window_size=9, stride=1, min_sequence_length=10, emit_tail=False)
over the same sorted check-ins (embeddings.parquet metadata, sorted
['userid','datetime']). The reconstruction is **byte-exact**: the resulting
(userid, next_category) sequence equals next_region.parquet row-for-row (verified
in-session: 96,326/96,326 userid match, 100% next_category match). This is the
windowing the dk_ovl builder itself used, so the placeid/hour windows row-align to
the dk_ovl labels by construction.

================================================================================
LEAK-SAFETY (HARD REQUIREMENT)
================================================================================
* Folds: StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed) over
  load_next_data(state, CHECK2HGI_DK_OVL), groups=userid, y=next_category —
  user-disjoint, identical algorithm/groups/y/seed to the champion split (just
  over the dk_ovl rows). ``--only-fold k`` runs one of the 5 board folds.
* PER-FOLD pretraining (the CTLE leak rule): for each fold, CTLE's MLM+MH is
  pre-trained on the TRAIN users' check-in trajectories ONLY (mirrors the per-
  (state,seed,fold) discipline of build_ctle_substrate.pretrain_and_embed: it
  filters ``train_trajs = [t for t in all_trajs if t['userid'] in train_userids]``
  and asserts disjointness from val users). The supervised E2E fine-tune then
  trains on train_idx rows only; the val pass updates no parameter. We assert
  val users are DISJOINT from train users before any training.
* The location vocab is the full public POI set (a placeid is a public POI id,
  not a user-private label) — leak-safety is enforced by which TRAJECTORIES the
  encoder weights see, exactly as in build_ctle_substrate._build_vocab.
* Region labels are looked up from the dk_ovl next_region.parquet (a static TIGER
  partition via the check2hgi graph maps), never learned -> no region-label leak.
* OOD restriction: reg top10_acc_indist is computed against the per-fold TRAIN
  region label set (training.runners.mtl_eval._ood_from_streamed) — the board
  protocol.

================================================================================
DEVIATIONS FROM THE PAPER (faithfulness ledger)
================================================================================
D1. Downstream task = TIGER-tract next-REGION (~1.1k classes) + 7-root
    next-CATEGORY under TWO linear heads on the pooled CTLE contextual output,
    NOT CTLE's original next-location MC/RNN predictor. This is the board's
    two-task surface (same as the champion / flashback_e2e / b3).
D2. END-TO-END fine-tune: the encoder is pre-trained (MLM+MH) then fine-tuned
    jointly with the heads. The substrate-column variant (build_ctle_substrate)
    freezes the encoder; here we keep CTLE native (its strength is the contextual
    encoder, exercised E2E).
D3. Pooling: we read the CTLE contextual output at the LAST valid (non-pad)
    window position as the per-window representation (the most-recent check-in's
    contextual embedding), matching the "predict from the latest context" setup.
D4. Temporal encoding: ctle_lib's Time2Vec-style continuous hour encoding +
    the MH (Masked-Hour) objective verbatim (ctle_lib docstring deviation #2).
D5. embed_dim pinned to 64 (board); CTLE default is 128. depth/heads/mask follow
    CTLE defaults (4 layers, 8 heads, GELU, pre-LN, mask 0.15), scaled to dim 64.

================================================================================
SMOKE
================================================================================
PYTHONPATH=src MTL_RAM_HEADROOM_GB=2 OMP_NUM_THREADS=3 \
  .venv/bin/python scripts/baselines/ctle_e2e.py --smoke
  -> state=alabama, 1 fold (fold 0), 2 pretrain + 2 finetune epochs, tiny CTLE
     (2 layers / 4 heads), seed 0. Prints cat f1 + reg top10_acc_indist +
     geom_simple and asserts user-disjoint folds. Writes a JSON sidecar.

Full board run (P3, do NOT run here): omit --smoke, set --folds 5 --epochs <E>
--seed in {0,1,7,100} over the target states.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F

# --- repo imports (read-only; we IMPORT, never modify) ----------------------
_ROOT = Path(__file__).resolve().parents[2]
_SRC = str(_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from configs.paths import EmbeddingEngine, IoPaths, OUTPUT_DIR, RESULTS_ROOT  # noqa: E402
from data.folds import load_next_data  # noqa: E402
from data.inputs.core import generate_sequences  # noqa: E402  (the dk_ovl windower)
from data.inputs.region_sequence import _load_graph_maps  # noqa: E402
from tracking.metrics import StreamingClsMetrics, compute_classification_metrics  # noqa: E402
from training.runners.mtl_eval import _ood_from_streamed  # noqa: E402

# repo-local CTLE model lib (native architecture, reused verbatim)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from ctle_lib.ctle_model import (  # noqa: E402
    CTLE, CTLEConfig, N_SPECIAL, PAD_ID, build_mlm_mh_batch,
)

ENGINE = EmbeddingEngine.CHECK2HGI_DK_OVL  # the BOARD BASE (stride-1 overlap)
ENGINE_NAME = "ctle_e2e_b1"  # disk namespace; NOT an EmbeddingEngine member
PAD = -1

# dk_ovl windowing params (from next_build_provenance.json) — MUST match the base
WIN = 9
STRIDE = 1
MIN_SEQ = 10
EMIT_TAIL = False


# ============================================================================
# Reconstruct row-aligned placeid + hour windows for the dk_ovl base.
# ============================================================================
def _build_dk_ovl_windows(state: str, expected_userids: np.ndarray,
                          expected_cats: np.ndarray):
    """Reconstruct, ROW-ALIGNED to dk_ovl next_region.parquet:

      poi_win  : [N, 9] int64 placeids (PAD=-1)
      hour_win : [N, 9] int64 hour-of-day (0 at pad)
      userids  : [N] int64

    by replaying generate_sequences with the dk_ovl params over the same sorted
    check-ins (embeddings.parquet metadata). We ASSERT the reconstructed
    (userid, next_category) stream equals the parquet's row-for-row — the proof
    that windows row-align to the dk_ovl labels.
    """
    emb = IoPaths.load_embedd(state, ENGINE)[["userid", "placeid", "category", "datetime"]]
    # MUST match the canonical dk_ovl builder's STABLE sort
    # (data.inputs.builders.generate_next_input_from_checkins, kind='mergesort').
    # The default 'quicksort' is unstable, so on the 28 florida rows that share a
    # (userid, datetime) it reorders the tie differently than the builder did,
    # shifting 2 window targets and tripping the next_category alignment assert.
    # mergesort is stable -> preserves the parquet row order under ties -> 0 diffs.
    emb = emb.sort_values(["userid", "datetime"], kind="mergesort").reset_index(drop=True)

    poi_rows, hour_rows, uid_rows, cat_rows = [], [], [], []
    for uid, sub in emb.groupby("userid", sort=False):
        sub = sub.sort_values("datetime", kind="mergesort").reset_index(drop=True)
        places = sub["placeid"].astype(np.int64).tolist()
        cats = sub["category"].tolist()
        hours = pd.to_datetime(sub["datetime"]).dt.hour.astype(np.int64).tolist()
        seqs = generate_sequences(
            places, window_size=WIN, stride=STRIDE,
            return_start_indices=True,
            min_sequence_length=MIN_SEQ, emit_tail=EMIT_TAIL,
        )
        for start_idx, seq in seqs:
            history = seq[:WIN]
            tgt_pos = start_idx + WIN  # emit_tail=False => always in-bounds
            hw = []
            for k in range(WIN):
                pos = start_idx + k
                hw.append(hours[pos] if (history[k] != PAD and pos < len(hours)) else 0)
            poi_rows.append(history)
            hour_rows.append(hw)
            uid_rows.append(int(uid))
            cat_rows.append(cats[tgt_pos] if tgt_pos < len(cats) else None)

    poi_win = np.asarray(poi_rows, dtype=np.int64)
    hour_win = np.asarray(hour_rows, dtype=np.int64)
    userids = np.asarray(uid_rows, dtype=np.int64)

    # row-alignment proof (fail loud if dk_ovl was rebuilt with different params)
    assert len(userids) == len(expected_userids), (
        f"row count mismatch: reconstructed {len(userids)} vs dk_ovl {len(expected_userids)} "
        f"(check window_size/stride/min_seq/emit_tail vs next_build_provenance.json)"
    )
    assert np.array_equal(userids, expected_userids.astype(np.int64)), \
        "LEAK/ALIGN: reconstructed userid order != dk_ovl row order"
    rec_cat = pd.Series(cat_rows).fillna("NA").to_numpy()
    exp_cat = pd.Series(expected_cats).fillna("NA").to_numpy()
    assert (rec_cat == exp_cat).all(), \
        "ALIGN: reconstructed next_category != dk_ovl next_category"
    return poi_win, hour_win, userids


# ============================================================================
# Build all CTLE inputs (vocab, windows, labels), row-aligned to dk_ovl.
# ============================================================================
def build_context(state: str):
    # board fold inputs + category labels over the dk_ovl rows
    X, y_cat, userids_lnd, _ = load_next_data(state, ENGINE)
    nr = IoPaths.load_next_region(state, ENGINE)
    assert len(nr) == len(X), (len(nr), len(X))

    region_y = nr["region_idx"].astype(np.int64).to_numpy()
    next_cat_str = nr["next_category"].to_numpy()  # for alignment proof

    poi_win, hour_win, userids = _build_dk_ovl_windows(state, nr["userid"].astype(int).to_numpy(),
                                                       next_cat_str)
    # cross-check the load_next_data userid stream matches the reconstruction
    assert np.array_equal(userids, userids_lnd.astype(np.int64)), \
        "load_next_data userid order != reconstructed window order"

    # category label space (from load_next_data's y; mapped 7 root classes)
    y_cat = np.asarray(y_cat, dtype=np.int64)
    n_cats = int(y_cat.max()) + 1

    # CTLE location vocab over ALL placeids (public POI ids; leak-safe — see hdr)
    all_pids = sorted(set(int(p) for p in poi_win.reshape(-1) if p != PAD))
    placeid_to_loc = {pid: i + N_SPECIAL for i, pid in enumerate(all_pids)}
    vocab_size = len(all_pids) + N_SPECIAL

    _, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1

    return dict(
        poi_win=poi_win, hour_win=hour_win, userids=userids,
        y_cat=y_cat, region_y=region_y,
        placeid_to_loc=placeid_to_loc, vocab_size=vocab_size,
        n_cats=n_cats, n_regions=n_regions,
    )


# ============================================================================
# CTLE-E2E model: native CTLE encoder body + region & cat heads (E2E fine-tune).
# ============================================================================
class CTLE_E2E(nn.Module):
    """Native CTLE contextual Transformer (ctle_lib.CTLE) + two linear heads.

    The CTLE encoder (loc_embed + TemporalEncoding + Transformer, ctle_lib lines
    106-149) IS the body. After per-fold MLM+MH pretraining we keep it trainable
    and fine-tune jointly with the heads on the supervised next-region + next-cat
    loss. The per-window representation is the contextual output at the LAST valid
    position (most-recent check-in's contextual embedding).
    """

    def __init__(self, cfg: CTLEConfig, n_regions: int, n_cats: int):
        super().__init__()
        self.ctle = CTLE(cfg)  # native CTLE (encoder + MLM/MH heads reused in pretrain)
        self.fc_region = nn.Linear(cfg.embed_dim, n_regions)
        self.fc_cat = nn.Linear(cfg.embed_dim, n_cats)

    def pretrain_step(self, masked_loc, hours_f, mlm_tgt, mh_tgt, sel):
        """One MLM+MH pretext step (native CTLE.forward)."""
        return self.ctle(masked_loc, hours_f, mlm_tgt, mh_tgt, sel)

    def forward(self, loc_ids, hours_f):
        """Supervised forward: contextual encode -> last-valid pool -> heads.

        loc_ids: [B, L] long (PAD_ID at pad), hours_f: [B, L] float hour-of-day.
        """
        ctx = self.ctle.encode(loc_ids, hours_f)         # [B, L, D]
        valid = loc_ids.ne(PAD_ID).float()               # [B, L]
        # last valid position index per row (>=1 valid guaranteed: history non-empty)
        last_idx = (valid.cumsum(dim=1).argmax(dim=1)).long()  # [B]
        bi = torch.arange(loc_ids.size(0), device=loc_ids.device)
        pooled = ctx[bi, last_idx]                        # [B, D]
        return self.fc_cat(pooled), self.fc_region(pooled)

    def _pool(self, loc_ids, hours_f):
        ctx = self.ctle.encode(loc_ids, hours_f)         # [B, L, D]
        valid = loc_ids.ne(PAD_ID).float()
        last_idx = (valid.cumsum(dim=1).argmax(dim=1)).long()
        bi = torch.arange(loc_ids.size(0), device=loc_ids.device)
        return ctx[bi, last_idx]                          # [B, D]

    def forward_cat(self, loc_ids, hours_f):
        """Cat-only forward (skips the wide fc_region matmul) — for the per-epoch
        best-epoch tracking, where the reg head's [B, n_regions] logits are unused.
        Avoids recomputing the 4703-wide reg projection 150x on the FL val set."""
        return self.fc_cat(self._pool(loc_ids, hours_f))


# ============================================================================
# Tensor prep: map placeids -> CTLE loc ids (PAD_ID at pad), build hour floats.
# ============================================================================
def _make_tensors(ctx, device):
    poi = ctx["poi_win"]
    p2l = ctx["placeid_to_loc"]
    flat = poi.reshape(-1)
    loc = np.array([p2l.get(int(p), PAD_ID) if p != PAD else PAD_ID for p in flat],
                   np.int64).reshape(poi.shape)
    hours_f = ctx["hour_win"].astype(np.float32)
    return dict(
        loc=torch.from_numpy(loc).to(device),
        hours_f=torch.from_numpy(hours_f).to(device),
        cat_y=torch.from_numpy(ctx["y_cat"]).to(device),
        region_y=torch.from_numpy(ctx["region_y"]).to(device),
    )


# ============================================================================
# Train / eval one fold (per-fold CTLE pretrain on TRAIN users -> E2E finetune).
# ============================================================================
def run_fold(ctx, train_idx, val_idx, args, device):
    # --- leak-safety: val users disjoint from train users ---
    train_users = set(int(u) for u in ctx["userids"][train_idx])
    val_users = set(int(u) for u in ctx["userids"][val_idx])
    assert val_users.isdisjoint(train_users), "LEAK: val users overlap train users"

    cfg = CTLEConfig(
        vocab_size=ctx["vocab_size"], embed_dim=64, max_len=WIN,
        n_layers=(2 if args.smoke else 4),
        n_heads=(4 if args.smoke else 8),
    )
    model = CTLE_E2E(cfg, n_regions=ctx["n_regions"], n_cats=ctx["n_cats"]).to(device)

    t = _make_tensors(ctx, device)
    tr = torch.as_tensor(train_idx, device=device, dtype=torch.long)
    va = torch.as_tensor(val_idx, device=device, dtype=torch.long)
    bs = args.batch_size
    gen = torch.Generator(device=device).manual_seed(args.seed)

    # ---------------------------------------------------------------------
    # STAGE 1 — CTLE MLM + Masked-Hour PRETRAIN on TRAIN-FOLD rows ONLY.
    # Mirrors build_ctle_substrate.pretrain_and_embed: the encoder weights see
    # ONLY train-user trajectories (here the train_idx windows of those users).
    # ---------------------------------------------------------------------
    pre_opt = torch.optim.AdamW(model.ctle.parameters(), lr=args.pretrain_lr,
                                weight_decay=0.01)
    model.train()
    for ep in range(args.pretrain_epochs):
        perm = tr[torch.randperm(tr.numel(), device=device, generator=gen)]
        tot = mlm_t = mh_t = 0.0
        nb = 0
        for s in range(0, perm.numel(), bs):
            b = perm[s:s + bs]
            loc = t["loc"][b]
            hr_f = t["hours_f"][b]
            hr_i = hr_f.long()
            masked, mlm_tgt, mh_tgt, sel = build_mlm_mh_batch(
                loc, hr_i, ctx["vocab_size"], cfg.mask_ratio, gen)
            total, mlm_l, mh_l = model.pretrain_step(masked, hr_f, mlm_tgt, mh_tgt, sel)
            pre_opt.zero_grad()
            total.backward()
            torch.nn.utils.clip_grad_norm_(model.ctle.parameters(), 1.0)
            pre_opt.step()
            tot += float(total.detach()); mlm_t += float(mlm_l.detach()); mh_t += float(mh_l.detach()); nb += 1
        print(f"    [pretrain {ep+1}/{args.pretrain_epochs}] loss={tot/max(nb,1):.4f} "
              f"mlm={mlm_t/max(nb,1):.4f} mh={mh_t/max(nb,1):.4f}")

    # ---------------------------------------------------------------------
    # STAGE 2 — supervised E2E FINE-TUNE (encoder NOT frozen) on TRAIN rows.
    # ---------------------------------------------------------------------
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    ce = nn.CrossEntropyLoss()
    # Track the BEST-epoch val cat macro-F1 alongside the FINAL-epoch one. The board
    # cat ceiling this baseline is compared to uses "macro-F1 at the f1-best epoch"
    # (score_stl_cat_ceiling.py), so reporting ONLY final-epoch under-states CTLE
    # (correctness-advisor finding #1). We keep final-epoch as the AL-comparable
    # headline AND record best-epoch so the paper can choose the fair rule. The
    # per-epoch eval is cat-only ([N,7], cheap) and uses NO generator -> it does NOT
    # perturb the training RNG, so the final number is unchanged at fixed seed.
    best_cat_f1, best_epoch = -1.0, -1
    for ep in range(args.epochs):
        model.train()
        perm = tr[torch.randperm(tr.numel(), device=device, generator=gen)]
        running = 0.0
        for s in range(0, perm.numel(), bs):
            b = perm[s:s + bs]
            cat_logits, reg_logits = model(t["loc"][b], t["hours_f"][b])
            loss = ce(cat_logits, t["cat_y"][b]) + ce(reg_logits, t["region_y"][b])
            opt.zero_grad()
            loss.backward()
            opt.step()
            running += float(loss) * b.numel()
        # per-epoch val cat macro-F1 (best-epoch tracking) — cat-only forward
        # (forward_cat skips the wide reg head; the reg logits are unused here).
        model.eval()
        with torch.no_grad():
            cat_ep = torch.cat([model.forward_cat(t["loc"][va[s:s + bs]], t["hours_f"][va[s:s + bs]])
                                for s in range(0, va.numel(), bs)])
        f1_ep = float(compute_classification_metrics(
            cat_ep, t["cat_y"][va], num_classes=ctx["n_cats"])["f1"])
        if f1_ep > best_cat_f1:
            best_cat_f1, best_epoch = f1_ep, ep + 1
        print(f"    [finetune {ep+1}/{args.epochs}] train_loss={running/max(tr.numel(),1):.4f} "
              f"val_cat_f1={f1_ep:.4f} (best={best_cat_f1:.4f}@{best_epoch})")

    # --- eval (matched board metrics) ---
    model.eval()
    # STREAMED reg metric. The full [n_val, n_regions] logit is ~20 GB at california (8501
    # regions) / texas (6553) — this used to cat it whole and would simply OOM there. Every
    # quantity the OOD block needs (top-k hit, strict-`>` rank, target) is per-ROW, so the
    # accumulators are O(N) and the result is identical: `_ood_from_streamed` is the same
    # computation `_ood_restricted_topk` performs, on the same numbers. Masking after the fact
    # is equivalent to masking first, because top-k of row i does not depend on any other row.
    # cat stays on the full path — 7-8 classes, the buffer is nothing.
    cat_logits_all = []
    reg_acc = StreamingClsMetrics(ctx["n_regions"], top_k=(1, 5, 10), diagnose_ties=True)
    with torch.no_grad():
        for s in range(0, va.numel(), bs):
            b = va[s:s + bs]
            cl, rl = model(t["loc"][b], t["hours_f"][b])
            cat_logits_all.append(cl)
            reg_acc.update(rl, t["region_y"][b])
    cat_logits = torch.cat(cat_logits_all)
    cat_tgt = t["cat_y"][va]

    cat_metrics = compute_classification_metrics(cat_logits, cat_tgt, num_classes=ctx["n_cats"])
    train_region_labels = set(int(r) for r in ctx["region_y"][train_idx])
    _, _rt, _rr, _rh = reg_acc.concat()
    reg_ood = _ood_from_streamed(_rt, _rr, _rh, train_region_labels)

    cat_f1 = float(cat_metrics["f1"])
    reg_top10 = float(reg_ood["top10_acc_indist"])
    geom = math.sqrt(max(cat_f1, 0.0) * max(reg_top10, 0.0))
    return {
        "cat_f1": cat_f1,                      # FINAL-epoch (AL-comparable headline)
        "cat_f1_best": best_cat_f1,            # BEST-epoch (matches board cat-ceiling rule)
        "cat_f1_best_epoch": best_epoch,
        "cat_accuracy": float(cat_metrics.get("accuracy", 0.0)),
        "reg_top10_acc_indist": reg_top10,
        "reg_top5_acc_indist": float(reg_ood["top5_acc_indist"]),
        "reg_top1_acc_indist": float(reg_ood["top1_acc_indist"]),
        "reg_n_indist": float(reg_ood["n_indist"]),
        "reg_n_ood": float(reg_ood["n_ood"]),
        "geom_simple": geom,
        "n_train": int(len(train_idx)),
        "n_val": int(len(val_idx)),
        "n_train_users": len(train_users),
        "n_val_users": len(val_users),
    }


def main():
    ap = argparse.ArgumentParser(description="CTLE (AAAI'21) NATIVE-E2E baseline B1")
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=30, help="supervised E2E fine-tune epochs")
    ap.add_argument("--pretrain-epochs", type=int, default=10, help="CTLE MLM+MH pretrain epochs")
    ap.add_argument("--only-fold", type=int, default=None,
                    help="run ONLY this board fold index (0..4); respects the 5-split")
    ap.add_argument("--batch-size", type=int, default=2048)
    ap.add_argument("--lr", type=float, default=1e-3, help="E2E fine-tune lr")
    ap.add_argument("--pretrain-lr", type=float, default=1e-3)
    ap.add_argument("--device", default=None, help="override device (cpu/cuda/mps)")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny AL run: 1 fold (fold 0), 2 pretrain + 2 finetune epochs, "
                         "2-layer/4-head CTLE — proves plumbing + leak-safety + dk_ovl alignment")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    if args.smoke:
        args.state = "alabama"
        args.folds = 1
        args.epochs = 2
        args.pretrain_epochs = 2
        args.only_fold = 0
        args.seed = 0
        args.batch_size = 1024

    # Determinism (correctness-advisor finding #2): the data-shuffle Generator was
    # seeded, but model init (CTLE encoder + the two linear heads) drew from the
    # UN-seeded global RNG -> the cited number was not bit-reproducible. Seed all
    # three global RNGs (mirrors src/data/folds.py FoldCreator). Per-fold reseed in
    # the loop below makes each fold's init order-independent (so --only-fold matches).
    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    random.seed(args.seed)

    if args.device:
        device = torch.device(args.device)
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"[ctle_e2e_b1] state={args.state} seed={args.seed} folds={args.folds} "
          f"epochs={args.epochs} pretrain_epochs={args.pretrain_epochs} "
          f"device={device} engine={ENGINE.value} (stride-1 overlap base)")

    # --- board fold split over the dk_ovl rows (StratifiedGroupKFold, 5 splits) ---
    from sklearn.model_selection import StratifiedGroupKFold
    X, y_cat, userids, _ = load_next_data(args.state, ENGINE)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(X, y_cat, groups=userids))

    ctx = build_context(args.state)
    print(f"[ctle_e2e_b1] rows={len(X)} n_regions={ctx['n_regions']} "
          f"n_cats={ctx['n_cats']} vocab={ctx['vocab_size']}")
    assert len(ctx["region_y"]) == len(X), (len(ctx["region_y"]), len(X))

    # which folds to run
    if args.only_fold is not None:
        fold_iter = [(args.only_fold, splits[args.only_fold])]
    else:
        fold_iter = [(i, splits[i]) for i in range(min(args.folds, 5))]

    results = []
    t0 = time.time()
    for fold_idx, (train_idx, val_idx) in fold_iter:
        print(f"[fold {fold_idx}] train={len(train_idx)} val={len(val_idx)}")
        torch.manual_seed(1000 * args.seed + fold_idx)  # fold-stable model init
        r = run_fold(ctx, train_idx, val_idx, args, device)
        r["fold"] = fold_idx
        results.append(r)
        print(f"[fold {fold_idx}] cat_f1={r['cat_f1']:.4f} "
              f"reg_top10_acc_indist={r['reg_top10_acc_indist']:.4f} "
              f"geom_simple={r['geom_simple']:.4f} "
              f"(train_users={r['n_train_users']} val_users={r['n_val_users']})")

    agg = {
        "engine": ENGINE_NAME,
        "baseline": "B1_ctle_aaai2021_native_e2e",
        "base_substrate": ENGINE.value,
        "windowing": "stride-1 overlap (gated): window=9 stride=1 min_seq=10 emit_tail=False",
        "state": args.state,
        "seed": args.seed,
        "folds_run": len(results),
        "epochs": args.epochs,
        "pretrain_epochs": args.pretrain_epochs,
        "cat_f1_mean": float(np.mean([r["cat_f1"] for r in results])) if results else 0.0,
        "cat_f1_best_mean": float(np.mean([r["cat_f1_best"] for r in results])) if results else 0.0,
        "reg_top10_acc_indist_mean": float(np.mean([r["reg_top10_acc_indist"] for r in results])) if results else 0.0,
        "geom_simple_mean": float(np.mean([r["geom_simple"] for r in results])) if results else 0.0,
        "per_fold": results,
        "wall_seconds": round(time.time() - t0, 1),
        "smoke": args.smoke,
    }

    out_dir = Path(args.out_dir) if args.out_dir else (RESULTS_ROOT / ENGINE_NAME / args.state.lower())
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = "smoke" if args.smoke else f"seed{args.seed}"
    if args.only_fold is not None and not args.smoke:
        tag += f"_fold{args.only_fold}"
    out_path = out_dir / f"ctle_e2e_{tag}.json"
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"[ctle_e2e_b1] cat_f1_mean(final)={agg['cat_f1_mean']:.4f} "
          f"cat_f1_best_mean={agg['cat_f1_best_mean']:.4f} "
          f"reg_top10_acc_indist_mean={agg['reg_top10_acc_indist_mean']:.4f} "
          f"geom_simple_mean={agg['geom_simple_mean']:.4f}")
    print(f"[ctle_e2e_b1] wrote {out_path}")


if __name__ == "__main__":
    main()
