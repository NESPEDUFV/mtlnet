#!/usr/bin/env python
"""POI2Vec (Feng et al., AAAI 2017) — NATIVE-E2E baseline trainer (class-B).

Paper: Shanshan Feng, Gao Cong, Bo An, Yeow Meng Chee. "POI2Vec: Geographical
Latent Representation for Predicting Future Visitors." AAAI 2017, pp. 102-108.
Reference impl: https://github.com/yongqyu/POI2Vec

================================================================================
WHAT THIS IS
================================================================================
A NATIVE-E2E driver for POI2Vec, mirroring ``flashback_e2e.py`` / ``b3_hmt_grn.py``:
a standalone trainer under ``scripts/baselines/`` that

  (1) REUSES the exact board fold split (user-disjoint StratifiedGroupKFold,
      groups=userid, y=next_category, shuffle=True, random_state=seed) — identical
      to the champion split and to FoldCreator._create_check2hgi_mtl_folds;
  (2) REUSES the board metrics — cat macro-``f1`` from
      tracking.metrics.compute_classification_metrics, and reg
      ``top10_acc_indist`` from training.runners.mtl_eval._ood_from_streamed (the
      streamed form of _ood_restricted_topk; same numbers, O(N) memory)
      (OOD-restricted Acc@10 against the per-fold TRAIN region label set);
  (3) ALIGNS to the GATED STRIDE-1 OVERLAP base ``check2hgi_dk_ovl`` (AL = 96,326
      rows; stride-1, emit_tail gated False, MIN_SEQ 10≡5) — NOT canonical
      stride-9 (12,709 rows). Region labels: next_region.parquet ``region_idx``
      (n_regions=1109 for AL, shared TIGER-tract partition via poi_to_region).
      Category labels: the 7 root classes from load_next_data's y.
  (4) emits per-fold JSON to ``results/poi2vec_e2e/<state>/`` mirroring the
      champion's key names so the board aggregator reads it uniformly.

It TOUCHES NO src/ file and adds NO EmbeddingEngine enum member (CHECK2HGI_DK_OVL
already exists in paths.py). Results land under ``results/poi2vec_e2e/<state>/``.

================================================================================
"NATIVE E2E" FOR A SHALLOW MODEL (faithfulness ledger)
================================================================================
POI2Vec is SHALLOW: its only learned bodies are (a) a per-POI input/context
embedding table ``poi_embed``, (b) a per-user latent ``user_embed``, and (c) the
geo-tree routing vectors ``node_vec`` used by hierarchical softmax. There is no
deep sequence encoder to "swap a head onto." So "native E2E" here = use POI2Vec's
NATIVE LEARNED BODY (its poi_embed + user_embed, trained by the exact AAAI'17
mechanism — CBOW context-sum + FIXED midpoint binary tree + OVERLAP-AREA phi +
hierarchical softmax + negative-sampled user term) and put ADAPTED next-CATEGORY
and next-REGION heads on the POOLED window representation that POI2Vec itself
produces (its ``context_sum``: SUM of the window's poi_embed + the user vector).

Reused VERBATIM from ``poi2vec_lib/model.py`` (the faithful AAAI'17 model that
``build_poi2vec_substrate.py`` uses):
  * ``build_midpoint_tree``           — mechanism #1 (FIXED midpoint binary tree)
  * ``build_poi_routes``              — mechanism #2 (OVERLAP-AREA phi)
  * ``POI2VecAAAI`` (forward_nll, context_sum, _build_edge_index)
                                       — mechanism #3 (CBOW + hier-softmax + user)
                                         + mechanism #4 (poi_embed/user_embed tables)

Reused (pattern, adapted to the dk_ovl base) from ``build_poi2vec_substrate.py``:
  * ``build_cbow_examples`` body      — TRAIN-USER-ONLY forward-CBOW windows
  * ``reproduce_fold_train_idx`` idea — the bit-identical SGKF fold split

DEVIATIONS (documented for the audit)
  D1. REGION + CATEGORY heads on the pooled POI2Vec context vector. The paper's
      native output is a next-POI distribution via the geo-tree path probs. But
      the board's headline tasks are next-CATEGORY (7 classes) and next-REGION
      (TIGER tract, ~1.1k classes), and the geo-tree LEAVES are NOT the TIGER
      regions (different partitions). The FAITHFUL adaptation is therefore a
      LINEAR head on the pooled POI2Vec sequence embedding (poi_embed sum over the
      window + user_embed) — exactly the vector POI2Vec scores its tree against
      (``context_sum``). We do NOT fabricate a region<-leaf surjection (that would
      be an unfaithful, lossy re-projection of a different geometry). The pooled
      representation IS POI2Vec's native sentence vector; a linear region/cat head
      is the minimal adapter. Documented as the native-E2E adaptation.
  D2. WINDOW = the dk_ovl stride-1 9-step window (poi_0..poi_8 -> target). The
      reference runs over variable-length user trajectories. We pool the board's
      fixed 9-window so it row-aligns with the dk_ovl eval inputs and stays
      leak-clean per fold.
  D3. DIM = 64 (matched to the board; paper uses 200-d) — same matched-protocol
      deviation as build_poi2vec_substrate.py (README_poi2vec.md §DIM).

================================================================================
LEAK-SAFETY (HARD REQUIREMENT)
================================================================================
* Folds: StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed) over
  load_next_data(state, CHECK2HGI_DK_OVL) with groups=userid, y=next_category —
  BIT-IDENTICAL to the board split. We assert val users are DISJOINT from train
  users before training. ``--only-fold k`` runs a single fold of the SAME 5-split
  partition (never re-partitions into k splits — that would change the geometry).
* PER-FOLD POI2Vec PRETRAINING ON TRAIN USERS ONLY. The CBOW examples that train
  poi_embed/user_embed/node_vec are built ONLY from check-ins of the fold's TRAIN
  users (build_cbow_examples drops non-train-user rows). The midpoint tree +
  overlap-area phi are STATIC geometry (bbox + theta + POI coords), not labels —
  leak-safe to compute on the full POI universe. The val pass never updates a
  parameter (heads OR body). This is the protocol the SC substrate builder uses
  per (state,seed,fold); see docs/studies/closing_data/BASELINES_IMPL_AUDIT.md
  (the CTLE 81.8% transductive leak under --folds 1 is avoided here because the
  body is re-pretrained on TRAIN-only per fold, never once on all data).
* OOD restriction: top10_acc_indist is computed against
  train_label_set = set(region labels seen in train_idx) — the board protocol.

================================================================================
SMOKE
================================================================================
  MTL_RAM_HEADROOM_GB=2 OMP_NUM_THREADS=3 PYTHONPATH=src \
    .venv/bin/python scripts/baselines/poi2vec_e2e.py --smoke
  -> state=alabama, 1 fold (fold 0 of the 5-split partition), 2 epochs pretrain +
     2 epochs head, seed 0, dim 32. Prints cat f1 + reg top10_acc_indist + geom +
     asserts user-disjoint folds. Writes NO checkpoint; writes a smoke JSON.

Full board run (P3, do NOT run here): omit --smoke, set --folds 5, --epochs E,
--head-epochs E2, --seed in {0,1,7,100} over all 6 states. Executed by the user.
"""
from __future__ import annotations

import argparse
import json
import math
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

from configs.paths import EmbeddingEngine, IoPaths, RESULTS_ROOT  # noqa: E402
from configs.model import InputsConfig  # noqa: E402
from data.folds import load_next_data  # noqa: E402
from data.inputs.region_sequence import _load_graph_maps  # noqa: E402
from tracking.metrics import StreamingClsMetrics, compute_classification_metrics  # noqa: E402
from training.runners.mtl_eval import _ood_from_streamed  # noqa: E402

# Reuse the FAITHFUL AAAI'17 POI2Vec body VERBATIM (mechanisms #1-#4).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from poi2vec_lib import POI2VecAAAI, build_midpoint_tree, build_poi_routes  # noqa: E402

ENGINE = EmbeddingEngine.CHECK2HGI_DK_OVL  # the GATED STRIDE-1 OVERLAP board base
ENGINE_NAME = "poi2vec_e2e"  # disk namespace; NOT a new EmbeddingEngine member
PAD = -1


# ============================================================================
# DATA — dk_ovl stride-1 windows + aligned cat/region labels + POI coords
# ============================================================================
def build_context(state: str):
    """Build, ROW-ALIGNED to the dk_ovl next_region.parquet / sequences_next.parquet:

      poi_win    : [N, 9] int64 placeids (PAD=-1)
      region_y   : [N] int64 next-region label (region_idx)
      cat_y      : [N] int64 next-category label (load_next_data's y; 7 classes)
      userids    : [N] int64
      placeid_to_idx, poi_to_region : the SHARED check2hgi graph maps
      poi_xy     : [n_poi, 2] float64 (lon, lat) POI centroids (static geometry)
      bbox       : (lon0, lat0, lon1, lat1) over filled coords
      n_poi, n_regions, n_cats
    """
    seq_path = IoPaths.get_seq_next(state, ENGINE)
    seq = pd.read_parquet(seq_path)
    nr = IoPaths.load_next_region(state, ENGINE)
    assert len(seq) == len(nr), (len(seq), len(nr))

    poi_cols = [f"poi_{i}" for i in range(InputsConfig.SLIDE_WINDOW)]
    poi_win = seq[poi_cols].astype(np.int64).to_numpy()
    userids = seq["userid"].astype(np.int64).to_numpy()
    region_y = nr["region_idx"].astype(np.int64).to_numpy()

    # category labels row-aligned (load_next_data's y over the SAME dk_ovl base)
    X, y_cat, ld_userids, _ = load_next_data(state, ENGINE)
    assert len(y_cat) == len(seq), (len(y_cat), len(seq))
    assert np.array_equal(np.asarray(ld_userids, dtype=np.int64), userids), \
        "userid order mismatch: load_next_data vs sequences_next (dk_ovl)"
    cat_y = np.asarray(y_cat, dtype=np.int64)
    n_cats = int(cat_y.max()) + 1

    # SHARED graph maps (placeid->compact idx, poi_to_region TIGER partition)
    placeid_to_idx, poi_to_region = _load_graph_maps(state)
    n_poi = max(placeid_to_idx.values()) + 1
    n_regions = int(poi_to_region.max()) + 1
    assert n_regions == int(region_y.max()) + 1 or n_regions >= int(region_y.max()) + 1, \
        (n_regions, int(region_y.max()) + 1)

    # POI coordinates (STATIC geography — for the midpoint tree + overlap phi).
    checkins = IoPaths.load_city(state)
    coord = checkins.groupby("placeid")[["longitude", "latitude"]].mean()
    poi_xy = np.full((n_poi, 2), np.nan, dtype=np.float64)
    for pid, idx in placeid_to_idx.items():
        if pid in coord.index:
            poi_xy[idx] = coord.loc[pid, ["longitude", "latitude"]].to_numpy()
    fin = np.isfinite(poi_xy).all(axis=1)
    lon, lat = poi_xy[fin, 0], poi_xy[fin, 1]
    bbox = (float(lon.min()), float(lat.min()), float(lon.max()), float(lat.max()))

    return dict(
        poi_win=poi_win, region_y=region_y, cat_y=cat_y, userids=userids,
        placeid_to_idx=placeid_to_idx, poi_to_region=poi_to_region,
        poi_xy=poi_xy, bbox=bbox,
        n_poi=int(n_poi), n_regions=int(n_regions), n_cats=int(n_cats),
    )


def build_cbow_examples(seq_df: pd.DataFrame, placeid_to_idx: dict,
                        userid_to_idx: dict, train_userids: set,
                        context_window: int, rng: np.random.Generator):
    """TRAIN-USER-ONLY forward-CBOW examples (body VERBATIM from
    build_poi2vec_substrate.build_cbow_examples, minus the max-examples cap).

    Each sequences_next row is a window poi_0..poi_8 + target_poi + userid. We
    slide a forward CBOW window over the non-pad POIs of each row: for each
    position t, the CONTEXT is the preceding up-to ``context_window`` POIs and the
    TARGET is the POI at t. LEAK-SAFE: rows whose userid is not in train_userids
    are dropped here.

    Returns ctx_idx[N,W] (pad=-1), tgt_idx[N], usr_idx[N].
    """
    poi_cols = [f"poi_{i}" for i in range(InputsConfig.SLIDE_WINDOW)] + ["target_poi"]
    mask = seq_df["userid"].astype(int).isin(train_userids)
    sub = seq_df.loc[mask, poi_cols + ["userid"]]

    ctx_rows: list[np.ndarray] = []
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
        for t in range(1, L):
            lo = max(0, t - W)
            ctx = toks[lo:t]
            if not ctx:
                continue
            padded = np.full(W, -1, dtype=np.int64)
            padded[:len(ctx)] = np.asarray(ctx, dtype=np.int64)
            ctx_rows.append(padded)
            tgts.append(toks[t])
            usrs.append(uidx)

    if not ctx_rows:
        return (np.zeros((0, W), np.int64), np.zeros(0, np.int64), np.zeros(0, np.int64))
    return (np.stack(ctx_rows, 0),
            np.asarray(tgts, np.int64), np.asarray(usrs, np.int64))


# ============================================================================
# NATIVE-E2E MODEL — POI2Vec body (frozen-or-tuned) + pooled-context heads
# ============================================================================
class POI2VecE2E(nn.Module):
    """POI2Vec's native learned body (poi_embed + user_embed, pretrained by the
    AAAI'17 mechanism) with ADAPTED next-CATEGORY + next-REGION linear heads on
    the POOLED window representation == POI2Vec's native ``context_sum``.

    The body (``self.body``) is a fully-built ``POI2VecAAAI`` whose poi_embed /
    user_embed were trained on the fold's TRAIN-USER CBOW examples. We reuse its
    ``context_sum`` (SUM of the window poi_embed + user_embed) — the exact vector
    POI2Vec scores its geo-tree against — as the sequence representation, then
    apply linear heads. The body's parameters are fine-tuned jointly with the
    heads on the SUPERVISED next-cat / next-region task (still TRAIN-only), so the
    full pipeline is genuinely end-to-end on POI2Vec's own representation.
    """

    def __init__(self, body: POI2VecAAAI, n_regions: int, n_cats: int):
        super().__init__()
        self.body = body
        d = body.embed_dim
        self.fc_cat = nn.Linear(d, n_cats)
        self.fc_region = nn.Linear(d, n_regions)

    def forward(self, poi_win: torch.Tensor, user_idx: torch.Tensor):
        """poi_win[B,9] compact POI indices (pad=-1), user_idx[B].

        Pools via POI2Vec's native context_sum (window poi_embed SUM + user_embed).
        """
        ctx_mask = poi_win >= 0  # [B,9] real-POI mask
        # context_sum clamps negatives to 0 and masks them out (see model.py)
        z = self.body.context_sum(poi_win, ctx_mask, user_idx)  # [B,D]
        return self.fc_cat(z), self.fc_region(z)


# ============================================================================
# TRAIN / EVAL one fold
# ============================================================================
def run_fold(ctx, seq_df, train_idx, val_idx, args, device):
    # --- leak-safety: disjoint users ---
    train_users = set(int(u) for u in ctx["userids"][train_idx])
    val_users = set(int(u) for u in ctx["userids"][val_idx])
    assert val_users.isdisjoint(train_users), "LEAK: val users overlap train users"

    # user index map over ALL users (static identity vocab; per-user latent table)
    all_uids = np.unique(ctx["userids"].astype(np.int64))
    userid_to_idx = {int(u): i for i, u in enumerate(all_uids)}
    n_user = len(all_uids)
    user_compact = np.array([userid_to_idx[int(u)] for u in ctx["userids"]], np.int64)

    # --- (1) STATIC geometry: FIXED midpoint tree + OVERLAP-AREA phi ---
    tree = build_midpoint_tree(ctx["bbox"], theta=args.theta)
    routes = build_poi_routes(ctx["poi_xy"], tree, theta=args.theta,
                              route_count=args.route_count)

    # --- (2) NATIVE POI2Vec body, pretrained on TRAIN-USER CBOW examples ONLY ---
    body = POI2VecAAAI(
        ctx["n_poi"], n_user, tree, routes,
        embed_dim=args.dim, route_count=args.route_count,
        n_neg_user=args.n_neg_user, loss_form=args.loss_form,
    ).to(device)

    rng = np.random.default_rng(args.seed)
    cbow_ctx, cbow_tgt, cbow_usr = build_cbow_examples(
        seq_df, ctx["placeid_to_idx"], userid_to_idx, train_users,
        context_window=args.context_window, rng=rng)
    assert len(cbow_tgt) > 0, "no TRAIN-user CBOW examples — check fold/userids"

    opt_body = torch.optim.Adam(body.parameters(), lr=args.pretrain_lr)
    c_t = torch.from_numpy(cbow_ctx)
    m_t = torch.from_numpy(cbow_ctx >= 0)
    t_t = torch.from_numpy(cbow_tgt)
    u_t = torch.from_numpy(cbow_usr)
    n = len(cbow_tgt)
    body.train()
    for ep in range(args.epochs):
        perm = torch.randperm(n)
        for s in range(0, n, args.pretrain_batch):
            bi = perm[s:s + args.pretrain_batch]
            loss = body.forward_nll(c_t[bi].to(device), m_t[bi].to(device),
                                    t_t[bi].to(device), u_t[bi].to(device))
            opt_body.zero_grad()
            loss.backward()
            opt_body.step()

    # --- (3) NATIVE-E2E supervised heads on the pooled context vector ---
    # compact placeid window (pad -> -1; context_sum masks negatives)
    p2i = ctx["placeid_to_idx"]
    flat = ctx["poi_win"].reshape(-1)
    mapped = np.array([p2i.get(int(p), -1) if p != PAD else -1 for p in flat],
                      np.int64).reshape(ctx["poi_win"].shape)
    poi_t = torch.from_numpy(mapped).to(device)
    usr_all = torch.from_numpy(user_compact).to(device)
    cat_y_t = torch.from_numpy(ctx["cat_y"]).to(device)
    reg_y_t = torch.from_numpy(ctx["region_y"]).to(device)

    model = POI2VecE2E(body, ctx["n_regions"], ctx["n_cats"]).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.head_lr, weight_decay=0.01)
    ce = nn.CrossEntropyLoss()

    tr = torch.as_tensor(train_idx, device=device, dtype=torch.long)
    va = torch.as_tensor(val_idx, device=device, dtype=torch.long)
    bs = args.batch_size
    head_epochs = args.head_epochs
    for ep in range(head_epochs):
        model.train()
        perm = tr[torch.randperm(tr.numel(), device=device)]
        for s in range(0, perm.numel(), bs):
            b = perm[s:s + bs]
            cl, rl = model(poi_t[b], usr_all[b])
            loss = ce(cl, cat_y_t[b]) + ce(rl, reg_y_t[b])  # equal-weight CE
            opt.zero_grad()
            loss.backward()
            opt.step()

    # --- eval (matched metrics; val never updates a parameter) ---
    model.eval()
    # STREAMED reg metric. The full [n_val, n_regions] logit is ~20 GB at california (8501
    # regions) / texas (6553) — this used to cat it whole and would simply OOM there. Every
    # quantity the OOD block needs (top-k hit, strict-`>` rank, target) is per-ROW, so the
    # accumulators are O(N) and the result is identical: `_ood_from_streamed` is the same
    # computation `_ood_restricted_topk` performs, on the same numbers. Masking after the fact
    # is equivalent to masking first, because top-k of row i does not depend on any other row.
    # cat stays on the full path — 7-8 classes, the buffer is nothing.
    cls = []
    reg_acc = StreamingClsMetrics(ctx["n_regions"], top_k=(1, 5, 10), diagnose_ties=True)
    with torch.no_grad():
        for s in range(0, va.numel(), bs):
            b = va[s:s + bs]
            cl, rl = model(poi_t[b], usr_all[b])
            cls.append(cl)
            reg_acc.update(rl, reg_y_t[b])
    cat_logits = torch.cat(cls)
    cat_tgt = cat_y_t[va]

    cat_metrics = compute_classification_metrics(cat_logits, cat_tgt, num_classes=ctx["n_cats"])
    train_region_labels = set(int(r) for r in ctx["region_y"][train_idx])
    _, _rt, _rr, _rh = reg_acc.concat()
    reg_ood = _ood_from_streamed(_rt, _rr, _rh, train_region_labels)

    cat_f1 = float(cat_metrics["f1"])
    reg_top10 = float(reg_ood["top10_acc_indist"])
    geom = math.sqrt(max(cat_f1, 0.0) * max(reg_top10, 0.0))
    return {
        "cat_f1": cat_f1,
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
        "n_cbow_examples": int(n),
    }


def main():
    ap = argparse.ArgumentParser(description="POI2Vec (AAAI'17) NATIVE-E2E baseline")
    ap.add_argument("--state", default="alabama")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--folds", type=int, default=5,
                    help="how many of the 5-split folds to RUN (partition is always 5-split)")
    ap.add_argument("--only-fold", type=int, default=None,
                    help="run ONLY fold k (0..4) of the SAME 5-split partition (board pattern)")
    ap.add_argument("--epochs", type=int, default=20, help="POI2Vec body pretrain epochs (train-only)")
    ap.add_argument("--head-epochs", type=int, default=20, help="supervised head/e2e epochs")
    ap.add_argument("--batch-size", type=int, default=2048, help="supervised head batch size")
    ap.add_argument("--pretrain-batch", type=int, default=1024, help="POI2Vec CBOW batch size")
    ap.add_argument("--dim", type=int, default=64, help="MATCHED to board (paper:200)")
    ap.add_argument("--head-lr", type=float, default=1e-3)
    ap.add_argument("--pretrain-lr", type=float, default=0.025)
    ap.add_argument("--context-window", type=int, default=9)
    ap.add_argument("--theta", type=float, default=0.05, help="midpoint-tree leaf cell size (deg)")
    ap.add_argument("--route-count", type=int, default=4, help="max leaves/POI by overlap area")
    ap.add_argument("--n-neg-user", type=int, default=5, help="negative-sampled user softmax k")
    ap.add_argument("--loss-form", choices=["mixture", "noisy_or"], default="mixture",
                    help="mixture=stable -log(sum phi*pr_path); noisy_or=paper exact")
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--smoke", action="store_true",
                    help="tiny AL run: fold 0, 2 pretrain + 2 head epochs, dim 32")
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    if args.smoke:
        args.state = "alabama"
        args.only_fold = 0
        args.folds = 1
        args.epochs = 2
        args.head_epochs = 2
        args.dim = 32
        args.seed = 0

    device = torch.device(args.device)
    print(f"[{ENGINE_NAME}] state={args.state} seed={args.seed} engine={ENGINE.value} "
          f"folds={args.folds} only_fold={args.only_fold} "
          f"pretrain_epochs={args.epochs} head_epochs={args.head_epochs} "
          f"dim={args.dim} theta={args.theta} loss_form={args.loss_form} device={device}")

    # --- board fold split (BIT-IDENTICAL to the champion; ALWAYS 5 splits) ---
    from sklearn.model_selection import StratifiedGroupKFold
    X, y_cat, userids, _ = load_next_data(args.state, ENGINE)
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=args.seed)
    splits = list(sgkf.split(X, y_cat, groups=userids))

    ctx = build_context(args.state)
    seq_df = pd.read_parquet(IoPaths.get_seq_next(args.state, ENGINE))
    assert len(ctx["region_y"]) == len(X), (len(ctx["region_y"]), len(X))
    print(f"[{ENGINE_NAME}] rows={len(X)} n_poi={ctx['n_poi']} "
          f"n_regions={ctx['n_regions']} n_cats={ctx['n_cats']}")

    # which folds to run: --only-fold k overrides; else first --folds of the 5
    if args.only_fold is not None:
        assert 0 <= args.only_fold < 5, args.only_fold
        run_folds = [args.only_fold]
    else:
        run_folds = list(range(min(args.folds, 5)))

    results = []
    t0 = time.time()
    for fold_idx in run_folds:
        train_idx, val_idx = splits[fold_idx]
        r = run_fold(ctx, seq_df, train_idx, val_idx, args, device)
        r["fold"] = fold_idx + 1
        results.append(r)
        print(f"[fold {fold_idx + 1}] cat_f1={r['cat_f1']:.4f} "
              f"reg_top10_acc_indist={r['reg_top10_acc_indist']:.4f} "
              f"geom_simple={r['geom_simple']:.4f} "
              f"(train_users={r['n_train_users']} val_users={r['n_val_users']} "
              f"cbow={r['n_cbow_examples']:,})")

    agg = {
        "engine": ENGINE_NAME,
        "base_engine": ENGINE.value,
        "baseline": "poi2vec_aaai2017_native_e2e",
        "state": args.state,
        "seed": args.seed,
        "folds_run": [r["fold"] for r in results],
        "epochs_pretrain": args.epochs,
        "epochs_head": args.head_epochs,
        "dim": args.dim,
        "theta": args.theta,
        "route_count": args.route_count,
        "loss_form": args.loss_form,
        "cat_f1_mean": float(np.mean([r["cat_f1"] for r in results])) if results else 0.0,
        "reg_top10_acc_indist_mean": float(np.mean([r["reg_top10_acc_indist"] for r in results])) if results else 0.0,
        "geom_simple_mean": float(np.mean([r["geom_simple"] for r in results])) if results else 0.0,
        "per_fold": results,
        "wall_seconds": round(time.time() - t0, 1),
        "smoke": args.smoke,
        "windowing": "stride-1 OVERLAP (check2hgi_dk_ovl) — AL=96,326 rows",
    }

    out_dir = Path(args.out_dir) if args.out_dir else (RESULTS_ROOT / ENGINE_NAME / args.state.lower())
    out_dir.mkdir(parents=True, exist_ok=True)
    if args.smoke:
        tag = "smoke"
    elif args.only_fold is not None:
        tag = f"seed{args.seed}_fold{args.only_fold}"
    else:
        tag = f"seed{args.seed}"
    out_path = out_dir / f"poi2vec_e2e_{tag}.json"
    out_path.write_text(json.dumps(agg, indent=2))
    print(f"[{ENGINE_NAME}] cat_f1_mean={agg['cat_f1_mean']:.4f} "
          f"reg_top10_acc_indist_mean={agg['reg_top10_acc_indist_mean']:.4f} "
          f"geom_simple_mean={agg['geom_simple_mean']:.4f}")
    print(f"[{ENGINE_NAME}] wrote {out_path}")


if __name__ == "__main__":
    main()
