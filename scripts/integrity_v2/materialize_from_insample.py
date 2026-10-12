"""Materialize a study arm's engine directory from the ONE-SHOT full-graph export.

WHY THIS EXISTS, AND WHEN IT IS VALID
=====================================
`materialize_engine.py` consumes a per-window npz produced by `infer_checkins.py --readout
prefix_forward_only`. That readout costs ONE FORWARD PASS PER WINDOW (infer_checkins.py's own COST
note: "O(n^2) in a user's history length; no saving is claimed"), which is affordable at Alabama
(96 k windows) and ruinous at Texas (3.83 M windows) -- roughly 17 h of single-threaded CPU across
Florida, California and Texas.

The per-window rebuild exists because, on a BIDIRECTIONAL check-in graph, a visit's vector genuinely
depends on which window it appears in: node v is convolved over v+1, so cutting the path at the
window's end changes v's value. That is the whole point of the strict readout.

**A forward-only graph has no such dependence.** Edges are kept only where src < tgt, so messages
flow strictly past -> future and a visit's representation is a function of its own prefix alone.
Truncating the graph at the window's last observed visit therefore cannot change any slot, and the
per-window rebuild recomputes -- at O(n_windows) cost -- exactly what the single full-graph forward
pass already produced. This script uses that identity: it reads `embeddings_insample.parquet` (the
one-shot GPU export the builder already writes) and assembles the same [n_windows, 9, 64] tensor by
indexing, at O(n_windows) memory and no forward passes at all.

Measured equivalence (max |per-window − full-graph|, embeddings of scale ~1.05):

    alabama   2.384e-06      arizona   2.384e-06      istanbul  1.907e-06

and, decisively, slot 8 -- the window's last observed visit, the ONE node whose degree changes under
truncation and hence the only place a normalization difference could appear -- is no worse than
slot 0. The residual is float32 round-off from a different op ordering, not a semantic difference.

THE GUARD
=========
This shortcut is WRONG for a bidirectionally-trained arm, where the per-window rebuild is doing real
work. So this script HARD-FAILS unless the build manifest says the graph was trained forward-only.
Do not add a flag to bypass that check; use `materialize_engine.py` on a real npz instead.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
WINDOW = 9


def build_windows(emb: np.ndarray, ins_uid: np.ndarray, nxt_uid: np.ndarray) -> np.ndarray:
    """Assemble [n_rows_of_next, 9, dim] by indexing the per-visit export.

    For a user with n visits the builder emits max(0, n - 9) windows, window w covering visits
    w..w+8 (target w+9), in that order -- the same convention `encode_user_windows_prefix` uses
    (`n_win = n - WINDOW`) and the same order `materialize_engine.load_arm` assumes.
    """
    dim = emb.shape[1]
    out = np.zeros((len(nxt_uid), WINDOW, dim), dtype=np.float32)

    # stable grouping: positions of each user, in original (visit / row) order
    ins_order = np.argsort(ins_uid, kind="stable")
    nxt_order = np.argsort(nxt_uid, kind="stable")
    ins_sorted, nxt_sorted = ins_uid[ins_order], nxt_uid[nxt_order]
    ins_users, ins_starts = np.unique(ins_sorted, return_index=True)
    nxt_users, nxt_starts = np.unique(nxt_sorted, return_index=True)
    ins_counts = np.diff(np.append(ins_starts, len(ins_sorted)))
    nxt_counts = np.diff(np.append(nxt_starts, len(nxt_sorted)))
    ins_at = dict(zip(ins_users.tolist(), zip(ins_starts.tolist(), ins_counts.tolist())))

    missing = 0
    for u, s_n, c_n in zip(nxt_users.tolist(), nxt_starts.tolist(), nxt_counts.tolist()):
        if u not in ins_at:
            missing += c_n
            continue
        s_i, c_i = ins_at[u]
        vis = ins_order[s_i:s_i + c_i]          # this user's visit rows, in order
        win = nxt_order[s_n:s_n + c_n]          # this user's next.parquet rows, in order
        expect = max(0, c_i - WINDOW)
        assert expect == c_n, (
            f"user {u}: next.parquet has {c_n} windows but {c_i} visits imply {expect}; the row "
            "space does not match the visit sequence, so the arms would not be paired")
        # window k -> visits k..k+8
        idx = vis[np.arange(c_n)[:, None] + np.arange(WINDOW)[None, :]]
        out[win] = emb[idx]
    assert missing == 0, f"{missing} next.parquet rows belong to users absent from the export"
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--state", required=True)
    ap.add_argument("--study-run", required=True,
                    help="the build's cell dir, holding build.json + embeddings_insample.parquet")
    ap.add_argument("--source-engine", default="check2hgi_dk_ovl",
                    help="engine whose next.parquet defines the row space and supplies region labels")
    ap.add_argument("--dest-engine", required=True)
    ap.add_argument("--validate-against-npz", default=None,
                    help="a per-window npz for the SAME arm; asserts agreement and records it")
    ap.add_argument("--tolerance", type=float, default=1e-4,
                    help="max abs diff allowed vs the npz (float32 round-off is ~2e-6)")
    args = ap.parse_args()

    st = args.state.lower()
    run = Path(args.study_run)
    prov = json.loads((run / "build.json").read_text())

    # ---- THE GUARD: this identity holds only for a forward-only graph -------------------
    cg = prov.get("causal_graph") or {}
    if cg.get("forward_only") is not True:
        raise SystemExit(
            f"REFUSING: {run}/build.json does not report a forward-only graph "
            f"(causal_graph.forward_only={cg.get('forward_only')!r}). On a bidirectional arm a "
            "visit's vector IS window-dependent, so the per-window rebuild is doing real work and "
            "this shortcut would silently produce wrong vectors. Use materialize_engine.py with a "
            "real prefix npz instead.")

    src_dir = REPO / "output" / args.source_engine / st / "input"
    nxt = pd.read_parquet(src_dir / "next.parquet", columns=["userid", "next_category"])
    ins = pd.read_parquet(run / "embeddings_insample.parquet")
    dim_cols = [c for c in ins.columns if c.isdigit()]
    dim_cols.sort(key=int)
    emb = ins[dim_cols].to_numpy(np.float32)
    S = build_windows(emb, ins["userid"].to_numpy(np.int64), nxt["userid"].to_numpy(np.int64))
    dim = S.shape[2]

    equiv = None
    if args.validate_against_npz:
        z = np.load(args.validate_against_npz)
        seq = z["seq"].astype(np.float32)
        uu = z["userid"].astype(np.int64)
        stt = z["window_start"].astype(np.int64)
        nu = nxt["userid"].to_numpy(np.int64)
        rows = np.empty(len(uu), dtype=np.int64)
        for u in np.unique(uu):
            m = uu == u
            rw = np.where(nu == u)[0]
            rows[m] = rw[stt[m]]
        d = np.abs(S[rows] - seq)
        equiv = {"n_windows_compared": int(len(rows)),
                 "max_abs_diff": float(d.max()), "mean_abs_diff": float(d.mean()),
                 "slot8_max_abs_diff": float(d[:, 8].max()),
                 "tolerance": args.tolerance}
        print(f"[validate] {st}: max |insample - per_window| = {d.max():.3e} "
              f"(slot8 {d[:, 8].max():.3e}, mean {d.mean():.3e}) over {len(rows)} windows")
        if d.max() > args.tolerance:
            raise SystemExit(
                f"REFUSING: max abs diff {d.max():.3e} exceeds tolerance {args.tolerance:.1e}. "
                "The one-shot export does NOT reproduce the per-window readout for this arm.")

    n_feat = WINDOW * dim
    out = pd.DataFrame(S.reshape(len(S), n_feat), columns=[str(i) for i in range(n_feat)])
    out["userid"] = nxt["userid"].to_numpy()
    out["next_category"] = nxt["next_category"].to_numpy()

    dest = REPO / "output" / args.dest_engine / st / "input"
    dest.mkdir(parents=True, exist_ok=True)
    out.to_parquet(dest / "next.parquet", index=False)

    src_reg = src_dir / "next_region.parquet"
    if src_reg.exists():                      # full row space -> straight copy, order preserved
        shutil.copy(src_reg, dest / "next_region.parquet")
    for extra in src_dir.glob("*.parquet"):
        if extra.name not in ("next.parquet", "next_region.parquet"):
            shutil.copy(extra, dest / extra.name)

    meta = {
        "study": prov.get("study"), "state": st, "cell": prov.get("cell"),
        "source_engine": args.source_engine, "dest_engine": args.dest_engine,
        "method": "one-shot full-graph forward-only export (embeddings_insample.parquet), "
                  "windowed by indexing",
        "why_valid": "the graph is forward-only, so a visit's vector depends on its own prefix "
                     "only and the per-window prefix rebuild is an identity",
        "forward_only": True,
        "study_run": str(run),
        "build_revision": prov.get("revision"),
        "n_windows": int(len(out)), "n_windows_source": int(len(nxt)),
        "window": WINDOW, "embedding_dim": dim,
        "equivalence_vs_per_window_npz": equiv,
        "region_labels": "copied from the source engine, full row space, order preserved",
    }
    (dest.parent / "materialize.json").write_text(json.dumps(meta, indent=2))
    print(f"[materialize-insample] {st}: wrote {dest}/next.parquet "
          f"({len(out)} windows, dim={dim})")


if __name__ == "__main__":
    main()
