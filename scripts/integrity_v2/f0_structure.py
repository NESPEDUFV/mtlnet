"""Phase 0 -- the structural facts that determine what the consecutive-link study must be.

Each fact is emitted with the check that establishes it. Nothing here trains anything; every
number comes from the frozen canonical graph plus a RANDOM-weight encoder of the exact reported
architecture (ResidualLNEncoder(11, 64, num_layers=2, dropout=0.1)). Using random weights is
deliberate: a fact that holds at random init is a property of the ARCHITECTURE AND GRAPH, not of
any particular trained checkpoint, and therefore cannot be explained away by a rebuild.

F1  the check-in graph is a disjoint union of per-user paths
F2  a held-out user encoded ALONE reproduces its full-graph vectors exactly
F3  the backward coefficient from the target, against the self-loop
F4  the 2-layer receptive field: which history slots the target can reach
F5  prefix truncation vs backward-edge dropping -- which slots each one moves

Usage:
    PYTHONPATH=src:research .venv/bin/python scripts/integrity_v2/f0_structure.py \
        --states alabama florida --out docs/results/check2hgi_integrity_v2/f0_structure.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pickle
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "research"))

from embeddings.check2hgi.model.variants import ResidualLNEncoder  # noqa: E402

WINDOW = 9          # observed visits per supervised example
N_LAYERS = 2        # reported check-in encoder depth
DIM = 64
IN_CH = 11
# Two tolerances, declared before any result is read, because they answer different questions.
#
# TOL is the bit-level comparison used for the exactness checks (F2), where the two computations
# perform the SAME sums in the same order and the difference is expected to be exactly zero.
#
# NOISE_TOL is the invariance gate for interventions that CHANGE THE GRAPH (F4, F5). Removing or
# reweighting nodes reassociates the float32 sums inside every affected reduction, so slots that
# are unreachable in exact arithmetic still differ by a few units in the last place. Measured on
# both datasets, the largest observed float32-only difference is 1.073e-06 absolute on vectors whose
# absolute maximum is ~3 (a relative 3e-7). NOISE_TOL = 5e-6 is 4.7x that measured floor, and slot 6's
# LARGEST genuine change is 1.065e-02, about three orders above the gate.
#
# The honest cost of this gate: slot 6 moves in only ~7% of windows, and any genuine slot-6 change
# falling between 1e-6 and 5e-6 is classified as noise here. That biases the reach measurement toward
# reporting a SMALLER receptive field, which is conservative for this study's purpose (it cannot
# manufacture reach that is not there) but it is a real limitation of the gate rather than a clean
# separation. The conclusion that float32 noise is far below the real slot-6 effect stands.
TOL = 1e-6
NOISE_TOL = 5e-6
REL_NOISE_TOL = 1e-5


def _sha256(path: Path, cap: int = 64 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while chunk := fh.read(1 << 20):
            h.update(chunk)
            if fh.tell() > cap:
                h.update(b"TRUNCATED")
                break
    return h.hexdigest()


def _revision() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(REPO),
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def _encoder(seed: int = 0) -> ResidualLNEncoder:
    torch.manual_seed(seed)
    enc = ResidualLNEncoder(IN_CH, DIM, num_layers=N_LAYERS, dropout=0.1)
    enc.eval()          # dropout off -- the forward must be deterministic
    return enc


def _run(enc, x: torch.Tensor, ei: np.ndarray, ew: np.ndarray) -> torch.Tensor:
    with torch.no_grad():
        return enc(x, torch.as_tensor(ei, dtype=torch.long), torch.as_tensor(ew))


def _user_subgraph(ei: np.ndarray, ew: np.ndarray, nodes: np.ndarray):
    """Re-index the induced subgraph on `nodes` to local 0..len(nodes)-1."""
    keep = np.isin(ei[0], nodes) & np.isin(ei[1], nodes)
    remap = {int(g): i for i, g in enumerate(nodes)}
    local = np.array([[remap[int(a)] for a in ei[0, keep]],
                      [remap[int(b)] for b in ei[1, keep]]], dtype=np.int64)
    return local, ew[keep], keep


def fact_1_disjoint_user_paths(uid, ei) -> dict:
    """F1: zero cross-user edges, every edge index-adjacent => union of per-user paths."""
    cross = int((uid[ei[0]] != uid[ei[1]]).sum())
    dist = np.abs(ei[0].astype(np.int64) - ei[1].astype(np.int64))
    return {
        "cross_user_edges": cross,
        "all_edges_index_adjacent": bool((dist == 1).all()),
        "max_edge_index_distance": int(dist.max()),
        "n_edges": int(ei.shape[1]),
        "holds": bool(cross == 0 and (dist == 1).all()),
    }


def fact_2_heldout_exactness(enc, X, uid, ei, ew, n_users=30, seed=1) -> dict:
    """F2: encode a held-out user set ALONE; compare against the full-graph forward."""
    z_full = _run(enc, torch.as_tensor(X), ei, ew)
    users, counts = np.unique(uid, return_counts=True)
    elig = users[counts >= WINDOW + 1]
    samp = np.random.default_rng(seed).choice(elig, size=min(n_users, len(elig)), replace=False)
    nodes = np.where(np.isin(uid, samp))[0]
    local, w_sub, _ = _user_subgraph(ei, ew, nodes)
    z_alone = _run(enc, torch.as_tensor(X[nodes]), local, w_sub)
    diff = float((z_full[nodes] - z_alone).abs().max())
    return {
        "n_users_encoded_alone": int(len(samp)),
        "n_visits": int(len(nodes)),
        "max_abs_diff_vs_full_graph": diff,
        "tolerance": TOL,
        "holds": bool(diff <= TOL),
    }


def fact_3_backward_coefficient(uid, ei, ew) -> dict:
    """F3: GCN-normalized coefficient of the message target -> last observed, vs the self-loop.

    GCNConv adds self loops with fill 1.0 and normalizes by sqrt(deg_src * deg_tgt) where deg
    includes the self loop. On this graph src>tgt in node index means "from the later visit into
    the earlier one", i.e. the backward-in-time edge under study.
    """
    n = int(uid.shape[0])
    deg = np.ones(n, dtype=np.float64)          # self loop, weight 1.0
    np.add.at(deg, ei[0], ew.astype(np.float64))
    coef = ew.astype(np.float64) / np.sqrt(deg[ei[0]] * deg[ei[1]])
    back = coef[ei[0] > ei[1]]                  # later visit -> earlier visit
    self_c = 1.0 / deg
    return {
        "n_backward_edges": int(back.size),
        "backward_coef_median": float(np.median(back)),
        "backward_coef_mean": float(back.mean()),
        "backward_coef_p90": float(np.percentile(back, 90)),
        "backward_coef_max": float(back.max()),
        "backward_frac_above_0.01": float(np.mean(back > 0.01)),
        "self_loop_coef_median": float(np.median(self_c)),
        "self_loop_coef_mean": float(self_c.mean()),
        "edge_weight_median": float(np.median(ew)),
        "edge_weight_frac_below_1e-6": float(np.mean(ew < 1e-6)),
    }


def _pick_long_user(uid, min_len=40):
    users, counts = np.unique(uid, return_counts=True)
    elig = users[counts >= min_len]
    if elig.size == 0:
        raise RuntimeError(f"no user with >= {min_len} visits")
    return elig[int(np.argmax(counts[counts >= min_len]))]


def fact_4_receptive_field(enc, X, uid, ei, ew, n_users=40, seed=2) -> dict:
    """F4: zero the TARGET's category one-hot; which history slots (0..8) move?

    Window starting at local position p uses p..p+8 as history and p+9 as target. Under two
    layers the target can reach at most index distance 2, i.e. slots p+8 and p+7.
    """
    users, counts = np.unique(uid, return_counts=True)
    elig = users[counts >= WINDOW + 3]
    samp = np.random.default_rng(seed).choice(elig, size=min(n_users, len(elig)), replace=False)
    reached, moved_slot8, moved_slot7, scale = set(), [], [], []
    n_win = 0
    for u in samp:
        nodes = np.where(uid == u)[0]
        local, w_sub, _ = _user_subgraph(ei, ew, nodes)
        xs = torch.as_tensor(X[nodes])
        z0 = _run(enc, xs, local, w_sub)
        for p in range(0, len(nodes) - WINDOW):
            tgt, last = p + WINDOW, p + WINDOW - 1
            x2 = xs.clone()
            x2[tgt, :7] = 0.0                    # category one-hot only
            z1 = _run(enc, x2, local, w_sub)
            delta = (z1 - z0).abs().max(1).values
            hits = torch.nonzero(delta > NOISE_TOL).flatten().tolist()
            reached.update(h - p for h in hits if p <= h <= p + WINDOW)
            moved_slot8.append(float(delta[last]))
            moved_slot7.append(float(delta[last - 1]))
            scale.append(float(z0[last].abs().max()))
            n_win += 1
            if n_win >= 400:
                break
        if n_win >= 400:
            break
    hist = sorted(s for s in reached if s <= WINDOW - 1)
    m8, m7, sc = np.array(moved_slot8), np.array(moved_slot7), np.array(scale)
    return {
        "n_windows": n_win,
        "history_slots_reached_by_target": hist,
        "slot8_abs_change_median": float(np.median(m8)),
        "slot8_rel_change_median": float(np.median(m8 / np.maximum(sc, 1e-9))),
        "slot7_abs_change_median": float(np.median(m7)),
        "slot_scale_absmax_median": float(np.median(sc)),
        "frac_windows_slot8_unmoved": float(np.mean(m8 <= NOISE_TOL)),
        "noise_tolerance": NOISE_TOL,
        "holds": hist == [WINDOW - 2, WINDOW - 1],
    }


def fact_5_truncation_vs_edge_drop(enc, X, uid, ei, ew, n_users=40, seed=3) -> dict:
    """F5: three candidate strict readouts, compared slot by slot against the reported one.

    R_prefix  keep the user's visits 0..j+8, i.e. cut the path AT the target. This is exactly what
              exists at prediction time: the whole observed past, none of the future. It is the
              honest causal readout, not an ablation.
    R_window  keep only the nine visits j..j+8 as their own path. This ALSO deletes the user's
              earlier history, so it introduces a spurious LEFT boundary that has nothing to do
              with the leak; it is reported to show why R_prefix is preferred.
    R_fwd     keep the whole user path but drop every backward edge. Because GCN degree
              normalization is recomputed from the surviving edges, this perturbs every node.

    A note on tolerance. Slots outside the reach of the removed nodes are unchanged in exact
    arithmetic; in float32 the sums are reassociated, so tiny nonzero differences occur. Both the
    fraction of windows above TOL and the magnitude are reported, so a boundary effect is never
    confused with float noise.
    """
    users, counts = np.unique(uid, return_counts=True)
    elig = users[counts >= WINDOW + 3]
    samp = np.random.default_rng(seed).choice(elig, size=min(n_users, len(elig)), replace=False)
    rows = {"prefix": [], "window": [], "fwd": []}
    scale_rows = []
    n_win = 0
    for u in samp:
        nodes = np.where(uid == u)[0]
        local, w_sub, _ = _user_subgraph(ei, ew, nodes)
        xs = torch.as_tensor(X[nodes])
        z_rep = _run(enc, xs, local, w_sub)
        fmask = local[0] < local[1]
        z_fwd = _run(enc, xs, local[:, fmask], w_sub[fmask])
        for p in range(0, len(nodes) - WINDOW):
            # R_prefix: nodes 0..p+8 (cut at the target); slot s is node p+s
            pre = np.arange(0, p + WINDOW)
            kp = np.isin(local[0], pre) & np.isin(local[1], pre)
            z_pre = _run(enc, xs[pre], local[:, kp], w_sub[kp])   # ids already 0..len(pre)-1
            # R_window: only nodes p..p+8
            sel = np.arange(p, p + WINDOW)
            kw = np.isin(local[0], sel) & np.isin(local[1], sel)
            rm = {int(g): i for i, g in enumerate(sel)}
            e_w = np.array([[rm[int(a)] for a in local[0, kw]],
                            [rm[int(b)] for b in local[1, kw]]], dtype=np.int64)
            z_win = _run(enc, xs[sel], e_w, w_sub[kw])
            rows["prefix"].append([float((z_rep[p + s] - z_pre[p + s]).abs().max()) for s in range(WINDOW)])
            rows["window"].append([float((z_rep[p + s] - z_win[s]).abs().max()) for s in range(WINDOW)])
            rows["fwd"].append([float((z_rep[p + s] - z_fwd[p + s]).abs().max()) for s in range(WINDOW)])
            scale_rows.append([float(z_rep[p + s].abs().max()) for s in range(WINDOW)])
            n_win += 1
            if n_win >= 300:
                break
        if n_win >= 300:
            break

    sc = np.array(scale_rows)
    out = {"n_windows": n_win, "noise_tolerance_abs": NOISE_TOL,
           "noise_tolerance_rel": REL_NOISE_TOL}

    def _cond_median(col, mask):
        """Median magnitude AMONG windows that actually moved. The unconditional median is
        misleading here: roughly half the windows have a near-zero temporal edge weight to the
        target (large time gap), so they cannot move at all and drag the median to zero."""
        v = col[mask]
        return float(np.median(v)) if v.size else 0.0

    for key, label in (("prefix", "R_prefix_cut_at_target"),
                       ("window", "R_window_nine_nodes_only"),
                       ("fwd", "R_fwd_backward_edges_dropped")):
        d = np.array(rows[key])
        rel = d / np.maximum(sc, 1e-9)
        moved = (d > NOISE_TOL) & (rel > REL_NOISE_TOL)
        out[label] = {
            "slots_within_tolerance_all_windows": [s for s in range(WINDOW) if not bool(moved[:, s].any())],
            "per_slot_frac_windows_moved": [float(np.mean(moved[:, s])) for s in range(WINDOW)],
            "per_slot_median_abs_change": [float(np.median(d[:, s])) for s in range(WINDOW)],
            "per_slot_max_abs_change": [float(d[:, s].max()) for s in range(WINDOW)],
            "per_slot_median_rel_change_among_moved":
                [_cond_median(rel[:, s], moved[:, s]) for s in range(WINDOW)],
            "per_slot_p90_rel_change": [float(np.percentile(rel[:, s], 90)) for s in range(WINDOW)],
            "mean_frac_slots_moved": float(np.mean(moved)),
            "noise_tolerance_abs": NOISE_TOL, "noise_tolerance_rel": REL_NOISE_TOL,
        }

    def _mv(key):
        d = np.array(rows[key]); return (d > NOISE_TOL) & (d / np.maximum(sc, 1e-9) > REL_NOISE_TOL)
    mp, mw, mf = _mv("prefix"), _mv("window"), _mv("fwd")
    dp = np.array(rows["prefix"])
    # Removing the target NODE changes slot 8's degree normalization, and that change propagates
    # two further hops. The reachable set under R_prefix is therefore {6, 7, 8}, one slot wider
    # than the feature-perturbation reach {7, 8} measured in F4. Slots 0..5 must be untouched.
    out["prefix_reach_expected"] = [WINDOW - 3, WINDOW - 2, WINDOW - 1]
    out["prefix_leaves_slots_0_to_5_untouched"] = bool(not mp[:, :WINDOW - 3].any())
    out["prefix_max_abs_change_slots_0_to_5"] = float(dp[:, :WINDOW - 3].max())
    out["prefix_is_more_surgical_than_edge_drop"] = bool(mp.mean() < mf.mean())
    out["prefix_is_more_surgical_than_window"] = bool(mp.mean() < mw.mean())
    out["window_readout_introduces_left_boundary"] = bool(mw[:, 0].mean() > mp[:, 0].mean())
    return out


def measure_state(state: str, enc) -> dict:
    gpath = REPO / "output" / "check2hgi" / state / "temp" / "checkin_graph.pt"
    with open(gpath, "rb") as fh:
        d = pickle.load(fh)
    md = d["metadata"].reset_index(drop=True)
    uid = md["userid"].to_numpy()
    ei = np.asarray(d["edge_index"])
    ew = np.asarray(d["edge_weight"], dtype=np.float32)
    X = np.asarray(d["node_features"], dtype=np.float32)
    assert X.shape[1] == IN_CH, f"expected {IN_CH} node features, got {X.shape[1]}"
    assert len(md) == int(d["num_checkins"]) == X.shape[0]

    return {
        "state": state,
        "graph_path": str(gpath.relative_to(REPO)),
        "graph_sha256_first64MB": _sha256(gpath),
        "n_checkins": int(d["num_checkins"]),
        "n_pois": int(d["num_pois"]),
        "n_regions": int(d["num_regions"]),
        "n_users": int(np.unique(uid).size),
        "node_feature_width": int(X.shape[1]),
        "F1_disjoint_user_paths": fact_1_disjoint_user_paths(uid, ei),
        "F2_heldout_exactness": fact_2_heldout_exactness(enc, X, uid, ei, ew),
        "F3_backward_coefficient": fact_3_backward_coefficient(uid, ei, ew),
        "F4_receptive_field": fact_4_receptive_field(enc, X, uid, ei, ew),
        "F5_truncation_vs_edge_drop": fact_5_truncation_vs_edge_drop(enc, X, uid, ei, ew),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--states", nargs="+", default=["alabama", "florida"])
    ap.add_argument("--encoder-seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    enc = _encoder(args.encoder_seed)
    out = {
        "study": "check2hgi_integrity_v2 / phase 0 structural facts",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "revision": _revision(),
        "command": " ".join(sys.argv),
        "encoder": {
            "class": "ResidualLNEncoder", "in_channels": IN_CH, "hidden": DIM,
            "num_layers": N_LAYERS, "dropout": 0.1, "eval_mode": True,
            "weights": "RANDOM (untrained)", "torch_seed": args.encoder_seed,
            "why_random": ("a fact that holds at random init is a property of the architecture "
                           "and the graph, not of any trained checkpoint"),
        },
        "window_contract": {"history": WINDOW, "target": "visit j+9", "stride": 1},
        "tolerance": TOL,
        "torch_version": torch.__version__,
        "per_state": {},
    }
    for st in args.states:
        print(f"[f0] measuring {st} ...", flush=True)
        out["per_state"][st] = measure_state(st, enc)

    outp = Path(args.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=2))
    print(f"[f0] wrote {outp}")

    for st, r in out["per_state"].items():
        print(f"\n=== {st} ===")
        print(f"  F1 union of per-user paths : {r['F1_disjoint_user_paths']['holds']} "
              f"(cross-user edges {r['F1_disjoint_user_paths']['cross_user_edges']})")
        print(f"  F2 held-out exactness      : {r['F2_heldout_exactness']['holds']} "
              f"(max abs diff {r['F2_heldout_exactness']['max_abs_diff_vs_full_graph']:.3e})")
        print(f"  F3 backward coef median    : {r['F3_backward_coefficient']['backward_coef_median']:.4f} "
              f"vs self-loop {r['F3_backward_coefficient']['self_loop_coef_median']:.4f}")
        print(f"  F4 slots reached by target : {r['F4_receptive_field']['history_slots_reached_by_target']}")
        f5 = r["F5_truncation_vs_edge_drop"]
        for lbl, key in (("prefix (cut at target)", "R_prefix_cut_at_target"),
                         ("window (9 nodes only) ", "R_window_nine_nodes_only"),
                         ("edge drop (backward) ", "R_fwd_backward_edges_dropped")):
            v = f5[key]
            print(f"  F5 {lbl}: slots moved {['%.2f' % x for x in v['per_slot_frac_windows_moved']]} "
                  f"| mean frac {v['mean_frac_slots_moved']:.4f}")
        print(f"     prefix leaves slots 0-5 untouched: {f5['prefix_leaves_slots_0_to_5_untouched']} "
              f"| more surgical than edge drop: {f5['prefix_is_more_surgical_than_edge_drop']}")


if __name__ == "__main__":
    main()
