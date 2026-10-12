"""Causal intervention on the target visit, with frozen weights, measuring three distinct things.

The distinction this script exists to enforce. Phase 0 F3 established that a RANDOM-weight encoder
already moves the last observed visit's vector by a median 16% when the target's category changes.
So the vector DEPENDING on the target is guaranteed by the architecture and decides nothing. What
has to be measured is whether the dependence carries the target's category IDENTITY in a form a
predictor can read.

  (1) dependence   how far the last observed vector moves. Reported, never decided on.
  (2) carriage     does moving the target's category to c' move the vector TOWARD what c' looks
                   like? Measured by a discriminability statistic that needs no trained predictor:
                   if the perturbed vectors separate by substituted class, a classifier could read
                   the target's category out of them.
  (3) use          whether the reported predictor's output tracks the target. That needs the
                   downstream model and lives in counterfactual.py.

INTERVENTION ARMS
  zero_cat      set the target's 7-d category one-hot to zero
  sub_cat=c     set the target's category one-hot to class c (all 7 run)
  shuffle_cat   replace each target's category with one drawn from the GLOBAL pool of target
                category rows (keeps the marginal, breaks the pairing, and unlike a within-user
                permutation is never the identity for short histories)
  resample_all  replace the target's full 11-d feature vector with another visit's (category AND
                time, so the time channel is covered)
  edge_weight   redraw the target's incident temporal edge weight from its marginal, leaving all
                node features intact. This isolates the "how long until the next visit" channel,
                which category-only perturbation cannot see.
  drop_target   remove the target node entirely (the prefix readout)

EXACTNESS AND COST. A window's measurement is exact only if no other perturbed target lies inside
its receptive field. Targets are therefore perturbed in GROUPS spaced more than 2 hops apart along
each user's path, so one forward pass measures many windows without interference. The spacing is
asserted, not assumed.
"""
from __future__ import annotations

import argparse
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
sys.path.insert(0, str(REPO / "scripts"))

from integrity_v2.infer_checkins import load_encoder, _fwd, _user_path  # noqa: E402

WINDOW = 9
N_CAT = 7
HOPS = 2            # 2 GCN layers
SPACING = 2 * HOPS + 2      # >= 6 apart: receptive fields (radius 2) cannot overlap or touch
NOISE_TOL = 5e-6


def _groups(positions: np.ndarray) -> list[np.ndarray]:
    """Partition target positions into groups whose members are >= SPACING apart."""
    out: list[list[int]] = []
    for p in np.sort(positions):
        placed = False
        for g in out:
            if p - g[-1] >= SPACING:
                g.append(int(p)); placed = True; break
        if not placed:
            out.append([int(p)])
    return [np.asarray(g) for g in out]


def _cohens_d_multiclass(Z: np.ndarray, y: np.ndarray) -> float:
    """Between-class over within-class scatter of the perturbed vectors (a Fisher ratio).

    This is the carriage statistic. It asks whether vectors produced under different substituted
    target categories are SEPARABLE, without fitting a classifier, so it cannot be inflated by
    probe overfitting or by row overlap. Zero means the substitutions produce indistinguishable
    vectors; large means the target's category identity is legible in the history vector.
    """
    mu = Z.mean(0)
    sb = sw = 0.0
    for c in np.unique(y):
        Zc = Z[y == c]
        if len(Zc) < 2:
            continue
        sb += len(Zc) * float(((Zc.mean(0) - mu) ** 2).sum())
        sw += float(((Zc - Zc.mean(0)) ** 2).sum())
    return float(sb / sw) if sw > 0 else float("inf")


def run_state(state: str, ck_path: Path, split: dict, user_key: str,
              max_windows: int, rng_seed: int) -> dict:
    state_lc = state.lower()
    with open(REPO / "output" / "check2hgi" / state_lc / "temp" / "checkin_graph.pt", "rb") as fh:
        d = pickle.load(fh)
    md = d["metadata"].reset_index(drop=True)
    uid = md["userid"].to_numpy()
    ei_g = np.asarray(d["edge_index"]); ew_g = np.asarray(d["edge_weight"], dtype=np.float32)
    X = np.asarray(d["node_features"], dtype=np.float32)
    cat_idx = md["category"].astype("category").cat.codes.to_numpy()

    enc, prov, _, _trained_fo, _trained_mb, _in_ch = load_encoder(ck_path)
    rng = np.random.default_rng(rng_seed)

    want = np.asarray(split[user_key], dtype=uid.dtype) if user_key != "all" else np.unique(uid)
    users = np.intersect1d(np.unique(uid), want)
    rng.shuffle(users)

    # marginal pools for the resample / edge-weight arms, taken from the SAME user set
    pool_nodes = np.where(np.isin(uid, users))[0]
    feat_pool = X[pool_nodes]
    # Category one-hot rows pooled across all users, for the shuffle arm. Pooling globally is what
    # makes that arm non-degenerate: a within-user permutation is the identity for short histories.
    cat_pool = X[pool_nodes][:, :N_CAT]
    ew_pool = ew_g[np.isin(ei_g[0], pool_nodes) & np.isin(ei_g[1], pool_nodes)]

    acc: dict[str, list] = {k: [] for k in
                            ("zero_cat", "shuffle_cat", "resample_all", "edge_weight", "drop_target")}
    sub_vecs: list[np.ndarray] = []      # perturbed last-slot vectors, for the carriage statistic
    sub_labels: list[int] = []
    base_vecs: list[np.ndarray] = []
    true_tgt_cat: list[int] = []
    n_win = 0

    for u in users:
        if n_win >= max_windows:
            break
        nodes = np.where(uid == u)[0]
        if len(nodes) < WINDOW + 1:
            continue
        local, ew = _user_path(ei_g, ew_g, nodes)
        xs = torch.as_tensor(X[nodes])
        z0 = _fwd(enc, xs, local, ew)
        tpos = np.arange(WINDOW, len(nodes))              # every valid target position
        for grp in _groups(tpos):
            if n_win >= max_windows:
                break
            assert all(np.diff(np.sort(grp)) >= SPACING), "group spacing violated"
            last = grp - 1

            def _delta(x2=None, e_w=None, drop=None):
                if drop is not None:
                    keep = np.setdiff1d(np.arange(len(nodes)), drop)
                    km = np.isin(local[0], keep) & np.isin(local[1], keep)
                    rm = {int(g): i for i, g in enumerate(keep)}
                    e2 = np.array([[rm[int(a)] for a in local[0, km]],
                                   [rm[int(b)] for b in local[1, km]]], dtype=np.int64)
                    zz = _fwd(enc, xs[keep], e2, ew[km])
                    pos = np.searchsorted(keep, last)
                    return zz[pos]
                return _fwd(enc, x2 if x2 is not None else xs, local,
                            e_w if e_w is not None else ew)[last]

            b = z0[last]
            scale = b.abs().amax(1).clamp(min=1e-9)

            def _rec(key, zp):
                dv = (zp - b)
                acc[key].append(np.stack([
                    dv.abs().amax(1).numpy() / scale.numpy(),                       # rel L-inf
                    dv.norm(dim=1).numpy(),                                         # L2
                    torch.nn.functional.cosine_similarity(zp, b, dim=1).numpy(),    # cosine
                ], 1))

            x2 = xs.clone(); x2[grp, :N_CAT] = 0.0
            _rec("zero_cat", _delta(x2=x2))

            # Permute from a GLOBAL pool of target category rows, not within this user's own
            # targets. A within-group permutation is the identity whenever the group has one member,
            # which happens for every user with fewer than about fifteen visits, so a large share of
            # windows would receive no perturbation at all and a null result would be uninterpretable.
            # Drawing from the pooled rows keeps the category marginal while breaking the pairing,
            # which is what this arm is for, and guarantees every window is actually perturbed.
            x2 = xs.clone()
            src = cat_pool[rng.integers(0, len(cat_pool), len(grp))]
            x2[grp, :N_CAT] = torch.as_tensor(src)
            _rec("shuffle_cat", _delta(x2=x2))

            x2 = xs.clone()
            x2[grp] = torch.as_tensor(feat_pool[rng.integers(0, len(feat_pool), len(grp))])
            _rec("resample_all", _delta(x2=x2))

            e_w = ew.copy()
            inc = np.where(np.isin(local[0], grp) | np.isin(local[1], grp))[0]
            if inc.size:
                e_w[inc] = ew_pool[rng.integers(0, len(ew_pool), inc.size)]
            _rec("edge_weight", _delta(e_w=e_w))

            _rec("drop_target", _delta(drop=grp))

            # carriage: substitute each of the 7 classes into the target and keep the vectors
            for c in range(N_CAT):
                x2 = xs.clone(); x2[grp, :N_CAT] = 0.0; x2[grp, c] = 1.0
                zc = _delta(x2=x2)
                sub_vecs.append(zc.numpy()); sub_labels.extend([c] * len(grp))
            base_vecs.append(b.numpy())
            true_tgt_cat.extend(cat_idx[nodes][grp].tolist())
            n_win += len(grp)

    out: dict = {"n_windows": int(n_win), "n_users_used": int(len(users)),
                 "spacing_between_perturbed_targets": SPACING}
    for k, v in acc.items():
        if not v:
            continue
        a = np.concatenate(v, 0)
        rel, l2, cos = a[:, 0], a[:, 1], a[:, 2]
        moved = rel > 1e-5
        out[k] = {
            "n": int(len(a)),
            "frac_windows_moved": float(moved.mean()),
            "rel_linf_median": float(np.median(rel)),
            "rel_linf_median_among_moved": float(np.median(rel[moved])) if moved.any() else 0.0,
            "rel_linf_p90": float(np.percentile(rel, 90)),
            "l2_median": float(np.median(l2)),
            "cosine_median": float(np.median(cos)),
            "cosine_p10": float(np.percentile(cos, 10)),
            "invariant_within_tolerance": bool((rel <= 1e-5).all()),
        }

    if sub_vecs:
        Zs = np.concatenate(sub_vecs, 0)
        ys = np.asarray(sub_labels)
        Zb = np.concatenate(base_vecs, 0)
        out["carriage"] = {
            "n_perturbed_vectors": int(len(Zs)),
            "fisher_ratio_by_substituted_class": _cohens_d_multiclass(Zs, ys),
            "fisher_ratio_shuffled_labels_control":
                _cohens_d_multiclass(Zs, np.random.default_rng(0).permutation(ys)),
            "note": ("between-class over within-class scatter of the last-observed vector as a "
                     "function of the SUBSTITUTED target category; the shuffled-label row is the "
                     "floor this statistic reaches when substitution carries nothing"),
        }
        out["baseline_vectors"] = {"n": int(len(Zb)),
                                  "absmax_median": float(np.median(np.abs(Zb).max(1)))}
    out["checkpoint"] = {"path": str(ck_path), "cell": prov["cell"],
                         "encoder": prov["encoder"], "repr_seed": prov["repr_seed"],
                         "restricted": prov["graph"].get("restricted")}
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--checkpoints", nargs="+", required=True,
                    help="label=path pairs, e.g. U1=results/.../U1/checkpoint.pt")
    ap.add_argument("--split", required=True)
    ap.add_argument("--user-key", default="val_users")
    ap.add_argument("--max-windows", type=int, default=3000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    split = json.loads(Path(args.split).read_text())
    res = {
        "study": "check2hgi_integrity_v2 / intervention",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(sys.argv),
        "state": args.state, "split_file": args.split, "user_key": args.user_key,
        "split": {k: split[k] for k in ("seed", "fold", "n_folds", "engine") if k in split},
        "torch_version": torch.__version__,
        "what_each_number_means": {
            "dependence": "rel_linf / l2 / cosine -- guaranteed nonzero by the architecture (F3), never decisive",
            "carriage": "fisher_ratio_by_substituted_class vs its shuffled-label floor -- whether the target's category identity is legible",
        },
        "arms": {},
    }
    for spec in args.checkpoints:
        label, path = spec.split("=", 1)
        print(f"[intervene] {args.state} arm {label} ...", flush=True)
        res["arms"][label] = run_state(args.state, Path(path), split, args.user_key,
                                       args.max_windows, args.seed)
        a = res["arms"][label]
        print(f"  windows={a['n_windows']} zero_cat rel={a['zero_cat']['rel_linf_median']:.4f} "
              f"drop rel={a['drop_target']['rel_linf_median']:.4f} "
              f"fisher={a['carriage']['fisher_ratio_by_substituted_class']:.4f} "
              f"(shuffled floor {a['carriage']['fisher_ratio_shuffled_labels_control']:.4f})",
              flush=True)

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2))
    print(f"[intervene] wrote {outp}")


if __name__ == "__main__":
    main()
