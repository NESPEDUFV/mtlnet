"""The probe ladder: can the target's category be DECODED from the observed history vectors?

This replaces the earlier last-vector linear screen, which had four defects this script fixes.

  1. It ran one unseeded classifier draw. Here the MAIN probes (linear and nonlinear on the history
     vectors) run --probe-seeds draws, default 10, and reports an interval. Two auxiliary
     quantities deliberately run fewer: the shuffled-label floor uses the first 3 seeds and the
     calibration ladder the first 5, because each is a reference point rather than a reported
     result and each additional seed costs a full probe fit. Their intervals are correspondingly
     wider and should not be quoted as precise.
  2. It was linear only, and is known to have passed an encoder that a sequence model showed was
     far above control. Here a linear and a small nonlinear probe both run, and the reported
     verdict follows the STRONGER of the two.
  3. Its splits were row-level GroupKFold on windows. Because stride-1 windows share check-in
     vectors across rows, a row-level split can place the SAME vector on both sides. All splits
     here are user-disjoint, taken from the frozen fold file.
  4. It compared against other encoders only, so a channel shared by every arm stayed invisible.
     Here the reference set includes an architectural floor (random-weight encoder), a structural
     zero (the prefix readout, provably target-free), a label-shuffled floor, and the label-only
     history benchmarks.

CALIBRATION, which is what turns a null into a bounded statement. A probe that fails to recover
the target proves nothing unless we know what it COULD have recovered. So a known signal is
injected at a range of strengths: the target's one-hot, projected into the embedding space and
added at scale epsilon. The smallest epsilon the probe detects is its minimum detectable effect,
and a null result then reads "effects at or above this size would have been seen".
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "src"))

from configs.globals import CATEGORIES_MAP  # noqa: E402

WINDOW = 9
_CAT = {v: k for k, v in CATEGORIES_MAP.items()}


def _fit_probe(Xtr, ytr, Xte, yte, kind: str, seed: int, n_classes: int,
               epochs: int = 300, device: str = "cpu") -> float:
    """Macro-F1 of one probe fit. Standardization uses TRAINING rows only."""
    torch.manual_seed(seed)
    mu, sd = Xtr.mean(0), Xtr.std(0) + 1e-6
    xtr = torch.as_tensor((Xtr - mu) / sd, dtype=torch.float32, device=device)
    xte = torch.as_tensor((Xte - mu) / sd, dtype=torch.float32, device=device)
    ytr_t = torch.as_tensor(ytr, dtype=torch.long, device=device)
    d_in = Xtr.shape[1]
    if kind == "linear":
        clf = torch.nn.Linear(d_in, n_classes)
    elif kind == "mlp":
        clf = torch.nn.Sequential(torch.nn.Linear(d_in, 128), torch.nn.ReLU(),
                                  torch.nn.Dropout(0.1), torch.nn.Linear(128, n_classes))
    else:
        raise ValueError(kind)
    clf = clf.to(device)
    opt = torch.optim.AdamW(clf.parameters(), lr=1e-2, weight_decay=1e-4)
    clf.train()
    for _ in range(epochs):
        opt.zero_grad(); F.cross_entropy(clf(xtr), ytr_t).backward(); opt.step()
    clf.eval()
    with torch.no_grad():
        pred = clf(xte).argmax(1).cpu().numpy()
    return float(f1_score(yte, pred, average="macro", zero_division=0))


def _probe_seeds(Xtr, ytr, Xte, yte, kind, n_classes, seeds, device) -> dict:
    v = [_fit_probe(Xtr, ytr, Xte, yte, kind, s, n_classes, device=device) for s in seeds]
    a = np.asarray(v)
    return {"mean": float(a.mean()), "sd": float(a.std()), "n_seeds": len(seeds),
            "ci95_lo": float(np.percentile(a, 2.5)), "ci95_hi": float(np.percentile(a, 97.5)),
            "per_seed": [float(x) for x in a]}


def label_only_baselines(hist_cat: np.ndarray, y: np.ndarray, tr, te,
                         n_classes: int, seeds, device) -> dict:
    """Benchmarks that use only the observed CATEGORY LABELS, never an embedding.

    These are the reference points a representation must beat to be carrying anything beyond
    ordinary next-category predictability. None of them is a mathematical ceiling: each is the
    result of one implemented predictor.
    """
    maj = int(np.bincount(y[tr], minlength=n_classes).argmax())
    out = {
        "majority_class": float(f1_score(y[te], np.full(len(te), maj),
                                         average="macro", zero_division=0)),
        "last_category_persistence": float(f1_score(y[te], hist_cat[te, -1],
                                                    average="macro", zero_division=0)),
    }
    oh_last = np.eye(n_classes, dtype=np.float32)[hist_cat[:, -1]]
    out["last_category_classifier"] = _probe_seeds(oh_last[tr], y[tr], oh_last[te], y[te],
                                                   "linear", n_classes, seeds, device)
    oh_all = np.eye(n_classes, dtype=np.float32)[hist_cat].reshape(len(hist_cat), -1)
    out["nine_position_category_history"] = _probe_seeds(oh_all[tr], y[tr], oh_all[te], y[te],
                                                         "linear", n_classes, seeds, device)
    out["note"] = ("implemented predictors, not mathematical ceilings; the nine-position row is "
                   "the strongest label-only reference available here")
    return out


def calibration(X, y, tr, te, n_classes, seeds, device, eps_grid) -> dict:
    """Inject a known target-category signal at increasing strength; find what the probe detects.

    The injected direction is a fixed random projection of the target's one-hot into the embedding
    space, scaled by the data's own standard deviation, so epsilon is expressed in units of the
    representation rather than arbitrary ones.
    """
    rng = np.random.default_rng(0)
    W = rng.normal(size=(n_classes, X.shape[1])).astype(np.float32)
    W /= np.linalg.norm(W, axis=1, keepdims=True)
    scale = float(X.std())
    base = _probe_seeds(X[tr], y[tr], X[te], y[te], "linear", n_classes, seeds, device)
    rows = []
    for eps in eps_grid:
        Xi = X + eps * scale * W[y]              # the true target category, injected
        r = _probe_seeds(Xi[tr], y[tr], Xi[te], y[te], "linear", n_classes, seeds, device)
        rows.append({"epsilon": float(eps), "macro_f1": r["mean"], "sd": r["sd"],
                     "delta_vs_base": r["mean"] - base["mean"]})
    detected = [r for r in rows if r["delta_vs_base"] > 2 * max(base["sd"], 1e-9)]
    return {
        "base_macro_f1": base["mean"], "base_sd": base["sd"],
        "injected_direction": "fixed random unit vector per class, scaled by the data std",
        "grid": rows,
        "min_detectable_epsilon": (float(detected[0]["epsilon"]) if detected else None),
        "detection_rule": "delta above 2 x the base probe's seed standard deviation",
        "interpretation": ("a null decodability result excludes injected effects at or above "
                           "min_detectable_epsilon; it cannot exclude smaller ones"),
    }


def load_arm_windows(path: str, nxt_all: pd.DataFrame) -> dict:
    """Assemble the window matrices for one arm, accepting either output shape.

    A per-visit parquet (readouts full / streaming / forward) is windowed here. A per-window npz
    (readout prefix) already carries [N, 9, 64] and is only matched to its labels, because a
    visit's vector under that readout depends on which window it appears in and therefore cannot
    be recovered from a per-visit table.
    """
    if str(path).endswith(".npz"):
        z = np.load(path)
        S = z["seq"].astype(np.float32)
        uu = z["userid"].astype(np.int64)
        starts = z["window_start"].astype(np.int64)
        nu = nxt_all["userid"].astype(np.int64).to_numpy()
        y_all = nxt_all["next_category"].map(_CAT).to_numpy()
        # window w of user u is that user's w-th row in the reported window table, in order
        rows = np.empty(len(uu), dtype=np.int64)
        for u in np.unique(uu):
            m = uu == u
            rw = np.where(nu == u)[0]
            st = starts[m]
            assert st.max() < len(rw), f"user {u}: window {st.max()} beyond {len(rw)} reported rows"
            rows[m] = rw[st]
        return {"seq": S, "slot8": S[:, WINDOW - 1], "slot7": S[:, WINDOW - 2],
                "hist_cat": None, "y": y_all[rows], "userid": uu, "rows": rows,
                "per_window_source": True}
    emb = pd.read_parquet(path)
    users = np.unique(emb["userid"].astype(np.int64).to_numpy())
    # `rows` must index the SAME frame for every arm or the row ids are not comparable. The
    # per-window branch above indexes nxt_all directly, so this branch must too: filtering with
    # reset_index would renumber the rows and make identical ids mean different windows. That is a
    # silent-wrong-answer bug, not a crash, whenever a user subsample makes the arms differ -- it
    # did not surface at Alabama because no subsample was applied there and the two numberings
    # coincided. Keep the original index and carry it through as the row id.
    mask = nxt_all["userid"].astype(np.int64).isin(users).to_numpy()
    nxt = nxt_all[mask]
    orig_index = np.where(mask)[0]
    W = build_window_matrix(emb, nxt.reset_index(drop=True))
    W["rows"] = orig_index[W["rows"]]          # map local positions back to nxt_all row ids
    W["per_window_source"] = False
    return W


def build_window_matrix(emb: pd.DataFrame, nxt: pd.DataFrame) -> dict:
    """Assemble per-window slot matrices from a per-visit embedding table.

    Both frames are sorted the way the reported window builder sorts them (userid, datetime,
    mergesort), and windows for a user are emitted in increasing start position, so window k of
    user u maps to that user's visits k..k+8.
    """
    cols = [str(i) for i in range(64)]
    e = emb.sort_values(["userid", "datetime"], kind="mergesort").reset_index(drop=True)
    E = e[cols].to_numpy(np.float32)
    eu = e["userid"].astype(np.int64).to_numpy()
    ecat = e["category"].map(_CAT).to_numpy()
    nu = nxt["userid"].astype(np.int64).to_numpy()
    y = nxt["next_category"].map(_CAT).to_numpy()

    seq, hist, keep = [], [], []
    for u in np.unique(nu):
        rw = np.where(nu == u)[0]
        ei = np.where(eu == u)[0]
        for k, r in enumerate(rw):
            if k + WINDOW >= len(ei):      # a real target visit must exist after the nine
                break
            seq.append(E[ei[k:k + WINDOW]])            # [9, 64] the full input window
            hist.append(ecat[ei[k:k + WINDOW]])        # observed categories of those nine visits
            keep.append(r)
    keep = np.asarray(keep)
    S = np.stack(seq)                                   # [N, 9, 64]
    return {"seq": S, "slot8": S[:, WINDOW - 1], "slot7": S[:, WINDOW - 2],
            "hist_cat": np.stack(hist), "y": y[keep], "userid": nu[keep], "rows": keep}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--state", required=True)
    ap.add_argument("--arms", nargs="+", required=True, help="label=embeddings.parquet pairs")
    ap.add_argument("--next-parquet", required=True)
    ap.add_argument("--categories-from", required=True,
                    help="a per-visit embeddings parquet used ONLY for its category column, so the "
                         "history-label baselines are identical across arms")
    ap.add_argument("--split", required=True)
    ap.add_argument("--probe-seeds", type=int, default=10)
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    split = json.loads(Path(args.split).read_text())
    nxt_all = pd.read_parquet(args.next_parquet)
    seeds = list(range(args.probe_seeds))
    n_classes = len(CATEGORIES_MAP) - 1          # 'None' is not an observed class

    res = {
        "study": "check2hgi_integrity_v2 / probe ladder",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "command": " ".join(sys.argv), "state": args.state,
        "split": {k: split[k] for k in ("seed", "fold", "n_folds", "engine") if k in split},
        "protocol": {
            "splits": "user-disjoint, taken from the frozen fold file",
            "why_user_disjoint": ("stride-1 windows share check-in vectors across rows, so a "
                                  "row-level split would place the same vector on both sides"),
            "standardization": "training rows only",
            "probe_seeds": args.probe_seeds,
            "verdict_follows": "the stronger of the linear and nonlinear probes",
        },
        "arms": {},
    }

    # The observed categories of the nine history slots are a property of the DATA, not of any
    # arm's embeddings, so they are derived once from a per-visit reference table and matched to
    # each arm by row. Per-window arms cannot supply them, and re-deriving per arm would risk two
    # arms disagreeing about the same window's history.
    # Build the reference through the SAME loader as every arm. Calling build_window_matrix here
    # with a reset_index frame was the duplicated form of the row-id bug: it produced ids in the
    # filtered index space while the arms carry global ids, so the intersection collapsed to the
    # coincidental overlap of two numbering schemes (2731 of 23679 windows at Florida) instead of
    # failing loudly. One code path, one index space.
    W_ref = load_arm_windows(args.categories_from, nxt_all)
    hist_by_row = dict(zip(W_ref["rows"].tolist(), W_ref["hist_cat"]))
    assert W_ref["hist_cat"] is not None, "--categories-from must be a per-visit table"

    # Load every arm FIRST and reduce them all to the rows they have in common, including the
    # reference table that supplies the history labels. Two reasons, one correctness and one
    # methodological. Correctness: a per-window arm and a per-visit arm do not necessarily produce
    # the same window set (a per-visit table needs ten consecutive visits to form a window with a
    # target, a per-window readout is built from nine plus its target), so indexing one by the
    # other's rows can raise or, worse, silently mismatch. Methodological: the ladder compares arms
    # to each other, and that comparison is only meaningful if every arm is scored on exactly the
    # same windows with the same labels. Pairing is enforced here rather than assumed.
    loaded = {}
    for spec in args.arms:
        label, path = spec.split("=", 1)
        loaded[label] = (path, load_arm_windows(path, nxt_all))
    common = set(hist_by_row)
    for label, (_, W) in loaded.items():
        common &= set(int(r) for r in W["rows"])
    common_rows = np.array(sorted(common), dtype=np.int64)
    assert common_rows.size > 0, "arms share no windows; check that every arm used the same user cap and seed"
    # A pairing that keeps only a fraction of the smallest arm is a symptom of arms being built
    # differently, not a legitimate reduction. Fail loudly rather than silently score a probe on an
    # unexplained subset: the Florida collapse to 2731 of 23679 windows looked like a plausible
    # result and was actually two index spaces intersecting by coincidence.
    _smallest = min(W["rows"].size for _, W in loaded.values())
    _retained = common_rows.size / max(_smallest, 1)
    assert _retained >= 0.95, (
        f"pairing kept only {common_rows.size} of the smallest arm's {_smallest} windows "
        f"({_retained:.1%}); arms are not built on a common basis -- refusing to report")
    # Guard the invariant that makes pairing meaningful: a row id must denote the same window, and
    # therefore carry the same label, in every arm. If two arms disagree, their row ids are indexing
    # different frames and every paired comparison built on them would be silently wrong.
    _ref_lab = None
    for label, (_, W) in loaded.items():
        k = np.isin(W["rows"], common_rows)
        o = np.argsort(W["rows"][k], kind="mergesort")
        lab, usr = W["y"][k][o], W["userid"][k][o]
        if _ref_lab is None:
            _ref_lab, _ref_usr, _ref_name = lab, usr, label
        else:
            # BOTH label and user must agree: a row id has to denote the same window of the same
            # user in every arm. Checking labels alone would pass a permutation that happens to
            # preserve the label sequence.
            assert np.array_equal(lab, _ref_lab), (
                f"arm '{label}' and arm '{_ref_name}' assign different labels to the same row ids; "
                "the arms are indexing different frames")
            assert np.array_equal(usr, _ref_usr), (
                f"arm '{label}' and arm '{_ref_name}' assign different USERS to the same row ids; "
                "the arms are indexing different frames")
    res["protocol"]["paired_windows"] = int(common_rows.size)
    res["protocol"]["pairing"] = ("all arms reduced to the windows present in every arm and in the "
                                  "category reference, so every arm is scored on identical rows")
    per_arm_before = {}
    for label, (_, W) in loaded.items():
        per_arm_before[label] = int(W["rows"].size)
    res["protocol"]["windows_per_arm_before_pairing"] = per_arm_before
    print(f"[probe] pairing arms on {common_rows.size} common windows "
          f"(per-arm before: {per_arm_before})", flush=True)

    for label, (path, W) in loaded.items():
        keep = np.isin(W["rows"], common_rows)
        order = np.argsort(W["rows"][keep], kind="mergesort")
        for k in ("seq", "slot8", "slot7", "y", "userid", "rows"):
            if W.get(k) is not None:
                W[k] = W[k][keep][order]
        if W["hist_cat"] is None:
            W["hist_cat"] = np.stack([hist_by_row[int(r)] for r in W["rows"]])
        else:
            W["hist_cat"] = W["hist_cat"][keep][order]
        users = np.unique(W["userid"])
        uu = W["userid"]
        tr_u = np.asarray(split["train_users"]); va_u = np.asarray(split["val_users"])
        # when an arm holds only held-out users, split those users in half (still user-disjoint)
        if np.intersect1d(users, tr_u).size == 0:
            half = np.array_split(np.sort(np.unique(uu)), 2)
            a_tr, a_te = half[0], half[1]
            split_note = "arm contains held-out users only; users split in half, user-disjoint"
        else:
            a_tr, a_te = tr_u, va_u
            split_note = "reported fold split"
        tr = np.where(np.isin(uu, a_tr))[0]; te = np.where(np.isin(uu, a_te))[0]
        assert np.intersect1d(uu[tr], uu[te]).size == 0, "probe split is not user-disjoint"

        y = W["y"]
        arm = {"n_windows": int(len(y)), "n_train_rows": int(len(tr)), "n_test_rows": int(len(te)),
               "n_train_users": int(np.unique(uu[tr]).size),
               "n_test_users": int(np.unique(uu[te]).size),
               "split_note": split_note, "embeddings": path}
        for slot in ("slot8", "slot7"):
            X = W[slot]
            arm[slot] = {
                "linear": _probe_seeds(X[tr], y[tr], X[te], y[te], "linear", n_classes, seeds, args.device),
                "mlp": _probe_seeds(X[tr], y[tr], X[te], y[te], "mlp", n_classes, seeds, args.device),
                "label_shuffled_floor": _probe_seeds(
                    X[tr], np.random.default_rng(0).permutation(y[tr]), X[te], y[te],
                    "linear", n_classes, seeds[:3], args.device),
            }
        arm["both_slots"] = {
            "linear": _probe_seeds(np.concatenate([W["slot7"], W["slot8"]], 1)[tr], y[tr],
                                   np.concatenate([W["slot7"], W["slot8"]], 1)[te], y[te],
                                   "linear", n_classes, seeds, args.device)}
        arm["label_only_baselines"] = label_only_baselines(W["hist_cat"], y, tr, te,
                                                           n_classes, seeds, args.device)
        arm["calibration_slot8"] = calibration(W["slot8"], y, tr, te, n_classes, seeds[:5],
                                                args.device, [0.02, 0.05, 0.1, 0.2, 0.4, 0.8])
        res["arms"][label] = arm
        print(f"[probe] {label}: slot8 linear {arm['slot8']['linear']['mean']:.4f} "
              f"mlp {arm['slot8']['mlp']['mean']:.4f} | "
              f"history {arm['label_only_baselines']['nine_position_category_history']['mean']:.4f} "
              f"| majority {arm['label_only_baselines']['majority_class']:.4f} "
              f"| eps_min {arm['calibration_slot8']['min_detectable_epsilon']}", flush=True)

    outp = Path(args.out); outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(res, indent=2))
    print(f"[probe] wrote {outp}")


if __name__ == "__main__":
    main()
