#!/usr/bin/env python
"""B5 — Flashback (Yang et al., IJCAI 2020) — E2E baseline trainer (class-B).

Paper: Dingqi Yang, Benjamin Fankhauser, Paolo Rosso, Philippe Cudre-Mauroux.
"Location Prediction over Sparse User Mobility Traces Using RNNs: Flashback in
Hidden States!" IJCAI 2020, pp. 2184-2190.
https://www.ijcai.org/proceedings/2020/302
Reference code: https://github.com/eXascaleInfolab/Flashback_code

================================================================================
WHAT THIS IS
================================================================================
Flashback is a FULL spatiotemporal RNN architecture inseparable from its
output head — it cannot be reduced to a 64-d substrate column. Per the
INTEGRATION GUIDE it is therefore a **class-(B) E2E-TRAINER**: a standalone
trainer under ``scripts/baselines/`` that

  (1) REUSES the exact board fold split (user-disjoint StratifiedGroupKFold,
      groups=userid, y=next_category, shuffle=True, random_state=seed) — the
      same split FoldCreator._create_check2hgi_mtl_folds and
      compute_region_transition._build_per_fold produce;
  (2) REUSES the board metrics — cat macro-``f1`` from
      tracking.metrics.compute_classification_metrics, and reg
      ``top10_acc_indist`` from training.runners.mtl_eval._ood_from_streamed (the
      streamed form of _ood_restricted_topk; same numbers, O(N) memory)
      (OOD-restricted Acc@10 against the per-fold train label set);
  (3) emits per-fold JSON to ``results/<engine>/<state>/`` mirroring the
      champion's key names so the board aggregator reads it uniformly.

It TOUCHES NO src/ file and adds NO EmbeddingEngine enum member (zero
shared-file edits). Results land under ``results/flashback_b5/<state>/`` — a
disk namespace owned by this baseline alone.

================================================================================
FLASHBACK FORMULATION (faithful to the reference code)
================================================================================
For a window of past check-ins j=0..i with RNN hidden states h_j, the model
re-weights every past hidden state by a spatiotemporal kernel:

    f_t(dt) = ((cos(2*pi*dt/86400) + 1) / 2) * exp(-(dt/86400) * lambda_t)
    f_s(ds) = exp(-(ds) * lambda_s)
    w_j     = f_t(dt_{i,j}) * f_s(ds_{i,j}) + 1e-10
    out_i   = (sum_j w_j * h_j) / (sum_j w_j)

where dt is the time gap (seconds) and ds the geographic distance between
check-in i and j. The aggregated state ``out_i`` is concatenated with a learned
user embedding and linearly projected to the label space (network.py forward).

Defaults (setting.py, GOWALLA): lambda_t=0.1, lambda_s=1000, hidden_dim=10,
rnn='rnn', lr=0.01. We keep lambda_t=0.1. For lambda_s we expose a CLI flag and
default to **0.3** because our distances are in KILOMETRES (haversine): lambda_s=100
underflowed exp(-ds_km*100) (~85% of past positions floored → aggregation collapsed
to a vanilla RNN); 0.3 keeps exp(-ds_km*0.3)~O(0.1–1) for the observed 2–9 km gaps.
See DEVIATIONS D3 + the [AUDIT-FIX B5] note at the CLI.

================================================================================
DEVIATIONS FROM THE PAPER (documented for the audit)
================================================================================
D1. REGION HEAD (the "swap POI head -> region head" of the spec). The paper
    predicts next-POI. We mirror the repo's STAN region adaptation and predict
    next-REGION directly (TIGER tract, ~1.1k-8.5k classes). Reg metric is
    top10_acc_indist over regions. We ALSO train a category head (the board's
    second task), giving the same two-task surface as the champion. Reported as
    a deviation; well-justified for sparse AL/AZ traces where the region label
    is denser than the POI label.
D2. WINDOWED INPUT (not full trajectory). The board uses fixed 9-step windows
    (sequences_next.parquet: poi_0..poi_8 -> target). The reference Flashback
    runs over variable-length user trajectories. We run Flashback over the
    9-window so it row-aligns with the board's eval inputs and stays leak-clean
    per fold. Paper-grade overlapping (stride-1) windows are POST-FREEZE (P3).
D3. DISTANCE UNITS. Haversine km between POI centroids vs the reference's
    raw lat/lon Euclidean distance -> lambda_s rescaled (CLI; default 0.3).
D4. hidden_dim raised from the reference toy default (10) to 128 for the
    larger TIGER label space; CLI-overridable.

================================================================================
LEAK-SAFETY (HARD REQUIREMENT)
================================================================================
* Folds: StratifiedGroupKFold(n_splits, shuffle=True, random_state=seed) over
  load_next_data(state, CHECK2HGI) with groups=userid, y=next_category —
  BIT-IDENTICAL to the board split. We assert val users are DISJOINT from train
  users before training.
* POI coordinates / category lookups are STATIC geography (placeid -> centroid,
  placeid -> region), not learned — no train/val leak. The RNN + heads + user
  embeddings are trained ONLY on rows whose index is in train_idx. The val pass
  never updates a parameter.
* OOD restriction: top10_acc_indist is computed against
  train_label_set = set(region labels seen in train_idx) — exactly the board's
  protocol (_ood_from_streamed).

================================================================================
SMOKE
================================================================================
PYTHONPATH=src python scripts/baselines/flashback_e2e.py --smoke
  -> state=alabama, 1 fold, 2 epochs, seed 0, hidden 32. Prints cat f1 +
     reg top10_acc_indist and asserts user-disjoint folds. Writes NO checkpoint.

Full board run (P3, do NOT run here): omit --smoke, set --folds 5
--epochs <E> --seed in {0,1,7,100} over all 6 states; for paper-grade reg
ranking parity, the champion uses a per-fold seeded log_T prior — Flashback's
own spatiotemporal kernel is its analogue, so we do NOT add log_T (documented).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# --- repo imports (read-only; we IMPORT, never modify) ----------------------
_ROOT = Path(__file__).resolve().parents[2]
_SRC = str(_ROOT / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

from configs.paths import (  # noqa: E402
    EmbeddingEngine, IoPaths, OUTPUT_DIR, RESULTS_ROOT, IO_CHECKINS,
)
from data.folds import load_next_data  # noqa: E402
from data.inputs.region_sequence import _load_graph_maps  # noqa: E402
from tracking.metrics import StreamingClsMetrics, compute_classification_metrics  # noqa: E402
from training.runners.mtl_eval import _ood_from_streamed  # noqa: E402

ENGINE_NAME = "flashback_b5"  # disk namespace; NOT an EmbeddingEngine member
PAD = -1
SECONDS_PER_DAY = 86400.0


# ============================================================================
# Geography + temporal context (STATIC — placeid -> centroid / first-seen time)
# ============================================================================
def _haversine_km(lat1, lon1, lat2, lon2):
    """Vectorised great-circle distance in km. Inputs are np arrays (radians-free)."""
    r = 6371.0088
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlmb = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def _load_poi_geo(state: str):
    """placeid -> (lat, lon) centroid from raw check-ins (STATIC geography).

    Uses the per-placeid mean lat/lon over the raw Gowalla file for the state.
    This is geography, not a learned signal, so it is leak-safe to compute on
    the full corpus.
    """
    # raw file is Title-cased (e.g. Alabama.parquet); IO_CHECKINS honors $DATA_ROOT
    fname = state.replace("_", " ").title() + ".parquet"
    raw = pd.read_parquet(IO_CHECKINS / fname,
                          columns=["placeid", "latitude", "longitude"])
    g = raw.groupby("placeid")[["latitude", "longitude"]].mean()
    return g["latitude"].to_dict(), g["longitude"].to_dict()


def _build_window_context(state: str, engine: EmbeddingEngine = EmbeddingEngine.CHECK2HGI_DK_OVL):
    """Build, ROW-ALIGNED to next_region.parquet / sequences_next.parquet:

      poi_win   : [N, 9] int64 placeids (PAD=-1)
      lat_win   : [N, 9] float32 (0 at pad)
      lon_win   : [N, 9] float32
      dt_win    : [N, 9] float32 — seconds from window step k to the TARGET step
                  (the reference's dt_{i,j}); used by f_t. Reconstructed from a
                  uniform inter-checkin spacing prior (see note) when raw
                  timestamps per window position are unavailable post-windowing.
      region_y  : [N] int64 next-region label
      cat_y     : [N] int64 next-category label
      userids   : [N] int64
      n_regions, n_cats
    """
    seq = pd.read_parquet(IoPaths.get_seq_next(state, engine))
    nr = pd.read_parquet(IoPaths.get_next_region(state, engine))
    assert len(seq) == len(nr), (len(seq), len(nr))

    poi_cols = [f"poi_{i}" for i in range(9)]
    poi_win = seq[poi_cols].astype(np.int64).to_numpy()

    lat_map, lon_map = _load_poi_geo(state)
    # vectorised centroid lookup with pad handling
    flat = poi_win.reshape(-1)
    lat = np.array([lat_map.get(int(p), 0.0) if p != PAD else 0.0 for p in flat], np.float32)
    lon = np.array([lon_map.get(int(p), 0.0) if p != PAD else 0.0 for p in flat], np.float32)
    lat_win = lat.reshape(poi_win.shape)
    lon_win = lon.reshape(poi_win.shape)

    # Temporal context. The windowed artifact drops raw per-step timestamps, so
    # we reconstruct dt with the reference's "average dt = step_gap * k" prior:
    # step k (0=oldest .. 8=most recent before target) is (9-k) steps before the
    # target. We scale by ONE_STEP_SECONDS (median Gowalla inter-checkin gap ~
    # a few hours); the cos() periodicity + exp decay then act exactly as in the
    # paper. This is the documented D2 windowing deviation. (P3 stride-1 runs can
    # carry true per-step datetimes.)
    ONE_STEP_SECONDS = 6 * 3600.0
    steps_back = np.arange(9, 0, -1, dtype=np.float32)  # [9,8,...,1]
    dt_win = np.tile(steps_back, (poi_win.shape[0], 1)) * ONE_STEP_SECONDS

    region_y = nr["region_idx"].astype(np.int64).to_numpy()
    cat_y, n_cats = _load_cat_labels(state, len(seq), engine)
    userids = seq["userid"].astype(np.int64).to_numpy()

    _, poi_to_region = _load_graph_maps(state)
    n_regions = int(poi_to_region.max()) + 1
    return dict(
        poi_win=poi_win, lat_win=lat_win, lon_win=lon_win, dt_win=dt_win,
        region_y=region_y, cat_y=cat_y, userids=userids,
        n_regions=n_regions, n_cats=int(n_cats),
    )


def _load_cat_labels(state: str, expected_len: int,
                     engine: EmbeddingEngine = EmbeddingEngine.CHECK2HGI_DK_OVL):
    """next_category labels, row-aligned (from load_next_data's y)."""
    _, y_cat, _, _ = load_next_data(state, engine)
    assert len(y_cat) == expected_len, (len(y_cat), expected_len)
    y_cat = np.asarray(y_cat, dtype=np.int64)
    n_cats = int(y_cat.max()) + 1
    return y_cat, n_cats


# ============================================================================
# Flashback model (faithful spatiotemporal hidden-state weighting)
# ============================================================================
class Flashback(nn.Module):
    """Flashback RNN with spatiotemporal flashback weighting + region & cat heads.

    Mirrors network.py: an RNN over the window, then for each position i a
    spatiotemporally-weighted sum over past hidden states, concatenated with a
    per-user embedding, then a linear head. Here the window is fixed at 9 and we
    read the aggregated state at the LAST position to predict the target.
    """

    def __init__(self, n_pois, n_regions, n_cats, n_users,
                 poi_dim=64, user_dim=64, hidden=128,
                 lambda_t=0.1, lambda_s=0.3, rnn_type="rnn"):  # [AUDIT-FIX B5] km-regime lambda_s
        super().__init__()
        self.lambda_t = lambda_t
        self.lambda_s = lambda_s
        self.hidden = hidden
        self.poi_emb = nn.Embedding(n_pois + 1, poi_dim, padding_idx=n_pois)  # last idx = pad
        self.pad_poi = n_pois
        self.user_emb = nn.Embedding(n_users + 1, user_dim)
        rnn_cls = {"rnn": nn.RNN, "gru": nn.GRU, "lstm": nn.LSTM}[rnn_type]
        self.rnn = rnn_cls(poi_dim, hidden, batch_first=True)
        self.rnn_type = rnn_type
        self.fc_region = nn.Linear(hidden + user_dim, n_regions)
        self.fc_cat = nn.Linear(hidden + user_dim, n_cats)

    def _ft(self, dt):  # temporal kernel — faithful to trainer.py f_t lambda
        return ((torch.cos(dt * 2 * math.pi / SECONDS_PER_DAY) + 1) / 2) * \
            torch.exp(-(dt / SECONDS_PER_DAY) * self.lambda_t)

    def _fs(self, ds):  # spatial kernel — faithful to trainer.py f_s lambda
        return torch.exp(-(ds * self.lambda_s))

    def forward(self, poi_idx, lat, lon, dt, user_idx):
        """poi_idx[B,9] (pad mapped to self.pad_poi), lat/lon/dt[B,9], user_idx[B]."""
        B, L = poi_idx.shape
        valid = (poi_idx != self.pad_poi).float()  # [B,9]
        emb = self.poi_emb(poi_idx)  # [B,9,poi_dim]
        out, _ = self.rnn(emb)  # [B,9,hidden]

        # Spatiotemporal flashback weighting, anchored at the LAST valid step i.
        # dt[:,k] already encodes seconds from step k to the target -> dt_{i,k}.
        # Spatial gap: distance from each step k to the most-recent valid step.
        last_idx = (valid.cumsum(dim=1).argmax(dim=1)).long()  # [B] last valid pos
        bi = torch.arange(B, device=poi_idx.device)
        lat_i = lat[bi, last_idx].unsqueeze(1)  # [B,1]
        lon_i = lon[bi, last_idx].unsqueeze(1)
        # haversine in torch (km)
        ds = self._haversine_torch(lat_i, lon_i, lat, lon)  # [B,9]
        a = self._ft(dt) * self._fs(ds)  # [B,9]
        a = a * valid + 1e-10  # zero-out pads
        a = a.unsqueeze(-1)  # [B,9,1]
        agg = (a * out).sum(dim=1) / a.sum(dim=1)  # [B,hidden]

        u = self.user_emb(user_idx)  # [B,user_dim]
        z = torch.cat([agg, u], dim=1)
        return self.fc_cat(z), self.fc_region(z)

    @staticmethod
    def _haversine_torch(lat1, lon1, lat2, lon2):
        r = 6371.0088
        d2r = math.pi / 180.0
        p1 = lat1 * d2r
        p2 = lat2 * d2r
        dphi = (lat2 - lat1) * d2r
        dlmb = (lon2 - lon1) * d2r
        a = torch.sin(dphi / 2) ** 2 + torch.cos(p1) * torch.cos(p2) * torch.sin(dlmb / 2) ** 2
        return 2 * r * torch.asin(torch.clamp(a, 0, 1).sqrt())


# ============================================================================
# Train / eval one fold
# ============================================================================
def _make_tensors(ctx, placeid_to_compact, n_pois, device):
    poi = ctx["poi_win"].copy()
    # map placeids -> compact 0..n_pois-1; pad -> n_pois
    flat = poi.reshape(-1)
    mapped = np.array([placeid_to_compact.get(int(p), n_pois) if p != PAD else n_pois
                       for p in flat], np.int64).reshape(poi.shape)
    t = dict(
        poi=torch.from_numpy(mapped).to(device),
        lat=torch.from_numpy(ctx["lat_win"]).to(device),
        lon=torch.from_numpy(ctx["lon_win"]).to(device),
        dt=torch.from_numpy(ctx["dt_win"].astype(np.float32)).to(device),
        region_y=torch.from_numpy(ctx["region_y"]).to(device),
        cat_y=torch.from_numpy(ctx["cat_y"]).to(device),
    )
    return t


def run_fold(ctx, train_idx, val_idx, args, device):
    # disjoint-user assert (leak-safety proof)
    train_users = set(int(u) for u in ctx["userids"][train_idx])
    val_users = set(int(u) for u in ctx["userids"][val_idx])
    assert val_users.isdisjoint(train_users), "LEAK: val users overlap train users"

    # compact placeid vocab — built from ALL placeids (static geography vocab,
    # no label leak); user vocab likewise. Padding handled by self.pad_poi.
    all_pids = sorted(set(int(p) for p in ctx["poi_win"].reshape(-1) if p != PAD))
    placeid_to_compact = {p: i for i, p in enumerate(all_pids)}
    n_pois = len(all_pids)
    all_uids = sorted(set(int(u) for u in ctx["userids"]))
    uid_to_compact = {u: i for i, u in enumerate(all_uids)}
    user_compact = np.array([uid_to_compact[int(u)] for u in ctx["userids"]], np.int64)

    t = _make_tensors(ctx, placeid_to_compact, n_pois, device)
    user_t = torch.from_numpy(user_compact).to(device)

    model = Flashback(
        n_pois=n_pois, n_regions=ctx["n_regions"], n_cats=ctx["n_cats"],
        n_users=len(all_uids), hidden=args.hidden,
        lambda_t=args.lambda_t, lambda_s=args.lambda_s, rnn_type=args.rnn,
    ).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    ce = nn.CrossEntropyLoss()

    tr = torch.as_tensor(train_idx, device=device, dtype=torch.long)
    va = torch.as_tensor(val_idx, device=device, dtype=torch.long)
    bs = args.batch_size

    for epoch in range(args.epochs):
        model.train()
        perm = tr[torch.randperm(tr.numel(), device=device)]
        for s in range(0, perm.numel(), bs):
            b = perm[s:s + bs]
            cat_logits, reg_logits = model(t["poi"][b], t["lat"][b], t["lon"][b],
                                           t["dt"][b], user_t[b])
            loss = ce(cat_logits, t["cat_y"][b]) + ce(reg_logits, t["region_y"][b])
            opt.zero_grad()
            loss.backward()
            opt.step()

    # eval
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
            cl, rl = model(t["poi"][b], t["lat"][b], t["lon"][b], t["dt"][b], user_t[b])
            cat_logits_all.append(cl)
            reg_acc.update(rl, t["region_y"][b])
    cat_logits = torch.cat(cat_logits_all)
    cat_tgt = t["cat_y"][va]

    cat_metrics = compute_classification_metrics(cat_logits, cat_tgt, num_classes=ctx["n_cats"])
    train_region_labels = set(int(r) for r in ctx["region_y"][train_idx])
    _, _rt, _rr, _rh = reg_acc.concat()
    reg_ood = _ood_from_streamed(_rt, _rr, _rh, train_region_labels)

    geom = math.sqrt(max(cat_metrics["f1"], 0.0) * max(reg_ood["top10_acc_indist"], 0.0))
    return {
        "cat_f1": float(cat_metrics["f1"]),
        "cat_accuracy": float(cat_metrics.get("accuracy", 0.0)),
        "reg_top10_acc_indist": float(reg_ood["top10_acc_indist"]),
        "reg_top5_acc_indist": float(reg_ood["top5_acc_indist"]),
        "reg_top1_acc_indist": float(reg_ood["top1_acc_indist"]),
        "reg_n_indist": float(reg_ood["n_indist"]),
        "reg_n_ood": float(reg_ood["n_ood"]),
        "geom_simple": float(geom),
        "n_train_users": len(train_users),
        "n_val_users": len(val_users),
    }


def main():
    ap = argparse.ArgumentParser(description="Flashback (IJCAI'20) E2E baseline B5")
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=2048)
    ap.add_argument("--hidden", type=int, default=128)
    ap.add_argument("--lr", type=float, default=0.01)
    ap.add_argument("--lambda-t", type=float, default=0.1, help="temporal decay (paper default)")
    ap.add_argument("--lambda-s", type=float, default=0.3,
                    help="[AUDIT-FIX B5] spatial decay in the KM regime. Paper Gowalla=1000 acts on raw "
                         "lat/lon-DEGREE units (~0.0x deg gaps); our distances are haversine-KM (AL median "
                         "intra-window gaps 2-9 km). lambda_s=100 underflowed exp(-ds_km*100) for any gap "
                         ">0.1 km (->~85% of past positions at the 1e-10 floor; agg collapsed onto the "
                         "anchor = vanilla-RNN, disabling 'flashback'). 0.3 keeps exp(-ds_km*0.3)~O(0.1-1) "
                         "for few-km gaps (effective attended positions ~3.6) = real flashback re-weighting.")
    ap.add_argument("--rnn", default="rnn", choices=["rnn", "gru", "lstm"])
    ap.add_argument("--engine", "--base", dest="engine", default="check2hgi_dk_ovl",
                    help="board base engine that supplies the fold inputs + region/cat labels. "
                         "DEFAULT 'check2hgi_dk_ovl' = the GATED STRIDE-1 OVERLAP base the board + "
                         "Check2HGI + the SC baselines run on (AL=96,326 rows). Pass 'check2hgi' for "
                         "the legacy CANONICAL stride-9 base (AL=12,709 rows; back-compat only).")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny AL run: 1 fold, 2 epochs, hidden 32 — proves plumbing+leak-safety")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    if args.smoke:
        args.state = "alabama"
        args.folds = 1
        args.epochs = 2
        args.hidden = 32
        args.seed = 0

    engine = EmbeddingEngine(args.engine)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[flashback_b5] state={args.state} seed={args.seed} folds={args.folds} "
          f"epochs={args.epochs} hidden={args.hidden} device={device} "
          f"lambda_t={args.lambda_t} lambda_s={args.lambda_s} rnn={args.rnn} "
          f"engine={engine.value}")

    # --- board fold split (BIT-IDENTICAL to the champion) -------------------
    from sklearn.model_selection import StratifiedGroupKFold
    X, y_cat, userids, _ = load_next_data(args.state, engine)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(X, y_cat, groups=userids))

    ctx = _build_window_context(args.state, engine)
    assert len(ctx["region_y"]) == len(X), (len(ctx["region_y"]), len(X))
    print(f"[flashback_b5] rows={len(X)} n_regions={ctx['n_regions']} n_cats={ctx['n_cats']}")

    results = []
    t0 = time.time()
    for fold_idx, (train_idx, val_idx) in enumerate(splits):
        if fold_idx >= args.folds:
            break
        r = run_fold(ctx, train_idx, val_idx, args, device)
        r["fold"] = fold_idx + 1
        results.append(r)
        print(f"[fold {fold_idx + 1}] cat_f1={r['cat_f1']:.4f} "
              f"reg_top10_acc_indist={r['reg_top10_acc_indist']:.4f} "
              f"geom_simple={r['geom_simple']:.4f} "
              f"(train_users={r['n_train_users']} val_users={r['n_val_users']})")

    agg = {
        "engine": ENGINE_NAME,
        "base_engine": engine.value,
        "baseline": "B5_flashback_ijcai2020",
        "state": args.state,
        "seed": args.seed,
        "folds_run": len(results),
        "epochs": args.epochs,
        "hidden": args.hidden,
        "lambda_t": args.lambda_t,
        "lambda_s": args.lambda_s,
        "rnn": args.rnn,
        "cat_f1_mean": float(np.mean([r["cat_f1"] for r in results])) if results else 0.0,
        "reg_top10_acc_indist_mean": float(np.mean([r["reg_top10_acc_indist"] for r in results])) if results else 0.0,
        "geom_simple_mean": float(np.mean([r["geom_simple"] for r in results])) if results else 0.0,
        "per_fold": results,
        "wall_seconds": round(time.time() - t0, 1),
        "smoke": args.smoke,
    }

    out_dir = Path(args.out_dir) if args.out_dir else (RESULTS_ROOT / ENGINE_NAME / args.state.lower())
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = "smoke" if args.smoke else f"seed{args.seed}"
    out_path = out_dir / f"flashback_{tag}.json"
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"[flashback_b5] cat_f1_mean={agg['cat_f1_mean']:.4f} "
          f"reg_top10_acc_indist_mean={agg['reg_top10_acc_indist_mean']:.4f} "
          f"geom_simple_mean={agg['geom_simple_mean']:.4f}")
    print(f"[flashback_b5] wrote {out_path}")


if __name__ == "__main__":
    main()
