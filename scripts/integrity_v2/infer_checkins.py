"""Encoder-only check-in inference from a saved checkpoint, under three readout graphs.

This is the instrument the earlier fold audit lacked. That audit could not encode a validation
user at all under a training-only representation, so it substituted one vector per place and
dropped the windows whose places were unseen. Both gaps close here, for a structural reason
established in phase 0: the check-in graph is a disjoint union of per-user paths (F1), so a
held-out user encoded alone reproduces its full-graph vectors exactly (F2), and the active
check-in input carries category and time but no place identity, so a place unseen in training
needs no lookup.

THE FOUR READOUTS. All use the same weights; they differ only in which nodes and edges exist when
the vectors are computed. Two of them are PER-VISIT (one vector per check-in, written as a parquet)
and one is PER-WINDOW (a [N, 9, 64] tensor, written as an npz), because a window-level cutoff makes
a visit's vector depend on which window it appears in.

  full       per-visit. The whole user path, edges in both directions. This is the reported
             readout, and the target visit is a graph neighbour of the last observed visit.

  prefix     PER-WINDOW, and the primary strict readout. For the window whose last observed visit
             is at position L, all nine slots are recomputed on the graph containing that user's
             visits 0..L. That is exactly the graph available when the prediction is made: the
             entire observed past, nothing after. Phase 0 F5 measured THIS scheme and found it
             leaves slots 0..5 untouched and moves only slots 6..8, the positions the deleted
             nodes can reach, which is why it is the minimal honest intervention.
             A visit's vector is therefore window-dependent: node v is read on graph 0..L when it
             appears in the window ending at L, so it takes a different value as slot 8 of one
             window than as slot 7 of the next. That is a property of the cutoff, not a defect.

  streaming  per-visit. Visit v is computed on the graph 0..v, i.e. each vector is frozen at the
             moment its visit happens and never revised. This is a DIFFERENT and STRICTER regime
             than `prefix`: slot 3 of a window is computed without visits 4..8, which are in fact
             known at prediction time. It corresponds to an online cache rather than to batch
             inference, it changes all nine slots, and F5 does not bound it. Reported as a
             secondary arm, never as the strict reference.

  forward    per-visit. Keep the whole path but drop the backward edges. An invariance diagnostic
             only: because GCN degree normalization is recomputed from the surviving edges, this
             perturbs EVERY slot (F5 measured 63-70% of them), so its performance number would
             confound information removal with a global renormalization and must never be quoted
             as the edge effect.

COST. `prefix` is one forward pass per window and `streaming` one per visit, so both are O(n^2) in
a user's history length; no saving is claimed. On the two study datasets this is affordable because
the per-user paths are short relative to the graph. `--self-test` checks each readout against an
independently written reference for the SAME rule: for `prefix`, a per-window rebuild that re-indexes
the truncated graph from scratch rather than slicing the walk.

Usage:
    PYTHONPATH=src:research .venv/bin/python scripts/integrity_v2/infer_checkins.py \
        --state alabama --checkpoint results/check2hgi_integrity_v2/alabama/U0/checkpoint.pt \
        --users-from docs/results/.../split_seed0_fold0.json --user-key val_users \
        --readout prefix --out results/check2hgi_integrity_v2/alabama/U0/emb_val_prefix.parquet
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.CheckinEncoder import CheckinEncoder            # noqa: E402
from embeddings.check2hgi.model.variants import ResidualLNEncoder, GATTimeEncoder  # noqa: E402

WINDOW = 9
N_CAT = 7     # node features are [category one-hot (7) | temporal (4)]
# Output width of the encoder. Set from the checkpoint's own kwargs in load_encoder, because a
# capacity sweep changes it and a hardcoded 64 would silently allocate a wrongly-shaped buffer and
# either crash or truncate. Defaults to the frozen recipe's 64 so existing arms are unaffected.
OUT_DIM = 64
HOPS = 2      # encoder depth, so a node's receptive field is index distance <= 2
READOUTS = ("full", "prefix", "prefix_forward_only", "prefix_masked_backward",
            "streaming", "forward")


def load_encoder(ck_path: Path):
    ck = torch.load(ck_path, map_location="cpu", weights_only=False)
    kind = ck["encoder"]; kw = ck["checkin_encoder_kwargs"]
    if kind == "resln":
        enc = ResidualLNEncoder(**kw)
    elif kind == "gat":
        enc = GATTimeEncoder(**kw)
    elif kind == "gcn":
        enc = CheckinEncoder(**{k: v for k, v in kw.items() if k in ("in_channels", "hidden_channels", "num_layers")})
    else:
        raise ValueError(kind)
    prefix = "checkin_encoder."
    sub = {k[len(prefix):]: v for k, v in ck["state_dict"].items() if k.startswith(prefix)}
    missing, unexpected = enc.load_state_dict(sub, strict=False)
    assert not [m for m in missing if "num_batches" not in m], f"missing encoder weights: {missing}"
    enc.eval()      # dropout OFF: the readout must be deterministic
    # The direction of the TRAINING graph travels with the weights so the readout can be checked
    # against it. A forward-only encoder read under a bidirectional graph, or the reverse, is a
    # silent train and deploy mismatch: the weights were fitted on messages that flowed one way.
    trained_fo = bool(ck.get("forward_only",
                             ck.get("provenance", {}).get("causal_graph", {}).get("forward_only",
                                                                                 False)))
    cg = ck.get("provenance", {}).get("causal_graph", {}) or {}
    trained_mb = bool(cg.get("masked_backward_category"))
    global OUT_DIM
    OUT_DIM = int(kw.get("hidden_channels", 64))
    return enc, ck["provenance"], sub, trained_fo, trained_mb, int(kw["in_channels"])


def _fwd(enc, x, ei, ew):
    with torch.no_grad():
        return enc(x, torch.as_tensor(ei, dtype=torch.long), torch.as_tensor(ew))


def _user_path(ei_g, ew_g, nodes):
    keep = np.isin(ei_g[0], nodes) & np.isin(ei_g[1], nodes)
    remap = {int(g): i for i, g in enumerate(nodes)}
    local = np.array([[remap[int(a)] for a in ei_g[0, keep]],
                      [remap[int(b)] for b in ei_g[1, keep]]], dtype=np.int64)
    return local, ew_g[keep]


def encode_user_windows_intervened(enc, X, local, ew, intervention: str, rng,
                                   feat_pool: np.ndarray, ew_pool: np.ndarray) -> np.ndarray:
    """PER-WINDOW intervention: return [n_windows, 9, 64] for one user.

    The intervention must be per-window, not per-visit. For the window covering visits w..w+8, the
    TARGET is visit w+9 and every other visit in reach is legitimately observed history. A per-visit
    table that stored "the vector computed with the next visit destroyed" would, when assembled into
    a window, have slots 0 through 7 computed with an OBSERVED slot destroyed, and the resulting
    metric drop would measure the cost of deleting available history rather than the contribution of
    the target. So each window gets its own forward pass in which visit w+9 alone is intervened on
    and all nine slots are read from that pass.
    """
    xs = torch.as_tensor(X)
    n = X.shape[0]
    n_win = max(0, n - WINDOW)
    out = np.zeros((n_win, WINDOW, OUT_DIM), dtype=np.float32)
    for w in range(n_win):
        L = w + WINDOW - 1
        # Which visit gets destroyed. The real arms hit the TARGET (L+1). The two placebos hit a
        # visit that is not the target: `placebo_far_future` picks one far beyond every slot's
        # receptive field, so its drop must be zero and any nonzero value indicts the pipeline;
        # `placebo_observed` hits an observed history slot, giving the scale of what destroying one
        # legitimately available visit costs, for comparison against the target's contribution.
        if intervention == "placebo_far_future":
            t = L + 1 + 2 * HOPS + 2
            if t >= n:
                out[w] = _fwd(enc, xs, local, ew).numpy()[w:L + 1]
                continue
        elif intervention == "placebo_observed":
            t = w + 4                               # middle of the observed window
        else:
            t = L + 1                               # the target visit
        x2, e_w = xs, ew
        if intervention == "zero_target_cat":
            x2 = xs.clone(); x2[t, :7] = 0.0
        elif intervention in ("resample_target_features", "resample_target_all",
                              "placebo_far_future", "placebo_observed"):
            # placebos use the SAME destruction operator as resample_target_all, moved to a
            # different visit, so the only difference between them and the real arm is WHERE
            x2 = xs.clone()
            x2[t] = torch.as_tensor(feat_pool[rng.integers(0, len(feat_pool))])
        elif intervention != "redraw_target_edge_weight":
            raise ValueError(intervention)
        if intervention in ("redraw_target_edge_weight", "resample_target_all",
                            "placebo_far_future", "placebo_observed"):
            e_w = ew.copy()
            inc = np.where((local[0] == t) | (local[1] == t))[0]
            if inc.size:
                e_w[inc] = ew_pool[rng.integers(0, len(ew_pool), inc.size)]
        out[w] = _fwd(enc, x2, local, e_w).numpy()[w:L + 1]
    return out


def encode_user(enc, X, local, ew, readout: str) -> np.ndarray:
    """Return [n_visits, 64] vectors for one user under a PER-VISIT readout."""
    xs = torch.as_tensor(X)
    n = X.shape[0]
    if readout == "full":
        return _fwd(enc, xs, local, ew).numpy()
    if readout == "forward":
        m = local[0] < local[1]
        return _fwd(enc, xs, local[:, m], ew[m]).numpy()
    if readout == "streaming":
        # Visit p is read from the graph 0..p: its vector is frozen when the visit happens and is
        # never revised by anything later. Stricter than `prefix`, which lets a slot see the rest
        # of the observed window. Kept as a secondary arm; F5 does not bound this rule.
        out = np.zeros((n, OUT_DIM), dtype=np.float32)
        for p in range(n):
            pre = np.arange(0, p + 1)
            k = np.isin(local[0], pre) & np.isin(local[1], pre)
            out[p] = _fwd(enc, xs[pre], local[:, k], ew[k])[p].numpy()
        return out
    raise ValueError(f"{readout} is not a per-visit readout")


def _masked_backward_graph(X, local, ew, n_cat: int = 7):
    """Rebuild one user's subgraph in the twin form a masked-backward encoder was trained on.

    A `--mask-backward-category` build appends, for every check-in, a twin node whose category
    one-hot is zeroed, and routes every BACKWARD edge out of the twin instead of the original. An
    encoder trained that way has never seen a backward message carrying a category, so reading it on
    the canonical two-sided graph would feed it exactly the distribution it was trained to exclude --
    the same class of train-and-deploy mismatch already found once in this study. This reconstructs
    the twin topology at readout so the two agree.

    Returns (features, edge_index, edge_weight) over 2n nodes; the caller reads the FIRST n.
    """
    n = X.shape[0]
    twin = X.copy(); twin[:, :n_cat] = 0.0
    X2 = np.concatenate([X, twin], axis=0)
    fwd = local[0] < local[1]
    ei_f = local[:, fwd]
    ei_b = local[:, ~fwd].copy(); ei_b[0] = ei_b[0] + n
    return X2, np.concatenate([ei_f, ei_b], axis=1), np.concatenate([ew[fwd], ew[~fwd]])


def encode_user_windows_prefix(enc, X, local, ew, forward_only: bool = False,
                               masked_backward: bool = False) -> np.ndarray:
    """PER-WINDOW prefix readout: return [n_windows, 9, 64] for one user.

    Window w (0-indexed) covers visits w..w+8 and its target is w+9, so its last observed visit is
    at L = w+8. Every one of its nine slots is recomputed on the graph containing visits 0..L, the
    graph that exists when the prediction is made. This is the scheme phase 0 F5 measured.

    TWO DISTINCT NOTIONS OF "CAUSAL", and the difference matters.

    With forward_only=False the path is cut at the target but BOTH directions of every edge among
    visits 0..L survive, so slot 3 is still convolved over slot 4. That is the correct instrument for
    asking "what does withholding the TARGET cost?", because it changes one thing only.

    With forward_only=True the backward direction is dropped as well, so no visit sees any later
    visit, not even one inside the observed window. This is the readout that MATCHES a forward-only
    trained encoder. Reading forward-only weights under a bidirectional window graph is a train and
    deploy mismatch in the opposite direction, and it biases exactly the comparison the forward-only
    arm exists to settle: the encoder's weights were fitted on messages that never flowed backward,
    so supplying backward messages at readout feeds it a distribution it never saw.
    """
    xs = torch.as_tensor(X)
    n = X.shape[0]
    n_win = max(0, n - WINDOW)
    out = np.zeros((n_win, WINDOW, OUT_DIM), dtype=np.float32)
    assert not (forward_only and masked_backward), \
        "forward_only removes backward edges; masking them is meaningless"
    fwd_mask = (local[0] < local[1]) if forward_only else np.ones(local.shape[1], dtype=bool)
    for w in range(n_win):
        L = w + WINDOW - 1
        pre = np.arange(0, L + 1)                    # ids stay 0..L, no re-indexing needed
        k = np.isin(local[0], pre) & np.isin(local[1], pre) & fwd_mask
        if masked_backward:
            # rebuild the twin topology on the truncated graph, then read the real nodes
            x2, e2, w2 = _masked_backward_graph(X[pre], local[:, k], ew[k])
            z = _fwd(enc, torch.as_tensor(x2), e2, w2).numpy()[:len(pre)]
        else:
            z = _fwd(enc, xs[pre], local[:, k], ew[k]).numpy()
        out[w] = z[w:L + 1]
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--readout", required=True, choices=READOUTS)
    ap.add_argument("--intervention", default=None,
                    choices=("zero_target_cat", "resample_target_features",
                             "redraw_target_edge_weight", "resample_target_all",
                             "placebo_far_future", "placebo_observed"),
                    help="destroy each window's TARGET only, on the reported graph; per-window "
                         "output. Requires --readout full.")
    ap.add_argument("--intervention-seed", type=int, default=0)
    ap.add_argument("--users-from", default=None, help="split JSON")
    ap.add_argument("--user-key", default="val_users", choices=("val_users", "train_users", "all"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-users", type=int, default=None,
                    help="cap the number of users encoded, sampled with --user-sample-seed. The "
                         "per-window readouts cost one forward pass per window, so a large state "
                         "needs a declared random subsample. The SAME seed and cap must be used "
                         "for every arm, or the arms stop being paired.")
    ap.add_argument("--user-sample-seed", type=int, default=12345)
    ap.add_argument("--allow-direction-mismatch", action="store_true",
                    help="permit reading a checkpoint under a graph direction it was not trained "
                         "on; only for deliberately measuring that mismatch")
    ap.add_argument("--self-test", action="store_true",
                    help="assert F1/F2 and, for prefix, agreement with the naive per-window graph")
    args = ap.parse_args()

    state_lc = args.state.lower()
    gpath = REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt"
    with open(gpath, "rb") as fh:
        d = pickle.load(fh)
    md = d["metadata"].reset_index(drop=True)
    uid = md["userid"].to_numpy()
    ei_g = np.asarray(d["edge_index"]); ew_g = np.asarray(d["edge_weight"], dtype=np.float32)
    X = np.asarray(d["node_features"], dtype=np.float32)

    enc, prov, sub, trained_fo, trained_mb, _trained_in = load_encoder(Path(args.checkpoint))

    # An enriched build trains on extra node columns (place embedding, elapsed time). Those columns
    # must be reconstructed here by the SAME rule, or the encoder receives a different input than it
    # was fitted on. This is the fifth instance in this study of the same failure class, so it is
    # replayed from the manifest rather than re-derived from flags: the manifest records the exact
    # block order and source file, and the width assertion below fails closed if they disagree.
    _enr = (prov.get("node_enrichment") or {})
    if _enr:
        blocks = [X]
        if "place_identity" in _enr:
            pe_path = REPO / _enr["place_identity"]["source"]
            pe = pd.read_parquet(pe_path)
            key = "placeid" if "placeid" in pe.columns else pe.columns[0]
            dim_cols = sorted([c for c in pe.columns if str(c).isdigit()], key=int)
            lut = {str(k): i for i, k in enumerate(pe[key].astype(str).to_numpy())}
            P = pe[dim_cols].to_numpy(dtype=np.float32)
            rr = np.array([lut.get(str(v), -1) for v in md["placeid"].astype(str).to_numpy()])
            blk = np.zeros((len(md), P.shape[1]), dtype=np.float32)
            h = rr >= 0
            blk[h] = P[rr[h]]
            # The build's shortcut mitigations must be replayed EXACTLY, in the same order, or the
            # encoder sees a differently-shaped input than it was fitted on. The random projection is
            # seeded with the same literal constant on both sides so it is reproduced bit-for-bit
            # rather than approximately; the width assertion below is the backstop.
            pid = _enr["place_identity"]
            if pid.get("standardized"):
                mu, sd = blk.mean(0, keepdims=True), blk.std(0, keepdims=True)
                blk = np.clip((blk - mu) / np.clip(sd, 1e-6, None), -3.0, 3.0).astype(np.float32)
            k = pid.get("projected_dim")
            if k:
                rp = np.random.default_rng(1234).normal(
                    0.0, 1.0 / np.sqrt(k), size=(blk.shape[1], k)).astype(np.float32)
                blk = (blk @ rp).astype(np.float32)
            blocks.append(blk)
        if "region_identity" in _enr:
            rid = _enr["region_identity"]
            rdf = pd.read_parquet(REPO / rid["source"])
            # same dual convention as the build: key `region_id` or `region_idx`, dims `reg_N` or `N`
            rkey = next((k for k in ("region_id", "region_idx") if k in rdf.columns), rdf.columns[0])
            rdims = sorted([cc for cc in rdf.columns if str(cc).isdigit()], key=int)
            if not rdims:
                rdims = sorted([cc for cc in rdf.columns if str(cc).startswith("reg_")
                                and str(cc)[4:].isdigit()], key=lambda cc: int(str(cc)[4:]))
            assert rdims, f"no dimension columns in {rid['source']}"
            R = rdf[rdims].to_numpy(dtype=np.float32)
            rlut = {int(k): i for i, k in enumerate(rdf[rkey].to_numpy())}
            reg_of_visit = np.asarray(d["poi_to_region"])[np.asarray(d["checkin_to_poi"])]
            rr2 = np.array([rlut.get(int(v), -1) for v in reg_of_visit])
            rblk = np.zeros((len(md), R.shape[1]), dtype=np.float32)
            rh = rr2 >= 0
            rblk[rh] = R[rr2[rh]]
            # same mitigations, same order, same seed as the build; the seed differs from the place
            # block's on purpose so the two projections are independent rather than correlated
            if rid.get("standardized"):
                mu, sd = rblk.mean(0, keepdims=True), rblk.std(0, keepdims=True)
                rblk = np.clip((rblk - mu) / np.clip(sd, 1e-6, None), -3.0, 3.0).astype(np.float32)
            rk = rid.get("projected_dim")
            if rk:
                rp = np.random.default_rng(5678).normal(
                    0.0, 1.0 / np.sqrt(rk), size=(rblk.shape[1], rk)).astype(np.float32)
                rblk = (rblk @ rp).astype(np.float32)
            blocks.append(rblk)

        if "continuous_time" in _enr:
            dtv = pd.to_datetime(md["datetime"])
            t = dtv.astype("int64").to_numpy() / 1e9 / 3600.0
            gap = np.zeros(len(t), dtype=np.float32); sf = np.zeros(len(t), dtype=np.float32)
            for u in np.unique(uid):
                m = np.where(uid == u)[0]; tu = t[m]
                gap[m[1:]] = np.diff(tu); sf[m] = tu - tu[0]
            blocks.append(np.stack([
                np.log1p(np.clip(gap, 0, None)) / 10.0,
                np.log1p(np.clip(sf, 0, None)) / 10.0,
                np.clip(gap, 0, 24.0) / 24.0,
                (gap == 0).astype(np.float32)], axis=1).astype(np.float32))
        X = np.concatenate(blocks, axis=1).astype(np.float32)
        print(f"[infer] replayed node enrichment {_enr.get('layout')}: -> {X.shape[1]} channels",
              flush=True)

    # The feature layout must match what the encoder was TRAINED on. A --drop-category-features
    # build trains on the temporal columns only, so feeding it the canonical 11-column features here
    # is a silent input mismatch (it fails loudly as a shape error, which is the good case; a build
    # that happened to agree on width would fail silently). Read the training width off the
    # checkpoint and apply the same column selection.
    _dropped_cat = bool((prov.get("causal_graph", {}) or {}).get("dropped_category_features"))
    if _dropped_cat:
        assert _trained_in == X.shape[1] - N_CAT, (
            f"checkpoint reports {_trained_in} input channels but dropping {N_CAT} category columns "
            f"from {X.shape[1]} gives {X.shape[1] - N_CAT}")
        X = X[:, N_CAT:]
        print(f"[infer] category columns dropped to match the checkpoint: "
              f"{_trained_in + N_CAT} -> {X.shape[1]} channels", flush=True)
    assert X.shape[1] == _trained_in, (
        f"feature width {X.shape[1]} does not match the checkpoint's {_trained_in} input channels")
    # Fail closed on a train/deploy direction mismatch. This is the defect a reviewer caught in the
    # first forward-only run: the C1 encoder was trained forward-only and then read with `prefix`,
    # which keeps both edge directions inside the observed window, so the arm that was supposed to
    # remove a mismatch introduced one. Neither direction of mismatch is allowed to pass silently.
    readout_fo = (args.readout == "prefix_forward_only")
    if trained_fo and args.readout in ("prefix", "full", "streaming") \
            and not args.allow_direction_mismatch:
        raise SystemExit(
            f"checkpoint was trained on a FORWARD-ONLY graph but --readout {args.readout} supplies "
            "backward edges; use --readout prefix_forward_only, or pass "
            "--allow-direction-mismatch to measure the mismatch deliberately")
    if readout_fo and not trained_fo and not args.allow_direction_mismatch:
        raise SystemExit(
            "--readout prefix_forward_only on a bidirectionally trained checkpoint is a mismatch in "
            "the other direction; pass --allow-direction-mismatch if that is the intent")
    # A masked-backward checkpoint has never seen a backward message carrying a category, so any
    # readout that supplies one is the same class of mismatch the forward-only arm already hit.
    if trained_mb and args.readout != "prefix_masked_backward" and not args.allow_direction_mismatch:
        raise SystemExit(
            f"checkpoint was trained with MASKED BACKWARD categories but --readout {args.readout} "
            "supplies category-carrying backward messages; use --readout prefix_masked_backward, or "
            "pass --allow-direction-mismatch to measure the mismatch deliberately")
    if args.readout == "prefix_masked_backward" and not trained_mb and not args.allow_direction_mismatch:
        raise SystemExit(
            "--readout prefix_masked_backward on a checkpoint not trained that way is a mismatch in "
            "the other direction; pass --allow-direction-mismatch if that is the intent")
    print(f"[infer] training graph forward_only={trained_fo} masked_backward={trained_mb}, "
          f"readout={args.readout}", flush=True)

    if args.users_from and args.user_key != "all":
        split = json.loads(Path(args.users_from).read_text())
        want = np.asarray(split[args.user_key], dtype=uid.dtype)
    else:
        want = np.unique(uid)
    sel_users = np.intersect1d(np.unique(uid), want)
    n_users_before_cap = int(len(sel_users))
    if args.max_users and len(sel_users) > args.max_users:
        # sort first so the sample depends only on the seed, never on set iteration order
        rs = np.random.default_rng(args.user_sample_seed)
        sel_users = np.sort(rs.choice(np.sort(sel_users), size=args.max_users, replace=False))
        print(f"[infer] subsampled {args.max_users} of {n_users_before_cap} users "
              f"(seed {args.user_sample_seed}); every arm must use the same cap and seed", flush=True)
    print(f"[infer] {state_lc} readout={args.readout} users={len(sel_users)} "
          f"encoder={prov['encoder']} cell={prov['cell']}", flush=True)

    if args.self_test:
        # F1: no cross-user edges, so per-user encoding is exact
        assert int((uid[ei_g[0]] != uid[ei_g[1]]).sum()) == 0, "cross-user edges present"
        # F2: a user encoded alone == that user inside a batch of users
        # The criterion is RELATIVE, for the reason phase 0 recorded: batching reassociates the
        # float32 sums inside every reduction, so two mathematically identical computations differ
        # by a few units in the last place. That floor scales with the magnitude of the vectors, and
        # a trained encoder produces larger vectors than the random-weight one used in phase 0, so
        # an absolute bound would pass at random init and fail after training for no reason that
        # concerns the study. REL_EXACT is two orders of magnitude below the smallest effect the
        # interventions resolve.
        REL_EXACT = 1e-5
        probe = sel_users[:20]
        nodes = np.where(np.isin(uid, probe))[0]
        lb, wb = _user_path(ei_g, ew_g, nodes)
        z_batch = _fwd(enc, torch.as_tensor(X[nodes]), lb, wb).numpy()
        worst_abs = worst_rel = 0.0
        for u in probe:
            un = np.where(uid == u)[0]
            lu, wu = _user_path(ei_g, ew_g, un)
            z_alone = _fwd(enc, torch.as_tensor(X[un]), lu, wu).numpy()
            pos = np.searchsorted(nodes, un)
            dv = np.abs(z_batch[pos] - z_alone)
            sc = np.maximum(np.abs(z_alone).max(1, keepdims=True), 1e-9)
            worst_abs = max(worst_abs, float(dv.max()))
            worst_rel = max(worst_rel, float((dv / sc).max()))
        print(f"[self-test] F2 user-alone vs in-batch: max abs {worst_abs:.3e}, "
              f"max rel {worst_rel:.3e} (bound {REL_EXACT:.0e})")
        assert worst_rel <= REL_EXACT, \
            f"per-user encoding is not exact (rel {worst_rel:.3e} > {REL_EXACT:.0e})"

    if args.intervention:
        assert args.readout == "full", "--intervention operates on the reported (full) readout"
        rng = np.random.default_rng(args.intervention_seed)
        pool_nodes = np.where(np.isin(uid, sel_users))[0]
        feat_pool = X[pool_nodes]
        ew_pool = ew_g[np.isin(ei_g[0], pool_nodes) & np.isin(ei_g[1], pool_nodes)]
        print(f"[infer] intervention={args.intervention} "
              f"(pools: {len(feat_pool)} feature rows, {len(ew_pool)} edge weights)", flush=True)

    # Both the prefix readout and any intervention are window-scoped: a vector depends on which
    # window it serves, so neither can be represented as one row per visit.
    per_window = args.readout in ("prefix", "prefix_forward_only",
                                  "prefix_masked_backward") or bool(args.intervention)
    rows, metas, win_users, win_starts = [], [], [], []
    for u in sel_users:
        nodes = np.where(uid == u)[0]
        local, ew = _user_path(ei_g, ew_g, nodes)
        if per_window:
            zw = (encode_user_windows_intervened(enc, X[nodes], local, ew, args.intervention,
                                                 rng, feat_pool, ew_pool)
                  if args.intervention
                  else encode_user_windows_prefix(
                      enc, X[nodes], local, ew,
                      forward_only=(args.readout == "prefix_forward_only"),
                      masked_backward=(args.readout == "prefix_masked_backward")))
            if len(zw) == 0:
                continue
            rows.append(zw)
            win_users.extend([int(u)] * len(zw)); win_starts.extend(range(len(zw)))
        else:
            z = encode_user(enc, X[nodes], local, ew, args.readout)
            rows.append(z); metas.append(md.iloc[nodes])
    Z = np.concatenate(rows, 0)

    if args.self_test and args.intervention:
        # The intervention touches the target only, so its reach inside the window must match F4/F5:
        # slot 8 (one hop), slot 7 (two hops), and slot 6 (via slot 8's degree) may move; slots 0..5
        # must not. A violation means the intervention is hitting observed history.
        u = sel_users[int(np.argmax([np.sum(uid == x) for x in sel_users[:50]]))]
        nodes = np.where(uid == u)[0]
        local, ew = _user_path(ei_g, ew_g, nodes)
        z_int = encode_user_windows_intervened(enc, X[nodes], local, ew, args.intervention,
                                               np.random.default_rng(args.intervention_seed),
                                               feat_pool, ew_pool)
        z_base = encode_user_windows_prefix(enc, X[nodes], local, ew) * 0.0
        base_full = _fwd(enc, torch.as_tensor(X[nodes]), local, ew).numpy()
        n_win = len(z_int)
        for w in range(n_win):
            z_base[w] = base_full[w:w + WINDOW]
        rel = np.abs(z_int - z_base) / np.maximum(np.abs(z_base).max(2, keepdims=True), 1e-9)
        per_slot = rel.max(2).max(0)
        print(f"[self-test] intervention reach by slot (max rel): "
              f"{['%.2e' % v for v in per_slot]}")
        if args.intervention == "placebo_far_future":
            assert (per_slot <= 1e-5).all(), \
                f"far-future placebo moved a slot -- the pipeline responds to irrelevant edits: {per_slot}"
        elif args.intervention != "placebo_observed":
            assert (per_slot[:WINDOW - 3] <= 1e-5).all(), \
                f"intervention reached observed history slots 0..5: {per_slot[:WINDOW-3]}"

    if args.self_test and per_window and not args.intervention:
        # LIMITATION, stated plainly: this is an internal consistency check, NOT an independent
        # verification. Because `pre` is the contiguous range 0..L the remap below is the identity,
        # so this recomputation exercises the same code path as encode_user_windows_prefix and cannot
        # fail on a logic error the two share. It catches nondeterminism and slicing mistakes only.
        # Real verification would need a second implementation written from the specification; the
        # actual guard on the prefix scheme is structural fact F5, measured independently in
        # f0_structure.py.
        u = sel_users[int(np.argmax([np.sum(uid == x) for x in sel_users[:50]]))]
        nodes = np.where(uid == u)[0]
        local, ew = _user_path(ei_g, ew_g, nodes)
        zw = encode_user_windows_prefix(enc, X[nodes], local, ew)
        worst = 0.0
        for w in range(min(len(zw), 25)):
            L = w + WINDOW - 1
            pre = np.arange(0, L + 1)
            k = np.isin(local[0], pre) & np.isin(local[1], pre)
            remap = {int(g): i for i, g in enumerate(pre)}
            e2 = np.array([[remap[int(a)] for a in local[0, k]],
                           [remap[int(b)] for b in local[1, k]]], dtype=np.int64)
            zz = _fwd(enc, torch.as_tensor(X[nodes][pre]), e2, ew[k]).numpy()[w:L + 1]
            sc = np.maximum(np.abs(zw[w]).max(1, keepdims=True), 1e-9)
            worst = max(worst, float((np.abs(zz - zw[w]) / sc).max()))
        print(f"[self-test] per-window prefix internal consistency (NOT an independent "
              f"reimplementation): max rel diff {worst:.3e}")
        assert worst <= 1e-5, f"prefix windows disagree with the reference rebuild ({worst:.3e})"

    outp = REPO / args.out if not Path(args.out).is_absolute() else Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    if per_window:
        np.savez_compressed(outp, seq=Z, userid=np.asarray(win_users, dtype=np.int64),
                            window_start=np.asarray(win_starts, dtype=np.int64))
        n_out = len(Z)
    else:
        M = pd.concat(metas).reset_index(drop=True)
        df = pd.DataFrame(Z, columns=[str(i) for i in range(Z.shape[1])])
        for col in ("datetime", "category", "placeid", "userid"):
            df.insert(0, col, M[col].values)
        df.to_parquet(outp, index=False)
        n_out = len(df)

    sidecar = {
        "study": "check2hgi_integrity_v2", "generated_utc": datetime.now(timezone.utc).isoformat(),
        "state": state_lc, "readout": args.readout,
        "output_shape": ("per-window [N, 9, 64] npz" if per_window else "per-visit parquet"),
        "readout_semantics": {
            "full": "whole user path, both directions (the reported readout)",
            "prefix": ("PER-WINDOW: the window whose last observed visit is L has all nine slots "
                       "recomputed on the graph 0..L, the graph available at prediction time. This "
                       "is the scheme phase 0 F5 measured (slots 0..5 untouched, 6..8 move). A "
                       "visit's vector is window-dependent by construction."),
            "prefix_masked_backward": (
                "PER-WINDOW, path cut at the target, and every BACKWARD message routed through a "
                "twin node whose category one-hot is zeroed. This is the readout that MATCHES a "
                "--mask-backward-category build: the future still supplies when and where, never "
                "which category. Use it with such a checkpoint and no other."),
            "prefix_forward_only": (
                "PER-WINDOW and fully causal: the path is cut at the target AND the backward "
                "direction of every remaining edge is dropped, so no visit sees any later visit, "
                "not even one inside the observed window. This is the readout that MATCHES a "
                "forward-only trained encoder; use it with such a checkpoint and no other."),
            "streaming": ("PER-VISIT: visit v computed on the graph 0..v and never revised. "
                          "STRICTER than prefix and NOT bounded by F5; secondary arm only."),
            "forward": "backward edges dropped; DIAGNOSTIC ONLY, renormalizes every node",
        }[args.readout],
        "checkpoint": str(args.checkpoint), "checkpoint_cell": prov["cell"],
        "checkpoint_encoder": prov["encoder"], "checkpoint_repr_seed": prov["repr_seed"],
        "checkpoint_restricted": prov["graph"].get("restricted"),
        "intervention": args.intervention,
        "intervention_semantics": (
            "PER-WINDOW: the window covering visits w..w+8 is recomputed in a pass where ONLY its "
            "target (visit w+9) is intervened on, and all nine slots are read from that pass. A "
            "per-visit table would have slots 0..7 computed with an OBSERVED slot destroyed and "
            "would measure the cost of deleting available history instead."
            if args.intervention else None),
        "intervention_seed": (args.intervention_seed if args.intervention else None),
        "users_from": args.users_from, "user_key": args.user_key,
        "n_users": int(len(sel_users)),
        "n_users_before_cap": n_users_before_cap,
        "max_users": args.max_users, "user_sample_seed": args.user_sample_seed,
        ("n_windows" if per_window else "n_visits"): int(n_out),
        "embeddings_sha256": hashlib.sha256(np.ascontiguousarray(Z).tobytes()).hexdigest(),
        "self_test": bool(args.self_test),
    }
    Path(str(outp) + ".meta.json").write_text(json.dumps(sidecar, indent=2))
    print(f"[infer] wrote {outp} ({n_out} {'windows' if per_window else 'visits'})")


if __name__ == "__main__":
    main()
